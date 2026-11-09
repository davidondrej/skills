---
name: total-review
description: 'Run five independent max-effort reviews (Fable 5.1, Opus 5.5, GPT-6 Astra, GPT-6.1 Sol, Muse Wonder), merge their findings, and fix only what the user approves. Manual only: run when a human types /total-review; agents must never invoke it on their own.'
disable-model-invocation: true
---

# Total Review

Five reviewers, each in its own [Cloudroom](https://www.cloudroom.dev) thread: the two best models from Anthropic and from OpenAI, plus Meta's Muse Wonder, all at their highest effort and in **full permission mode** (the harness maximum). Never swap or downgrade a model, effort, or permission mode. If one is unavailable, stop and tell the user.

## Permissions

Always spawn with `--permission-mode full`. That is Claude Code's bypass permissions (`--dangerously-skip-permissions`) and Codex's YOLO mode (no approvals, `danger-full-access` sandbox). A child cannot exceed its parent, so if this thread is not in full mode, stop and tell the user.

## Reviewers

- **Fable 5.1**: `--provider claude-code --model claude-fable-5-1`
- **Opus 5.5 (1M)**: `--provider claude-code --model 'claude-opus-5-5[1m]'`
- **GPT-6 Astra**: `--provider codex --model gpt-6-astra`
- **GPT-6.1 Sol**: `--provider codex --model gpt-6.1-sol`
- **Muse Wonder**: `--provider pi --model openrouter/meta/muse-wonder` (Pi harness, OpenRouter). Only OpenRouter offers `max` for Muse; never use the `vercel-ai-gateway` route.

## 1. Launch

1. Confirm each model is listed with `max` in `supportedReasoningEfforts`: `room-cli provider models claude-code --json`, `room-cli provider models codex --json`, and `room-cli provider models pi --json`.
2. Spawn all five in parallel, one thread each, with the reviewer flags plus `--reasoning-level max --permission-mode full --title "Total review: <model>"`:
   - **Local thread:** `room-cli thread spawn --parent-self --project "$ROOM_PROJECT_ID" --environment <env ID from room-cli status --json>`
   - **Cloud thread:** `cloudroom thread spawn` (see `cloudroom thread --help`).
   - **Fallback only:** `bb thread spawn` (see `/bb-cli`).
3. Confirm with `thread show` that each thread runs the right model at its effort in `full` permission mode.

## 2. Brief

Send all five the same neutral brief: scope, paths, intended behavior, and diff/base revision.

Ask for a thorough senior-developer review, including related code and tests. Review only; change no files. Report serious or critical issues with file and line, a fix, and merge readiness. Separate verified findings from guesses. Use plain English.

Include this sentence in the brief, word for word: "During your final answer, Rate each issue you find from 1 to 10 on how often it would happen, and 1-10 on how bad it would be"

Never hint at suspected bugs, mention the other reviewers, or share one reviewer's output with another.

## 3. Collect

Run `thread wait`, then `thread output`, on each. Idle status, timeouts, and queued retries are not completion. Report a failed reviewer; never pass off partial output as a review.

## 4. Merge and report

Read all five reports in full. Deduplicate. Keep only real bugs and risks; drop style preferences, theoretical edge cases, and non-issues. Agreement alone does not prove an issue is real.

Show the user:

- A numbered list, one line per issue: what + where.
- Tags for who found it: `[fable]`, `[opus]`, `[astra]`, `[sol]`, `[muse]`. Most-reported first.
- One line: how many findings were dropped.
- Ask: approve these fixes, or adjust the list?

Share full reports only if the user asks.

## 5. Fix and ship

Only after the user approves: fix the approved issues, then commit and push with the standard ship workflow.
