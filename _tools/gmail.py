#!/usr/bin/env python3
"""
Gmail API tool for Founder OS.
Fetches emails and creates draft responses.
"""

import os
import json
import base64
import argparse
from pathlib import Path
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.modify',
]

# Paths
SCRIPT_DIR = Path(__file__).parent
CREDS_DIR = SCRIPT_DIR / '.credentials'
CLIENT_SECRET_PATH = CREDS_DIR / 'client_secret.json'
TOKEN_PATH = CREDS_DIR / 'gmail_token.json'
OUTPUT_DIR = SCRIPT_DIR.parent / 'inbox'


def get_gmail_service():
    """Authenticate and return Gmail API service."""
    creds = None

    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CLIENT_SECRET_PATH.exists():
                print(f"ERROR: Client secret not found at {CLIENT_SECRET_PATH}")
                print("\nRun 'python3 setup.py' to configure your credentials.")
                return None

            print("\nOpening browser for Gmail authorization...")
            print("Sign in with your Google account.\n")

            flow = InstalledAppFlow.from_client_secrets_file(
                str(CLIENT_SECRET_PATH), SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save token
        CREDS_DIR.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


def fetch_emails(max_results=20, query='is:unread', output_file=None):
    """
    Fetch emails from Gmail and save to inbox folder.

    Args:
        max_results: Maximum number of emails to fetch
        query: Gmail search query (default: unread emails)
        output_file: Output filename (default: YYYY-MM-DD-emails.json)
    """
    service = get_gmail_service()
    if not service:
        return

    print(f"Fetching emails (query: {query})...")

    results = service.users().messages().list(
        userId='me',
        maxResults=max_results,
        q=query
    ).execute()

    messages = results.get('messages', [])

    if not messages:
        print("No emails found.")
        return

    emails = []
    for msg in messages:
        full_msg = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='full'
        ).execute()

        headers = {h['name']: h['value'] for h in full_msg['payload']['headers']}

        # Extract body
        body = ''
        payload = full_msg['payload']
        if 'body' in payload and payload['body'].get('data'):
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        elif 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain' and part['body'].get('data'):
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break

        emails.append({
            'id': msg['id'],
            'thread_id': msg['threadId'],
            'from': headers.get('From', ''),
            'to': headers.get('To', ''),
            'subject': headers.get('Subject', ''),
            'date': headers.get('Date', ''),
            'snippet': full_msg.get('snippet', ''),
            'body': body[:5000],  # Truncate long emails
            'labels': full_msg.get('labelIds', []),
        })
        print(f"  - {headers.get('Subject', '(no subject)')[:50]}")

    # Save to inbox
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if not output_file:
        output_file = f"{datetime.now().strftime('%Y-%m-%d')}-emails.json"

    output_path = OUTPUT_DIR / output_file
    with open(output_path, 'w') as f:
        json.dump(emails, f, indent=2)

    print(f"\nSaved {len(emails)} emails to {output_path}")
    return emails


def text_to_html(text):
    """Convert plain text to simple HTML, preserving paragraphs."""
    import html
    escaped = html.escape(text)
    paragraphs = escaped.split('\n\n')
    html_paragraphs = []
    for p in paragraphs:
        p = p.replace('\n', '<br>\n')
        html_paragraphs.append(f'<p style="margin: 0 0 1em 0;">{p}</p>')
    return '\n'.join(html_paragraphs)


def create_draft(to, subject, body, reply_to_id=None, cc=None):
    """
    Create a draft email in Gmail.

    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body text
        reply_to_id: Message ID to reply to (optional)
        cc: CC recipients, comma-separated (optional)
    """
    service = get_gmail_service()
    if not service:
        return

    # Build raw message
    headers = f"To: {to}\r\n"
    if cc:
        headers += f"Cc: {cc}\r\n"
    headers += f"Subject: {subject}\r\nContent-Type: text/html; charset=UTF-8\r\n"

    html_body = text_to_html(body)
    raw_message = f"{headers}\r\n{html_body}"
    raw = base64.urlsafe_b64encode(raw_message.encode('utf-8')).decode('utf-8')

    draft_body = {'message': {'raw': raw}}

    # If replying, add thread info
    if reply_to_id:
        original = service.users().messages().get(
            userId='me',
            id=reply_to_id
        ).execute()
        draft_body['message']['threadId'] = original['threadId']

    draft = service.users().drafts().create(
        userId='me',
        body=draft_body
    ).execute()

    print(f"Draft created: {subject}")
    print(f"  Draft ID: {draft['id']}")
    return draft


