---
name: prompt-for-others
description: 'Turn a fix, upgrade, or setup step into ONE paste-ready paragraph that every teammate (including the user) sends to their own AI coding agent on their own machine. Use when the user says "prompt for others", "prompt for the team", "one-paragraph prompt everyone should run", "what should the team tell their agent", or wants a fix rolled out to many Macs. Differentiator: writes for an agent with root access on a stranger''s machine, so it is self-contained, verifiable, and refuses to guess.'
---

# Prompt For Others

The reader is an AI agent on a teammate's machine. It has no context from this chat. The teammate may be non-technical and will not edit the prompt. One paragraph, no headers, no bullets, ready to copy.

## Workflow

1. Confirm the fix is real. Run it on the user's machine first if you have not already. Never broadcast an untested command.
2. Draft the paragraph in this exact order:
   - **Goal** in one sentence ("Upgrade X on this Mac to version Y and restart it.")
   - **Context** in one or two sentences: what X is, what the bug is, why the fix does not happen by itself.
   - **Steps** as exact commands, in backticks, in order.
   - **Verify** with exact commands and the exact expected output ("must show 0.1.1").
   - **Stop rule**: what to do if a precondition is missing ("If `brew` is missing, stop and tell me instead of installing anything.").
   - **Report back**: the one or two facts the teammate should get back.
3. Re-read as a stranger's agent: could it run this with zero questions? If anything needs the user's context, inline it.
4. Send the user the paragraph inside a blockquote, then stop. No commentary inside the paragraph.

## Rules

- One paragraph. If it needs two, the fix is too big; split it or say so.
- Commands must be copy-safe: absolute where it matters, no placeholders like `<your-name>` unless the agent can resolve them (`$(id -u)` is fine).
- Prefer reversible steps. If a step is destructive, say so and require the agent to confirm with the human first.
- Never include secrets, tokens, or private URLs. Point to where the agent can find them locally instead.
- Include the "why" in plain English. Agents obey better and humans trust it more.
- Assume nothing is installed. Use a stop rule instead of an install fallback unless the user asked for one.

## Example

> Upgrade the repo-sync background service on this Mac to v0.1.1 and restart it. Context: repo-sync (installed via Homebrew cask `vectal-labs/tap/repo-sync`) is a daemon that auto-syncs our Git repos. v0.1.0 sends a scary macOS popup per repo on any short network blip; v0.1.1 fixes this. Casks do not auto-update, and the old process keeps running until restarted. Steps: run `brew update && brew upgrade --cask repo-sync`, then `launchctl kickstart -k gui/$(id -u)/com.vectal-labs.repo-sync`. Verify with `brew list --cask --versions repo-sync` (must show 0.1.1) and `tail -3 ~/Library/Logs/repo-sync/stdout.log` (must show a fresh `watching N repositories` line). If `brew` or the cask is missing, stop and tell me instead of installing anything. Report back the version and the log line.
