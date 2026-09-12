---
name: nagent
description: Launch a new bb worker thread with the right project, model, worktree, and task brief. Use for nagent, launching a bb session, or a standalone bb agent. Covers thread creation; use bb-cli for managing existing threads.
---

# nagent

Read this before `bb thread spawn`. Use `bb-cli` for other thread operations.

## Defaults

Use Codex `gpt-5.6-sol`, reasoning `high`, service tier `fast` ("GPT 5.6 Sol High Fast"). Use `xhigh` for larger refactors. The user's explicit choices override these defaults.

For a different requested model, use its catalog `defaultReasoningEffort` when unspecified, and enable fast only when asked. Do not infer a higher reasoning level from the model name.

Prefer bare `bb`; `"$BB_CLI"` is also valid when set.

## Look Up the Target

```bash
bb project list --json
bb provider list --json
bb provider models <provider-id> --json
```

- **Project:** Match the name and confirm `sources[].path` is the requested repository. Always pass `--project`; never hardcode an ID.
- **Provider:** Look it up. Common mappings are Cursor CLI → `acp-cursor`, Codex/ChatGPT subscription → `codex`, and Claude Code → `claude-code`. Grok via Cursor is not `acp-grok`, which is Grok Build.
- **Model:** Use the catalog ID. Match both `displayName` and `supportedReasoningEfforts[].description`; model IDs, reasoning labels, and service tiers are separate.

For Cursor/Grok or Codex Max naming traps, read [provider details](references/providers.md). Verify examples against the current catalog; do not guess IDs or substitute a different provider.

## Permission Checks

The user's investigation/build workers default to `full`. A child cannot exceed the parent's permission mode, so verify the parent before requesting it and the child after spawning.

Run the bundled script relative to this skill's directory:

```bash
scripts/permission-mode.sh "$BB_THREAD_ID"
```

For a `full` worker, this must print `full`. Otherwise, stop and report that the requested mode is unavailable under the parent's limits. Do not bypass those limits. If the user requests another mode, confirm the provider supports it.

The modes are `accept-edits` (sandbox, human-reviewed escalations), `auto` (sandbox, automatic review), and `full` (no sandbox). A read-only brief must forbid writes regardless of mode. For Cursor permission issues, use the provider-details reference.

## Spawn

Use the resolved IDs and chosen settings. This example shows the default worker's reasoning, tier, and permissions; replace them when the user requests different settings.

```bash
bb thread spawn --json \
  --project <project-id> \
  --new-environment worktree \
  --provider <provider-id> \
  --model <model-id> \
  --reasoning-level high \
  --service-tier fast \
  --permission-mode full \
  --title "Short title" \
  --prompt "$(cat <<'EOF'
Objective: ...
Constraints: ...
Skills and files: ...
Deliverable: ...
Validation: ...
Report back: ...
EOF
)"
```

Always include `--json`, `--title`, and a complete prompt. The quoted heredoc preserves quotes in the brief.

## Parent and Sidebar Placement

- Omit parent flags for a standalone, top-level thread: "not as your own subagent".
- Use `--parent-self` when this thread coordinates the worker or the job is its subtask.
- Use `--parent-thread <id>` to nest under another thread. Never combine the two parent flags.

Do not nest unrelated one-off work by default.

## Worktree

Use `--new-environment worktree` for a bb-managed worktree. Do not create one manually unless the user asks.

- Worktrees start with tracked files. Include required untracked files such as `.env` through the repo's `.worktreeinclude`; setup may also use `.bb-env-setup.sh`. See `bb guide environments`.
- Omit `--base-branch` for the project default; specify it only when needed.
- Do not combine `--machine` with an existing `--environment` ID.
- A null `environmentId` in the spawn response can mean the worktree is still being created.

## Task Brief

The worker does not see this conversation. State the objective, constraints, relevant skills/files, deliverable, validation, and expected report. Name the skills it must read rather than assuming your context carries over.

For read-only jobs, explicitly say **no code changes, no Git writes, no database writes**. For implementation, specify the allowed scope and any Git or production restrictions. Ask for a concise report, including changed files and validation when relevant.

## Verify and Report

```bash
scripts/permission-mode.sh <child-thread-id>
```

Confirm the child received the requested mode. If it differs or is unknown, report the mismatch rather than claiming a successful setup.

Report the thread ID, title, project, provider/model/reasoning/tier, worktree yes/no, and read-only versus implementation scope. Then stop. Do not dump the prompt, open/focus the thread, poll, wait, or read work logs unless the user asks.

## Blocked Workers and Lifecycle

If bb reports a blocker, inspect it with `bb thread interactions list <id> --json`. Resolve routine input within the brief, and approve an action with `bb thread interactions approve <interactionId> <id>` only when it is authorized and safe. Ask the user about destructive actions, production access, unclear decisions, or work outside the brief. Do not monitor just to look for blockers.

Use `bb-cli` for lifecycle commands. Archive only when the user asks, then stop the thread to release its runtime. Never delete without an explicit request, and do not use hiding as a substitute for archiving.
