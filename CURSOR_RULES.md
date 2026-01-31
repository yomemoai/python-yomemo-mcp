# Cursor best practice: proactive Yomemo long-term memory

After configuring the Yomemo MCP in Cursor, add the rule below to **Rules for AI**. The AI will then **proactively** call `save_memory` when it detects important information—no need to say "remember this" every time.

---

## Option 1: Cursor global / project Rules for AI

Open Cursor settings → **Rules for AI**, add a new rule, and paste the following:

```
You are equipped with Yomemo.ai MCP.

## When to use `save_memory`:
- **Tech Stack**: When we decide on a specific library or version.
- **Business Logic**: When I explain a complex internal rule.
- **Preferences**: If I tell you "I prefer using early returns in Go".

## When to use `load_memories`:
- At the start of a new feature implementation, check if there's relevant context in the 'coding' or 'project-name' handle.

## Feedback:
- After saving, just add a ✓ in your response. No need for a long confirmation.
```

---

## Option 2: Project-level rule file (.cursor/rules)

Create `.cursor/rules/` in your project root and add a file such as `yomemo-memory.mdc` with the same content above. The rule will then apply only in that project.

---

## What you get

- The AI will call `save_memory` when it recognizes **preferences, decisions, or reusable logic**.
- After saving, it will add a ✓ in its reply—smooth and low-friction.
- At the start of new chats or features, it will call `load_memories` when it needs historical context.

Use this together with your [yomemoai-mcp](https://github.com/yomemoai/python-yomemo-mcp) MCP setup.
