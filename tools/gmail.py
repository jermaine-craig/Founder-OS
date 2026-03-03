#!/usr/bin/env python3
"""
Gmail API tool for Founder OS.
Fetches emails, creates drafts, archives messages, and downloads attachments.
"""

import sys
import json
import html
import base64
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.auth import get_service
from tools.config import OUTPUT_DIR, TEMP_DIR


def get_gmail():
    """Return authenticated Gmail API service."""
    return get_service('gmail', 'v1')


def fetch_emails(max_results=20, query='in:inbox', output_file=None):
    """
    Fetch emails from Gmail and save to output folder.

    Args:
        max_results: Maximum number of emails to fetch.
        query: Gmail search query (default: inbox emails).
        output_file: Output filename (default: YYYY-MM-DD-emails.json).

    Returns:
        List of email dicts, or None if no emails found.
    """
    service = get_gmail()

    print(f"Fetching emails (query: {query})...")

    results = service.users().messages().list(
        userId='me',
        maxResults=max_results,
        q=query
    ).execute()

    messages = results.get('messages', [])

    if not messages:
        print("No emails found.")
        return None

    emails = []
    for msg in messages:
        full_msg = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='full'
        ).execute()

        headers = {h['name']: h['value'] for h in full_msg['payload']['headers']}

        body = _extract_body(full_msg['payload'])

        emails.append({
            'id': msg['id'],
            'thread_id': msg['threadId'],
            'from': headers.get('From', ''),
            'to': headers.get('To', ''),
            'subject': headers.get('Subject', ''),
            'date': headers.get('Date', ''),
            'snippet': full_msg.get('snippet', ''),
            'body': body[:5000],
            'labels': full_msg.get('labelIds', []),
        })
        print(f"  - {headers.get('Subject', '(no subject)')[:50]}")

    # Save to output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if not output_file:
        output_file = f"{datetime.now().strftime('%Y-%m-%d')}-emails.json"

    output_path = OUTPUT_DIR / output_file
    with open(output_path, 'w') as f:
        json.dump(emails, f, indent=2)

    print(f"\nSaved {len(emails)} emails to {output_path}")
    return emails


def create_draft(to, subject, body, reply_to_id=None, cc=None):
    """
    Create a draft email in Gmail.

    Args:
        to: Recipient email address.
        subject: Email subject.
        body: Email body text.
        reply_to_id: Message ID to reply to (optional).
        cc: CC recipients, comma-separated (optional).

    Returns:
        Draft resource dict.
    """
    service = get_gmail()

    headers = f"To: {to}\r\n"
    if cc:
        headers += f"Cc: {cc}\r\n"
    headers += f"Subject: {subject}\r\nContent-Type: text/html; charset=UTF-8\r\n"

    html_body = _text_to_html(body)
    raw_message = f"{headers}\r\n{html_body}"
    raw = base64.urlsafe_b64encode(raw_message.encode('utf-8')).decode('utf-8')

    draft_body = {'message': {'raw': raw}}

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
    Archive emails by removing INBOX and UNREAD labels.

    Args:
        message_ids: List of message IDs to archive.
    """
    service = get_gmail()

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
        message_id: Gmail message ID.
        output_dir: Directory to save attachments (default: _temp/attachments).

    Returns:
        List of downloaded file paths.
    """
    service = get_gmail()

    print(f"Fetching attachments for message {message_id}...")

    message = service.users().messages().get(
        userId='me',
        id=message_id,
        format='full'
    ).execute()

    if output_dir:
        from pathlib import Path
        save_dir = Path(output_dir)
    else:
        save_dir = TEMP_DIR / 'attachments'
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


def _extract_body(payload):
    """Extract plain text body from email payload."""
    if 'body' in payload and payload['body'].get('data'):
        return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
    elif 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain' and part['body'].get('data'):
                return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
    return ''


def _text_to_html(text):
    """Convert plain text to simple HTML, preserving paragraphs."""
    escaped = html.escape(text)
    paragraphs = escaped.split('\n\n')
    html_paragraphs = []
    for p in paragraphs:
        p = p.replace('\n', '<br>\n')
        html_paragraphs.append(f'<p style="margin: 0 0 1em 0;">{p}</p>')
    return '\n'.join(html_paragraphs)


def main():
    parser = argparse.ArgumentParser(description='Gmail API for Founder OS')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Fetch
    fetch_parser = subparsers.add_parser('fetch', help='Fetch emails from Gmail')
    fetch_parser.add_argument('-n', '--max', type=int, default=20, help='Max emails to fetch')
    fetch_parser.add_argument('-q', '--query', default='in:inbox', help='Gmail search query')
    fetch_parser.add_argument('-o', '--output', help='Output filename')

    # Draft
    draft_parser = subparsers.add_parser('draft', help='Create a draft email')
    draft_parser.add_argument('--to', required=True, help='Recipient email')
    draft_parser.add_argument('--subject', required=True, help='Email subject')
    draft_parser.add_argument('--body', required=True, help='Email body')
    draft_parser.add_argument('--reply-to', help='Message ID to reply to')
    draft_parser.add_argument('--cc', help='CC recipients (comma-separated)')

    # Archive
    archive_parser = subparsers.add_parser('archive', help='Archive emails')
    archive_parser.add_argument('ids', nargs='+', help='Message IDs to archive')

    # Attachments
    attach_parser = subparsers.add_parser('attachments', help='Download attachments')
    attach_parser.add_argument('id', help='Message ID')
    attach_parser.add_argument('-o', '--output', help='Output directory')

    # Auth
    subparsers.add_parser('auth', help='Test authentication')

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
        get_gmail()
        print("Gmail authentication successful!")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
