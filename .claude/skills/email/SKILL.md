---
name: email
description: Process your inbox. Fetches unread emails, categorises them by urgency, and drafts replies for approval. Use when the user says "email", "check emails", "help with inbox", or "process emails".
argument-hint: or "email --query 'from:investor'"
---

# Email Triage Skill

Process the user's inbox: fetch unread emails, categorise by urgency, and draft replies on request.

## Workflow

### 1. Fetch emails

Run from the project root:

```bash
python3 tools/gmail.py fetch
```

If the user provided a custom query (e.g. `/email --query 'from:investor'`), pass it through:

```bash
python3 tools/gmail.py fetch -q "from:investor"
```

The command outputs a JSON file to `output/`. Read that file to get the email data.

### 2. Categorise each email

Assign exactly one action to every email:

| Action | When to use |
|---|---|
| **Reply today** | Urgent, time-sensitive, or blocking something |
| **Reply this week** | Important but not urgent |
| **Review + reply** | Needs reading before responding |
| **Archive** | Newsletters, notifications, no action needed |

### 3. Present the inbox summary

Use the exact format from `templates/email-triage.md`:

```
## Inbox Summary

X unread emails . X urgent . X action needed . X FYI

| # | From | Subject | Context | Action |
|---|------|---------|---------|--------|
| 1 | [Name] | [Subject line] | [Brief context] | [Suggested action] |

---

Let me know which emails you'd like me to draft replies for.
```

Rules for the table:
- **From** column: sender name, not email address
- **Context** column: 3 to 5 words max
- Sort by urgency: Reply today first, then Reply this week, then Review + reply, then Archive
- Always end by asking which emails to draft replies for

### 4. Wait for user input

Do NOT draft anything until the user tells you which emails to reply to. This is critical.

### 5. Draft replies

When the user picks emails to reply to, draft each reply using the format from `templates/email-draft.md`:

```
## Draft Reply

**To:** [recipient@email.com]
**Cc:** [other@email.com, another@email.com]
**Subject:** Re: [Original subject]

---

[Email body]

Best,
[User's name]

---

Want me to add this to Gmail as a draft?
```

Rules for drafts:
- Default to reply-all (include all original recipients in Cc)
- Always show To, Cc (even if empty), and Subject
- Use "Draft Reply" for replies, "Draft Email" for new emails
- Match the user's tone: professional but not stiff
- Keep the signature simple: "Best," and the name

### 6. Create draft in Gmail (only with approval)

Only after the user confirms, create the draft:

```bash
python3 tools/gmail.py draft --to "recipient@email.com" --subject "Re: Subject" --body "Email body here" --reply-to MESSAGE_ID --cc "cc1@email.com,cc2@email.com"
```

### 7. Archive (only with approval)

If the user asks to archive emails:

```bash
python3 tools/gmail.py archive MESSAGE_ID_1 MESSAGE_ID_2
```

## Safety Rules

- **Never send emails without explicit approval.** Always draft first.
- **Never archive without explicit confirmation.** Present recommendations, wait for the word.
- **Never assume approval.** Always ask "Want me to add this to Gmail as a draft?" before creating it.
- **Default to reply-all.** Include all original recipients unless the user says otherwise.
