---
name: herdr
description: Operate and coordinate AI agents in Herdr workspaces in Ghostty. Use when the user mentions Herdr or asks to inspect, message, wait for, or coordinate its agents. Excludes cmux and ordinary terminal sessions.
---

# Herdr

Herdr's CLI controls terminal panes through a local socket; it provides neither native agent-to-agent communication nor shared memory. It works with Pi, Codex, Claude Code, Cursor CLI, and other terminal agents. Native integrations improve detection, status accuracy, and session restoration.

## Preconditions

Run the controlling agent inside Herdr in Ghostty. Verify access and workspace scope:

```bash
test "${HERDR_ENV:-}" = "1"
test -n "${HERDR_WORKSPACE_ID:-}"
```

If either fails, tell the user this agent must be launched inside Herdr; do not claim access to other agents.

One-time installation:

```bash
npx skills add ogulcancelik/herdr --skill herdr -g
```

## Inspect, message, wait, read

Append `--session <name>` to every Herdr command. `HERDR_SESSION` alone can silently select an already-running server. Discover pane IDs; never guess them.

```bash
herdr pane list --workspace "$HERDR_WORKSPACE_ID" --session <name>
herdr pane read <pane-id> --source recent-unwrapped --lines 200 --session <name>

# For TUI agent composers, separate text from Enter
herdr pane send-text <pane-id> "Check the failing tests and report back." --session <name>
sleep 1
herdr pane send-keys <pane-id> enter --session <name>

# Confirm submission, then wait for completion (idle if the integration uses it)
herdr agent wait <pane-id> --status working --timeout 120000 --session <name>
herdr agent wait <pane-id> --status done --timeout 120000 --session <name>
herdr pane read <pane-id> --source recent-unwrapped --lines 200 --session <name>
```

Stay in the current workspace. Read before messaging; send nothing for inspection-only requests. Confirm submission through a native status transition to `working`/`blocked` after Enter, never merely changed pane content. Wait for `done`, `idle`, or `blocked`, then read again; do not assume the prompt was acted on. Corroborate `idle` with pane text as described below.

When coordinating agents, share missing context, prevent duplicate work, and return one combined summary.

Do not close, rename, move, resize, or reconfigure panes you did not create. Create or close panes only when the user explicitly asks. “Use the Herdr skill” means execute the CLI workflow, not merely explain it.

## Operational details

### Sessions and targeting

- Use named `herdr session stop <name>` / `herdr session delete <name>` for destructive operations. Never use `herdr server stop`; it targets the ambient server.
- Targets are `<session>:<pane-id>`. Pane IDs contain a colon (`w1:p2`); split on the **first** colon only.
- CLI calls do not auto-start a server. Start headless with `herdr server --session <name>`.
- Managed processes receive `HERDR_ENV=1` and `HERDR_PANE_ID`. Inside nested tmux, `$TMUX` wins: treat the pane as tmux.
- Use an isolated named session, never `default`, for risky experiments. Re-check `herdr session list --json --session <name>` immediately before stopping or deleting.

### Input

- `pane send-text` types without submitting. `pane run` sends text + Enter and works at shell prompts, but TUI composers (Claude Code, Cursor CLI) may swallow Enter as part of a paste. Use separate `send-text`, ~1s pause, then `send-keys <pane> enter` calls for TUIs.
- C0 control bytes (e.g. ASCII 0x1f) trigger terminal actions and can erase typed text. Use U+2063 INVISIBLE SEPARATOR for invisible text markers.
- Slash-command autocomplete may consume the first Enter to close the popup or fill an argument placeholder. `escape` dismisses the popup while preserving text.

### Reading and status

- `pane read --lines N` returns empty output if N is below viewport height. Request at least 200 lines and at least the viewport height; trim locally with `tail -n N`.
- `pane get` `.cwd` is fixed at creation; `.foreground_cwd` is live.
- Use `pane read --format ansi` to distinguish placeholder text from human drafts: suggestions are dim (SGR-2) or dark truecolor; typed input renders normally. Plain text cannot reliably distinguish them.
- `herdr agent get <pane>` reports native `working`/`idle`/`done`/`blocked`/`unknown` status; prefer it to regex guesses. Long-running foreground tools may still report `idle`; check busy banners such as "esc to interrupt" before treating the pane as free or stale.
- Native waits: `herdr agent wait <pane> --status <s> --timeout MS`, `herdr wait agent-status <pane> --status <s> --timeout MS`, and `herdr wait output <pane> --match <text>`.
- Socket protocol >=16 offers `pane.agent_status_changed` and `pane.output_matched` events. Prefer events, with polling as a backstop.
- Scripts can register via `pane report-agent` and report idle/working/blocked.

