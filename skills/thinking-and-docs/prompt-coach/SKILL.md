---
name: prompt-coach
description: >-
  Convert raw voice notes, transcripts, and unstructured thoughts into
  micro-scoped, execution-ready prompts tailored for Herdr agent panes and CLI
  runtimes (Claude Code, Codex, Grok). Use when the user types /po, /coach, or
  provides messy dictation, Loom/call transcripts, or rough task ideas.
  Differentiator vs prompt-me: non-interactive one-shot delivery; vs bb-specify:
  instant prompt polish and agent routing rather than heavy multi-phase spec
  authoring.
---

# Prompt Coach (`/po`, `/coach`)

Turn raw voice notes, meeting transcripts, and rough thoughts into one
execution-ready prompt formatted for direct dispatch to a Herdr pane or agent CLI.
Zero back-and-forth — one shot.

---

## Output Template

Generate immediately as native Markdown:

### 1. Agent & Harness Dispatch
- **Target:** `[Claude Code | Codex | Grok | Cursor]` — [one-line rationale: e.g., deep refactor vs rapid script vs proactive exploratory]
- **Pane / Harness:** `Herdr` pane or `bb agent-sessions`
- **Pipeline:** `[Small (direct) | Standard (before-building → implement → decisions) | Risky (risky-changes) | Spec-Heavy (/bb-specify)]`

### 2. Micro-Scoped Prompt (Copy-Paste)
```text
Goal: [Single verifiable objective — 1 sentence]

Context & Scope:
- [Strict boundary: what to touch, what to leave untouched]
- [Key files or modules]

Acceptance Criteria:
- [ ] [Objective verification step 1 — e.g. linter/tests clean, CLI command passes]
- [ ] [Objective verification step 2 — e.g. verified via /trust-but-verify or edge cases tested]

Session Rule: If blocked > 2 turns, pause and request human input (or call Herdr socket to split pane).
```

### 3. Missing Inputs & Edge Flags
- *(Optional, 1–2 bullets max)*: Flag only blocker ambiguities (e.g. auth secrets, destructive DB ops). If none, omit.

---

## Agent Routing Heuristics

| Task Profile | Recommended Agent | Harness / Next Step |
|---|---|---|
| Deep logic, multi-file architectural code | **Claude Code** (high effort) | Herdr pane → `/before-building` |
| Scripts, data pipelines, test runs, repetitive tasks | **OpenAI Codex** | Herdr pane → run & verify |
| Proactive exploration, quick POC, unblocking tasks | **Grok Bot** | Herdr pane (runs fast, minimal pings) |
| Hands-on UI micro-tweaks | **Cursor Agent** | In-editor session |
| High ambiguity / massive multi-component feature | Any | Route to `/bb-specify` first |

---

## Session Hygiene & Context Health

David's Rule: Never argue with a drifting agent in a long context. If an agent fails
twice, kill the pane or run `bb agent-sessions resume`.

Append the Traffic Light footer to every output:

- 🟢 **< 30 steps:** `> 🟢 Context: Optimal (~Step X) · Focus 100%`
- 🟡 **30–60 steps:** `> 🟡 Context: Moderate (~Step Y) · suggest /remind or /short`
- 🔴 **> 60 steps or drift:** `> 🔴 Context: Saturated · kill pane or /handoff for clean session`
