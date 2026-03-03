# Founder OS

A personal operating system that handles your email, calendar, and meeting prep, so you can stay in your genius zone.

## What It Does

- **Email triage**: Categorise your inbox, draft replies, archive with approval
- **Calendar management**: View schedule, check availability, create events
- **Meeting prep**: Context from emails and Drive for every meeting
- **Research**: Look up topics with Perplexity (optional)

## Quick Start

```bash
# Clone the repo
git clone https://github.com/jermaine-craig/Founder-OS.git
cd Founder-OS

# Install dependencies
pip install -r requirements.txt

# Run setup wizard
python3 setup.py
```

The wizard guides you through:
- Creating a Google Cloud project
- Enabling Gmail, Calendar, and Drive APIs
- Authenticating your account
- Configuring your name and timezone
- Optional Perplexity API key for research

Then open Claude Code:

```bash
claude
```

## Usage

Just ask for what you need:

```
"Help me with my emails"
"What's on my calendar this week?"
"When am I free on Friday?"
"Prep for my call with Sarah tomorrow"
"Find the meeting transcript from last week"
```

Or use slash commands for guided workflows:

| Command | What it does |
|---------|-------------|
| `/email` | Process your inbox, categorise, draft replies |
| `/calendar` | Check schedule, availability, create events |
| `/meeting` | Prepare for a meeting with full context |
| `/research` | Research a topic with Perplexity |

## How It Works

```
You (natural language) → Claude → Tools (Python) → Google APIs
                                ↓
                          You stay in control
                    (nothing sends without approval)
```

- **Tools** (`tools/`): Python scripts that talk to Google APIs. Deterministic, testable.
- **Skills** (`.claude/skills/`): Instructions that tell Claude when and how to use the tools.
- **Templates** (`templates/`): Consistent output formats for email triage, drafts, meeting briefs.

## Folder Structure

```
founder-os/
├── .claude/
│   ├── CLAUDE.md              # System prompt and rules
│   └── skills/                # Slash command workflows
│       ├── email/
│       ├── calendar/
│       ├── meeting/
│       └── research/
├── tools/                     # Python API tools
│   ├── auth.py                # Shared Google OAuth
│   ├── config.py              # User settings
│   ├── gmail.py               # Gmail API
│   ├── gcal.py                # Google Calendar API
│   └── gdrive.py              # Google Drive API
├── tests/                     # Test suite
├── templates/                 # Output format templates
├── output/                    # Workflow outputs
├── setup.py                   # Setup wizard
└── requirements.txt           # Dependencies
```

## Requirements

- Python 3.9+
- Google account (Gmail, Calendar, Drive)
- [Claude Code](https://claude.ai/code)
- Perplexity API key (optional, for research)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add new tools and skills.

## Troubleshooting

**"Client secret not found"**: Run `python3 setup.py`

**"Token expired"**: Delete `.credentials/token.json` and run `python3 setup.py`

**"Access blocked"**: Add yourself as a test user in Google Cloud OAuth consent screen.

## Licence

MIT

Built by [Other Shapes](https://other-shapes.com)
