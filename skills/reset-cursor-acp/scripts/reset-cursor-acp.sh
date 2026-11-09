#!/usr/bin/env bash
# Reset a stuck Cursor ACP agent inside bb.
#
# Generic public utility. Works on any machine with two publicly available
# products installed: the bb agentic IDE (`bb` CLI) and the Cursor CLI
# (`cursor-agent`). They talk over ACP (Agent Client Protocol, an open
# standard by Zed). Nothing here is specific to one person's setup, and no
# credentials, hostnames, or private infrastructure are involved.
#
# bb runs one `cursor-agent acp` subprocess per thread, spawned on demand by its
# public provider-acp plugin. There is no global server. "Reset" therefore means:
#   1. release the thread's runtime (bb thread stop)
#   2. kill orphaned cursor-agent acp processes bb no longer owns
#   3. check login + CLI version, the two most common root causes
# The next message sent to the thread spawns a fresh cursor-agent acp, which
# re-reads rules, skills and .cursor/mcp.json.
#
# Usage:
#   reset-cursor-acp.sh [<thread-id> | --self] [--kill-all] [--dry-run]
#
#   <thread-id> / --self  bb thread to stop (--self uses $BB_THREAD_ID).
#                         Omit to skip the stop and only clean up + health-check.
#   --kill-all            also kill cursor-agent acp processes still owned by a
#                         live bb bridge worker. This restarts EVERY Cursor
#                         thread in bb. Default: orphans only.
#   --dry-run             print what would happen, change nothing.
set -euo pipefail

THREAD=""
KILL_ALL=0
DRY_RUN=0
for arg in "$@"; do
  case "$arg" in
    --self)      THREAD="${BB_THREAD_ID:-}"; [ -n "$THREAD" ] || { echo "error: --self given but BB_THREAD_ID is empty" >&2; exit 2; } ;;
    --kill-all)  KILL_ALL=1 ;;
    --dry-run)   DRY_RUN=1 ;;
    -h|--help)   sed -n '2,20p' "$0"; exit 0 ;;
    -*)          echo "error: unknown flag $arg" >&2; exit 2 ;;
    *)           THREAD="$arg" ;;
  esac
done

run() { if [ "$DRY_RUN" = 1 ]; then echo "  [dry-run] $*"; else "$@"; fi; }
say() { printf '\n== %s\n' "$*"; }

CURSOR_BIN="$(command -v cursor-agent || true)"
[ -n "$CURSOR_BIN" ] || CURSOR_BIN="$HOME/.local/bin/cursor-agent"

# ---------------------------------------------------------------- 1. stop thread
say "1/4 release thread runtime"
if [ -n "$THREAD" ]; then
  if command -v bb >/dev/null 2>&1; then
    run bb thread stop "$THREAD" || echo "  warning: bb thread stop failed (thread may already be idle)"
  else
    echo "  warning: bb CLI not on PATH, skipping thread stop"
  fi
else
  echo "  no thread given, skipping (pass <thread-id> or --self to release the runtime)"
fi

# ---------------------------------------------------------- 2. kill orphan agents
say "2/4 clean up cursor-agent acp processes"
# Give bb a moment to reap its child after the stop.
[ "$DRY_RUN" = 1 ] || sleep 1

# Columns: pid ppid command. Match only the ACP server mode, never the TUI.
ACP_ROWS="$(ps -axo pid=,ppid=,command= | grep -E 'cursor-agent[^ ]* acp( |$)' | grep -v grep || true)"
if [ -z "$ACP_ROWS" ]; then
  echo "  none running"
else
  while read -r pid ppid _cmd; do
    [ -n "$pid" ] || continue
    parent_cmd="$(ps -o command= -p "$ppid" 2>/dev/null || true)"
    if [ "$ppid" = 1 ] || ! printf '%s' "$parent_cmd" | grep -q 'bb-provider-bridge-worker'; then
      state="orphan"
    else
      state="owned by bb bridge worker $ppid"
    fi
    if [ "$state" = orphan ] || [ "$KILL_ALL" = 1 ]; then
      echo "  killing pid $pid ($state)"
      run kill -TERM "$pid" 2>/dev/null || true
    else
      echo "  keeping pid $pid ($state); use --kill-all to restart every Cursor thread"
    fi
  done <<< "$ACP_ROWS"
  if [ "$DRY_RUN" = 0 ]; then
    sleep 2
    # Escalate for anything that ignored TERM.
    while read -r pid ppid _cmd; do
      [ -n "$pid" ] || continue
      if kill -0 "$pid" 2>/dev/null; then
        parent_cmd="$(ps -o command= -p "$ppid" 2>/dev/null || true)"
        if [ "$ppid" = 1 ] || [ "$KILL_ALL" = 1 ] || ! printf '%s' "$parent_cmd" | grep -q 'bb-provider-bridge-worker'; then
          echo "  pid $pid ignored TERM, sending KILL"
          kill -KILL "$pid" 2>/dev/null || true
        fi
      fi
    done <<< "$ACP_ROWS"
  fi
fi

# ------------------------------------------------------------- 3. health checks
say "3/4 cursor-agent health"
# cursor-agent prints harmless certificate warnings on stderr; hide them.
VERSION="$("$CURSOR_BIN" --version 2>/dev/null | tail -1 || echo unknown)"
echo "  version: $VERSION"
if STATUS="$("$CURSOR_BIN" status 2>/dev/null)"; then
  echo "  login:   $STATUS"
else
  echo "  login:   NOT logged in -> run: cursor-agent login"
fi
if command -v bb >/dev/null 2>&1; then
  UPD="$(bb updates status 2>/dev/null | grep -i 'cursor' || true)"
  [ -n "$UPD" ] && echo "  update:  $UPD" || echo "  update:  (bb updates status has no Cursor row)"
  case "$UPD" in
    *"Up to date"*|"") ;;
    *) echo "  -> newer Cursor CLI available: bb updates apply" ;;
  esac
fi

# -------------------------------------------------------------------- 4. done
say "4/4 next step"
echo "  send the next message to the thread; bb spawns a fresh cursor-agent acp"
echo "  (rules, skills and .cursor/mcp.json are re-read on that spawn)"
