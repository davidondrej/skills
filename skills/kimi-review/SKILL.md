---
name: kimi-review
description: Launch an independent Kimi K3.1 Pro Max code review and return it verbatim, falling back across harnesses and routes until one works. Use for /kimi-review, or when the user or another agent asks for a Kimi review.
triggers: [user, model]
---

# Kimi Review

Always use **Kimi K3.1 Pro at Max reasoning**, orchestrated by [Cloudroom](https://www.cloudroom.dev). The model and effort never change. Only the harness or route may change, and only to get the review running.

## Routes

Try these in order. Move to the next one only when the current one fails.

1. `--provider pi --model vercel-ai-gateway/moonshotai/kimi-k3.1-pro --reasoning-level max`
2. `--provider acp-fx --model moonshotai/kimi-k3.1-pro --reasoning-level max` (fx uses Vercel AI Gateway)
3. `--provider acp-opencode --model vercel/moonshotai/kimi-k3.1-pro --reasoning-level max`
4. `--provider pi --model openrouter/moonshotai/kimi-k3.1-pro --reasoning-level max`
5. `--provider acp-opencode --model openrouter/moonshotai/kimi-k3.1-pro --reasoning-level max`

Vercel comes first because it keeps no data and does not train on it. OpenRouter serves this model only through Moonshot itself. Vercel routes bill the user's Vercel AI Gateway credits.

## Pi setup

Pi's built-in catalog lacks this model. Both Pi routes need the entries in [references/pi-models.json](references/pi-models.json), placed under `providers.<provider>.models` in `~/.pi/agent/models.json`. If an entry is missing (common in fresh Cloud sandboxes), back up the file, merge the entry in, and confirm with `pi --list-models | grep k3.1`.

After a `models.json` edit, Cloudroom's Pi catalog can stay stale for about 5 idle minutes. A stale catalog makes the spawn fail instantly, at no cost. Wait 5 minutes without querying Pi models, then retry once.

## Run

Read `/room-cli` and follow its launch checks. Reuse the current environment, including uncommitted work, and use `--parent-self`.

A route fails when the spawn errors, `room-cli thread show` reports a different model or effort, or the first turn errors (gateway errors, auth errors, an empty balance). Stop and archive the failed thread, note its error, and try the next route.

Report a blocker only after every route has failed, with each route's error.

## Review brief

Give neutral context: scope, paths, intended behavior, and diff/base revision. Ask for a thorough senior-developer review, including related code and tests, without steering toward suspected bugs, solutions, or verdicts. Review only; do not change files. Request a concise plain-English report of serious or critical issues, fixes, and production merge readiness. Distinguish verified findings from uncertainty and identify validation gaps.

Include this sentence in the brief, word for word: "During your final answer, Rate each issue you find from 1 to 10 on how often it would happen, and 1-10 on how bad it would be"

## Result

Use `room-cli thread wait` and `room-cli thread output`. Verify this review actually completed; idle status, timeouts, gateway errors, and queued retries are not completion. If a route dies mid-review, start the next route with the same brief.

Return the completed reviewer's full final response verbatim, followed by one line naming the route used.
