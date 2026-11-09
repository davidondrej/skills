---
name: new-grok-bot
description: Design a Grok Bot role and create its setup prompt. Use only when the user explicitly invokes /new-grok-bot.
disable-model-invocation: true
---

# New Grok Bot

Design a Grok Bot role and produce a prompt to paste into the app. Apply the **unit-of-work test** before drafting.

## Product context (last verified 2026-08-30)

Refresh through the deepapi skill (scrape x.ai/bot) only if something looks outdated or the user asks. Do not auto-refresh.

- Grok Bots are always-on AI teammates from SpaceXAI + Cursor. All Bots on an account share one persistent cloud computer with a browser, filesystem, terminal, and logins. They use real apps and websites, including those without APIs, and work while the user's laptop is closed.
- Bots retain preferences, voice, edge cases, and when to ask versus continue. Teach-a-task saves a demonstrated workflow as a routine to repeat independently or on a schedule.
- Bots can message each other, share context, and coordinate in group chats. A Chief of Staff can coordinate specialists.
- Bots choose plugins or browser interaction themselves; there is no model selection. Plugins include Gmail, Notion, Slack, Google Drive, and custom integrations. Purchases can use a connected payment link.
- Separate Bots are **not security boundaries**: they share files, sessions, and logins.
- Distinguish Grok Automations (scheduled/triggered prompts), Grok Build (terminal coding agent), and @grok on X (reply bot).

## Unit-of-work test

A good Bot role owns a repeatable outcome. Check all eight criteria:

1. **Owns an outcome.** One narrow lane per Bot: "handle churn win-backs," not "email this customer."
2. **Delivers in the real tool.** CRM updated, inbox draft created, or ticket filed. Chat-only output belongs in regular Grok.
3. **Recurs.** Runs daily, weekly, or on frequent triggers so memory and setup pay off.
4. **Demonstrable once.** The user can teach the workflow by showing it once.
5. **Async-tolerant.** Can finish overnight without the user's involvement mid-run, except at agreed approval gates.
6. **Clear approvals.** Sending, publishing, paying, deleting, and other consequential actions wait for the user. Other work proceeds independently.
7. **Limited damage.** Mistakes are reviewable and reversible before reaching the world.
8. **Worth delegating.** Saves meaningful weekly effort or makes money; would the user hire a part-time human for it?

**Redirect unsuitable ideas:**
- One-off question or task → regular Grok chat.
- One stable prompt on a schedule → Grok Automations.
- Repository coding → Cursor / Grok Build.
- Needs the user's judgment at every step → narrow the scope.
- Needs hard isolation between duties → unsuitable on the shared computer.

**Split rule:** If the idea spans separate roles, explain why and create one prompt per Bot. Offer a Chief of Staff only when Bots must hand work to each other.

## Workflow

1. Silently assess the user's idea against the test. Explain any failed criterion and suggest a suitable scope or redirect. Apply the split rule when needed.
2. Ask one concise question at a time, with options A–D and a preferred choice plus a one-line reason. Cover only unclear points, in this order:
   - **What:** outcome, lane, and boundaries.
   - **Why:** value and what the user stops doing.
   - **How:** tools/logins, steps, schedule, approvals, and reporting.
   - **Prototype:** one first task the Bot can do today to prove useful.
3. Stop as soon as you can draft; ask no more than five questions.

## Deliverable

Write one single-paragraph prompt in a code block, ready as the Bot's first message in the app. Outside it, include only one line naming the tools the user must sign the Bot into. For multiple Bots, give each a separate, self-contained code block.

Each prompt must naturally cover:

- Name, role, owned outcome, and relevant context about the user and their business.
- Tools and their purposes, step-by-step workflow, and routine or schedule.
- Memory instructions for preferences, voice, and edge cases.
- Actions requiring approval, plus how and when to report back.
- The first prototype task as the immediate job to start on.

## Validate before finishing

Check all eight criteria, confirm the first task is doable today with the listed tools, and ensure approvals cover irreversible or outward-facing actions. Fix any gaps before delivering.
