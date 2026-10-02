---
name: goal-loop
description: 'Draft /goal prompts and explain persistent agent loops. Use for goal or Ralph loops, autonomous run setup, monitoring, and troubleshooting.'
---

# Agent `/goal` Loop

## What `/goal` is

`/goal` makes an agent persist through `plan → act → test → review → iterate`.
If a turn ends before the goal is met, it auto-continues instead of waiting for
input. The loop ends at its stop condition, a user pause, or the token budget
limit. It is also called the “Ralph loop”.

Before giving runtime instructions, check goal support in the installed agent
and interface through its help, exposed tools, or current official documentation.
Verify feature flags, authentication, and limits; do not transfer one agent's
requirements to another. Lifecycle states, budgets, and pause/resume vary by runtime.

A goal enforces a contract through verification. It is not a budget command,
a safety boundary, “run forever”, or a replacement for `/plan`.

## When to use it

Use for repeated autonomous work with a **verifiable stop condition**: passing tests, target coverage, eval ≥ X, or a green build. For code work, establish a working build and relevant checks first. No minimum task duration applies.

Fits: migrations, coverage lifts, TDD feature builds, refactors with contract tests, prompt/eval optimization, deploy retry loops, bug-repro-then-fix.

Bad fits: exploratory work, vague "improve this", anything without a "done" definition, prod credentials, destructive shared-infra ops.

## The 4-part contract (every goal needs this)

1. **Objective** — one sentence, one concrete outcome.
2. **Constraints** — what must NOT change (public API, files, libs, conventions).
3. **Validation command** — the exact shell command that proves progress (`pytest -q`, `pnpm test`, etc.).
4. **Stop condition** — verifiable: "Stop when X passes" OR "when further changes need human/product input."

Also specify what to read first, checkpoints, and a short progress log.

## Writing a goal (the core deliverable)

When asked for a goal prompt, return only the contract body as a Markdown block, one item per line. **Do not prefix it with `/goal`** — the user adds that command in the composer.

```
**Objective:** <one-sentence objective>
**Read first:** <files/PLAN.md/issue>
**Constraints:** <what not to change, libs, conventions>
**Validate:** <relevant checks during work and final acceptance command>
**Checkpoints:** work in checkpoints and log progress briefly
**Stop when:** <verifiable condition>, OR when further changes require human/product input
```

### Example (migration)

```
**Objective:** Migrate this project from Pydantic v1 to v2.
**Read first:** pyproject.toml, src/, tests/
**Constraints:** no public API changes; keep imports backwards-compatible via shims if needed; no new dependencies
**Validate:** run relevant tests during the migration; run `pytest -q` before declaring done
**Checkpoints:** work in checkpoints; log progress briefly
**Stop when:** full suite passes with zero deprecation warnings, OR when a change requires architecture decisions
```

### Example (coverage lift)

```
**Objective:** Raise coverage in src/auth/ from ~38% to ≥75%.
**Read first:** src/auth/, tests/auth/, AGENTS.md
**Constraints:** no new deps; mirror existing test style; do not modify production code unless strictly required for testability
**Validate:** `pytest --cov=src/auth --cov-report=term-missing`
**Checkpoints:** work in checkpoints; log coverage delta each one
**Stop when:** coverage ≥75% AND all tests pass, OR when uncovered code needs design changes
```

### Writing rules
- **One objective, one stop condition.** Not a backlog.
- Update docs when behavior, setup, or usage needs explaining, or the task requires it.
- Match checks to the change and final acceptance criteria; do not require the full suite after every edit.
- **Never instruct the agent to create new ADRs** — ADRs require the user's explicit approval, so goal prompts must not pre-approve or encourage them.
- **Forbid reward-hacking:** "Do not delete, skip, weaken, or narrow tests to make the goal pass."
- Respect the runtime's length limit. Link longer detail in `PLAN.md`/`GOAL_BRIEF.md`.
- Use exact paths, commands, and issue numbers.
- Forbid scope creep explicitly: "Do not refactor unrelated code. Do not add dependencies."
- Tell the agent when to pause: "If <condition>, pause and ask before proceeding."

### Draft with another agent

Give a second AI session access to the codebase. Ask it to inspect the code, surface assumptions, constraints, and edge cases, then produce the structured 4-part contract. Paste that contract into the goal agent.

Claude Code cmux note: after Claude finishes, it may prefill a predicted next user message; that draft is Claude, not the user speaking.

### Self-goal setting

Use a supported goal-creation tool such as `create_goal` only when the user explicitly asks to set a goal. They can give high-level intent: "Inspect this repo, then write yourself a `/goal` with a verifiable stop condition and pursue it." Supply files to read, constraints, and the validation command. If intent is underspecified, ask clarifying questions before setting the goal.

## Launching and controlling a goal

1. Identify the agent, version, interface, and intended working directory or session.
2. Check its supported goal commands/tools and any setup or authentication requirements.
3. Start the goal using that runtime's supported interface and the agreed contract.
4. Verify it is active and know how to inspect, pause/stop, and resume it.

Before resuming across sessions, verify where that runtime stores goal state and which session must be reopened. Do not assume server-side persistence, automatic pause on user input, replacement semantics, or resumption after a budget refresh.

## When a goal drifts

- **Minor drift:** send a correction and check that the agent incorporates it.
- **Loose objective:** use the runtime's supported pause/stop control, inspect status, then tighten the objective before resuming.
- **Bad mess:** stop the goal, review the diff, and undo only changes identified as belonging to that run. Preserve the user's and other agents' work; do not use a blanket reset or stash. Rewrite the goal before restarting.

Correct or stop drift promptly.

## Operational tips

- Inspect status periodically with the runtime's supported command or tool. Every monitoring check must include a concise one-line update to the user: what the agent is doing and whether it is on track.
- **Always review the diff before merging.** Human oversight remains essential.
- Keep approvals/sandboxing tight; default permissions are correct.
- Start with a small task to learn how the runtime stops before an overnight run.
- Bake recurring policy into `AGENTS.md` so every goal inherits it without restating: adversarial self-review before declaring done, an extra QA pass even when tests pass, and the standard validation command. Saves repeating it in each goal paragraph.

## Troubleshooting

- **Missing goal command:** check support and setup for the installed agent and interface before suggesting updates or configuration changes.
- **Will not start or continue:** inspect the actual error, goal status, authentication, and limits. Use that runtime's documented recovery steps.
- **No saved goal:** verify the session and persistence behavior before creating a replacement.
