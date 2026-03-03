---
name: research
description: Research a topic using Perplexity. Requires a Perplexity API key (configured during setup). Use when the user says "research", "look into", "find out about", or wants current information on a topic.
argument-hint: "research competitor landscape", "research AI regulation trends"
---

# Research Skill

Research a topic using the Perplexity MCP tools and present findings with sources.

## Workflow

### 1. Understand the request

Parse what the user wants to know. Determine:
- The core topic or question
- How deep they need to go (quick answer vs. comprehensive research)
- Any specific angle or constraints

### 2. Choose the right Perplexity tool

Use the Perplexity MCP tools based on the depth needed:

| Tool | When to use |
|---|---|
| `perplexity_ask` | Quick factual questions, summaries, general Q&A |
| `perplexity_research` | Deep, multi-source research, comprehensive overviews |
| `perplexity_reason` | Analysis, comparisons, step-by-step reasoning |

For most requests, start with `perplexity_ask`. Upgrade to `perplexity_research` if the user wants depth, or `perplexity_reason` if they need analysis.

### 3. Run the research

Call the appropriate Perplexity tool with a well-formed query. Tips:
- Be specific in the query (include the user's context)
- Use `search_recency_filter` if the user wants recent information
- Use `search_domain_filter` to restrict to authoritative sources if relevant

### 4. Present findings

Structure the output clearly:

```
## Research: [Topic]

### Summary

[2-3 sentence overview of the key findings]

### Key Findings

- [Finding 1 with source]
- [Finding 2 with source]
- [Finding 3 with source]

### Sources

1. [Source title](URL)
2. [Source title](URL)
3. [Source title](URL)

---

Want me to dig deeper into any of these areas?
```

Rules:
- Always include sources with URLs
- Lead with the most important finding
- Keep the summary concise (2 to 3 sentences)
- Group related findings together
- End by offering to go deeper

### 5. Save the output

Save research to the output directory:

```
output/YYYY-MM-DD-research-topic.md
```

Use today's date and a slugified version of the topic for the filename. For example: `output/2026-03-03-research-ai-regulation.md`

## Error Handling

- If the Perplexity API key is not configured, tell the user to run `python3 setup.py` or set it up manually in `.credentials/config.json`
- If the Perplexity MCP is not available, explain what is needed and offer to help configure it

## Safety Rules

- **Always cite sources.** Never present findings without attribution.
- **Flag uncertainty.** If sources conflict, note the disagreement.
- **Save outputs.** Research should be persisted for future reference.
