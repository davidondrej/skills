---
name: adr-verbatim
description: 'Record concise ADRs that preserve the user''s decisions without conversational noise. Use for "adr-verbatim", "new ADR", "document that as an ADR", "record this decision", or supplied ADR wording.'
---

# ADR Verbatim

Preserve the user's meaning, not the conversation transcript. Record only the decision and context needed to understand it.

## Steps

1. Extract the decision the user stated or approved in the conversation. Ask only if the decision is unclear; do not require the user to dictate polished wording.
2. Use the project's established ADR location, including a previously specified repository. Do not assume the current checkout owns the ADRs. Read that directory and take the next number.
3. Write a short, clear ADR. Remove filler, emotional reactions, repetition, rhetorical questions, and instructions to the agent. Fix grammar and clarify references without changing the meaning, scope, conditions, or priorities.
4. Check every statement against the user's decision. Remove invented requirements and unapproved agent suggestions.
5. Show the saved path and full ADR in a code block.

## Format

Follow existing numbering and filenames, such as `docs/adr/0042-short-slug.md`.

```markdown
# 0042 — short title

Status: accepted (user, YYYY-MM-DD)

<The decision in plain English.>
```

## Rules

- Prefer a short paragraph or list. Add sections only when they improve clarity.
- Do not add speculative rationale, alternatives, consequences, or implementation details.
- Use exact wording only when the user explicitly asks for an exact quote or verbatim passage.
- A changed decision needs a new ADR. Correct an existing ADR when the user explicitly requests it, without changing unrelated history.
