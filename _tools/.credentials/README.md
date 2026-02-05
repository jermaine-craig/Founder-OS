# Credentials Setup

This folder stores your Google API credentials. **Never commit these files to git.**

---

## Required Files

After running `setup.py`, this folder should contain:

```
.credentials/
├── client_secret.json    # OAuth app credentials (from Google Cloud)
├── gmail_token.json      # Your Gmail access token (auto-generated)
└── calendar_token.json   # Your Calendar access token (auto-generated)
```

---

## Setup Instructions

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/projectcreate)
2. Create a new project (name it anything, e.g., "Founder OS")

### 2. Enable APIs

1. Go to [API Library](https://console.cloud.google.com/apis/library)
2. Search for and enable:
   - **Gmail API**
   - **Google Calendar API**

### 3. Configure OAuth Consent Screen

1. Go to [OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent)
2. Choose **External** user type
3. Fill in:
   - App name: "Founder OS"
   - User support email: your email
   - Developer contact: your email
4. Click through scopes (no changes needed)
5. Add your email as a **Test user**
6. Save

### 4. Create OAuth Credentials

1. Go to [Credentials](https://console.cloud.google.com/apis/credentials)
2. Click **Create Credentials** > **OAuth client ID**
3. Choose **Desktop app**
4. Name it anything (e.g., "Founder OS Desktop")
5. Download the JSON file
6. Rename to `client_secret.json`
7. Move to this folder (`.credentials/`)

### 5. Authenticate

Run the setup wizard:

```bash
python3 setup.py
```

Or authenticate manually:

```bash
python3 _tools/gmail.py auth
python3 _tools/gcal.py auth
```

---

## Troubleshooting

### "Access blocked: This app's request is invalid"

Your OAuth consent screen isn't configured correctly:
1. Go to OAuth consent screen
2. Make sure you added yourself as a test user
3. Try again

### "Token has been expired or revoked"

Delete the token files and re-authenticate:

```bash
rm .credentials/gmail_token.json
rm .credentials/calendar_token.json
python3 _tools/gmail.py auth
python3 _tools/gcal.py auth
```

### "Client secret not found"

Make sure `client_secret.json` is in this folder and named correctly.

---

## Security

- **Never commit credentials to git** — they're in `.gitignore`
- **Don't share your client_secret.json** — it's tied to your Google Cloud project
- **Tokens auto-refresh** — you shouldn't need to re-authenticate often
