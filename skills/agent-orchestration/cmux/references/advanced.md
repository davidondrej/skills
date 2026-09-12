# cmux advanced reference

## Layout and sidebar commands

Follow the main skill's targeting rules; verify layout changes. Read its viewer guide before moving or closing Markdown surfaces.

```bash
cmux list-workspaces --json
cmux new-pane --workspace "$CMUX_WORKSPACE_ID" --type browser --direction right --url http://localhost:3000 --focus false
cmux move-surface --surface surface:7 --pane pane:2 --focus false
cmux split-off --surface surface:7 right --focus false
cmux reorder-surface --surface surface:7 --before surface:3 --focus false
cmux close-surface --surface surface:7

cmux set-status build "compiling" --icon hammer --color "#ff9500"
cmux set-progress 0.5 --label "Building..."
cmux log --level success "All 42 tests passed"  # info|progress|success|warning|error
cmux trigger-flash --workspace "$CMUX_WORKSPACE_ID"
cmux sidebar-state --json
```

## Configuration

Before editing, read `cmux docs settings` and back up `cmux.json` to a timestamped `.bak` beside it.

```bash
cmux docs settings       # paths, schema, reload instructions
cmux settings path
cmux settings cmux-json  # open in editor
cmux reload-config      # reloads cmux and Ghostty settings
```

- cmux settings: `~/.config/cmux/cmux.json`; project overrides: `.cmux/cmux.json` or `./cmux.json`.
- Terminal rendering (font, cursor, theme, scrollback, opacity, blur): `~/.config/ghostty/config`.
- Schema: `https://raw.githubusercontent.com/manaflow-ai/cmux/main/web/data/cmux.schema.json`.

Keep both sidebar text previews off:

```jsonc
"sidebar": {
  "showWorkspaceDescription": false,  // custom/AI descriptions
  "showNotificationMessage": false   // latest agent message preview
}
```

`sidebar.hideAllDetails: true` additionally hides the entire detail block, including status, branch, and cwd.

## Installation and agent hooks

```bash
brew tap manaflow-ai/cmux && brew install --cask cmux
sudo ln -sf /Applications/cmux.app/Contents/Resources/bin/cmux /usr/local/bin/cmux
cmux hooks setup                # all supported agents found on PATH
cmux hooks setup --agent codex  # one agent; see cmux hooks setup --help
npx skills add manaflow-ai/cmux -g -y  # upstream agent skills
```

Session resume integrations include Claude Code, Codex, Grok, OpenCode, Pi, Amp, Cursor CLI, Gemini, Antigravity, Rovo Dev, Hermes, Copilot, CodeBuddy, Factory, and Qoder. Check installed hook help and agent docs for availability.

## Socket API and access modes

cmux terminals receive `CMUX_WORKSPACE_ID`, `CMUX_SURFACE_ID`, `CMUX_SOCKET_PATH`, and `CMUX_PORT`.

Use the raw socket when subprocess overhead matters; otherwise prefer the CLI. Use v2 `id`/`method`/`params` requests; legacy `{"command":...}` is rejected.

Use `CMUX_SOCKET_PATH`; otherwise the CLI defaults to `~/.local/state/cmux/cmux.sock` and discovers tagged/debug sockets. `/tmp/cmux.sock` is legacy. Raw clients must target the intended instance.

```bash
cmux_socket_path="${CMUX_SOCKET_PATH:-$HOME/.local/state/cmux/cmux.sock}"
echo '{"id":"1","method":"workspace.list","params":{}}' | nc -U "$cmux_socket_path"
```

Method families: `system.*`, `window.*`, `workspace.*`, `pane.*`, `surface.*`, `notification.*`, `browser.*`. Full list: `cmux capabilities --json`; API docs: `cmux docs api`.

Access modes in Settings > Automation:

- `cmuxOnly` (default): only cmux-spawned processes.
- `automation`: any local process.
- `password`: password authentication.
- `allowAll`: unrestricted access; unsafe.

External processes may fail under `cmuxOnly`: run inside cmux or choose an appropriate access mode. CLI authentication precedence: `--password`, `CMUX_SOCKET_PASSWORD`, then the password saved in Settings.

## Keyboard shortcuts

- Workspaces: ⌘N new, ⌘1–8 jump, ⌃⌘[ / ⌃⌘] previous/next, ⌘⇧W close, ⌘B sidebar.
- Surfaces: ⌘T new, ⌘⇧[ / ⌘⇧] previous/next, ⌘W close, ⌃1–8 jump.
- Splits: ⌘D right, ⌘⇧D down, ⌥⌘D browser right, ⌥⌘←→↑↓ focus, ⌘⇧↵ zoom.
- Browser: ⌘⇧L open, ⌘L address bar, ⌘[/⌘] back/forward, ⌥⌘I devtools.
- App: ⌘, settings, ⌘⇧, reload config, ⌘⇧P palette, ⌘⇧O restore session, ⌃⌥⌘. system-wide show/hide.

Use `cmux shortcuts` for the installed shortcut list.
