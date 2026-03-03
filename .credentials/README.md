# Credentials Setup

This folder stores your Google API credentials. **Never commit these files to git.**

After running `python3 setup.py`, this folder will contain:

```
.credentials/
├── client_secret.json    # OAuth app credentials (from Google Cloud)
├── token.json            # Google access token (auto-generated)
├── config.json           # Your settings (name, timezone)
└── README.md             # This file
```

## Quick Setup

Run the setup wizard:

```bash
python3 setup.py
```

## Manual Setup

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/projectcreate)
2. Create a new project (name it anything, e.g., "Founder OS")

### 2. Enable APIs

Go to [API Library](https://console.cloud.google.com/apis/library) and enable:
- **Gmail API**
- **Google Calendar API**
- **Google Drive API**

### 3. Configure OAuth Consent Screen

1. Go to [OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent)
2. Choose **External** user type
3. Fill in app name and your email
4. Add your email as a **Test user**

### 4. Create OAuth Credentials

1. Go to [Credentials](https://console.cloud.google.com/apis/credentials)
2. Click **Create Credentials** > **OAuth client ID**
3. Choose **Desktop app**
4. Download the JSON file
5. Rename to `client_secret.json`
6. Move to this folder (`.credentials/`)

### 5. Authenticate

```bash
python3 setup.py
```

## Troubleshooting

### "Access blocked: This app's request is invalid"

Your OAuth consent screen is not configured correctly:
1. Go to OAuth consent screen
2. Make sure you added yourself as a test user
3. Try again

### "Token has been expired or revoked"

Delete the token and re-authenticate:

```bash
rm .credentials/token.json
python3 setup.py
```

### "Client secret not found"

Make sure `client_secret.json` is in this folder and named correctly.

## Security

- Never commit credentials to git (they are in `.gitignore`)
- Do not share your `client_secret.json`
- Tokens auto-refresh so you should not need to re-authenticate often
