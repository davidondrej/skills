---
name: reset-cursor-acp
description: 'Reset a stuck Cursor ACP thread in <chat-system> and reload its configuration. Use only when the user explicitly invokes /reset-cursor-acp.'
disable-model-invocation: true
---

# Reset Cursor ACP in <chat-system>

For terminal sessions use `cursor-cli`; for general <chat-system> control use `<chat-cli>`.

## How resets work

- The `<ACP-plugin>` starts one `cursor-agent acp` subprocess **per thread, on demand**, owned by a `<bridge-worker>`.
- **There is no global Cursor ACP server.** Do not create one or keep it alive with a watchdog.
- Rules, skills, and `.cursor/mcp.json` reload when a new subprocess starts.
- `<chat-cli> thread stop <id>` releases the runtime and stops its subprocess, preserving history. The next message starts a fresh agent.

## Quick reset

Resolve `<reset-script>` relative to this `SKILL.md`. Run:

```bash
<reset-script> <thread-id>      # reset one Cursor thread
<reset-script> --self           # reset the current thread (<CURRENT_THREAD_ID>)
<reset-script>                  # no thread: orphan cleanup + health check only
<reset-script> --dry-run        # show what would happen
<reset-script> <id> --kill-all  # also kill live agents of OTHER Cursor threads
```

Find Cursor thread ids with `<chat-cli> status` (current thread) or:

```bash
<thread-list-command>
```

The script stops the selected thread, removes orphaned `cursor-agent acp` processes (parent gone or not a <bridge-worker>), reports CLI version/login/update status, and asks for the next message. Other threads stay running unless `--kill-all`.

If sandboxing blocks `ps` with "operation not permitted", rerun the script outside the sandbox.

## Verify

Send one short message to verify a fresh agent responds. If it hangs again, check the causes below before another reset.

## Known causes

- **Old Cursor CLI.** If the health check shows an update, run `<update-command>`, then reset.
- **Expired login.** Symptom "Failed to initialize session services". Fix: `cursor-agent login`, then reset.
- **Pending permission.** Cursor waits for `session/request_permission`. Check and resolve the thread's pending approval before resetting.
- **Resume failure.** For `session/load` → "Session not found", use a fresh session after `<chat-cli> thread stop` rather than retrying the load.
- **Team-level MCP servers** from the Cursor dashboard do not work in ACP mode. Only project or user `.cursor/mcp.json`.
- **Rate limits.** Enable retries with `<chat-cli> plugin enable <retry-plugin>`.

## Do not

- No launchd KeepAlive, cron, or watchdog for `cursor-agent acp`.
- Never blindly run `pkill -f cursor-agent`; it kills all Cursor threads and the interactive TUI. Use the script, which targets orphans by default.
- Do not restart <chat-system> for one stuck thread; use `<chat-cli> thread stop`.
- Do not use `<chat-cli> thread compact`; Cursor does not support it.
