---
name: setup-help
description: Guide setup one step at a time and show what remains. Use only when the user explicitly invokes /setup-help.
disable-model-invocation: true
---

# setup-help

Guide the user through any setup, one step at a time, in plain English.

## Response format (every single response)

1. **Current step** — ONE coherent setup step. Group tightly related actions and fields from the same form or screen, and provide every value the user needs to complete them. Use 1–4 concise lines. Split only at a real decision, verification point, or screen change.
2. A `----` divider.
3. **Still remaining** — a numbered list of the setup steps left after this one. Max 8 items, ever. Each item is a HEADLINE only: a few words, easy to glance at. No commands, URLs, event names, values, or explanations — that detail appears only when the item becomes the Current step.

Repeat this format for every response until setup is done.

## Rules

- Before the first step, build a complete canonical checklist from the user's outline, repo/docs, current screen, and any discovered prerequisites.
- The **Still remaining** list must never exceed 8 items — more is overwhelming. Track ALL unfinished checklist items internally; if more than 8 remain, show the nearest steps individually and merge the later ones into broader phase-level items so the list stays at 8 or fewer. Never silently drop a required step from internal tracking.
- If a new required step is discovered mid-setup, add it to **Still remaining** immediately in the correct order.
- Before every response, audit the current step plus **Still remaining** against the canonical checklist. If any unfinished step is missing, fix the list before replying.
- Only give instructions for the current step. Do not jump ahead. Never split one obvious form or tightly related field group into micro-steps; optimize for fewer handoffs. Keep the remaining list headline-only.
- Keep it concise. Short sentences. No filler.
- After the user finishes a step, move the next "remaining" item up to "Current step".
- Update the "Still remaining" list each time as steps get done.
- When nothing remains, say setup is complete instead of showing the list.
