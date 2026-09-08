---
name: save-idea
description: 'Capture ideas and insights in ~/code/ideas. Save video ideas, podcast/content topics, personal observations and hypotheses, marketing ideas, startup ideas, convictions, mini projects, and article ideas. Use for /save-idea, save this idea, save this observation, save this insight, add a topic, video idea, marketing idea, startup idea, save this conviction, mini project, or write this down for a video/podcast. Observations are personal insights or assumptions to test; topics are intended for content. Appends to idea backlogs, not reminders or tasks.'
---

# save-idea

Capture one thing fast, then get out of the way. Eight buckets, eight files, ONE repo (`~/code/ideas`):

| Bucket | File | What belongs there |
|---|---|---|
| Video idea | `~/code/ideas/VIDEO-IDEAS.md` | A concept big enough for a full video |
| Topic | `~/code/ideas/TOPICS.md` | Podcast/content topics, guests, and questions intended for discussion |
| Observation | `~/code/ideas/OBSERVATIONS.md` | Personal insights, hypotheses, and assumptions to test; no content intent required |
| Marketing idea | `~/code/ideas/MARKETING-IDEAS.md` | Marketing and distribution: how we get products in front of people |
| Startup idea | `~/code/ideas/STARTUP-IDEAS.md` | A business/product idea — a candidate for the user's next startup |
| Conviction | `~/code/ideas/CONVICTIONS.md` | A belief the user is CERTAIN about on AI-era building (startups, AI industry, agentic coding) — a conviction, not an idea |
| Mini project | `~/code/ideas/mini-projects.md` | A small technical/cool project to build — just cool shit, not a startup candidate |
| Article idea | `~/code/ideas/ARTICLE-IDEAS.md` | A topic for the user's daily public articles (X, blog, YouTube community, email) |

Note: a technical insight can go in the startup bucket too — some technical insights could lead to a startup idea. A cool thing to build that is NOT a business idea goes in mini projects.

## Workflow

1. **Get the text.** Everything after `/save-idea` is the entry. Keep the user's wording verbatim — never rephrase, shorten, or "improve" it. (One exception: startup ideas get tightened per their repo's rules — see step 4.)
2. **Route it.**
   - Starts with `video:` → video idea (strip the prefix).
   - Starts with `topic:` → topic (strip the prefix).
   - Starts with `observation:` → observation (strip the prefix).
   - Starts with `marketing:` → marketing idea (strip the prefix).
   - Starts with `startup:` → startup idea (strip the prefix).
   - Starts with `mini:` → mini project (strip the prefix).
   - Starts with `article:` → article idea (strip the prefix).
   - Convictions have NO prefix (deliberate, David 2026-08-18) — route them by judgment only.
   - No prefix → judge: a belief stated as a certainty about AI-era building (startups, AI industry, agentic coding) → conviction; business/product idea → startup idea; a small technical/cool project to build (not a company) → mini project; a way to get an existing product in front of people → marketing idea; full video concept → video idea; podcast/content topic, guest, or discussion question → topic; personal insight, hypothesis, assumption to test, or general observation → observation. Route tentative beliefs to observations; use convictions only for beliefs the user states as certain. An observation does not become a topic merely because it could be discussed on a podcast. Only if genuinely ambiguous, ask the user one short question.
3. **Read the target file** and find the last entry number. Next number = last + 1.
   - `TOPICS.md`, `OBSERVATIONS.md`, `MARKETING-IDEAS.md`, `ARTICLE-IDEAS.md`, `CONVICTIONS.md`, and `mini-projects.md` start at 1. `VIDEO-IDEAS.md` continues from an old Google Doc.
   - `STARTUP-IDEAS.md`: continue from the last idea in the STARTUP IDEAS list. Gaps in its numbering are normal — discarded ideas live in `startup/review/DISCARDED.md`, which has its own separate numbering. Ignore it; never reuse a gap number.
   - Never renumber anything.
4. **Append the entry.**
   - **Video ideas, topics, observations, marketing ideas & article ideas** — append at the bottom of the file, wording verbatim, context lines tab-indented under the numbered line:

```
NNNN. Idea title exactly as the user said it
	source: ~/code/some-repo, Cursor chat "Chat title", 2026-07-15
	any extra links or notes the user gave
```

   - **Startup ideas** — insert after the last numbered idea, keeping the trailing `----` separator and discarded-ideas note as the last lines of the file. Format per `~/code/ideas/startup/AGENTS.md`: one tight entry, `N. Title — one-line explanation.` Rewrite for clarity and concision but stay loyal to the user's wording and voice. Blank line between entries. Source line indented with 4 spaces (that file uses spaces, not tabs):

