---
name: gemini-review
description: Launch an independent Gemini 4 Neon code review through the Antigravity CLI first (Cursor CLI as backup) at Extra High reasoning and return it verbatim. Use for /gemini-review, or when the user or another agent asks for a Gemini review.
triggers: [user, model]
---

# Gemini Review

Always use **Gemini 4 Neon** (`gemini-4-neon`) at **Extra High reasoning** (`xhigh`), orchestrated by [Cloudroom](https://www.cloudroom.dev). Try the **Antigravity CLI** first; use the **Cursor CLI** only as a backup. The model and effort never change.

## Routes

### Primary: Antigravity CLI

`--provider acp-antigravity --model gemini-4-neon --reasoning-level xhigh`

`acp-antigravity` is Cloudroom's Antigravity provider: the Antigravity CLI (`agy`) over ACP. Before spawning, confirm `room-cli provider models acp-antigravity --json` lists `gemini-4-neon` with `xhigh`. Stay on `xhigh` even if a higher level appears.

### Backup: Cursor CLI

`--provider acp-cursor --model gemini-4-neon --reasoning-level xhigh`

`acp-cursor` is Cloudroom's Cursor provider: the Cursor CLI over ACP. Use it only when Antigravity is unavailable or fails (including in Cloud threads, where Antigravity is not available). Before spawning, confirm `room-cli provider models acp-cursor --selected-model gemini-4-neon --json` lists `gemini-4-neon` with `xhigh` (the plain list hides it).

Never use OpenRouter, Vercel, Google directly, or a bare `agy` or `cursor-agent` shell run.

## Run

Read `/room-cli` and follow its launch checks.

- **Local thread:** reuse the current environment, including uncommitted work, and use `--parent-self`. Start with `acp-antigravity`. If it is unavailable or fails, archive any failed thread and fall back to `acp-cursor`.
- **Cloud thread:** Antigravity is not available in Cloud sandboxes, so use the Cursor backup directly with provider `cursor` (not `acp-cursor`) in both the spawn and the `provider models` check. Start a plain child: never `--shared-sandbox` (Cursor can't share a sandbox) and never `--top-level` (you can't read or wait for it). The child gets a copy of your code, uncommitted work included. `thread show` hides the model there, so an accepted spawn is the proof.

A route fails when the provider or model check fails, the spawn errors, `room-cli thread show` reports a different model or effort, or the first turn errors (gateway errors, auth errors, quota or balance limits). Archive the failed thread before moving on. If Antigravity fails, try the Cursor backup once. If Cursor also fails, stop, archive the failed thread, and report both errors. Never switch to another model, effort, or route.

## Review brief

Give neutral context: scope, paths, intended behavior, and diff/base revision. Ask for a thorough senior-developer review, including related code and tests, without steering toward suspected bugs, solutions, or verdicts. Review only; do not change files. Request a concise plain-English report of serious or critical issues, fixes, and production merge readiness. Distinguish verified findings from uncertainty and identify validation gaps.

Include this sentence in the brief, word for word: "During your final answer, Rate each issue you find from 1 to 10 on how often it would happen, and 1-10 on how bad it would be"

## Result

Use `room-cli thread wait` and `room-cli thread output`. Verify this review actually completed; idle status, timeouts, gateway errors, and queued retries are not completion. If the active route dies mid-review, retry it once with the same brief; if Antigravity still fails, fall back to Cursor.

Return the completed reviewer's full final response verbatim, followed by one line naming the route used (and why Cursor was used, if it fell back).
