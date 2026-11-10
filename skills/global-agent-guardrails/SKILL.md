---
name: global-agent-guardrails
description: "Configure the shared guard against catastrophic shell commands in local AI agents. Use when changing block patterns, adding an agent or machine, or investigating why a command was or wasn't blocked."
---

# Global Agent Guardrails

Block catastrophic shell commands before a coding agent runs them. One patterns file feeds a shared hook script, or a small native adapter, for each agent. This guards against accidents, not malicious agents: obfuscation like `python -c "shutil.rmtree(...)"` slips past any regex.

This is a generic recipe built on each tool's public hook system. [Cloudroom](https://www.cloudroom.dev/security) ships a built-in Command Guard based on this design, on by default.

## File map

```
~/.agents/hooks/dangerous-patterns.txt   # THE denylist: one POSIX-ERE regex per line, # comments
~/.agents/hooks/deny-dangerous.sh        # shared guard: hook JSON on stdin -> exit 2 blocks
~/.agents/hooks/test-guard.sh            # test suite: run after ANY pattern change
~/.config/opencode/plugins/command-guard.ts   # OpenCode adapter (throws to block)
~/.pi/agent/extensions/command-guard.ts       # Pi adapter (returns {block:true})
~/.hermes/plugins/command-guard/              # Hermes plugin (returns {"action":"block"})
```

## Check installation

```bash
ls ~/.agents/hooks/deny-dangerous.sh ~/.agents/hooks/dangerous-patterns.txt
~/.agents/hooks/test-guard.sh   # must end "failed: 0"
```

If missing, rebuild from the script below and the wiring table.

## Guard script

`deny-dangerous.sh` reads the hook JSON on stdin, pulls out the command, and tests it against every pattern. Its core:

```bash
#!/bin/bash
PATTERNS="$HOME/.agents/hooks/dangerous-patterns.txt"
command -v jq >/dev/null || exit 0
CMD=$(jq -r '.tool_input.command // .toolInput.command // .command // empty' 2>/dev/null)
[ -n "$CMD" ] && [ -f "$PATTERNS" ] || exit 0
while IFS= read -r pattern; do
  case "$pattern" in ''|\#*) continue ;; esac
  if printf '%s\n' "$CMD" | grep -qE -- "$pattern"; then
    echo "Blocked by the command guard. Matched: $pattern. Do not retry or work around it; tell the user." >&2
    exit 2
  fi
done < "$PATTERNS"
```

Cursor wants JSON instead of exit 2: with the `cursor` arg, print `{"permission":"deny","agent_message":"..."}` or `{"permission":"allow"}` and exit 0.

## Add or tune a pattern

1. Edit `~/.agents/hooks/dangerous-patterns.txt`. Write POSIX ERE (`grep -E`). Use `[[:space:]]`, never `\s` — adapters auto-convert `[:space:]` to `\s` for JS/Python and compile in multiline mode.
2. Add block and allow cases to `test-guard.sh`, then run it; all must pass.
3. Verify the new pattern compiles in the adapter engines:

```bash
python3 -c 'import re,pathlib; [re.compile(l.strip().replace("[:space:]",r"\s"),re.M) for l in pathlib.Path.home().joinpath(".agents/hooks/dangerous-patterns.txt").read_text().splitlines() if l.strip() and not l.startswith("#")]; print("ok")'
```

4. Consumers re-read patterns for every command. Exception: Droid uses `commandBlocklist` in `~/.factory/settings.json` — mirror changes there manually.

Block only catastrophic commands: irreversible data loss, disk wipes, repo deletion, rewritten remote history. Recoverable local commands (`git status`, `git clean -fdx`, `rm -rf node_modules`) stay allowed. Over-blocking trains people to turn the guard off.

Each group in the patterns file has a comment saying what it blocks and what deliberately stays allowed. Read those comments before changing a pattern, and keep them current.

## Per-agent wiring (user-global)