```
69. Idea title — one-line explanation in the user's voice.
    - source: ~/code/some-repo, Cursor chat "Chat title", 2026-08-01
```

   - **Convictions** — append at the bottom of `CONVICTIONS.md`, same tight style as startup ideas: `N. Punchy conviction — one-line why.` Tighten for punch but stay loyal to the user's wording and voice. Blank line between entries, source line indented with 4 spaces:

```
1. Punchy conviction — one-line why.
    - source: ~/code/some-repo, Cursor chat "Chat title", 2026-08-18
```

   - **Mini projects** — append at the bottom of `mini-projects.md`, wording verbatim. Blank line between entries. Source line indented with 4 spaces (that file uses spaces, not tabs):

```
10. Idea title exactly as the user said it
    - source: ~/code/some-repo, Cursor chat "Chat title", 2026-08-24
```

5. **Build the source line.**
   - Repo: the folder the skill was invoked from, as `~/...` path (check `git rev-parse --show-toplevel`; if not a repo, use the cwd).
   - Chat: agent name plus chat title or session ID if the runtime exposes one (e.g. `Cursor chat "Fixing task sync"`, `Claude Code session abc123`). If unknown, just the agent name.
   - Date: today, YYYY-MM-DD.
6. **Commit and push** the repo. Always use `git -C` so the current working directory never matters — never `cd`, never launch another agent for this:

```bash
git -C ~/code/ideas pull --rebase --autostash origin main
# Stage only the file(s) changed in this capture, for example:
git -C ~/code/ideas add OBSERVATIONS.md
git -C ~/code/ideas commit -m "Add observation 1 on whether local agents are needed"
git -C ~/code/ideas push origin main
```

   - Stage ONLY the idea file(s) you touched. Never `git add -A` — unrelated work must not get swept in.
   - Commit message: `Add idea NNNN on <short description>` (or `Add topic NNNN on ...` / `Add observation NN on ...` / `Add marketing idea NN on ...` / `Add startup idea NN on ...` / `Add conviction NN on ...` / `Add mini project NN on ...`). Multiple entries → list the numbers.
   - If the pull or push fails, report the exact error to the user and stop. Never force-push.
7. **Confirm back to the user**: the exact entry text, its number, which file it went to, and that it was pushed.

## Rules

- Append only. Never edit, reorder, or renumber existing entries.
- Multiple ideas in one invocation → one numbered entry each.
- **Committing and pushing the idea files is REQUIRED and pre-authorized by the user** (26-07-2026; startup bucket 01-08-2026; convictions bucket 18-08-2026; mini-projects bucket 24-08-2026; observations bucket 08-09-2026). This is a deliberate exception to the global "never push to GitHub by yourself" rule in `~/code/AGENTS.md`. Do not "fix" this back — the whole point is that the user never has to commit idea entries by hand.
- The exception covers `VIDEO-IDEAS.md`, `TOPICS.md`, `OBSERVATIONS.md` (added 08-09-2026), `MARKETING-IDEAS.md`, `ARTICLE-IDEAS.md` (added 26-08-2026), `STARTUP-IDEAS.md`, `CONVICTIONS.md`, and `mini-projects.md` only. Any other change in the repo is still the user's to commit.
- All idea capture was centralized into `~/code/ideas` on 2026-08-14 (David's decision). The old `~/code/next-startup` repo is frozen pending archive — NEVER write or push there. Startup support material now lives in `~/code/ideas/startup/`.
- NEVER write to `~/code/ideas/startup/review/DISCARDED.md` — only the user moves ideas there.
- If `TOPICS.md` or `MARKETING-IDEAS.md` is missing, recreate it with its one-line header, then append entry 1.
- If `OBSERVATIONS.md` is missing, create it with `# OBSERVATIONS` and the description `Insights, hypotheses, and assumptions to test.`, then append entry 1.
- If `mini-projects.md` is missing, recreate it with its header (`# MINI PROJECTS` plus the one-line quote about cool shit to build), then append entry 1.
- Indent context lines to match the target file: real tabs in `VIDEO-IDEAS.md`, `TOPICS.md`, `OBSERVATIONS.md`, and `MARKETING-IDEAS.md`, 4 spaces in `STARTUP-IDEAS.md`, `CONVICTIONS.md`, and `mini-projects.md`.
