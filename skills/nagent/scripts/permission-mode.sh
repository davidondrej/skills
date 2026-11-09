#!/usr/bin/env bash
# Print the effective bb permission mode of a thread (last execution record).
# Usage: permission-mode.sh [thread-id]   (defaults to $BB_THREAD_ID)
set -euo pipefail
id="${1:-${BB_THREAD_ID:-}}"
[ -n "$id" ] || { echo "usage: permission-mode.sh <thread-id>" >&2; exit 2; }
bb thread log "$id" --json --all 2>/dev/null | python3 -c '
import json, sys
d = json.load(sys.stdin)
ev = d if isinstance(d, list) else d.get("events", d)
m = [e["data"]["execution"]["permissionMode"] for e in ev
     if e.get("type") == "client/turn/requested" and "execution" in e.get("data", {})]
print(m[-1] if m else "unknown")
'