### Workspace and tab lifecycle

- Labels are not unique. Check duplicates yourself; find-by-label adopts the first match. Unlabeled workspaces display their cwd basename, which can collide with an explicit label.
- `workspace create` seeds tab `1`. Closing the last tab deletes the workspace; closing a tab's only pane closes the tab.
- Workspace/tab creation respects `--no-focus`, except the first workspace in an empty session. `pane split --no-focus` still shrinks the host viewport: focus and geometry are separate.
- Named-session restarts preserve IDs and labels, but not processes or agent registrations. Restored panes are fresh shells (`agent_not_found`), not live duplicates; close and replace them only within the pane permissions above.

### Other details

- Do not use `tput cols` for layout in scripts launched through `pane run`; it can report a stale default of 80.
- `herdr integration install <harness>` (claude, codex, cursor, pi, ...) enables native status detection. `herdr notification show <title>` displays an alert.

## Launch agents only when the user asks

### Launching agents in new panes

Use each agent's normal approval and sandbox defaults unless the user has
explicitly authorized unattended execution for this specific pane. A worker
that waits for approval is safer than silently granting a prompt permission to
run arbitrary commands. The `global-agent-guardrails` deny-list is defense in
depth, not a permission boundary: it only matches known patterns and can miss
obfuscated commands or harmful changes that are not on the list.

For the normal, approval-aware launch, omit the bypass flags:

- Cursor CLI: `cursor-agent "task"`
- Codex CLI: `codex "task"`
- Claude Code: `claude "task"`

Only when the user has explicitly approved unattended execution, the worktree
is isolated, and the output is reviewable, use the corresponding force flag:

- Cursor CLI: `cursor-agent --yolo "task"` (alias for `--force`)
- Codex CLI: `codex --yolo "task"`
- Claude Code: `claude --dangerously-skip-permissions "task"`

Before using a force flag, confirm that the prompt is trusted, no credentials
are in scope, and the task does not include publishing, deleting, purchasing,
or changing account/security settings. First-run trust dialogs may still appear
despite these flags — peek the pane after launch. `herdr integration install
<cursor|codex|claude>` (once each) enables native agent-status detection.
The deny-list hook is defense in depth, not a permission boundary. First-run
trust dialogs may still appear; inspect the pane after launch. Install each
integration once for native status detection.

Verify launch with `herdr agent wait <pane> --status working --timeout MS` or `herdr wait output <pane> --match <text>`, then read. Never use `sleep N && pane read` as launch verification; the short input-submission pause above serves a different purpose.

### Cursor CLI

Use `cursor-agent` in scripts. `agent` is an alias/new docs name; the user's interactive `cur` shorthand expands to `cursor-agent --yolo`, but aliases do not expand in scripts.

Discover available model slugs with `cursor-agent --list-models` before launching into an existing shell pane:

```bash
herdr pane run <pane-id> "cd <worktree> && cursor-agent --model <verified-model-slug> --yolo 'fix the failing tests'" --session <name>
```

- **Interactive:** `cursor-agent "task"`, or no argument for an empty session. **Headless:** `cursor-agent -p "task" --output-format text|json|stream-json`.
- **Permissions:** `--force` / `--yolo` skips per-command approval; `--sandbox enabled|disabled` controls sandboxing. Script auth: `CURSOR_API_KEY`.
- **Model:** `--model <slug>` at launch, `/model` in-session. Slugs vary by version/account; never invent them from memory.
- **Effort:** no `--effort` flag. Use full slugs ending in `-low`, `-medium`, `-high`, or `-xhigh` (e.g. `gpt-5.3-codex-xhigh`, `claude-opus-4-8-thinking-high`). `-fast` controls speed, not effort. Despite `--help`, `model[effort=high]` is unsupported.
- Some builds silently drop `--model` reasoning suffixes. Verify with `/model` after launch; `--disable-auto-update` preserves a working build.
- **Resume:** `cursor-agent resume` (latest), `--resume <chatId>`, or `cursor-agent ls` to list.

## Direct shortcuts

Most defaults use `Ctrl+B`. Direct `Ctrl+Alt` shortcuts rarely conflict. Add to `~/.config/herdr/config.toml`:

```toml
[keys]
new_workspace = "ctrl+alt+n"
workspace_picker = "ctrl+alt+w"
goto = "ctrl+alt+g"
new_tab = "ctrl+alt+c"
```

Apply with:

```bash
herdr server reload-config --session <name>
```

To keep prefixed shortcuts with a different prefix, set `prefix = "ctrl+a"` under `[keys]`.
