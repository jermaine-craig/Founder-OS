#!/usr/bin/env python3
"""
Google Calendar API tool for Founder OS.
List, create, check availability, and delete calendar events.
"""

import json
import argparse
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from tools.auth import get_service
from tools.config import OUTPUT_DIR, get_timezone


def get_calendar():
    """Return authenticated Calendar API service."""
    return get_service('calendar', 'v3')


def parse_datetime(dt_str, tz=None):
    """
    Parse datetime string into timezone-aware datetime object.

    Supports formats: YYYY-MM-DD HH:MM, YYYY-MM-DDTHH:MM, DD/MM/YYYY HH:MM, etc.
    """
    tz_info = ZoneInfo(tz or get_timezone())

    formats = [
        '%Y-%m-%d %H:%M',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%dT%H:%M',
        '%Y-%m-%dT%H:%M:%S',
        '%d/%m/%Y %H:%M',
        '%d-%m-%Y %H:%M',
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(dt_str, fmt)
            return dt.replace(tzinfo=tz_info)
        except ValueError:
            continue

    raise ValueError(f"Could not parse datetime: {dt_str}")


def format_event(event):
    """Format a calendar event for display."""
    start = event['start'].get('dateTime', event['start'].get('date'))
    end = event['end'].get('dateTime', event['end'].get('date'))

    if 'T' in start:
        start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
        time_str = f"{start_dt.strftime('%H:%M')} - {end_dt.strftime('%H:%M')}"
        date_str = start_dt.strftime('%Y-%m-%d')
    else:
        time_str = "All day"
        date_str = start

    return {
        'id': event['id'],
        'summary': event.get('summary', '(No title)'),
        'date': date_str,
        'time': time_str,
        'location': event.get('location', ''),
        'description': event.get('description', ''),
        'attendees': [a.get('email') for a in event.get('attendees', [])],
        'link': event.get('htmlLink', ''),
    }


def list_events(days=7, max_results=20, output_file=None):
    """
    List upcoming calendar events.

    Args:
        days: Number of days to look ahead.
        max_results: Maximum number of events.
        output_file: Optional output filename.

    Returns:
        List of formatted event dicts.
    """
    service = get_calendar()

    now = datetime.utcnow().isoformat() + 'Z'
    end = (datetime.utcnow() + timedelta(days=days)).isoformat() + 'Z'

    print(f"Fetching events for next {days} days...")

    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        timeMax=end,
        maxResults=max_results,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])

    if not events:
        print("No upcoming events found.")
        return []

    formatted = []
    current_date = None

    for event in events:
        fmt = format_event(event)
        formatted.append(fmt)

        if fmt['date'] != current_date:
            current_date = fmt['date']
            print(f"\n  {current_date}")

        attendee_count = len(fmt['attendees'])
        attendee_str = f" ({attendee_count} attendees)" if fmt['attendees'] else ""
        print(f"    {fmt['time']}  {fmt['summary']}{attendee_str}")

    if output_file:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = OUTPUT_DIR / output_file
        with open(output_path, 'w') as f:
            json.dump(formatted, f, indent=2)
        print(f"\nSaved {len(formatted)} events to {output_path}")

    return formatted


def create_event(summary, start, end=None, duration=60, description='',
                 location='', attendees=None, timezone=None):
    """
    Create a calendar event.

    Args:
        summary: Event title.
        start: Start datetime (string).
        end: End datetime (string, optional).
        duration: Duration in minutes if end not specified.
        description: Event description.
        location: Event location.
        attendees: List of email addresses.
        timezone: Timezone override.
    """
    service = get_calendar()

    tz = timezone or get_timezone()
    start_dt = parse_datetime(start, tz)

    if end:
        end_dt = parse_datetime(end, tz)
    else:
        end_dt = start_dt + timedelta(minutes=duration)

    event_body = {
        'summary': summary,
        'start': {
            'dateTime': start_dt.isoformat(),
            'timeZone': tz,
        },
        'end': {
            'dateTime': end_dt.isoformat(),
            'timeZone': tz,
        },
    }

    if description:
        event_body['description'] = description

    if location:
        event_body['location'] = location

    if attendees:
        event_body['attendees'] = [{'email': email} for email in attendees]
        event_body['sendUpdates'] = 'all'

    event = service.events().insert(
        calendarId='primary',
        body=event_body
    ).execute()

    print(f"Event created: {summary}")
    print(f"  When: {start_dt.strftime('%Y-%m-%d %H:%M')} - {end_dt.strftime('%H:%M')} ({tz})")
    if attendees:
        print(f"  Invites sent to: {', '.join(attendees)}")
    print(f"  Link: {event.get('htmlLink')}")

    return event


