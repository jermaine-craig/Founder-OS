---
name: calendar
description: Check your schedule, availability, or create events. Use when the user asks about their calendar, schedule, availability, or wants to schedule something.
argument-hint: "calendar", "calendar today", "free on friday?"
---

# Calendar Skill

View the user's schedule, check availability, and create events.

## Commands

All commands run from the project root.

### View schedule

Default: next 7 days.

```bash
python3 tools/gcal.py list
```

Custom range:

```bash
python3 tools/gcal.py list -d 14    # next 14 days
python3 tools/gcal.py list -d 1     # today only
```

### Check availability

Show free and busy slots for a specific date:

```bash
python3 tools/gcal.py availability YYYY-MM-DD
```

Custom working hours:

```bash
python3 tools/gcal.py availability YYYY-MM-DD --start-hour 8 --end-hour 18
```

### Create events

```bash
python3 tools/gcal.py create --title "Call with Sarah" --start "YYYY-MM-DD HH:MM" --duration 30
```

With attendees:

```bash
python3 tools/gcal.py create --title "Team sync" --start "YYYY-MM-DD HH:MM" --duration 60 --attendees "sarah@example.com" "mike@example.com"
```

### Delete events

```bash
python3 tools/gcal.py delete EVENT_ID
```

## Workflow

### When the user asks about their schedule

1. Determine the relevant timeframe (today, this week, next N days)
2. Run `python3 tools/gcal.py list -d N`
3. Present events grouped by day
4. Highlight conflicts (overlapping events)

### When the user asks about availability

1. Parse the date they are asking about
2. Run `python3 tools/gcal.py availability YYYY-MM-DD`
3. Present free slots clearly, including the duration of each slot
4. If they ask "am I free at 2pm on Friday?", check availability for that date and confirm whether the specific time is open

### When the user wants to create an event

1. Confirm all details before creating:
   - Title
   - Date and time
   - Duration (default: 60 minutes)
   - Attendees (if any)
2. Check for conflicts by running availability first
3. If there is a conflict, warn the user before proceeding
4. Only create the event after explicit confirmation

## Safety Rules

- **Never create events without an explicit request and confirmation.** Always confirm the details first.
- **Always flag scheduling conflicts.** If a new event overlaps with an existing one, tell the user.
- **Show free slot durations.** When presenting availability, include how long each free window is.
- **Treat calendar data as private.** Do not share schedule details externally.
