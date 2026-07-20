---
name: global-agent-guardrails
description: 'One shared denylist of catastrophic shell commands (rm -rf on / or ~, dd/mkfs, sudo rm, fork bombs, curl|sh, git push --force, gh repo delete) enforced as a PreToolUse/pre-exec guard across every AI coding agent on the machine — Cursor, Claude Code, Codex, OpenCode, Pi, Hermes, Grok, Droid, Devin. Use when adding or tuning blocked-command patterns, wiring the guard into a new agent or a new machine, debugging why a command was (or was not) blocked, or when the user mentions command guard, guardrails, dangerous command hook, or PreToolUse safety.'
---

# Global Agent Guardrails

A "bouncer" that blocks catastrophic shell commands before any AI agent runs them. One patterns file is the single source of truth; every agent reads it via a shared hook script or a tiny native adapter. It is a seatbelt against accidents, NOT a sandbox against a malicious agent (obfuscation like `python -c "shutil.rmtree(...)"` can slip past regex).

## File map

```
~/.agents/hooks/dangerous-patterns.txt   # THE denylist: one POSIX-ERE regex per line, # comments
~/.agents/hooks/deny-dangerous.sh        # shared guard: hook JSON on stdin -> exit 2 blocks
~/.agents/hooks/test-guard.sh            # test suite: run after ANY pattern change
~/.config/opencode/plugins/command-guard.ts   # OpenCode adapter (throws to block)
~/.pi/agent/extensions/command-guard.ts       # Pi adapter (returns {block:true})
~/.hermes/plugins/command-guard/              # Hermes plugin (returns {"action":"block"})
```

## State check (is it installed?)

```bash
ls ~/.agents/hooks/deny-dangerous.sh ~/.agents/hooks/dangerous-patterns.txt
~/.agents/hooks/test-guard.sh   # must end "failed: 0"
```

If missing, rebuild from the wiring table below (full history: DeepAPI repo `docs/research/global-agent-command-guard-deep-research-2026-07-11.md`).

## Add or tune a pattern

1. Edit `~/.agents/hooks/dangerous-patterns.txt`. Write POSIX ERE (`grep -E`). Use `[[:space:]]`, never `\s` — adapters auto-convert `[:space:]` to `\s` for JS/Python.
2. Add block + allow cases to `test-guard.sh`, then run it. Must pass 100%.
3. Verify the new pattern compiles in the adapter engines:

```bash
python3 -c 'import re,pathlib; [re.compile(l.strip().replace("[:space:]",r"\s")) for l in pathlib.Path.home().joinpath(".agents/hooks/dangerous-patterns.txt").read_text().splitlines() if l.strip() and not l.startswith("#")]; print("ok")'
```

4. Changes apply instantly everywhere (all consumers re-read the file per command). Exception: Droid uses its own `commandBlocklist` in `~/.factory/settings.json` — mirror the change there manually.

Design rule: block only irreversible/catastrophic commands (data loss, disk wipe, repo deletion, token exfil). Local-destructive-but-recoverable commands (`git status`, `git clean -fdx`, `rm -rf node_modules`) stay ALLOWED — over-blocking kills agent usefulness.

## Primary-checkout branch guard (script-level rule, not a pattern)

Besides the regex denylist, `deny-dangerous.sh` enforces one cwd-aware rule: a **primary git checkout** (`.git` is a directory, not a worktree pointer file) **under `~/code` must stay on its default branch**. `git checkout` / `git switch` that would move HEAD off it — another branch, `-b/-B/-c/-C`, `--detach`, `--orphan`, `switch -`, tags/SHAs — is blocked. Still allowed: switching TO `main`/`master`/`HEAD` (recovery), file restores (`git checkout -- <paths>`, `git checkout <ref> <paths>`), everything inside linked worktrees, and every repo outside `~/code`. Born from the 2026-07-20 incident where an agent session in `~/code/DeepAPI` checked out a PR branch in the primary checkout instead of a worktree (the master-agent repo owns the worktree dispatch flow).

