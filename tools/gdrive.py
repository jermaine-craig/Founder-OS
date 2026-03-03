#!/usr/bin/env python3
"""
Google Drive API tool for Founder OS.
List, search, read, and download files from Google Drive.
"""

import io
import json
import argparse
from pathlib import Path
from datetime import datetime

from googleapiclient.http import MediaIoBaseDownload

from tools.auth import get_service
from tools.config import OUTPUT_DIR, TEMP_DIR


# Google Workspace MIME types and their export formats
EXPORT_MAP = {
    'application/vnd.google-apps.document': ('text/plain', '.txt'),
    'application/vnd.google-apps.spreadsheet': ('text/csv', '.csv'),
    'application/vnd.google-apps.presentation': ('text/plain', '.txt'),
}


def get_drive():
    """Return authenticated Drive API service."""
    return get_service('drive', 'v3')


def list_files(max_results=20, folder_id=None, mime_type=None, output_file=None):
    """
    List recent files from Google Drive.

    Args:
        max_results: Maximum number of files to return.
        folder_id: Filter by parent folder ID.
        mime_type: Filter by MIME type.
        output_file: Optional output filename.

    Returns:
        List of file metadata dicts.
    """
    service = get_drive()

    query_parts = ["trashed = false"]
    if folder_id:
        query_parts.append(f"'{folder_id}' in parents")
    if mime_type:
        query_parts.append(f"mimeType = '{mime_type}'")
    query = " and ".join(query_parts)

    print(f"Listing files from Drive...")

    results = service.files().list(
        q=query,
        pageSize=max_results,
        fields="files(id, name, mimeType, modifiedTime, size, webViewLink)",
        orderBy="modifiedTime desc"
    ).execute()

    files = results.get('files', [])

    if not files:
        print("No files found.")
        return []

    for f in files:
        modified = f.get('modifiedTime', '')[:10]
        size = _format_size(int(f.get('size', 0))) if f.get('size') else ''
        print(f"  {modified}  {f['name']:<40}  {size}")

    if output_file:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = OUTPUT_DIR / output_file
        with open(output_path, 'w') as out:
            json.dump(files, out, indent=2)
        print(f"\nSaved {len(files)} files to {output_path}")

    return files


def search_files(query_text, max_results=20, output_file=None):
    """
    Search files by name or content.

    Args:
        query_text: Search query string.
        max_results: Maximum number of results.
        output_file: Optional output filename.

    Returns:
        List of matching file metadata dicts.
    """
    service = get_drive()

    print(f"Searching Drive for: {query_text}")

    results = service.files().list(
        q=f"fullText contains '{query_text}' and trashed = false",
        pageSize=max_results,
        fields="files(id, name, mimeType, modifiedTime, size, webViewLink)",
        orderBy="modifiedTime desc"
    ).execute()

    files = results.get('files', [])

    if not files:
        print("No matching files found.")
        return []

    for f in files:
        modified = f.get('modifiedTime', '')[:10]
        print(f"  {modified}  {f['name']}")

    if output_file:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = OUTPUT_DIR / output_file
        with open(output_path, 'w') as out:
            json.dump(files, out, indent=2)
        print(f"\nSaved {len(files)} results to {output_path}")

    return files


def read_file(file_id):
    """
    Read file content from Drive.

    Google Docs/Sheets/Slides are exported as plain text.
    Other files are downloaded to _temp/ and the path is returned.

    Args:
        file_id: Google Drive file ID.

    Returns:
        String content for exportable files, or path to downloaded file.
    """
    service = get_drive()

    metadata = service.files().get(
        fileId=file_id,
        fields="id, name, mimeType, size"
    ).execute()

    name = metadata['name']
    mime = metadata['mimeType']

    print(f"Reading: {name} ({mime})")

    # Google Workspace files: export as text
    if mime in EXPORT_MAP:
        export_mime, _ = EXPORT_MAP[mime]
        content = service.files().export(
            fileId=file_id,
            mimeType=export_mime
        ).execute()
        text = content.decode('utf-8')
        print(f"  Exported as text ({len(text)} chars)")
        return text

    # Binary files: download
    return _download_binary(service, file_id, name)


