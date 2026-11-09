---
name: gpt-review
description: Launch an independent GPT-6-Astra code review and return it verbatim. Use only when the user explicitly invokes /gpt-review.
disable-model-invocation: true
triggers: [user, model]
---

# GPT Review

Always use **GPT-6-Astra** through Codex, orchestrated by [Cloudroom](https://www.cloudroom.dev). Default to **Extra High reasoning on the Fast tier**. Use another effort or tier only when the user explicitly asks. Never use another model.

## Run

Read `/room-cli` and follow its launch checks. Reuse the current environment, including uncommitted work, and use `--parent-self` when coordinating.

Spawn with these default flags:

```bash
--provider codex --model gpt-6-astra --reasoning-level xhigh --service-tier fast
```

- Before spawning, confirm `room-cli provider models codex --json` lists `gpt-6-astra` with `xhigh` in `supportedReasoningEfforts`.
- After spawning, confirm with `room-cli thread show` that the thread runs `gpt-6-astra` at `xhigh` on the `fast` tier.
- If either check fails, stop and report the blocker. Never silently fall back to another model, effort, tier, or harness.

## Review brief

Give neutral context: scope, paths, intended behavior, and diff/base revision. Ask for a thorough senior-developer review, including related code and tests, without steering toward suspected bugs, solutions, or verdicts. Review only; do not change files. Request a concise plain-English report of serious or critical issues, fixes, and production merge readiness. Distinguish verified findings from uncertainty and identify validation gaps.

Include this sentence in the brief, word for word: "During your final answer, Rate each issue you find from 1 to 10 on how often it would happen, and 1-10 on how bad it would be"

## Result

Use `room-cli thread wait` and `room-cli thread output`. Verify this review actually completed; idle status, timeouts, and queued retries are not completion. Report blockers rather than presenting partial output as a finished review.

Return the completed reviewer's full final response verbatim.
