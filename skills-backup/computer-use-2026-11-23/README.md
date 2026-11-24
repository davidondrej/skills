# Computer-use cleanup, 2026-11-23

David dogfoods only Cloudroom's built-in Computer Use (cloudroom ADR 20261123-101930).

## What moved here

- `skills/`: `cua-driver`, `codex-cu`, `codex-computer-use`, `browser-use`, `browser-harness` (from `~/.agents/skills`)
- `codex-cu-mcp.json`: the `codex-cu` user MCP entry, removed from `~/.claude.json` and all 6 Cloudroom Claude profiles
- `claude-settings.json`: `~/.claude/settings.json` before the Stop hook was removed

## Also removed

- Per-skill links in `~/.cursor/skills` (all 5) and `browser-use` in `~/.gemini/skills`, `~/.config/opencode/skills`, `~/.copilot/skills`

## Not touched

- `/Applications/CuaDriver.app`, `~/.local/bin/cua-driver`, `~/.local/bin/browser-use`, and the local codex-cu workspace
- Codex's own Computer Use plugins and Playwright MCP (`~/.codex/config.toml`)
- Claude desktop's `anthropic-skills`

## Undo

```sh
mv ~/.agents/skills-backup/computer-use-2026-11-23/skills/* ~/.agents/skills/
cp ~/.agents/skills-backup/computer-use-2026-11-23/claude-settings.json ~/.claude/settings.json
claude mcp add-json codex-cu -s user "$(cat ~/.agents/skills-backup/computer-use-2026-11-23/codex-cu-mcp.json)"
```