def download_file(file_id, output_dir=None):
    """
    Download a file from Drive to local filesystem.

    Args:
        file_id: Google Drive file ID.
        output_dir: Directory to save the file (default: _temp/).

    Returns:
        Path to downloaded file.
    """
    service = get_drive()

    metadata = service.files().get(
        fileId=file_id,
        fields="id, name, mimeType"
    ).execute()

    name = metadata['name']
    mime = metadata['mimeType']

    # Google Workspace files: export
    if mime in EXPORT_MAP:
        export_mime, ext = EXPORT_MAP[mime]
        content = service.files().export(
            fileId=file_id,
            mimeType=export_mime
        ).execute()

        save_dir = Path(output_dir) if output_dir else TEMP_DIR
        save_dir.mkdir(parents=True, exist_ok=True)
        filepath = save_dir / f"{name}{ext}"
        filepath.write_bytes(content)
        print(f"  Exported: {filepath}")
        return str(filepath)

    return _download_binary(service, file_id, name, output_dir)


def get_file_info(file_id):
    """
    Get detailed metadata for a file.

    Args:
        file_id: Google Drive file ID.

    Returns:
        Dict of file metadata.
    """
    service = get_drive()

    metadata = service.files().get(
        fileId=file_id,
        fields="id, name, mimeType, modifiedTime, createdTime, size, "
               "webViewLink, owners, shared, permissions"
    ).execute()

    print(f"  Name: {metadata['name']}")
    print(f"  Type: {metadata['mimeType']}")
    print(f"  Modified: {metadata.get('modifiedTime', 'unknown')}")
    if metadata.get('size'):
        print(f"  Size: {_format_size(int(metadata['size']))}")
    if metadata.get('webViewLink'):
        print(f"  Link: {metadata['webViewLink']}")

    return metadata


def _download_binary(service, file_id, name, output_dir=None):
    """Download a binary file from Drive."""
    request = service.files().get_media(fileId=file_id)
    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)

    done = False
    while not done:
        _, done = downloader.next_chunk()

    save_dir = Path(output_dir) if output_dir else TEMP_DIR
    save_dir.mkdir(parents=True, exist_ok=True)
    filepath = save_dir / name

    with open(filepath, 'wb') as f:
        f.write(buffer.getvalue())

    print(f"  Downloaded: {filepath}")
    return str(filepath)


def _format_size(size_bytes):
    """Format file size for display."""
    if size_bytes == 0:
        return ''
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.0f} {unit}" if unit == 'B' else f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def main():
    parser = argparse.ArgumentParser(description='Google Drive API for Founder OS')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # List
    list_parser = subparsers.add_parser('list', help='List recent files')
    list_parser.add_argument('-n', '--max', type=int, default=20, help='Max files')
    list_parser.add_argument('--folder', help='Filter by folder ID')
    list_parser.add_argument('--type', help='Filter by MIME type')
    list_parser.add_argument('-o', '--output', help='Output filename')

    # Search
    search_parser = subparsers.add_parser('search', help='Search files')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('-n', '--max', type=int, default=20, help='Max results')
    search_parser.add_argument('-o', '--output', help='Output filename')

    # Read
    read_parser = subparsers.add_parser('read', help='Read file content')
    read_parser.add_argument('file_id', help='File ID')

    # Download
    dl_parser = subparsers.add_parser('download', help='Download a file')
    dl_parser.add_argument('file_id', help='File ID')
    dl_parser.add_argument('-o', '--output', help='Output directory')

    # Info
    info_parser = subparsers.add_parser('info', help='Get file metadata')
    info_parser.add_argument('file_id', help='File ID')

    # Auth
    subparsers.add_parser('auth', help='Test authentication')

    args = parser.parse_args()

    if args.command == 'list':
        list_files(max_results=args.max, folder_id=args.folder,
                   mime_type=args.type, output_file=args.output)
    elif args.command == 'search':
        search_files(args.query, max_results=args.max, output_file=args.output)
    elif args.command == 'read':
        content = read_file(args.file_id)
        if isinstance(content, str) and not content.startswith('/'):
            print("\n" + content)
    elif args.command == 'download':
        download_file(args.file_id, output_dir=args.output)
    elif args.command == 'info':
        get_file_info(args.file_id)
    elif args.command == 'auth':
        get_drive()
        print("Drive authentication successful!")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