def archive_emails(message_ids):
    """
    Archive emails by removing INBOX label.

    Args:
        message_ids: List of message IDs to archive
    """
    service = get_gmail_service()
    if not service:
        return

    print(f"Archiving {len(message_ids)} emails...")

    for msg_id in message_ids:
        service.users().messages().modify(
            userId='me',
            id=msg_id,
            body={'removeLabelIds': ['INBOX', 'UNREAD']}
        ).execute()
        print(f"  - Archived {msg_id}")

    print(f"\nArchived {len(message_ids)} emails.")


def get_attachments(message_id, output_dir=None):
    """
    Download attachments from an email.

    Args:
        message_id: Gmail message ID
        output_dir: Directory to save attachments

    Returns:
        List of downloaded file paths
    """
    service = get_gmail_service()
    if not service:
        return []

    print(f"Fetching attachments for message {message_id}...")

    message = service.users().messages().get(
        userId='me',
        id=message_id,
        format='full'
    ).execute()

    if output_dir:
        save_dir = Path(output_dir)
    else:
        save_dir = OUTPUT_DIR / 'attachments'
    save_dir.mkdir(parents=True, exist_ok=True)

    downloaded = []

    def process_parts(parts):
        for part in parts:
            filename = part.get('filename', '')
            if filename and part.get('body', {}).get('attachmentId'):
                attachment_id = part['body']['attachmentId']
                attachment = service.users().messages().attachments().get(
                    userId='me',
                    messageId=message_id,
                    id=attachment_id
                ).execute()

                data = base64.urlsafe_b64decode(attachment['data'])
                filepath = save_dir / filename
                with open(filepath, 'wb') as f:
                    f.write(data)

                downloaded.append(filepath)
                print(f"  - Saved: {filename}")

            if 'parts' in part:
                process_parts(part['parts'])

    payload = message.get('payload', {})
    if 'parts' in payload:
        process_parts(payload['parts'])

    if not downloaded:
        print("  No attachments found.")
    else:
        print(f"\nDownloaded {len(downloaded)} attachment(s) to {save_dir}")

    return downloaded


def main():
    parser = argparse.ArgumentParser(description='Gmail API for Founder OS')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Fetch command
    fetch_parser = subparsers.add_parser('fetch', help='Fetch emails from Gmail')
    fetch_parser.add_argument('-n', '--max', type=int, default=20, help='Max emails to fetch')
    fetch_parser.add_argument('-q', '--query', default='is:unread', help='Gmail search query')
    fetch_parser.add_argument('-o', '--output', help='Output filename')

    # Draft command
    draft_parser = subparsers.add_parser('draft', help='Create a draft email')
    draft_parser.add_argument('--to', required=True, help='Recipient email')
    draft_parser.add_argument('--subject', required=True, help='Email subject')
    draft_parser.add_argument('--body', required=True, help='Email body')
    draft_parser.add_argument('--reply-to', help='Message ID to reply to')
    draft_parser.add_argument('--cc', help='CC recipients (comma-separated)')

    # Archive command
    archive_parser = subparsers.add_parser('archive', help='Archive emails')
    archive_parser.add_argument('ids', nargs='+', help='Message IDs to archive')

    # Attachments command
    attach_parser = subparsers.add_parser('attachments', help='Download attachments')
    attach_parser.add_argument('id', help='Message ID')
    attach_parser.add_argument('-o', '--output', help='Output directory')

    # Auth command
    auth_parser = subparsers.add_parser('auth', help='Authenticate with Gmail')

    args = parser.parse_args()

    if args.command == 'fetch':
        fetch_emails(max_results=args.max, query=args.query, output_file=args.output)
    elif args.command == 'draft':
        create_draft(args.to, args.subject, args.body, args.reply_to, cc=args.cc)
    elif args.command == 'archive':
        archive_emails(args.ids)
    elif args.command == 'attachments':
        get_attachments(args.id, output_dir=args.output)
    elif args.command == 'auth':
        service = get_gmail_service()
        if service:
            print("Gmail authentication successful!")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
