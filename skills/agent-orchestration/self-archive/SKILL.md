---
name: self-archive
description: Archive the current bb thread and release its runtime. Use when the user explicitly asks to "self-archive", "archive yourself", or "archive this thread".
---

# Self-archive

Only act on an explicit request to archive this thread. Never use `bb thread delete`.

1. Send a brief closing summary before running commands.
2. Archive this thread and its children. If this fails, report the error and do not stop the runtime.
   ```bash
   bb thread archive --self --json
   ```
3. After archiving succeeds, stop the runtime. Run nothing afterward.
   ```bash
   bb thread stop --self --json
   ```

Undo: `bb thread unarchive <id> --json`.
