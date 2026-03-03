---
name: meeting
description: Prepare for an upcoming meeting. Pulls calendar details, searches emails and Drive for context, and creates a briefing. Use when the user says "prep for", "prepare for", "meeting prep", "meeting", or "brief me on".
argument-hint: "prep for my call with Sarah", "prepare for tomorrow's board meeting"
---

# Meeting Prep Skill

Gather context for an upcoming meeting and create a briefing document.

## Workflow

### 1. Find the meeting on the calendar

Fetch upcoming events (next 3 days by default, or adjust based on the user's request):

```bash
python3 tools/gcal.py list -d 3
```

Identify the meeting the user is asking about. Extract:
- Meeting title
- Date and time
- Duration
- Attendees (names and email addresses)

If the meeting is ambiguous (multiple matches), ask the user to clarify.

### 2. Search emails for context on each attendee

For every attendee, search for recent email threads:

```bash
python3 tools/gmail.py fetch -q "from:attendee@email.com" -n 10
python3 tools/gmail.py fetch -q "to:attendee@email.com" -n 10
```

Read the output JSON files to extract conversation history.

### 3. Search Drive for relevant documents

Search for documents related to the meeting topic or attendee:

```bash
python3 tools/gdrive.py search "meeting topic"
```

Also check for meeting transcripts:

```bash
python3 tools/gdrive.py search "transcript"
```

If relevant transcripts or documents are found, read them:

```bash
python3 tools/gdrive.py read FILE_ID
```

### 4. Present the briefing

Use the exact format from `templates/meeting-prep.md`:

```
## Meeting Prep: [Meeting Title]

**When:** [Day, Date at Time (duration)]
**With:** [Name] ([email])

---

### Context

[2-3 sentences on who this person is and your relationship]

### Recent Conversations

- **[Date]:** [What was discussed or happened]
- **[Date]:** [What was discussed or happened]
- **[Date]:** [What was discussed or happened]

### Open Items

- [Unresolved item or pending action]
- [Unresolved item or pending action]

### Suggested Talking Points

1. [First talking point]
2. [Second talking point]
3. [Third talking point]

---

Anything specific you want me to look into before the call?
```

Rules for the briefing:
- **Recent Conversations** in reverse chronological order (most recent first)
- **Context** should be brief: 2 to 3 sentences max
- **Open Items** should be actionable things that need resolution
- **Talking Points** should be specific, not generic filler like "catch up"
- Always end with the offer to dig deeper

### 5. Offer to dig deeper

If the user wants more context:
- Search for additional email threads with broader queries
- Look for shared Drive documents, meeting notes, or proposals
- Search for the attendee's name across all emails

## Safety Rules

- **Always check the calendar first** to get accurate meeting details.
- **Search emails for each attendee separately** to build complete context.
- **Do not fabricate context.** If no email history is found, say so clearly.
- **If no meeting is found on the calendar**, tell the user and ask for more details.
