---
name: cyber-audit
description: Read-only exposure audit of the user's MacBook (and ~/Documents/code projects) for a CVE, breach, malicious package, or other security advisory, then write a structured report to ~/Documents/security-reports/. Use when the user shares a breach/CVE/malware/supply-chain advisory and asks if they're affected, says "scan my system for X", "are we affected by Y", "check if I'm vulnerable to Z", or requests any hack/breach/cyber/vulnerability audit on this MacBook. Output matches the existing audit format in ~/Documents/security-reports/.
disable-model-invocation: true
---

# cyber-audit

## Hard rules

- **Read-only.** No installs, removes, upgrades, restarts, network calls, or file modifications outside `~/Documents/security-reports/`.
- **No `sudo`.** Never.
- **One report per invocation.** Always end by writing the `.md` file (even if the verdict is "Not affected" — the audit trail matters).
- If a check requires a state-changing command, **skip it and note "not checked (would require state change)"** in the table. Do not run it.

## Workflow

1. **Identify scope.** Extract from the advisory: package/binary name, affected versions, platform (macOS / Linux / Windows), attack vector (supply chain / RCE / local / network).
2. **Run checks in parallel** (Bash tool, multiple calls in one message). Pick relevant checks for the advisory type — don't run all of them.
3. **Build the table** as you go. Each row = one check + concrete result (version number, path, "None", "N/A").
4. **Write the report** to `~/Documents/security-reports/YYYY-MM-DD-<short-kebab-slug>.md`. Use today's date from the environment header.
5. **Tell the user** the verdict in one line + path to the report.

## Check menu (pick what's relevant)

```bash
# --- Node / npm ecosystem (supply-chain advisories) ---
which npm pnpm yarn; npm root -g; pnpm root -g 2>/dev/null
ls /opt/homebrew/lib/node_modules                                  # global npm
find ~ -maxdepth 8 -type d -name "<pkg>" 2>/dev/null \
  | grep -v -E "(Library/Caches|\.Trash)"                          # installed copies
find ~/Documents ~/Desktop ~/Downloads -maxdepth 8 -type f \
  \( -name "package.json" -o -name "package-lock.json" \
     -o -name "pnpm-lock.yaml" -o -name "yarn.lock" \) 2>/dev/null \
  | xargs grep -l "<pkg>" 2>/dev/null                              # direct + transitive

# --- Python ecosystem ---
which python3 pip pipx uv
pip list 2>/dev/null | grep -i "<pkg>"
find ~/Documents -maxdepth 6 -name "requirements*.txt" -o -name "pyproject.toml" \
  -o -name "poetry.lock" -o -name "uv.lock" 2>/dev/null | xargs grep -l "<pkg>" 2>/dev/null

# --- Homebrew / system binaries ---
brew list --versions <formula> 2>/dev/null
which <binary>; <binary> --version 2>/dev/null

# --- Running processes / listeners (for RCE / network CVEs) ---
pgrep -lf "<binary>"
lsof -iTCP -sTCP:LISTEN -P -n 2>/dev/null | grep "<port>"

# --- LaunchAgents / LaunchDaemons (persistence / autostart) ---
ls ~/Library/LaunchAgents /Library/LaunchAgents /Library/LaunchDaemons 2>/dev/null \
  | grep -i "<vendor>"

# --- Env vars that change exposure (e.g. OLLAMA_HOST, listening addr) ---
launchctl getenv <VAR>; grep -r "<VAR>" ~/.zshrc ~/.zprofile ~/.config 2>/dev/null

# --- VS Code / browser extensions (for IDE-targeted advisories) ---
ls ~/.vscode/extensions 2>/dev/null | grep -i "<ext>"
```

If the advisory mentions an ecosystem not above (Rust cargo, Go modules, Ruby gems, Docker images, etc.), apply the same pattern: global install path + manifest grep + running processes.

## Report template

File: `~/Documents/security-reports/YYYY-MM-DD-<short-kebab-slug>.md`

```markdown
# <Subject> — Audit

**Date:** YYYY-MM-DD
**Host:** <machine name/model>

## <CVEs | Advisory> in scope

- **<ID or source> "<Name>"** — <one-line description>. <Affected versions or scope>.

## Audit results

| Check | Result |
|---|---|
| <Check 1> | <Result> |
| <Check 2> | <Result> |

## Verdict

**<Not affected. | Affected. | Partially affected.>**

- <Rationale bullet 1>
- <Rationale bullet 2>

## Action taken

None — diagnostic only, no files modified, no <packages installed/removed | services started/stopped | firewall rules changed>.

## Follow-ups

- <Actionable item, or "None" if truly nothing>
```

Match the tone of any existing reports in `~/Documents/security-reports/` — terse, factual, bulleted, no hedging.

## Verdict wording

- **Not affected.** — package/binary absent, or installed but patched, or not running and not exposed.
- **Affected.** — vulnerable version present *and* reachable by the attack vector.
- **Partially affected.** — present but mitigated (e.g. binary installed but service not running, or listener bound to loopback only). Spell out the mitigation in the bullets.

## When to break the read-only rule

Never on your own. If the verdict is "Affected", list the remediation command in **Follow-ups** and stop. The user runs it.

## Reference

If existing reports are present in `~/Documents/security-reports/`, match their established style and format rather than introducing a new one.
