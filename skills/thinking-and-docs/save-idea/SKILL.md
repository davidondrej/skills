---
name: save-idea
description: Save ideas, observations, content topics, projects, and convictions in the ideas repo. Use when the user asks to capture an idea or insight. Adds to idea backlogs, not reminders or tasks.
---

# save-idea

Capture the entry in the ideas repo, commit, push, and confirm. All paths below are relative to that repo.

## 1. Capture and Route

Everything after `/save-idea` is the entry. Multiple ideas get one entry each. Preserve the user's wording verbatim, except startup ideas and convictions, which may be tightened without changing the user's meaning or voice.

Use and strip an explicit prefix. Otherwise choose by the definitions below; ask one short question only if ambiguous.

- `video:` → `VIDEO-IDEAS.md`: a concept for a full video.
- `topic:` → `TOPICS.md`: podcast/content topics, guests, or discussion questions.
- `observation:` → `OBSERVATIONS.md`: personal insights, hypotheses, or assumptions to test, without requiring content intent.
- `marketing:` → `MARKETING-IDEAS.md`: getting an existing product in front of people.
- `startup:` → `STARTUP-IDEAS.md`: a business/product idea or technical insight that could become a startup.
- `mini:` → `mini-projects.md`: a small technical or cool project, not a startup candidate.
- `article:` → `ARTICLE-IDEAS.md`: a topic for the user's daily public articles.
- No prefix for convictions: use `CONVICTIONS.md` only for beliefs the user states as certain about AI-era building, startups, the AI industry, or agentic coding.

Tentative beliefs belong in observations. An observation is not a topic merely because it could be discussed on a podcast.

## 2. Read and Number

Read the target file. Use its last entry number + 1; never reuse gaps, renumber, reorder, or edit existing entries.

- Video numbering continues from the old Google Doc; do not restart it.
- Startup numbering follows the last idea in the STARTUP IDEAS list. Ignore the separate discarded-ideas numbering.
- Other files start at 1 and have independent numbering.

If missing, create `TOPICS.md` or `MARKETING-IDEAS.md` with a one-line purpose header; `OBSERVATIONS.md` with `# OBSERVATIONS` and `Insights, hypotheses, and assumptions to test.`; or `mini-projects.md` with `# MINI PROJECTS` and `> Just cool shit we wanna build — small projects we think would be cool.` Then append entry 1.

## 3. Append with Source

Source format: `<repo>, <agent and chat/session>, <YYYY-MM-DD>`.

- Repo: where the skill was invoked, from `git rev-parse --show-toplevel`, or cwd outside a repo. Use a `~/...` path.
- Chat/session: agent name plus title or session ID if available; otherwise just the agent name.
- Date: today. Preserve any extra links or notes the user supplied.

**Videos, topics, observations, marketing, and articles:** append verbatim at the bottom, with real tabs before source and context lines:

```text
N. Idea exactly as the user said it
	source: <repo>, <agent and chat/session>, <date>
	any extra links or notes the user gave
```

**Startups, convictions, and mini projects:** indent all source and context lines with four spaces; use `- source:` and a blank line between entries:

```text
N. Title — one-line explanation.
    - source: <repo>, <agent and chat/session>, <date>
```

- Startups: read `startup/AGENTS.md`. Tighten the entry while keeping the user's voice. Insert after the last numbered idea, before the trailing `----` separator and discarded-ideas note. Preserve the root `STARTUP-IDEAS.md` symlink to `startup/STARTUP-IDEAS.md`.
- Convictions: append `N. Punchy conviction — one-line why.`, tightened but faithful to the user's wording.
- Mini projects: append `N. Idea exactly as the user said it`; do not rewrite or add an explanation.

## 4. Commit and Push

Commit and push captures only when the user has authorized it. This applies only to the listed backlog files, including the startup symlink's target, not other repo changes.

Run Git yourself using `git -C`; do not change cwd or delegate this step:

```bash
git -C <ideas-repo> pull --rebase --autostash <remote> <branch>
# Stage only this capture's files; example:
git -C <ideas-repo> add OBSERVATIONS.md
git -C <ideas-repo> commit -m "Add observation 1 on local agents"
git -C <ideas-repo> push <remote> <branch>
```

- Stage only the captured idea files; never `git add -A`. For the startup symlink, stage `startup/STARTUP-IDEAS.md`. Keep unrelated staged changes or edits out of the commit.
- Commit message: `Add <entry type> <number> on <short description>`. List numbers for multiple entries.
- If any Git step fails, report the exact error and stop. Never force-push.

## 5. Confirm

Report the exact saved entry text, number, file, and successful push.

## Protected Locations

- Never write or push to the legacy startup repo. Startup support material belongs in the startup support directory.
- Never write to the discarded-ideas file; only the user moves ideas there.
