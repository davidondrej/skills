---
name: fable-review
description: Launch an independent Fable code review and return it verbatim. Use only when the user explicitly invokes /fable-review.
disable-model-invocation: true
triggers: [user, model]
---

# Fable Review

Use **Fable 5.1 Extra High** through Claude Code and the selected harness.

## Run

Read the selected harness's skill and follow its launch checks. Discover provider/model/effort IDs rather than guessing. Reuse the current environment, including uncommitted work, and use the harness's documented parent-context option when coordinating.

If the user names another harness, read its skill and use it with the same model, effort, workspace, brief, and output requirements. Report unavailable model/effort as blockers; never silently downgrade.

## Review brief

Give neutral context: scope, paths, intended behavior, and diff/base revision. Ask for a thorough senior-developer review, including related code and tests, without steering toward suspected bugs, solutions, or verdicts. Review only; do not change files. Request a concise plain-English report of serious or critical issues, fixes, and production merge readiness. Distinguish verified findings from uncertainty and identify validation gaps.

## Result

Use the selected harness's documented wait and output commands. Verify this review actually completed; idle status, timeouts, and queued retries are not completion. Report blockers rather than presenting partial output as a finished review.

Return the completed reviewer's full final response verbatim.