- Target dir resolution: `git -C <path>` wins, else the last `cd <path>` before the git word, else hook JSON `.cwd`, else the hook process cwd. Anything unresolvable fails OPEN.
- Coverage: shared-script consumers only (Claude Code, Codex, Cursor, Grok, Devin). The OpenCode/Pi/Hermes adapters and Droid's static blocklist only read the patterns file and can NOT express cwd-aware rules — they do not enforce this.
- Testing: fixture-repo cases live in `test-guard.sh`; `GUARD_CODE_ROOT` overrides the `~/code` root, and `GUARD=/path/to/candidate.sh test-guard.sh` tests an edited copy before install.

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

Hook entry shape for Claude/Codex/Devin (merge into existing `hooks` object, never overwrite):

```json
{"hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "/ABSOLUTE/HOME/.agents/hooks/deny-dangerous.sh"}]}]}}
```

Cursor entry (payload has `.command`, so pass the `cursor` arg):

```json
{"beforeShellExecution": [{"command": "/ABSOLUTE/HOME/.agents/hooks/deny-dangerous.sh cursor", "failClosed": false}]}
```

Use absolute paths in configs (`~` expansion is inconsistent across agents).

## Gotchas (hard-won — do not rediscover)

- **Codex trust is hash-pinned.** Any edit to the hook ENTRY in `hooks.json` (not the patterns file) invalidates trust; run `/hooks` in Codex and re-trust, else Codex silently skips the guard. Trust hashes live in `[hooks.state]` in `~/.codex/config.toml` and are shared by CLI, desktop app, and IDE extension. CI/scripts: `--dangerously-bypass-hook-trust`.
- **Cursor `failClosed` must stay `false`.** Cursor background/worker hosts cannot execute hook scripts; fail-closed blocks EVERY command there. Trade-off: Cursor background agents run unguarded.
- **Hermes plugin manifest key is `provides_hooks`** (not `hooks`). Plugin must be enabled: `plugins.enabled` list in `~/.hermes/config.yaml` (the `hermes plugins enable` CLI prompts interactively and hangs non-interactive shells). Hermes hooks are fail-open on exceptions — keep the plugin trivial. Shell tool name is `terminal`.
- **Pi `tool_call` handler errors block the tool** (fail-safe) — adapter must catch its own errors and fail open, or a broken patterns file bricks every bash call.
- **Droid semantics:** `commandDenylist` = ask for confirmation; `commandBlocklist` = never runs, even at full autonomy with `--skip-permissions-unsafe`. Use blocklist for catastrophic entries.
- **Guard script payload detection:** command lives at `.tool_input.command` (Claude/Codex/Devin), `.toolInput.command` (Grok), `.command` (Cursor). Keep all three in the jq fallback chain.
- **False-positive class:** a harmless command whose ARGUMENT text contains a dangerous-looking string (e.g. passing a prompt mentioning `git push --force` on a CLI) gets blocked. Workaround: put the text in a file and reference it.
- **Not coverable natively (no hook system as of 2026-07):** Gemini CLI, Qwen Code, Amp, kimi-cli. Codex cloud tasks and Cursor background agents also bypass the local guard.

## E2E verification recipe

Safe probe: ask the agent to run `git push --force` from a NON-git directory — blocked = guard works; "not a git repository" = guard failed but no harm done.

```bash
cd "$(mktemp -d)"
claude -p 'Run exactly: git push --force. Report the result in one line.' --permission-mode bypassPermissions
codex exec --skip-git-repo-check 'Run exactly: git push --force. Report the result in one line.' < /dev/null
droid exec --auto high -f prompt.txt        # prompt text in a file (see false-positive gotcha)
pi -p --no-session 'Run exactly: git push --force. Report the result in one line.'
hermes chat --query 'Run exactly this terminal command: git push --force. Report in one line.'
```

Direct script test without any agent:

```bash
echo '{"tool_input":{"command":"rm -rf /"}}' | ~/.agents/hooks/deny-dangerous.sh; echo "exit=$?"   # expect exit=2
```
