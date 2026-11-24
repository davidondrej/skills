# Capabilities

Discover the full installed surface instead of relying on a stale copied schema:

```bash
cua-driver list-tools
cua-driver describe get_window_state
cua-driver describe click
cua-driver manifest --pretty
```

These discovery commands do not create a desktop-control runtime. A listed tool
is not necessarily permitted by the current policy or supported by every app.

## Tool groups

- **Apps/windows:** `list_apps`, `launch_app`, `list_windows`, `set_window_frame`, `invoke_menu`.
- **Observation:** `get_window_state`, `get_accessibility_tree`, `verify_state`, `zoom`; full-screen `get_desktop_state` requires separately approved scope.
- **Input:** `click`, `double_click`, `right_click`, `type_text`, `set_value`, `press_key`, `hotkey`, `scroll`, `drag`.
- **Browser:** `browser_prepare`, `get_browser_state`, `browser_navigate`, `browser_click`, `browser_type`, `browser_pointer`, `browser_dialog`, `browser_download`, `browser_set_input_files`.
- **Sensitive/foreground:** `clipboard_read`, `clipboard_write`, `bring_to_front`, `kill_app`. Never treat discovery as authorization.
- **Sessions/cursors:** `start_session`, `get_session`, `list_sessions`, `end_session`, cursor inspection/configuration tools.
- **Recording:** `start_recording`, `get_recording_state`, `stop_recording`, `replay_trajectory`. Replay repeats actions; it is not just video playback.
- **Operations:** permission/configuration diagnostics, updates, telemetry, and optional history. These need operator approval when changing state.

## CLI pattern

Discover actual IDs and an allowed private output directory first. Replace the
illustrative numbers below; do not run them literally.

```bash
cua-driver call list_windows '{"pid":1234}'
cua-driver call get_window_state '{"pid":1234,"window_id":5678,"include_screenshot":false}'
# For visual grounding, capture to a private file allowed by the manifest:
cua-driver call get_window_state '{"pid":1234,"window_id":5678,"screenshot_out_file":"/approved/private/window.png"}'
# Read that image, then use the fresh element_token or matching snapshot_id.
```

`include_screenshot:false` is for semantic inspection, not pixel grounding.
Use the agent's image-reading tool rather than putting base64 in context.

## Browser and session limits

- Typed browser tools need an explicitly prepared, exact browser binding. Chromium/Electron support does not imply Safari/Firefox support.
- Prefer an isolated profile. A signed-in profile requires explicit approval; never copy cookies or profile files.
- Origin-scoped browser policies cannot also allow generic desktop input or window capture. Keep browser and native-app scopes separate.
- One-shot CLI calls have separate transport lifetimes. Use one persistent MCP/SDK connection for browser bindings, recording or shared lifecycle state. Repeating a public session label does not preserve that state.
- Pi has no built-in MCP. Do not add a bridge or dependency silently; basic CLI control works without one, while stateful workflows need an approved integration.

Sources: installed `list-tools` / `describe`,
[tools](https://cua.ai/docs/reference/cua-driver/mcp-tools),
[agent integration](https://cua.ai/docs/how-to-guides/driver/connect-your-agent),
[background limits](https://cua.ai/docs/concepts/the-no-foreground-contract),
[process model](https://cua.ai/docs/reference/cua-driver/process-model).
