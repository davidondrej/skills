---
name: rename
description: Manually-invoked skill that renames the current thread or session to 2-5 lowercase descriptive words. Use when the user says "rename", "rename this", "rename thread", or "rename session".
disable-model-invocation: true
triggers: [user, model]
---

Rename this thread now. Pick a name for the main thing happening here: 2-5 clear lowercase words. Don't overthink it.

## Do it in one command

```bash
room-cli thread update --self --title "your new name"
```

- Run exactly this. No `--help`, no searching, no `--json`, no pipes.
- If `room-cli` is missing (not in Cloudroom), say so in one line. Don't hunt for another way.
- Reply with one line: the new name.
