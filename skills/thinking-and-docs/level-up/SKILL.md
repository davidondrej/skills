---
name: level-up
description: 'Gauge the user''s technical + product knowledge through 7 adaptive questions, log verbatim answers with honest ratings, and grow a learning plan from the gaps found. Use when the user says "level up", "level-up session", "quiz me", "gauge my knowledge", or wants a new assessment round. Differentiator: this finds and maps gaps; the `teach` skill delivers lessons on them.'
disable-model-invocation: true
---

# Level Up

Run a 7-question adaptive assessment to map what the user knows and doesn't, relevant to the current project. The output is two files future agents rely on.

## Files (repo-relative)

- `notes/learning/david-knowledge.md` — verbatim Q&A pairs + ratings, one section per question, rounds appended.
- `notes/learning/LEARNING-PLAN.md` — one concise bullet per genuine gap found.

State-check first: read both files in full if they exist. If previous rounds exist, pick mostly-new territory and calibrate starting difficulty to the recorded level. If missing, create the folder and both files (plan starts as just a header).

## Question rules

- 7 questions, strictly one at a time, plain text — never the questions UI.
- Start easy, adapt difficulty each answer: good answer → harder, weak answer → sideways or down.
- Orchestrator level only: systems, architecture, failure modes, security, data, scaling, product strategy, unit economics. NEVER syntax or code trivia — the user architects via AI agents, they don't write code.
- Anchor questions in the current project's real stack and features. When a question touches real code, read it and show the actual snippet when teaching.
- Cover different territory across rounds (e.g. round 1: request flow, DB, billing, moats; round 2: deploys, testing, incidents, data modeling, AI engineering, webhook security, cost engineering).

## After every single answer

1. Rate honestly 1-10. No flattery — the user wants calibration, not comfort.
2. Say concisely what was missed or wrong, and teach the correct concept in a few sentences.
3. Immediately save the verbatim answer + rating + gap notes to `david-knowledge.md`.
4. If a genuine gap surfaced, append one concise bullet to `LEARNING-PLAN.md`. Skip minor misses.
5. If the user pushes back on a rating ("I knew that, just didn't say it"), bump only if genuinely deserved, and record the bump with its reason.
6. When the user says he has since learned a plan item, mark its bullet: strikethrough + `✓ learned YYYY-MM-DD`.

## After question 7

Append a final summary to `david-knowledge.md`: per-question ratings, overall score, the recurring pattern across answers (e.g. "architecture instincts ahead of failure-mode instincts"), strengths to build on, and gaps added. Give the user the same summary in chat, concise.
