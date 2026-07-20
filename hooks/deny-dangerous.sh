#!/bin/bash
# Global agent command guard.
# Blocks catastrophic shell commands before agents run them. Two checks:
#   1. Regex denylist: ~/.agents/hooks/dangerous-patterns.txt (one ERE per line).
#   2. Primary-checkout branch guard: a primary git checkout (.git is a
#      directory, not a worktree pointer file) under ~/code must stay on its
#      default branch — git checkout/switch that would move it off is blocked.
#      Agents do branch work in git worktrees (see the master-agent repo).
#      This rule is cwd-aware so it lives HERE, not in the patterns file;
#      adapter-only agents (OpenCode, Pi, Hermes, Droid) do not enforce it.
#
# Used by:
#   Claude Code  ~/.claude/settings.json  PreToolUse (matcher Bash)
#   Codex        ~/.codex/hooks.json      PreToolUse (matcher Bash)
#   Cursor       ~/.cursor/hooks.json     beforeShellExecution (arg: cursor)
#
# stdin:  hook JSON. Claude/Codex put the command at .tool_input.command,
#         Cursor at .command. Session cwd, when present, is at .cwd.
# Block:  default mode -> exit 2 + reason on stderr (Claude/Codex contract).
#         "cursor" mode -> {"permission":"deny",...} JSON on stdout, exit 0.
# Allow:  default mode -> exit 0, silent. cursor mode -> {"permission":"allow"}.
#
# Env:
#   GUARD_CODE_ROOT  root holding primary checkouts (default: ~/code).
#                    Override in tests to point at fixture repos.

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
PATTERNS_FILE="$HOME/.agents/hooks/dangerous-patterns.txt"
# Canonicalize: git reports physical paths, so the prefix match must compare
# against a symlink-free root (e.g. /var -> /private/var on macOS).
CODE_ROOT="${GUARD_CODE_ROOT:-$HOME/code}"
CODE_ROOT=$(cd "$CODE_ROOT" 2>/dev/null && pwd -P) || CODE_ROOT="${GUARD_CODE_ROOT:-$HOME/code}"
MODE="${1:-exitcode}"

allow() {
  [ "$MODE" = "cursor" ] && printf '{"permission":"allow"}\n'
  exit 0
}

deny() { # $1 = reason
  if [ "$MODE" = "cursor" ]; then
    jq -cn --arg m "$1" '{
      permission: "deny",
      user_message: "Command guard blocked a dangerous command.",
      agent_message: ($m + " Do not retry it or try to work around the guard; explain the block to the user instead.")
    }'
    exit 0
  fi
  echo "$1 Do not retry it or try to work around the guard; explain the block to the user instead." >&2
  exit 2
}

# Without jq we cannot inspect the command: fail open rather than break agents.
command -v jq >/dev/null 2>&1 || allow

INPUT=$(cat)
# .tool_input = Claude/Codex, .toolInput = Grok CLI (Claude-compat mode), .command = Cursor
CMD=$(printf '%s' "$INPUT" | jq -r '.tool_input.command // .toolInput.command // .command // empty' 2>/dev/null)

[ -z "$CMD" ] && allow

# ---- 1. Regex denylist ------------------------------------------------------
if [ -f "$PATTERNS_FILE" ]; then
  while IFS= read -r pattern; do
    case "$pattern" in ''|\#*) continue ;; esac
    if printf '%s\n' "$CMD" | grep -qE -- "$pattern" 2>/dev/null; then
      deny "Blocked by the global dangerous-command guard (~/.agents/hooks/dangerous-patterns.txt). Matched pattern: $pattern."
    fi
  done < "$PATTERNS_FILE"
fi

# ---- 2. Primary-checkout branch guard ---------------------------------------
# Best-effort token parse; anything unresolvable fails OPEN (seatbelt against
# accidents, not a sandbox). Allowed even in a primary checkout: switching TO
# main/master/HEAD (recovery) and file restores (`git checkout [-]- <paths>`,
# `git checkout <ref> <paths>`) — neither moves HEAD off the branch.

strip_path_token() { # naive unquote + ~ expansion for a path token
  local p=$1
  p=${p#\"}; p=${p%\"}; p=${p#\'}; p=${p%\'}
  case "$p" in "~") p=$HOME ;; "~/"*) p="$HOME/${p#"~/"}" ;; esac
  printf '%s' "$p"
}

branch_guard() {
  case "$CMD" in
    *git*checkout*|*git*switch*) ;;
    *) return 0 ;;
  esac

  local cwd dir sub target creates pathspec toplevel gitd commond
  cwd=$(printf '%s' "$INPUT" | jq -r '.cwd // empty' 2>/dev/null)
  [ -n "$cwd" ] || cwd=$PWD
  dir=$cwd

  set -f
  # shellcheck disable=SC2086
  set -- $CMD
  set +f

  while [ $# -gt 0 ]; do
    case "$1" in
      cd|'(cd')
        shift
        [ $# -gt 0 ] && { dir=$(strip_path_token "$1"); shift; }
        continue
        ;;
      git) ;;
      *) shift; continue ;;
    esac

    shift # past "git"; consume global options, honoring -C <path>
    while [ $# -gt 0 ]; do
      case "$1" in
        -C) shift; [ $# -gt 0 ] && { dir=$(strip_path_token "$1"); shift; } ;;
        -c) shift; [ $# -gt 0 ] && shift ;;
        -*) shift ;;
        *) break ;;
      esac
    done
    [ $# -gt 0 ] || return 0
    sub=$1; shift
    [ "$sub" = "checkout" ] || [ "$sub" = "switch" ] || continue

    # Parse this invocation's args up to the next command separator.
    target="" creates=0 pathspec=0
    while [ $# -gt 0 ]; do
      case "$1" in
        '&&'|'||'|';'|'|') break ;;
        --) pathspec=1; break ;;
        -b|-B|-c|-C|--orphan|--detach|-d|-) creates=1; break ;;  # "-" = previous branch
        -*) ;;
        *) if [ -z "$target" ]; then target=${1%\)}; else pathspec=1; break; fi ;;
      esac
      shift
    done

    if [ "$creates" -eq 0 ]; then
      [ "$pathspec" -eq 1 ] && continue
      case "$target" in ''|main|master|HEAD) continue ;; esac
    fi

    # A HEAD move is requested — is $dir inside a PRIMARY checkout under
    # $CODE_ROOT? (a linked worktree's git-dir differs from the common git-dir)
    toplevel=$(git -C "$dir" rev-parse --show-toplevel 2>/dev/null) || continue
    case "$toplevel" in "$CODE_ROOT"|"$CODE_ROOT"/*) ;; *) continue ;; esac
    gitd=$(git -C "$dir" rev-parse --absolute-git-dir 2>/dev/null) || continue
    commond=$(git -C "$dir" rev-parse --path-format=absolute --git-common-dir 2>/dev/null) || continue
    [ "$gitd" = "$commond" ] || continue

    deny "Blocked by the primary-checkout branch guard (~/.agents/hooks/deny-dangerous.sh): '$toplevel' is a primary checkout under $CODE_ROOT and must stay on its default branch. Do branch work in a git worktree instead (git worktree add, or the master-agent spawn script); switching back with 'git checkout main' is allowed."
  done
  return 0
}

branch_guard

allow
