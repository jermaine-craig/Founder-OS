# Founder OS

A personal operating system that handles your email, calendar, and meeting prep — so you can stay in your genius zone.

---

## What's Included

- **Email triage** — Categorize your inbox and draft replies
- **Calendar management** — View schedule, check availability, create events
- **Meeting prep** — Get context on attendees from past email interactions
- **Natural language** — Just tell Claude what you need

---

## Quick Start

### Option 1: One-line install (recommended)

```bash
curl -fsSL https://os.engineering/install | bash
```

### Option 2: Homebrew (macOS/Linux)

```bash
brew install jermaine-craig/os/founder-os
founder-os-setup
```

### Option 3: Manual install

```bash
# Clone the repo
git clone https://github.com/jermaine-craig/Founder-OS.git
cd Founder-OS

# Install dependencies
pip install google-auth google-auth-oauthlib google-api-python-client

# Run setup wizard
python3 setup.py
```

The wizard will guide you through:
- Creating a Google Cloud project
- Enabling Gmail and Calendar APIs
- Authenticating your account
- Configuring your timezone

### Then open Claude Code

```bash
claude
```

### Start talking

Just ask for what you need:

```
"Help me with my emails"

"What's on my calendar this week?"

"Can you schedule a call between me and john@example.com for next Tuesday?"

"Help me prepare for my meeting with Sarah tomorrow"

"When am I free on Friday?"
```

---

## What You Can Ask

### Email

- "Help me with my emails"
- "Check my inbox"
- "Draft a reply to the email from John"
- "Archive the newsletters"

### Calendar

- "What's on my calendar today?"
- "When am I free this week?"
- "Schedule a 30-minute call with sarah@example.com on Thursday at 2pm"
- "What meetings do I have tomorrow?"

### Meeting Prep

- "Help me prepare for my meeting with David"
- "What's the context on my call with Acme Corp?"
- "Pull up my past conversations with jane@example.com"

---

## How It Works

1. **Gmail API** — fetches your emails, creates drafts, archives messages
2. **Calendar API** — reads your schedule, checks availability, creates events
3. **Claude** — understands what you need and uses the right tools
4. **You stay in control** — nothing sends or archives without your approval

---

## Make It Your Own

This is your OS. Claude can help you customize it.

Just ask:
- "Add a workflow that summarizes my week every Friday"
- "Change how you categorize my emails"
- "Create a command that pulls my meeting notes"
- "Add Notion integration"

The configuration lives in `.claude/CLAUDE.md`. You can edit it directly or ask Claude to modify it for you.

---

## Folder Structure

```
founder-os/
├── .claude/              # Your OS configuration
│   └── CLAUDE.md         # Instructions and rules
├── _tools/               # Gmail and Calendar integrations
├── _logs/                # Daily execution logs
├── inbox/                # Email exports
├── assistant/            # Workflow documentation
└── setup.py              # Setup wizard
```

---

## Requirements

- Python 3.8+
- Google account with Gmail and Calendar
- [Claude Code](https://claude.ai/code)

---

## Troubleshooting

### "Client secret not found"

Run the setup wizard: `python3 setup.py`

### "Token expired"

Ask Claude: "Re-authenticate my Gmail and Calendar"

### "Access blocked"

Make sure you added yourself as a test user in the Google Cloud OAuth consent screen.

---

## License

MIT — use it however you want.

---

Built by [Other Shapes](https://othershapes.co)
