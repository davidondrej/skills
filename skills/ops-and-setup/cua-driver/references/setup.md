# Setup and recovery

## MacBook installation

- Binary: `~/.local/bin/cua-driver`; app: `/Applications/CuaDriver.app`.
- Operator notes: operator notes. Use normal `standard` mode; no custom capability manifest or agent-added session timeouts.
- Configuration: `~/.cua-driver/config.json`. Keep telemetry off and recording/history opt-in.
- Other hosts must be checked independently; installing this skill does not install the driver.

Use only the official stable installer after user approval. Review downloaded
scripts, pin a release, and verify the app signature. Do not auto-upgrade during
a GUI task or modify existing Codex/MCP settings.

## Permission approval — user present

Accessibility allows UI control; Screen Recording allows screenshots. Grants
must belong to `CuaDriver.app`, not an unrelated terminal process.

Only when the user is ready for dialogs:

```bash
cua-driver permissions grant
cua-driver permissions status --json
```

The user enables CuaDriver in System Settings → Privacy & Security →
Accessibility and Screen & System Audio Recording, and accepts any requested
relaunch. Tahoe may also ask for direct-capture consent.

Start only the reviewed daemon configuration from the operator notes. On macOS,
use LaunchServices or the approved LaunchAgent, not a raw shell-spawned daemon.
`--no-permissions-gate` suppresses onboarding UI; it does not grant OS access.
Never start a second, broader runtime to get around the current policy.

## Checks and failures

```bash
cua-driver status
cua-driver permissions status --json
cua-driver doctor --json
cua-driver telemetry status --json
```

- No daemon / unknown grants: do not infer readiness from a version string.
- Permission still missing after approval: fully relaunch the approved app, then check again. Never reset TCC or touch Keychain without approval.
- `permission_denied` / resource outside manifest / expired scope: stop; ask the user to review scope or authorize a new session. Do not broaden or renew it silently.
- Stale element: capture again. Blank/degraded state: do not click blindly or escalate to foreground.
- CLI unavailable in an app-launched shell: use `~/.local/bin/cua-driver`; do not rewrite shell settings unnecessarily.

## Maintenance

Keep the local skill separately owned. Do not run `cua-driver skills install`
or `skills update` over it. Use `list-tools` and `describe TOOL` for the installed
release's exact surface; review official docs when upgrading.

Before an authorized update, unload the approved LaunchAgent and stop its daemon.
Review/pin the replacement, preserve the user's configuration, then recheck
signature, telemetry, permissions and an authorized harmless action. Test logout/login
before claiming startup persistence. See operator notes for stop/uninstall.

Sources: [install](https://cua.ai/docs/how-to-guides/driver/install),
[permissions](https://cua.ai/docs/reference/cua-driver/macos-permissions),
[process model](https://cua.ai/docs/reference/cua-driver/process-model),
[capability manifests](https://cua.ai/docs/how-to-guides/driver/write-a-bounded-manifest).
