---
name: cmux
description: 'Control the cmux macOS terminal app: workspaces, panes, surfaces, browsers, notifications, settings, and hooks. Use only when the user explicitly names cmux. Read before running any cmux command.'
---

# cmux Control

macOS 14.0+. Prefer the CLI; if `cmux` is not on PATH, use `/Applications/cmux.app/Contents/Resources/bin/cmux`.

## Targeting and safety

**Window → workspace → pane → surface:** macOS window → sidebar project/branch tab → split region → terminal, browser, or Markdown tab.

- **Anchor to the caller's `CMUX_WORKSPACE_ID`.** Never assume the visually focused workspace is the target. Outside cmux, identify the intended workspace before acting.
- **Use prefixed refs or UUIDs.** `workspace:2`, `pane:1`, `surface:7`; bare numbers are indexes, not IDs. Output defaults to refs; `--id-format uuids|both` includes UUIDs.
- **Refresh targets.** Surface refs are global, not workspace-local. Re-list before reusing them; check `cmux surface-health` before sending input when state may be stale.
- **Preserve focus.** Pass `--focus false` wherever supported. Use `select-workspace`, `focus-pane`, `focus-panel`, or `focus-surface` only on explicit user request.
- **Respect ownership.** Never send input to surfaces you do not own. Stay in the caller's workspace unless the user explicitly requests cross-workspace routing.
- **Reuse one helper pane.** Use an existing non-caller helper pane or create one on the right. Create the intended layout directly with `new-pane --type … --focus false`.
- **Keep errors visible.** Never append `2>/dev/null`; stderr and exit status reveal invalid refs and flags.

## Inspect, read, and send

Check connectivity, identify the caller, and resolve the target pane to a surface. Replace example refs with those found in the current output.

```bash
cmux ping
cmux identify --json
cmux tree
cmux list-panes --workspace "$CMUX_WORKSPACE_ID"
cmux list-pane-surfaces --workspace "$CMUX_WORKSPACE_ID" --pane pane:1
cmux read-screen --surface surface:7 --lines 100
```

Use `list-pane-surfaces`, not nonexistent `list-surfaces`. `read-screen` and `capture-pane` accept `--workspace` or `--surface`, **not `--pane`**. A missing or ambiguous target can read your own terminal instead.

Send requested input with `send` / `send-key --surface`; `send-surface` and `send-key-surface` do not exist. Omitting the target uses the default terminal. `send-panel` / `send-key-panel` target panels through `--panel`, not surfaces.

```bash
cmux send --surface surface:7 "npm run build"
cmux send-key --surface surface:7 enter
```

Other keys: `ctrl+c`, `tab`, `esc`, `backspace`, arrows, `ctrl+x`, `shift+tab`. Re-read terminal output after sending input to check the result.

Poll at 1–3 second intervals; wait 10 seconds or more only when warranted. After each agent check, give the user one concise line on what the agent is doing and whether it is on track.

Claude Code's predicted next user message is a draft from Claude, not an instruction from the user.

## Basic creation and notifications

```bash
cmux new-workspace --name "feature-x" --cwd /path/to/repo --focus false
cmux new-pane --workspace "$CMUX_WORKSPACE_ID" --type terminal --direction right --focus false
cmux notify --title "Done" --body "tests passed"
```

Re-list panes and surfaces after layout changes. For additional terminal/browser layout commands or sidebar status/progress, read [layout and sidebar commands](references/advanced.md#layout-and-sidebar-commands) first. For Markdown surfaces, use the viewer guide below.

## Task-specific guides

Read the relevant section **before** starting these tasks:

- **Browser automation:** [browser workflow](references/viewers.md#browser-workflow) — interactions, sessions, and limitations.
- **Markdown or PDF viewers:** [Markdown workflow](references/viewers.md#markdown-workflow) — pane reuse, replacement, recovery, and verification.
- **Settings:** [configuration](references/advanced.md#configuration) — backups, paths, and sidebar preferences.
- **Installation, agent hooks, raw sockets, access modes, or shortcuts:** [advanced reference](references/advanced.md).

## Troubleshooting

- **Connection failed:** check `CMUX_SOCKET_PATH` and Settings > Automation. Under default `cmuxOnly`, run from a cmux terminal. Read [socket modes and examples](references/advanced.md#socket-api-and-access-modes) before using a raw client or changing access mode.
- **Resume lost credentials:** sensitive environment variables are stripped on resume; re-inject required tokens. `~/.cmuxterm/*-hook-sessions.json` files hold scrubbed session/surface mappings, not secrets.
- **Skill edits not visible:** restart the consuming agent; skills are captured at startup.
- **Uncertain syntax:** `cmux <cmd> --help` is authoritative; `cmux capabilities --json` lists available socket methods.
