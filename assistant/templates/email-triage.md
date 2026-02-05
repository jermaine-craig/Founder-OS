# Email Triage Output Template

Always use this exact format when presenting inbox results.

---

## Template

```
## Inbox Summary

X unread emails • X urgent • X action needed • X FYI

| # | From | Subject | Context | Action |
|---|------|---------|---------|--------|
| 1 | [Name] | [Subject line] | [Brief context] | [Suggested action] |

---

Let me know which emails you'd like me to draft replies for.
```

---

## Example Output

```
## Inbox Summary

12 unread emails • 2 urgent • 4 action needed • 6 FYI

| # | From | Subject | Context | Action |
|---|------|---------|---------|--------|
| 1 | David Park | Contract ready for signature | Final version after legal review | Reply today |
| 2 | Investor Relations | Due diligence docs needed | Series A follow-up | Reply today |
| 3 | Sarah Chen | Partnership proposal | New inbound from Acme Corp | Review + reply |
| 4 | Mike Johnson | Q1 planning follow-up | Waiting on your availability | Reply this week |
| 5 | Jane Smith | Intro to Tom at Figma | Warm intro, looks relevant | Reply this week |
| 6 | Calendly | Meeting scheduled | Notification | Archive |
| 7 | Stripe | Payment received | $2,400 from Client X | Archive |
| 8 | Product Hunt | Your weekly digest | Newsletter | Archive |

---

Let me know which emails you'd like me to draft replies for.
```

---

## Field Definitions

| Field | Description |
|-------|-------------|
| **From** | Sender's name (not email address) |
| **Subject** | Email subject line, truncated if long |
| **Context** | 3-5 words explaining what this is about |
| **Action** | One of: Reply today, Reply this week, Review + reply, Archive |

---

## Action Categories

- **Reply today** — Urgent, time-sensitive, or blocking something
- **Reply this week** — Important but not urgent
- **Review + reply** — Needs reading before responding
- **Archive** — Newsletters, notifications, no action needed

---

## Rules

1. Always start with the summary line
2. Use a table, not a list
3. Keep Context brief (3-5 words max)
4. End by asking which emails to draft
5. Don't draft anything until the user asks
