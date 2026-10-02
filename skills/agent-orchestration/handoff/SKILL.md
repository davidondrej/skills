---
name: handoff
description: Capture session context for a fresh agent. Use for handoffs, context limits, switching focus, ending sessions, or splitting work across sessions.
disable-model-invocation: true
triggers: [user, model]
---

# Handoff

Capture the context a fresh agent needs to continue without re-asking, re-discovering, or repeating mistakes.

## Core Principles

1. **Describe state.** Write "Auth is implemented; logout is not started," not "Implement logout next." The next agent chooses actions from the context.
2. **Link existing artifacts.** Reference PRDs, plans, ADRs, issues, commits, diffs, and design docs by path or URL instead of copying their content.
3. **Preserve why.** Capture decisions, rejected approaches, and failures that code alone cannot explain.
4. **Require verification.** Present claims as context to check against the actual code, not facts to trust blindly.
5. **Redact secrets and PII.** Never include keys, tokens, passwords, or personal data. Name credential locations (e.g. ".env.local, not committed"), never values.
6. **Keep only useful context.** Omit obvious, redundant, or explanatory material recoverable from code or project configuration.

## Procedure

1. Read existing project instructions (AGENTS.md or equivalent). Keep the handoff session-specific; do not repeat those instructions.
2. Read and update any prior handoff instead of starting from scratch.
3. Treat user-supplied arguments as the next session's focus.
4. Fill every template section; mark empty sections `None`.
5. Output the handoff in one fenced code block and save the same content as described under **File Output**.

## Output Format

Use this template inside a single fenced code block:

```
# HANDOFF: <short title of the work>
Generated: <timestamp> · Session focus: <one line>

## 1. Goal
<The overall objective in 1–3 sentences.>

## 2. Why This Matters / Background
<Motivation, intended users, timing, constraints, and hard requirements not already in project configuration.>

## 3. Current State
<What is DONE, PARTIAL, and NOT STARTED. Describe status, not actions:
- DONE: OAuth login flow, tests passing locally
- PARTIAL: Session storage wired up; refresh logic missing
- NOT STARTED: Logout endpoint>

## 4. Key Decisions (and why)
<Choices and reasoning, especially what cannot be recovered from code.
- Chose passport.js over custom OAuth — community support and less surface area
- Stored tokens in httpOnly cookies — XSS mitigation>

## 5. Traps & Dead Ends
<Failed approaches and pitfalls the next agent might repeat, with reasons.
- DB mocks made integration tests flaky; replaced with a test container
- SDK v3 breaks the streaming API this project relies on>

## 6. Relevant Files & Pointers
<Paths with line ranges and specific contents; link external artifacts instead of copying them.
- src/auth/oauth.ts:L40-L88 — provider config + token exchange
- docs/adr/0007-auth.md — full rationale
- PR #142 — in-progress session work
- Issue #150 — logout requirements>

## 7. Open Work (status, with dependencies)
<Remaining work and dependencies, stated as status rather than commands.
- Logout endpoint is not implemented
- Session persistence depends on the logout endpoint
- E2E auth tests are blocked until both are complete>

---
## Prompt for the Fresh Agent
<A short prompt with background context. Use declarative statements such as "X is complete" or "Y has not started." Preserve this exact closing instruction:>

Before responding, read every file listed under "Relevant Files & Pointers" above.
Do not summarize, paraphrase, or claim you already have context — actually read each
file. Treat every claim in this handoff as context to verify against the code, not
facts to trust blindly. Then wait for my instructions before taking any action.
```

## File Output

Save the same handoff outside the working tree, preferably in the OS temp directory: `$TMPDIR/handoff-<random-8-chars>.md` on macOS/Linux, or the system equivalent. If the user prefers an in-repo record, use `HANDOFF.md` in the project root.

Report the absolute path. The user can start a fresh session with:

```
Read the file <absolute-path> to get the context, then wait for instructions.
```
