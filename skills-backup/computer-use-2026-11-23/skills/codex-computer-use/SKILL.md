---
name: codex-computer-use
description: 'Use only when the user explicitly invokes this skill for human-style UI QA or click-heavy setup, such as testing components and user flows or configuring Google Cloud Console. Delegate the manual clicking and back-and-forth to Codex Computer Use.'
disable-model-invocation: true
triggers: [user, model]
---

**What it is.** Computer Use in the ChatGPT desktop app's Codex view lets the agent operate real apps and browsers: read interfaces, click, type, and verify results. On macOS, it combines accessibility data with visual inspection and uses its own background cursor while the user works elsewhere. This closes the gap between writing code or explaining steps and actually using the interface to finish the job.

**When and how.** Use only when the user explicitly invokes this skill. Focus on **UI QA**—test components and user flows like a human, reproduce bugs, fix them, and retest—and **click-heavy setup**, especially Google Cloud Console forms and settings that otherwise require tedious manual back-and-forth. With the native Computer Use plugin enabled and user-approved permissions, name the target, desired outcome, constraints, and proof of completion, such as screenshots or verified settings. Ask before new permissions, charges, destructive changes, or sensitive account actions.

## Working rules

- **Concurrency:** Run only one active Computer Use task per target app to avoid conflicting actions.
- **Browser:** Use the built-in browser for localhost testing. Use Brave for the user's existing signed-in browser context.
- **UI checks:** Confirm the correct app and window before acting, then inspect the result after meaningful actions. Pause if the UI state becomes unexpected.
- **Execution:** Use available Computer Use tools directly. If the current agent lacks them, give the user a ready-to-paste Codex prompt.
