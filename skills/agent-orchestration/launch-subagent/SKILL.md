---
name: launch-subagent
description: 'Read this BEFORE launching any subagent (Task tool, background agents, parallel agents, best-of-N, delegating work to another agent). Hard model rules for subagents plus consensus principles for using them well. Triggers: launch a subagent, spawn agents, run agents in parallel, delegate to a subagent.'
---

# SUBAGENTS
- for all Subagents use either "Fable 5 Max" or "GPT 5.6 Sol Max Fast" as the model
- DO NOT launch subagents, unless the User tells you to
- NEVER EVER use Composer 2.5 or Sonnet 5, for subagents
- only ever use GPT 5.6 Sol Max Fast, or Fable 5 Max, when launching Subagents

## General Subagent Principles

Consensus of Boris Cherny, Matt Pocock, Pietro Schirano, and Peter Steinberger:

- Delegate only self-contained tasks. Split work so subtasks have zero dependencies on each other; parallelize only independent work.
- Parallel subagents must never touch the same files — that is a recipe for conflicts. Partition the work or keep it in one agent.
- Subagents start blind: they see none of your context. Write the full brief into the prompt — scope, all needed context, constraints, and the exact output to return.
- Scope narrowly and concretely: "explore how payments work" beats "explore everything". One bounded task per subagent, small blast radius.
- The main agent stays the orchestrator. It plans the split, integrates results, and reviews/verifies every subagent output before trusting it.
- Keep critical implementation, tightly-coupled edits, and quick fixes in the main loop — delegation overhead is only worth it for independent, research-heavy, or review work.
- Have subagents return short summaries or concrete results, never raw transcripts or file dumps. That keeps the main context clean.

# SUBAGENTS
- for all Subagents use either "Fable 5 Max" or "GPT 5.6 Sol Max Fast" as the model
- DO NOT launch subagents, unless the User tells you to
- NEVER EVER use Composer 2.5 or Sonnet 5, for subagents
- only ever use GPT 5.6 Sol Max Fast, or Fable 5 Max, when launching Subagents
