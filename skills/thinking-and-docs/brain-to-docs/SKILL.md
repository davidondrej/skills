---
name: brain-to-docs
description: Use when the user wants to extract project vision, decisions, and preferences from their head into clear documentation (README + ADRs) through a back-and-forth Q&A loop. Triggers on "brain-to-docs", "build out the docs", "extract the vision", "let's document this project".
---

# brain-to-docs

The whole purpose: extract as much of the user's taste, judgment, knowledge, vision,
preferences, and decisions as possible into text — saved as clear, concise
markdown docs for the project. README holds the vision; `docs/adr/` holds the
decisions.

## The loop

1. **Check docs first, every time.** Read `docs/adr/` (and `README.md`) before
   doing anything — other agents and people add/edit ADRs constantly.
2. **Ask 5 different questions** in plain text (never a questions UI) — default 5
   unless the user asks for a different number. Make them high-variety: a wide,
   creative spectrum of unique angles, not all the same type (e.g. not all "tech
   stack" or all "product" or all "monetization"). Exception: if the user asks for a
   specific focus area, follow it. The user answers whichever they find most useful.
3. **Update docs after EVERY answer** — no exceptions. You decide whether it
   updates `README.md` or becomes a new ADR — whatever makes sense.
4. Repeat until the user says "we're done" (or similar).

## Rules

- All answers & responses during this "brain to docs" process must be VERY
  CONCISE, all sentences should be SHORT, and everything should be written in
  PLAIN ENGLISH.
- ADRs: short, numbered `NNNN-slug.md`, Status + Context + Decision + Consequences.
- README: vision only. Decisions go in ADRs.
- Don't challenge the user's thinking unless they ask, or they're making a severe mistake.
