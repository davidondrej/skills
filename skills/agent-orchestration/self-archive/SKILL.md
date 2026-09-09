---
name: self-archive
description: Archive the bb thread the agent is currently running in, then release its runtime. Use when the user says "self-archive", "archive yourself", "archive this thread", "close this thread out", or tells a bb agent to archive its own session. Differentiator: archives the CURRENT thread via `--self`; to archive other threads use bb-cli or nagent.
---

# Self-archive

Archive the bb thread you are running in. Works in any bb agent shell because bb sets `BB_THREAD_ID` and the CLI reads it via `--self`.

## When

Only when the user explicitly asks. Never archive yourself after finishing a task on your own.

## Workflow

1. **Say goodbye first.** Write the final summary now. Nothing prints after step 3.
2. **Archive** this thread. This also archives child threads.
   ```bash
   bb thread archive --self --json
   ```
3. **Stop** this thread. Frees the agent runtime, keeps history. Must be the last command.
   ```bash
   bb thread stop --self --json
   ```

## Do not

- Do not use `bb thread delete`. That is permanent.
- Do not use `bb thread update --visibility hidden` as a substitute. Hidden is sidebar-only; archive is the lifecycle close-out.
- Do not run any command after `stop`.

## Undo

The user can restore the thread with:

```bash
bb thread unarchive <id> --json
bb thread list --archived
```
