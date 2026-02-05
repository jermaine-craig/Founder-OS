# Founder OS

A personal operating system that handles your email and calendar, so you can stay in your genius zone.

---

## What's Included

- **Email triage** — Fetch, categorize, and draft replies to your emails
- **Calendar management** — View schedule, check availability, create events
- **Claude Code integration** — Use simple commands like `/triage` and `/calendar`

---

## Quick Start

### 1. Clone this repo

```bash
git clone https://github.com/other-shapes/founder-os.git
cd founder-os
```

### 2. Install dependencies

```bash
pip install google-auth google-auth-oauthlib google-api-python-client
```

### 3. Run setup wizard

```bash
python3 setup.py
```

The wizard will guide you through:
- Creating a Google Cloud project
- Enabling Gmail and Calendar APIs
- Authenticating your account
- Configuring your timezone

### 4. Open Claude Code

```bash
claude
```

### 5. Try it out

```
/triage     - Process your inbox
/calendar   - Check your schedule
```

---

## Commands

| Command | What it does |
|---------|--------------|
| `/triage` | Fetch unread emails, categorize them, draft replies |
| `/calendar` | Show upcoming events for the next 7 days |
| `/prep <meeting>` | Get context and talking points before a call |

---

## Manual Tool Usage

You can also use the tools directly:

### Email

```bash
# Fetch unread emails
python3 _tools/gmail.py fetch

# Fetch with custom query
python3 _tools/gmail.py fetch -q "from:important@example.com"

# Create a draft
python3 _tools/gmail.py draft --to "someone@example.com" --subject "Hello" --body "Message here"

# Archive emails
python3 _tools/gmail.py archive <message_id>
```

### Calendar

```bash
# List upcoming events
python3 _tools/gcal.py list

# List next 14 days
python3 _tools/gcal.py list -d 14

# Check availability on a date
python3 _tools/gcal.py availability 2024-03-15

# Create an event
python3 _tools/gcal.py create --title "Team sync" --start "2024-03-15 14:00"
```

---

## Folder Structure

```
founder-os/
├── .claude/              # Claude Code configuration
│   └── CLAUDE.md         # Your OS instructions
├── _tools/               # Gmail and Calendar scripts
│   ├── gmail.py
│   ├── gcal.py
│   └── .credentials/     # API tokens (git-ignored)
├── _logs/                # Daily execution logs
├── inbox/                # Email exports (JSON)
├── assistant/            # Workflow documentation
│   ├── email-triage/
│   └── calendar/
├── setup.py              # Setup wizard
└── README.md
```

---

## Customization

### Add Your Own Rules

Edit `.claude/CLAUDE.md` to:
- Add custom commands
- Change how emails are categorized
- Adjust the assistant's behavior

### Change Your Timezone

Edit `_tools/gcal.py` and update the `DEFAULT_TZ` variable, or re-run `setup.py`.

### Add More Tools

The `_tools/` folder can hold any Python scripts. Common additions:
- Notion integration
- Slack notifications
- Task manager sync

---

## How It Works

1. **Gmail API** fetches your emails and creates drafts
2. **Calendar API** reads and creates events
3. **Claude Code** uses these tools via the instructions in `.claude/CLAUDE.md`
4. **You stay in control** — nothing sends or archives without your approval

---

## Requirements

- Python 3.8+
- Google account with Gmail and Calendar
- Claude Code (for the `/triage` and `/calendar` commands)

---

## Troubleshooting

### "Client secret not found"

Run the setup wizard: `python3 setup.py`

### "Token expired"

Re-authenticate:
```bash
python3 _tools/gmail.py auth
python3 _tools/gcal.py auth
```

### "Access blocked"

Make sure you added yourself as a test user in the Google Cloud OAuth consent screen.

---

## License

MIT — use it however you want.

---

Built by [Other Shapes](https://othershapes.co)
