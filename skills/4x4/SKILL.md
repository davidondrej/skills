---
name: 4x4
description: 'Pull 16 fast decisions out of the user with 4 sets of 4 open questions, then present an implementation plan. Only for risky changes, large product decisions, or large refactors. Run when the user types /4x4. Agents may suggest it in one line but never start it on their own.'
---

# 4x4

Get the user's judgment, taste, and decisions in 4 quick rounds. 16 open questions. A full run should take them 2–3 minutes.

## The 4 sets

These are defaults. Adapt their names and focus to pull the most judgment and taste out of the user for this topic.

1. **Product** — what it does, who it's for, UI/UX, scope.
2. **Software design** — architecture, data, boundaries, what to reuse or delete.
3. **Practical** — execution order, rollout, what ships first.
4. **Edge cases** — the 4 most likely ways this breaks or surprises users. Each question asks how to handle one.

## Workflow

1. **Load context fast.** Use what's already in the thread. Skim only the files and docs that matter (scopes, ADRs, the diff). No research, no subagents.
2. **Pick the order.** Start with the set whose answers most change the others.
3. **Pick 4 questions per set.** Choose the 4 decisions with the biggest impact that only the user can make. Never ask what the code, docs, or common sense already answer. Skip anything already decided.
4. **Show one set at a time.** Never preview or list the other sets. Stop and wait. Show the next set only after the user answers.
5. **Adapt.** Rewrite later sets based on earlier answers.
6. **Present the plan.** After set 4, give plain step-by-step instructions to execute the work properly, built from the user's answers. Chat only. Then stop. Don't build or write docs until the user says go.

## Message format

```
## Set 2/4 · Software design

1. Where should X live?

2. ...

3. ...

4. ...
```

Nothing else. No intro, no outro.

## Rules

- Open questions only. Never give options, picks, recommendations, or hints. The point is the user's own thinking.
- One short sentence per question. Concrete, plain English, clear on first read.
- No meta questions, like how to measure success or what to test first. Ask about the work itself.
- Vague or skipped answer: move on and use your judgment.
- If the user calls a question bad, replace it or drop it. Your call.
- If an answer contradicts an ADR or scope, point it out in the plan.
- If an answer opens a big new question, note it in the plan. Don't add a 5th question.
