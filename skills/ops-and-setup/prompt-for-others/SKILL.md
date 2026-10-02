---
name: prompt-for-others
description: 'Write a prompt teammates can give their AI agents to apply a fix, upgrade, or setup change. Use only when the user explicitly invokes /prompt-for-others.'
disable-model-invocation: true
---

# Prompt For Others

Write for an AI agent on a teammate's machine with no chat context. The teammate may be non-technical and will not edit the prompt.

## Workflow

1. Test the fix on the user's machine unless already tested. Never include untested commands.
2. Draft the paragraph in this exact order:
   - **Goal** in one sentence.
   - **Context** in 1–2 sentences: what the tool does, the problem, and why the fix is needed.
   - **Steps** as exact commands, in backticks, in order.
   - **Verify** with exact commands and expected output.
   - **Stop rule**: what to do if a precondition is missing.
   - **Report back**: the 1–2 facts the teammate should receive.
3. Read as an agent with no context: could it run this without questions? Inline any missing context.
4. Give the user one ready-to-copy paragraph in a blockquote, without headings, bullets, or commentary; then stop.

## Rules

- One paragraph. If it needs two, the fix is too big; split it or say so.
- Commands must be copy-safe: absolute where it matters, no placeholders like `<your-name>` unless the agent can resolve them (`$(id -u)` is fine).
- Prefer reversible steps. If a step is destructive, say so and require the agent to confirm with the human first.
- Never include secrets, tokens, or private URLs. Point to where the agent can find them locally instead.
- Explain why the change is needed in plain English.
- Assume nothing is installed. Use a stop rule instead of an install fallback unless the user asked for one.

## Example

> Upgrade the repo-sync background service on this Mac to v0.1.1 and restart it. Context: repo-sync (Homebrew cask `vectal-labs/tap/repo-sync`) auto-syncs Git repos. v0.1.1 fixes misleading popups during network blips. The cask needs an explicit upgrade, followed by a service restart. Steps: run `brew update && brew upgrade --cask repo-sync`, then `launchctl kickstart -k gui/$(id -u)/com.vectal-labs.repo-sync`. Verify with `brew list --cask --versions repo-sync` (must show 0.1.1) and `tail -3 ~/Library/Logs/repo-sync/stdout.log` (must show a fresh `watching N repositories` line). If `brew` or the cask is missing, stop and tell the user instead of installing anything. Report back the version and the log line.
