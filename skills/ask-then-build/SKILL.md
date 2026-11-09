---
name: ask-then-build
description: 'Clarify a feature, change, or refactor through questions, then write a build prompt for another agent. Use for /ask-then-build or requests to ask questions before producing an implementation prompt.'
---

Turn a feature idea into a build prompt for another agent, in two phases.

## Phase 1 — Questions

1. Identify the 3-6 most non-obvious open questions about the feature or
   change: edge cases, where it lives in the UI, failure behavior, scope
   boundaries, how it interacts with existing rules.
2. Ask them ONE at a time. For each: the question, top options A-D, your
   preferred pick with a one-line reason. Then stop and wait.
   Use this exact layout. Put a blank line between EVERY block. Markdown
   renderers (bb included) collapse single newlines into one paragraph, so
   options written back-to-back render as one run-on blob.

   **Question title?**

   One line of context, if needed.

   A. First option.

   B. Second option.

   C. Third option.

   D. Fourth option.

   My pick: A. One-line reason.

   Never number questions as "1 of N" unless you truly know N. If the count
   is open, keep it open and keep asking until you have the context you need.
3. When the user answers, record the decision immediately — update the repo's
   docs (product requirements, ADR, or README) if the project has them.
4. If the user overrides an earlier documented decision, update the docs right
   away and say what was superseded.

## Phase 2 — Prompt

After the last answer, deliver ONE concise paragraph prompt for another
agent. It must include, in this order:

1. Read-first files: the authoritative docs (AGENTS.md, requirements, ADRs).
2. What to build: numbered implementation steps, concrete file-level where
   useful.
3. How to validate: build, lint, and a manual check with real data.
4. Rules: don't commit, report back with files changed.

## Style

- Very concise, plain English, short sentences.
- Never bundle questions. Never write the prompt before all answers are in.
- Never put two options on one line. Always a blank line between A, B, C, D
  and before "My pick".
- Keep the prompt to a single paragraph — if it needs two, the scope is too
  big; say so.
