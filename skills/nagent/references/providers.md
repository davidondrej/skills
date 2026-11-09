# Provider Details

Use these examples to interpret names, then verify IDs and supported settings in `bb provider models <provider-id> --json` before spawning.

## Cursor CLI: Grok 4.6 Extra High Fast

```bash
--provider acp-cursor \
--model cursor-grok-4.6-medium \
--reasoning-level xhigh \
--service-tier fast
```

- The model ID stays `cursor-grok-4.6-medium`; Extra High is a reasoning setting.
- In this example's catalog, `high` displays as Fast and `xhigh` as Extra High. The fast service tier is a separate flag.
- Cursor Task-tool names such as `cursor-grok-4.6-high-fast` are not bb model IDs.

## Codex: GPT 5.6 Sol Max

```bash
--provider codex \
--model gpt-5.6-sol \
--reasoning-level max
```

Use native `gpt-5.6-sol`, not the Cursor-routed `cursor/gpt-5.6-sol`. Max is a reasoning level, not a model suffix. Choose the service tier using the main skill's defaults and the user's request.

## Cursor Permissions

Cursor ACP supports `full` and `accept-edits`, not `auto`. Codex supports `auto`.

For a non-full Cursor worker, the Cursor allowlist applies because bb does not pass `--force` to `cursor-agent`. Check `~/.cursor/cli-config.json` → `permissions.allow` and any project `.cursor/cli.json`, which can override global settings.

A message such as "Not in allowlist: git -C" may come from a narrow entry like `Shell(git status)`. Inspect the requested command and the active configuration. Keep any permission change within the authorized brief; do not broaden access merely to silence an approval.
