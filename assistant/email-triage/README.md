# Email Triage

Process inbox efficiently: categorize emails and draft replies.

---

## When to Use

- Daily inbox processing
- When inbox feels overwhelming
- After returning from time away

---

## Process

### 1. Fetch Emails

```bash
python3 _tools/gmail.py fetch
```

This saves unread emails to `inbox/YYYY-MM-DD-emails.json`.

### 2. Categorize Each Email

| Category | Criteria | Action |
|----------|----------|--------|
| **Urgent** | Needs response today | Draft reply immediately |
| **Action Required** | Needs response this week | Draft reply |
| **FYI** | Informational, no reply needed | Read and archive |
| **Archive** | Newsletters, notifications | Archive without reading |

### 3. Draft Replies

For Urgent and Action Required emails:
- Draft a reply using the user's voice
- Keep it concise and actionable
- Flag any that need user input

### 4. Output Summary

Save to `output/YYYY-MM-DD-triage.md`:

```markdown
# Email Triage — YYYY-MM-DD

## Summary
- 15 emails processed
- 2 urgent, 4 action required, 5 FYI, 4 archive

## Urgent

### From: John Smith <john@example.com>
**Subject:** Contract deadline tomorrow
**Draft reply:**
> Hi John,
> [drafted response]

[Message ID: abc123]

## Action Required
[...]

## FYI
[...]

## Recommend Archive
- abc456: Newsletter from X
- def789: Notification from Y
```

### 5. Present for Approval

- Show summary to user
- Wait for explicit approval before:
  - Sending any drafts
  - Archiving any emails

---

## Never

- Send emails without explicit approval
- Archive without confirmation
- Make assumptions about urgency
- Skip showing the summary

---

## Output Location

`assistant/email-triage/output/YYYY-MM-DD-triage.md`
