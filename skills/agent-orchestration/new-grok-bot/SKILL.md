---
name: new-grok-bot
description: 'Design a new Grok Bot (SpaceXAI + Cursor AI teammate) with the user through a short clarification loop, then output one paste-ready prompt for the Grok Bot app. Use when the user says "new grok bot", "create a grok bot", "design a bot", or wants to hand a job to a Grok Bot. Differentiator: judges whether the idea is a GREAT UNIT OF WORK for a bot before writing anything.'
---

# New Grok Bot

Help the user design a new Grok Bot and hand them one paste-ready prompt.
The core value of this skill is the **unit-of-work test** — apply it before writing any prompt.

## What Grok Bot is (last verified 2026-08-30)

Product facts only; refresh via the deepapi skill (scrape x.ai/bot) ONLY if something looks outdated or the user asks. Do not auto-refresh.

- Grok Bot = always-on AI teammates from SpaceXAI + Cursor (launched Aug 11, 2026, beta). App looks like iMessage: you message named Bots like coworkers. Desktop (macOS/Windows) + iOS, full parity.
- All of an account's Bots share ONE persistent cloud computer: real browser, filesystem, terminal. Bots sign into the user's actual apps and websites (even ones with no API) and keep working after the laptop closes, 24/7.
- Bots come back only for approvals. They keep memory: voice, preferences, edge cases, when to ping vs. keep going.
- Teach-a-task: perform a workflow once while the Bot watches; it saves it as a routine and reruns it on its own or on a schedule.
- Multi-bot: Bots message each other, share context, coordinate in group chats. Common pattern: a Chief of Staff bot managing specialists.
- Plugins: Gmail, Notion, Slack, Google Drive, AWS, Browserbase, Composio, Context7, custom. Bot picks plugin vs. raw browser itself. No model selection.
- Availability: included from SuperGrok and Cursor Pro plans up (~$20/mo); own usage pool, separate from Grok/Cursor limits. Bots can also make purchases online via a connected payment link.
- Security: separate Bots are NOT security boundaries — they share the account computer, files, sessions, and logins.
- Sibling products, don't confuse: Grok Automations = scheduled/triggered prompt reruns; Grok Build = terminal coding agent; @grok on X = the reply bot.

## WHAT IS A GREAT UNIT OF WORK (the core test)

A Grok Bot is a hire, not a prompt. A great unit of work is a ROLE that owns a repeatable OUTCOME. Check every idea against these:

1. **Owns an outcome, not a task.** "Handle churn win-backs" beats "email this customer." One narrow lane per bot (inbox, outbound, expenses, reporting).
2. **Done means landed in the real tool.** CRM updated, draft in the inbox, ticket filed. If the output is just text back in chat, regular Grok is enough.
3. **Recurs.** Daily/weekly or triggered often. Recurrence is what compounds the Bot's memory and pays back setup.
4. **Demonstrable once.** The user can show the workflow one time (teach-a-task) instead of writing a spec.
5. **Async-tolerant.** Fine if it finishes overnight; doesn't need the user mid-run.
6. **Clear approval gates.** Consequential actions (send, publish, pay, delete) wait for the user. Everything else runs free.
7. **Low blast radius.** Mistakes are reviewable and reversible before they reach the world.
8. **Worth it.** Saves real hours weekly or makes money; passes the "would I hire a part-time human for this?" sniff test.

**Anti-patterns — redirect instead of building a Bot:**
- One-off question or task → regular Grok chat.
- A single stable prompt on a schedule (morning brief, weekly summary) → Grok Automations.
- Repo-centric coding → Cursor / Grok Build.
- Needs the user's judgment at every step → not delegable yet; shrink the scope.
- Needs hard isolation between duties (e.g. handling secrets one bot must not leak to another) → shared computer makes this unsafe.

**Split rule:** if the idea fails test #1 because it is really 2-3 jobs, say so plainly and produce one prompt per Bot. Offer a Chief of Staff bot only when the bots must hand work to each other.

## Workflow

1. Take the user's rough idea. Silently score it against the unit-of-work test. If it fails, say which test and propose the nearest shape that passes (or redirect per anti-patterns). If it's multiple jobs, invoke the split rule.
2. Run a clarification loop, ONE question at a time, very concise, options A-D plus your preferred pick with a one-line reason. Cover, in order, only what's still unclear:
   - **WHAT** — the outcome the Bot owns; its lane and boundaries.
   - **WHY** — the value; what the user stops doing.
   - **HOW** — tools/logins needed, workflow steps, routine schedule, approval gates, how it reports back.
   - **PROTOTYPE** — the quick-and-dirty version: the ONE first task the Bot can do TODAY to prove useful, before any perfecting.
3. Stop asking as soon as you can write the prompt. 3-5 questions max.

## Deliverable

ONE long single-paragraph prompt inside a single code block, ready to paste as the first message to the new Bot in the Grok Bot app. Nothing outside the code block except one line saying which tools the user must sign the Bot into. The paragraph must contain, flowing naturally: the Bot's name and role, the outcome it owns, context about the user/their business it needs, the tools it will use and what for, the step-by-step workflow, the routine/schedule, memory instructions (preferences, voice, edge cases to learn), hard approval boundaries (what it must never do without asking), how and when to report back, and its FIRST task — the quick-and-dirty prototype — stated as the immediate job to start on. If the split rule fired, output one such code block per Bot, each self-contained.

## Validate before finishing

Re-read the drafted prompt and check: passes all 8 unit-of-work tests, first task is doable today with the listed tools, approval gates cover anything irreversible or outward-facing. Fix and only then deliver.
