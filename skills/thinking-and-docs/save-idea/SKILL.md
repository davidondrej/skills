---
name: save-idea
description: 'Quickly capture a content idea into ~/code/content from any repo or chat. Video ideas go to VIDEO-IDEAS.md; smaller podcast topics, guest ideas, questions, and AI observations go to TOPICS.md. Every entry gets a source line referencing the chat and repo it came from. Use when the user says "/save-idea", "save this idea", "video idea", "add a topic", "write this down for a video/podcast". Differentiator: appends to the user''s content backlog — not a reminder, task, or general note tool.'
---

# save-idea

Capture one thing fast, then get out of the way. Two buckets, two files:

| Bucket | File | What belongs there |
|---|---|---|
| Video idea | `~/code/content/VIDEO-IDEAS.md` | A concept big enough for a full video |
| Topic | `~/code/content/TOPICS.md` | Smaller stuff: podcast topics, guests, questions, AI observations |

## Workflow

1. **Get the text.** Everything after `/save-idea` is the entry. Keep the user's wording verbatim — never rephrase, shorten, or "improve" it.
2. **Route it.**
   - Starts with `video:` → video idea (strip the prefix).
   - Starts with `topic:` → topic (strip the prefix).
   - No prefix → judge: full video concept → video idea; smaller thought → topic. Only if genuinely ambiguous, ask the user one short question.
3. **Read the target file** and find the last entry number. Next number = last + 1. TOPICS.md starts at 1. VIDEO-IDEAS.md continues from an old Google Doc — never renumber anything.
4. **Append at the bottom** (tab-indented context lines under the numbered line):

```
NNNN. Idea title exactly as the user said it
	source: ~/code/some-repo, Cursor chat "Chat title", 2026-07-15
	any extra links or notes the user gave
```

5. **Build the source line.**
   - Repo: the folder the skill was invoked from, as `~/...` path (check `git rev-parse --show-toplevel`; if not a repo, use the cwd).
   - Chat: agent name plus chat title or session ID if the runtime exposes one (e.g. `Cursor chat "Fixing task sync"`, `Claude Code session abc123`). If unknown, just the agent name.
   - Date: today, YYYY-MM-DD.
6. **Confirm back to the user**: the exact entry text, its number, and which file it went to.

## Rules

- Append only. Never edit, reorder, or renumber existing entries.
- Multiple ideas in one invocation → one numbered entry each.
- Do NOT git commit or push `~/code/content` — the user does that themselves.
- If `TOPICS.md` is missing, recreate it with its one-line header (topics + podcast material; video ideas live in VIDEO-IDEAS.md), then append entry 1.
- Indent context lines with a real tab character, matching the existing files.
