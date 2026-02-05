# Founder OS

Personal operating system for {{NAME}}.

---

## About You

- **Name:** {{NAME}}
- **Timezone:** {{TIMEZONE}}

---

## Available Tools

### Email

```bash
python3 _tools/gmail.py fetch              # Get unread emails
python3 _tools/gmail.py fetch -q "is:inbox" # Custom query
python3 _tools/gmail.py draft --to X --subject Y --body Z
python3 _tools/gmail.py archive <message_ids>
```

### Calendar

```bash
python3 _tools/gcal.py list                # Next 7 days
python3 _tools/gcal.py list -d 14          # Next 14 days
python3 _tools/gcal.py availability DATE   # Free slots on date
python3 _tools/gcal.py create --title X --start "YYYY-MM-DD HH:MM"
```

---

## Commands

- `/triage` — Process inbox: fetch emails, categorize, draft replies
- `/calendar` — Show upcoming events and check availability
- `/prep <meeting>` — Pull context and talking points before a call

---

## Workflows

### Email Triage (`/triage`)

1. Fetch unread emails
2. Categorize each email:
   - **Urgent** — needs response today
   - **Action Required** — needs response this week
   - **FYI** — read and archive
   - **Archive** — no action needed
3. Draft replies for Urgent and Action Required
4. Present summary for approval
5. Archive emails only with explicit confirmation

### Calendar Management (`/calendar`)

1. Show events for next 7 days
2. Check availability for specific dates
3. Create events when requested

---

## Rules

- **Never send emails without explicit approval** — always draft first
- **Never archive without confirmation** — present recommendations, wait for approval
- **Log actions** — record what was done in `_logs/YYYY-MM-DD.md`
- **Timestamp outputs** — use format `YYYY-MM-DD-description.ext`
- **Keep outputs organized** — save to workflow `output/` folders

---

## File Structure

```
founder-os/
├── _tools/           # Gmail and Calendar scripts
├── _logs/            # Daily execution logs
├── inbox/            # Email and calendar JSON exports
└── assistant/        # Workflow SOPs and outputs
    ├── email-triage/
    └── calendar/
```
