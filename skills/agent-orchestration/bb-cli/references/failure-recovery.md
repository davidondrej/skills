# Failure and interruption recovery

## Failures And Interruptions

- For failed threads, inspect `bb thread show <id> --json` and
  `bb thread log <id>` before deciding whether to retry, clarify, or update the
  user.
- Use `bb thread retry <thread-id>` to re-send a failed turn's original message
  verbatim. It re-submits the same input — it does not add a new user message to
  the timeline — and increments the attempt number (2 is the first retry). With
  no `--turn` it retries the most recent turn, the one whose failure put the
  thread in `error`; `--turn <requestId>` asserts which turn you mean and fails
  when the thread has moved on. It errors when the thread has not failed or
  `--turn` names a different turn (409 `no_failed_turn`), and when that turn
  already has a retry queued (`retry_already_queued`). Add `--send-at <when>` to
  queue the retry on the clock (same `<when>` grammar as `bb thread tell
  --send-at`); without it the retry is attempted now and may still queue behind
  a busy thread or a plugin's dispatch hook. `--reason <text>` labels the queued
  row. The SDK equivalent is `sdk.threads.retry({ threadId, turnRequestId?,
  sendAt?, reason? })`.
- The Provider retry plugin is enabled on fresh installations. When a turn fails
  on a structured Codex or Claude Code subscription-window limit that reports a
  reset, it queues that turn to be re-sent after the window opens, re-sending
  the original message verbatim and marked agent-only. A pending retry is an
  ordinary queued row on the thread, so it survives a restart and appears in
  `bb thread queue list <thread-id>`.
- For interrupted or stopped threads, inspect first. If the user stopped the
  thread, treat that as intentional unless they ask you to continue.
- Use `bb thread stop <id>` when a thread is stuck or no longer needed.
- `bb thread stop <id>` also releases an idle or stuck agent runtime. The
  command is idempotent and preserves thread history.
- Use `bb thread compact <id>` to send the built-in `/compact` command to an idle or errored thread. Completion or failure appears in the timeline. Codex, Claude Code, Pi, and OpenCode ACP support it; Cursor ACP does not expose compatible compaction through ACP.
- Use `bb thread cancel-plan <id>` to exit an active Plan turn without
  optimistically clearing its banner. Use `bb thread clear-goal <id>` to clear
  a Codex thread's durable active Goal. Both wait for provider confirmation.
