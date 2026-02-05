# Calendar Management

View schedule, check availability, and create events.

---

## When to Use

- Morning planning
- Responding to scheduling requests
- Before meetings (for context)
- When asked about availability

---

## Commands

### View Schedule

```bash
# Next 7 days (default)
python3 _tools/gcal.py list

# Next 14 days
python3 _tools/gcal.py list -d 14

# Save to file
python3 _tools/gcal.py list -o calendar.json
```

### Check Availability

```bash
# Check a specific date (9am-5pm default)
python3 _tools/gcal.py availability 2024-03-15

# Custom hours
python3 _tools/gcal.py availability 2024-03-15 --start-hour 8 --end-hour 18
```

### Create Event

```bash
# Basic event (1 hour default)
python3 _tools/gcal.py create --title "Team sync" --start "2024-03-15 14:00"

# With duration
python3 _tools/gcal.py create --title "Quick call" --start "2024-03-15 14:00" --duration 30

# With attendees (sends invites)
python3 _tools/gcal.py create --title "Meeting" --start "2024-03-15 14:00" --attendees john@example.com jane@example.com
```

### Delete Event

```bash
python3 _tools/gcal.py delete <event_id>
```

---

## Process

### Morning Review

1. Run `python3 _tools/gcal.py list`
2. Summarize today's schedule
3. Flag any conflicts or tight transitions
4. Note prep needed for upcoming meetings

### Availability Requests

When someone asks "When are you free?":

1. Ask which date(s) they're considering
2. Run availability check for those dates
3. Present free slots clearly
4. Let user choose which to offer

### Creating Events

Only create events when:
- User explicitly asks to schedule something
- All details are provided (title, time, duration)
- User confirms the details

---

## Never

- Double-book without flagging the conflict
- Create events without explicit request
- Share detailed calendar externally
- Assume scheduling intent from vague requests

---

## Output Location

`assistant/calendar/output/YYYY-MM-DD-calendar.md`
