---
name: adr-verbatim
description: 'Record concise ADRs that preserve the user''s decisions without conversational noise. Use for "adr-verbatim", "new ADR", "document that as an ADR", "record this decision", or supplied ADR wording.'
---

# ADR Verbatim

Preserve the user's meaning, not the conversation transcript. Record only the decision and context needed to understand it.

## Steps

1. Extract the decision the user stated or approved in the conversation. Ask only if the decision is unclear; do not require them to dictate polished wording.
2. Use the project's established ADR location, including a previously specified repository. Do not assume the current checkout owns the ADRs. Name the file by that directory's rule (check its README or AGENTS.md); if it has none, take the next number.
3. Write a short, clear ADR. Remove filler, emotional reactions, repetition, rhetorical questions, and instructions to the agent. Fix grammar and clarify references without changing the meaning, scope, conditions, or priorities.
4. Check every statement against the user's decision. Remove invented requirements and unapproved agent suggestions.
5. Show the saved path and full ADR in a code block.

## Format

Match the directory's filenames, such as `docs/adr/0042-short-slug.md` or `docs/adr/20261030-175900-short-slug.md`. Use the file's ID in the heading.

```markdown
# <ID> — short title

Status: accepted (<user>, YYYY-MM-DD)

<The decision in plain English.>
```

## Rules

- Prefer a short paragraph or list. Add sections only when they improve clarity.
- Do not add speculative rationale, alternatives, consequences, or implementation details.
- Use exact wording only when the user explicitly asks for an exact quote or verbatim passage.
- Newer decisions win. The user's latest decision overrides older ADRs, because they have more information and context now. Don't treat an older ADR as a blocker; record the new decision and name the ADR it supersedes.
- A changed decision needs a new ADR. Correct an existing ADR when the user explicitly requests it, without changing unrelated history.
