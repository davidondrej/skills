---
name: ask-then-build
description: 'Scope a feature, change, or refactor by asking the user 3-6 pointed questions ONE at a time (options A-D, state a preference, wait), record every answer, then deliver ONE concise paragraph prompt that another agent can implement from. Use when the user says "ask-then-build", "ask me questions then give me a prompt", or wants a spec turned into a build prompt for another agent. Differentiator: question-then-prompt loop; next-decision only drills decisions, brain-to-docs extracts vision into docs.'
---

Turn a feature idea into a build prompt for another agent, in two phases.

## Phase 1 — Questions

1. Identify the 3-6 most non-obvious open questions about the feature or
   change: edge cases, where it lives in the UI, failure behavior, scope
   boundaries, how it interacts with existing rules.
2. Ask them ONE at a time. For each: the question, top options A-D, your
   preferred pick with a one-line reason. Then stop and wait.
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
- Keep the prompt to a single paragraph — if it needs two, the scope is too
  big; say so.
