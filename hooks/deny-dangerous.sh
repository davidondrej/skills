#!/bin/bash
# Global agent command guard.
# Blocks catastrophic shell commands before agents run them.
# Denylist: ~/.agents/hooks/dangerous-patterns.txt (one ERE regex per line).
#
# Used by:
#   Claude Code  ~/.claude/settings.json  PreToolUse (matcher Bash)
#   Codex        ~/.codex/hooks.json      PreToolUse (matcher Bash)
#   Cursor       ~/.cursor/hooks.json     beforeShellExecution (arg: cursor)
#
# stdin:  hook JSON. Claude/Codex put the command at .tool_input.command,
#         Cursor at .command.
# Block:  default mode -> exit 2 + reason on stderr (Claude/Codex contract).
#         "cursor" mode -> {"permission":"deny",...} JSON on stdout, exit 0.
# Allow:  default mode -> exit 0, silent. cursor mode -> {"permission":"allow"}.

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
PATTERNS_FILE="$HOME/.agents/hooks/dangerous-patterns.txt"
MODE="${1:-exitcode}"

allow() {
  [ "$MODE" = "cursor" ] && printf '{"permission":"allow"}\n'
  exit 0
}

# Without jq we cannot inspect the command: fail open rather than break agents.
command -v jq >/dev/null 2>&1 || allow

INPUT=$(cat)
# .tool_input = Claude/Codex, .toolInput = Grok CLI (Claude-compat mode), .command = Cursor
CMD=$(printf '%s' "$INPUT" | jq -r '.tool_input.command // .toolInput.command // .command // empty' 2>/dev/null)

[ -z "$CMD" ] && allow
[ -f "$PATTERNS_FILE" ] || allow

while IFS= read -r pattern; do
  case "$pattern" in ''|\#*) continue ;; esac
  if printf '%s\n' "$CMD" | grep -qE -- "$pattern" 2>/dev/null; then
    if [ "$MODE" = "cursor" ]; then
      jq -cn --arg p "$pattern" '{
        permission: "deny",
        user_message: "Command guard blocked a dangerous command.",
        agent_message: ("This command was blocked by the global dangerous-command guard (~/.agents/hooks/dangerous-patterns.txt). Matched pattern: " + $p + ". Do not retry it or try to work around the guard; explain the block to the user instead.")
      }'
      exit 0
    fi
    echo "Blocked by the global dangerous-command guard (~/.agents/hooks/dangerous-patterns.txt). Matched pattern: $pattern. Do not retry it or try to work around the guard; explain the block to the user instead." >&2
    exit 2
  fi
done < "$PATTERNS_FILE"

allow