def check_availability(date, start_hour=9, end_hour=17):
    """
    Check available slots on a given date.

    Args:
        date: Date to check (YYYY-MM-DD).
        start_hour: Start of working hours.
        end_hour: End of working hours.

    Returns:
        Dict with 'busy' and 'free' slot lists.
    """
    service = get_calendar()

    tz_name = get_timezone()
    tz = ZoneInfo(tz_name)

    check_date = datetime.strptime(date, '%Y-%m-%d').replace(tzinfo=tz)
    day_start = check_date.replace(hour=start_hour, minute=0)
    day_end = check_date.replace(hour=end_hour, minute=0)

    print(f"Checking availability on {date} ({start_hour}:00 - {end_hour}:00 {tz_name})...")

    events_result = service.events().list(
        calendarId='primary',
        timeMin=day_start.isoformat(),
        timeMax=day_end.isoformat(),
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])

    busy_slots = []
    for event in events:
        start = event['start'].get('dateTime')
        end = event['end'].get('dateTime')
        if start and end:
            busy_slots.append({
                'start': datetime.fromisoformat(start.replace('Z', '+00:00')),
                'end': datetime.fromisoformat(end.replace('Z', '+00:00')),
                'summary': event.get('summary', '(busy)')
            })

    free_slots = []
    current = day_start

    for busy in sorted(busy_slots, key=lambda x: x['start']):
        if current < busy['start']:
            free_slots.append({
                'start': current,
                'end': busy['start']
            })
        current = max(current, busy['end'])

    if current < day_end:
        free_slots.append({
            'start': current,
            'end': day_end
        })

    if busy_slots:
        print("\n  Busy:")
        for slot in busy_slots:
            print(f"    {slot['start'].strftime('%H:%M')} - {slot['end'].strftime('%H:%M')}  {slot['summary']}")

    if free_slots:
        print("\n  Available:")
        for slot in free_slots:
            duration = (slot['end'] - slot['start']).seconds // 60
            print(f"    {slot['start'].strftime('%H:%M')} - {slot['end'].strftime('%H:%M')} ({duration} min)")
    else:
        print("\n  No availability in this time range.")

    return {'busy': busy_slots, 'free': free_slots}


def delete_event(event_id):
    """Delete a calendar event by ID."""
    service = get_calendar()

    service.events().delete(
        calendarId='primary',
        eventId=event_id
    ).execute()

    print(f"Event deleted: {event_id}")


def main():
    parser = argparse.ArgumentParser(description='Google Calendar API for Founder OS')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # List
    list_parser = subparsers.add_parser('list', help='List upcoming events')
    list_parser.add_argument('-d', '--days', type=int, default=7, help='Days to look ahead')
    list_parser.add_argument('-n', '--max', type=int, default=20, help='Max events')
    list_parser.add_argument('-o', '--output', help='Output filename')

    # Create
    create_parser = subparsers.add_parser('create', help='Create an event')
    create_parser.add_argument('--title', required=True, help='Event title')
    create_parser.add_argument('--start', required=True, help='Start time (YYYY-MM-DD HH:MM)')
    create_parser.add_argument('--end', help='End time (YYYY-MM-DD HH:MM)')
    create_parser.add_argument('--duration', type=int, default=60, help='Duration in minutes')
    create_parser.add_argument('--description', default='', help='Event description')
    create_parser.add_argument('--location', default='', help='Event location')
    create_parser.add_argument('--attendees', nargs='+', help='Attendee emails')
    create_parser.add_argument('--tz', help='Timezone override')

    # Availability
    avail_parser = subparsers.add_parser('availability', help='Check availability')
    avail_parser.add_argument('date', help='Date to check (YYYY-MM-DD)')
    avail_parser.add_argument('--start-hour', type=int, default=9, help='Working hours start')
    avail_parser.add_argument('--end-hour', type=int, default=17, help='Working hours end')

    # Delete
    delete_parser = subparsers.add_parser('delete', help='Delete an event')
    delete_parser.add_argument('event_id', help='Event ID to delete')

    # Auth
    subparsers.add_parser('auth', help='Test authentication')

    args = parser.parse_args()

    if args.command == 'list':
        list_events(days=args.days, max_results=args.max, output_file=args.output)
    elif args.command == 'create':
        create_event(
            summary=args.title,
            start=args.start,
            end=args.end,
            duration=args.duration,
            description=args.description,
            location=args.location,
            attendees=args.attendees,
            timezone=args.tz
        )
    elif args.command == 'availability':
        check_availability(args.date, args.start_hour, args.end_hour)
    elif args.command == 'delete':
        delete_event(args.event_id)
    elif args.command == 'auth':
        get_calendar()
        print("Calendar authentication successful!")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
