---
name: fable-review
description: Launch an independent Fable code review and return it verbatim. Use only when the user explicitly invokes /fable-review.
disable-model-invocation: true
triggers: [user, model]
---

# Fable Review

Use **Fable 5.2 High** through the Claude Code harness, orchestrated by [Cloudroom](https://www.cloudroom.dev). Don't research IDs or probe catalogs. Everything you need is below (verified 2026-11-10).

## Exact IDs

- Provider: `claude-code`, in Cloud threads and on the Mac.
- Model: `claude-fable-5-2`.
- Effort: `--reasoning-level high`. The effort is a separate flag.

## Launch (exactly once)

- Every `thread spawn` starts a real thread. Never spawn a test or dummy thread.
- If a Fable review of the same change is already running, don't start a duplicate. Wait for it.

1. Write the brief to a file.
2. Cloud thread:
   `room-cli thread spawn --provider claude-code --model claude-fable-5-2 --reasoning-level high --title "Fable review: <topic>" --prompt-file brief.md`
3. Local thread on the Mac:
   `room-cli thread spawn --parent-self --project "$ROOM_PROJECT_ID" --provider claude-code --model claude-fable-5-2 --reasoning-level high --title "Fable review: <topic>" --prompt-file brief.md`
4. If it fails, report the exact error as a blocker. Never switch to the backup or downgrade silently.

## Prove the model (if the user asks)

From a Cloud thread, run the Mac's CLI. `R` is the path to the Mac's room-cli binary:

- `room-cli mac run "$R thread show CHILD_ID --json"` should show `.execution.model = claude-fable-5-2` and `.execution.reasoningLevel = high`.
- `room-cli mac run "$R thread log CHILD_ID --json"`: the first `client/turn/requested` event records the model and effort sent to the harness.
- `.thread.model` is null. That's normal; read `.execution`.

## Review brief

Give neutral context: scope, paths, intended behavior, and diff/base revision. Ask for a thorough senior-developer review, including related code and tests, without steering toward suspected bugs, solutions, or verdicts. Review only; do not change files. Request a concise plain-English report of serious or critical issues, fixes, and production merge readiness. Distinguish verified findings from uncertainty and identify validation gaps.

Include this sentence in the brief, word for word: "During your final answer, Rate each issue you find from 1 to 10 on how often it would happen, and 1-10 on how bad it would be"

## Result

- Cloudroom messages you when the child finishes a turn. Don't poll in a loop.
- Then run `room-cli thread output CHILD_ID`.
- Early on, `thread list` can say `running` while `thread output` says `idle` with `reply: null`. That isn't completion.
- Timeouts and queued retries aren't completion either.
- Report blockers instead of partial output.

Return the completed reviewer's full final response verbatim.

## Backup: Cursor harness and Extra High

Use these only when the user asks, or approves them after a Claude Code failure. Never start with them.

- Extra High: `--reasoning-level xhigh`, on either harness.
- Cursor provider: `cursor` in a Cloud thread's `room-cli`, `acp-cursor` on the Mac. Same model ID, `claude-fable-5-2`.
- Never pass `claude-fable-5-2-xhigh` to Cloudroom. That's Cursor's CLI-only ID, and Cloudroom rejects it with `invalid model`.
- Since commit `d7d3576`, `claude-fable-5-2` is in Cursor's visible model list. Older apps still accept it as a hidden model.
- Cloudroom can't show which model Cursor's servers actually ran. Cursor's usage dashboard can.
- Cursor CLI, outside Cloudroom only: Cloudroom threads must not start agent CLIs from a shell. In the user's own terminal, or if they explicitly ask, `cursor-agent models` lists the IDs and `cursor-agent -p --model claude-fable-5-2-xhigh "$(cat brief.md)"` runs it headless.
