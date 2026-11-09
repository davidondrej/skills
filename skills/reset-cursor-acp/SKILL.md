---
name: reset-cursor-acp
description: 'Reset a stuck Cursor ACP thread in a thread manager and reload its configuration. Use only when the user explicitly invokes /reset-cursor-acp.'
disable-model-invocation: true
---

# Reset Cursor ACP in a thread manager

For terminal sessions use `cursor-cli`; for general thread-manager control, use its documented CLI.

## How resets work

- A thread manager may start one `cursor-agent acp` subprocess per thread, on demand.
- Do not assume there is a global Cursor ACP server or create one with a watchdog.
- Rules, skills, and `.cursor/mcp.json` reload when a new subprocess starts.
- Stop the selected thread using the thread manager's documented procedure to release its runtime while preserving history. The next message starts a fresh agent.

## Quick reset

Use the reset utility documented for your thread manager to reset the selected thread, the current thread, or perform a dry run. Only stop other threads if explicitly needed.

Find thread ids using the thread manager's status or thread-list command.

Use the utility's documented behavior to stop the selected thread, clean up orphaned `cursor-agent acp` processes, check CLI version/login/update status, and prompt for the next message. Avoid affecting other threads unless explicitly requested.

If sandboxing blocks process inspection, rerun the utility outside the sandbox.

## Verify

Send one short message to verify a fresh agent responds. If it hangs again, check the causes below before another reset.

## Known causes

- **Old Cursor CLI.** If the health check shows an update, update the thread manager and reset.
- **Expired login.** Symptom "Failed to initialize session services". Fix: `cursor-agent login`, then reset.
- **Pending permission.** Cursor waits for `session/request_permission`. Check and resolve the thread's pending approval before resetting.
- **Resume failure.** For `session/load` → "Session not found", use a fresh session after stopping the thread rather than retrying the load.
- **Team-level MCP servers** from the Cursor dashboard do not work in ACP mode. Only project or user `.cursor/mcp.json`.
- **Rate limits.** Enable retries using the thread manager's documented settings.

## Do not

- No launchd KeepAlive, cron, or watchdog for `cursor-agent acp`.
- Never blindly run `pkill -f cursor-agent`; it kills all Cursor threads and the interactive TUI. Use the documented reset utility, which should target orphans by default.
- Do not restart the thread manager for one stuck thread; stop only the affected thread.
- Do not compact the thread; Cursor does not support it.