| Agent | Config | Event | Blocks via |
|---|---|---|---|
| Claude Code | `~/.claude/settings.json` | `PreToolUse` matcher `Bash` | shared script, exit 2 |
| Codex CLI/app/IDE | `~/.codex/hooks.json` | `PreToolUse` matcher `Bash` | shared script, exit 2 |
| Cursor IDE + CLI | `~/.cursor/hooks.json` | `beforeShellExecution` | shared script with `cursor` arg, deny JSON |
| Grok (xAI) | auto-loads Claude + Cursor hook files (compat on by default); native option `~/.grok/hooks/*.json` | `PreToolUse` | shared script (reads `.toolInput.command`) |
| OpenCode | `~/.config/opencode/plugins/command-guard.ts` | `tool.execute.before` | adapter throws Error |
| Pi | `~/.pi/agent/extensions/command-guard.ts` | `pi.on("tool_call")` | adapter returns `{block:true}` |
| Hermes | `~/.hermes/plugins/command-guard/` (`plugin.yaml` + `__init__.py`) | `pre_tool_call` hook | plugin returns `{"action":"block"}` |
| Droid (Factory) | `~/.factory/settings.json` | native `commandBlocklist` | hard-block, no approval possible |
| Devin CLI | `~/.config/devin/config.json` | `PreToolUse` matcher `^exec$` | shared script, exit 2 |

Claude/Codex hook entry; for Devin, replace `Bash` with `^exec$`. Merge into the existing `hooks` object; never overwrite it:

```json
{"hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "/ABSOLUTE/HOME/.agents/hooks/deny-dangerous.sh"}]}]}}
```

Cursor entry (payload has `.command`, so pass the `cursor` arg):

```json
{"beforeShellExecution": [{"command": "/ABSOLUTE/HOME/.agents/hooks/deny-dangerous.sh cursor", "failClosed": false}]}
```

Use absolute paths in configs (`~` expansion is inconsistent across agents).

## Tool behavior to know

- **Codex trust is hash-pinned.** Any edit to the hook ENTRY in `hooks.json` (not the patterns file) invalidates trust. Run `/hooks` in Codex and re-trust, or Codex skips the hook. Trust hashes live in `[hooks.state]` in `~/.codex/config.toml` and are shared by CLI, desktop app, and IDE extension. CI/scripts: `--dangerously-bypass-hook-trust`.
- **Cursor: set `failClosed` to `false`.** Cursor's background/worker hosts cannot execute hook scripts, so fail-closed blocks EVERY command there.
- **Hermes plugin manifest key is `provides_hooks`** (not `hooks`). The plugin must be listed under `plugins.enabled` in `~/.hermes/config.yaml` (the `hermes plugins enable` CLI prompts interactively and hangs non-interactive shells). Hermes skips a hook that throws, so keep the plugin trivial. Shell tool name is `terminal`.
- **Pi blocks the tool when a `tool_call` handler throws.** The adapter must catch its own errors, or a broken patterns file bricks every bash call.
- **Droid semantics:** `commandDenylist` = ask for confirmation; `commandBlocklist` = never runs, even at full autonomy with `--skip-permissions-unsafe`. Use the blocklist for catastrophic entries.
- **Payload shapes:** the command lives at `.tool_input.command` (Claude/Codex/Devin), `.toolInput.command` (Grok), `.command` (Cursor). Keep all three in the jq fallback chain.
- **Adapter regexes require multiline mode.** Keep JavaScript's `m` flag and Python's `re.M` so `^` matches each shell line like `grep`.
- **False-positive class:** a harmless command whose ARGUMENT text contains a dangerous-looking string (e.g. passing a prompt mentioning `git push --force` on a CLI) gets blocked. Workaround: put the text in a file and reference it.
- **No pre-command hook (as of 2026-07):** Gemini CLI, Qwen Code, Amp, kimi-cli. Cloud-hosted runs (Codex cloud tasks, Cursor background agents) do not load local hooks either.

## E2E verification

Safe probe: ask the agent to run `git push --force` from a NON-git directory — blocked = guard works; "not a git repository" = guard failed but no harm done.

```bash
cd "$(mktemp -d)"
claude -p 'Run exactly: git push --force. Report the result in one line.' --permission-mode bypassPermissions
codex exec --skip-git-repo-check 'Run exactly: git push --force. Report the result in one line.' < /dev/null
droid exec --auto high -f prompt.txt        # prompt text in a file (see false-positive gotcha)
pi -p --no-session 'Run exactly: git push --force. Report the result in one line.'
hermes chat --query 'Run exactly this terminal command: git push --force. Report in one line.'
```

Direct script test:

```bash
echo '{"tool_input":{"command":"rm -rf /"}}' | ~/.agents/hooks/deny-dangerous.sh; echo "exit=$?"   # expect exit=2
```
