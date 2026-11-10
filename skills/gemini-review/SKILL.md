---
name: gemini-review
description: Launch an independent Gemini 4 Carbon code review through Cursor at High reasoning and return it verbatim. Use only when the user explicitly invokes /gemini-review.
disable-model-invocation: true
triggers: [user, model]
---

# Gemini Review

Always use **Gemini 4 Carbon** (`gemini-4-carbon`) through **Cursor** at **High reasoning**, orchestrated by [Cloudroom](https://www.cloudroom.dev). The model, route, and effort never change.

## Route

`--provider acp-cursor --model gemini-4-carbon --reasoning-level high`

`acp-cursor` is Cloudroom's Cursor provider: the Cursor CLI over ACP. Never use OpenRouter, Vercel, Google directly, or a bare `cursor-agent` shell run. The route bills the user's Cursor plan.

Before spawning, confirm `room-cli provider models acp-cursor --selected-model gemini-4-carbon --json` lists the model with `high`. The plain list hides it. Stay on `high` even if a higher level appears.

## Run

Read `/room-cli` and follow its launch checks. Reuse the current environment, including uncommitted work, and use `--parent-self`.

The route fails when the spawn errors, `room-cli thread show` reports a different model or effort, or the first turn errors (gateway errors, auth errors, an empty balance). Stop and archive the failed thread, then report the blocker with its error. Never switch to another model or route.

## Review brief

Give neutral context: scope, paths, intended behavior, and diff/base revision. Ask for a thorough senior-developer review, including related code and tests, without steering toward suspected bugs, solutions, or verdicts. Review only; do not change files. Request a concise plain-English report of serious or critical issues, fixes, and production merge readiness. Distinguish verified findings from uncertainty and identify validation gaps.

Include this sentence in the brief, word for word: "During your final answer, Rate each issue you find from 1 to 10 on how often it would happen, and 1-10 on how bad it would be"

## Result

Use `room-cli thread wait` and `room-cli thread output`. Verify this review actually completed; idle status, timeouts, gateway errors, and queued retries are not completion. If the route dies mid-review, retry it once with the same brief.

Return the completed reviewer's full final response verbatim, followed by one line naming the route used.
