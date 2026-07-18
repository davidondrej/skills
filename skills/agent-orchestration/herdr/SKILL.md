---
name: herdr
description: Operate and coordinate AI agents running inside Herdr in Ghostty. Use when the user says "Use the Herdr skill," mentions Herdr, or asks to inspect, message, wait for, or coordinate agents in a Herdr workspace. Herdr-specific; do not use for cmux or ordinary terminal sessions.
---

# Herdr

Herdr is terminal orchestration, not native agent-to-agent communication or shared memory. Agents call the `herdr` CLI, which controls panes through Herdr's local socket. This works across Pi, Codex, Claude Code, Cursor CLI, and other terminal agents. Native integrations only improve detection, status accuracy, and session restoration.

## Preconditions

The controlling agent must run inside Herdr in Ghostty. Verify access and workspace scope:

```bash
test "${HERDR_ENV:-}" = "1"
test -n "${HERDR_WORKSPACE_ID:-}"
```

If either fails, do not pretend to access other agents; tell the user the agent must be launched inside Herdr.

One-time installation:

```bash
npx skills add ogulcancelik/herdr --skill herdr -g
```

## CLI workflow

```bash
# Discover pane IDs in this workspace; never guess them
herdr pane list --workspace "$HERDR_WORKSPACE_ID"

# Read the target's recent context
herdr pane read <pane-id> --source recent-unwrapped --lines 120

# Send a prompt and press Enter
herdr pane run <pane-id> "Check the failing tests and report back."

# Wait for completion; use idle instead if that integration reports idle
herdr wait agent-status <pane-id> --status done --timeout 120000

# Read the result
herdr pane read <pane-id> --source recent-unwrapped --lines 120
```

Stay inside the current workspace. Read before messaging; for inspection-only requests, send nothing. After messaging, wait for `done`, `idle`, or `blocked`, then read the output again. Never assume the prompt was acted on.

Do not close, rename, move, resize, or reconfigure panes you did not create. Do not create or close panes unless the user explicitly asks. “Use the Herdr skill” means execute these CLI operations, not merely explain them.

## Sharp edges (empirically verified)

Hard-won facts from driving herdr in production. Trust these over intuition.

### Sessions & targeting

- Always append `--session <name>` to every command. The `HERDR_SESSION` env var alone silently falls back to whatever server is already running.
- Destructive ops only via `herdr session stop <name>` / `herdr session delete <name>` (explicit positional name). Never `herdr server stop` — it acts on whatever server is ambient.
- Target shape is `<session>:<pane-id>`; the pane id itself contains a colon (`w1:p2`). Split on the FIRST colon only.
- A bare CLI call does not auto-start a server. Start headless with `herdr server --session <name>`.
- Every herdr-managed process gets `HERDR_ENV=1` and `HERDR_PANE_ID`. Inside nested tmux, `$TMUX` wins — treat that pane as tmux.

### Sending input

- `pane send-text` types but does NOT submit — follow with `pane send-keys <pane> enter`. `pane run` = text + Enter in one call.
- C0 control bytes (e.g. ASCII 0x1f) are consumed as terminal control actions and can erase already-typed text. For invisible markers use U+2063 INVISIBLE SEPARATOR — it travels as text.
- Slash commands open an autocomplete popup; the first Enter may only close the popup or fill an argument placeholder, not submit. `escape` dismisses the popup and keeps the text.
- Never verify a submit by "pane content changed". Confirm via native agent status flipping to `working`/`blocked` after Enter.

### Reading panes

- `pane read --lines N` returns COMPLETELY EMPTY output when N is smaller than the pane's viewport height. Always request >=200 lines and trim locally (`tail -n N`).
- `pane get` `.cwd` is frozen at pane creation. Use `.foreground_cwd` for the live working directory.
- `pane read --format ansi` preserves styling. Ghost/placeholder composer text (rotating suggestions, hints) renders dim (SGR-2) or dark truecolor; real typed input renders normal. This is the only reliable way to tell an empty composer from a human draft.

### Agent state

- `herdr agent get <pane>` reports `working`/`idle`/`done`/`blocked`/`unknown` — native detection, better than regex-guessing.
- Known gap: status reads `idle` during a long-running foreground tool call (the model finished its turn; the tool is still grinding). Corroborate an `idle` verdict with pane text (busy banners like "esc to interrupt") before treating a pane as free or stale.
- Blocking waits exist: `herdr agent wait <pane> --status <s> --timeout MS` and `herdr wait output <pane> --match <text>`.
- Push events over the socket (protocol >=16): `pane.agent_status_changed`, `pane.output_matched`. Use as the fast path; keep polling as the backstop.
- Any script can register itself as an agent via `pane report-agent` and report idle/working/blocked.

### Workspace / tab lifecycle

- NO label uniqueness anywhere: workspaces and tabs can share labels. Do your own duplicate checks; find-by-label adopts the first match. An unlabeled workspace displays its cwd basename as its label — a real collision hazard (once caused an adapter to kill a live agent pane it wrongly adopted).
- `workspace create` seeds one default tab labeled `1`. Closing a workspace's LAST tab deletes the workspace. Closing a tab's only pane closes the tab.
- `--no-focus` is respected on workspace/tab create, except the very first workspace in an empty session (always focuses). `pane split --no-focus` still shrinks the host tab's viewport — the flag governs focus, not geometry.
- Workspace/tab/pane IDs and labels survive a server restart within a named session. The processes and agent registrations do NOT — panes return as husks (fresh shell, `agent get` reports `agent_not_found`). Close-and-replace husks; don't treat them as live duplicates.

### Misc

- `tput cols` inside a script launched via `pane run` reports a stale default (80). Never trust it for layout math.
- For risky experiments use an isolated named session (never `default`), and re-check `herdr session list --json` immediately before any stop/delete.
- `herdr integration install <harness>` (claude, codex, cursor, pi, ...) enables native status detection per agent. `herdr notification show <title>` fires a desktop-style alert.

## Prompt patterns

- **Inspect:** “Use the Herdr skill. Inspect every agent in this workspace, read its recent output, and summarize its task and status. Do not send anything.”
- **Ask:** “Use Herdr to find the testing agent, read its context, ask whether the test suite passes, wait for its response, and report back.”
- **Coordinate:** “Act as lead agent. Inspect all agents, share missing context, prevent duplicate work, wait for results, and give me one combined summary.”

## Direct shortcuts

Most defaults use the `Ctrl+B` prefix. Prefer direct `Ctrl+Alt` shortcuts, which rarely conflict. Add to `~/.config/herdr/config.toml`:

```toml
[keys]
new_workspace = "ctrl+alt+n"
workspace_picker = "ctrl+alt+w"
goto = "ctrl+alt+g"
new_tab = "ctrl+alt+c"
```

Apply changes:

```bash
herdr server reload-config
```

To keep prefixed shortcuts but change the prefix, set `prefix = "ctrl+a"` under `[keys]`.
