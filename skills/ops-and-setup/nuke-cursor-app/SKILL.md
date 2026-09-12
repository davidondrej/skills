---
name: nuke-cursor-app
description: 'End-to-end Cursor IDE restart on the user''s MacBook: snapshot metrics, kill ALL Cursor processes, relaunch Cursor, report before/after memory. Recovers from the known renderer memory leak that makes Cursor lag. Manual-only — run ONLY when the user explicitly invokes it (/nuke-cursor-app, "nuke cursor"). Differentiator: kills the Cursor desktop app; cursor-cli sessions are unrelated.'
disable-model-invocation: true
---

# Nuke Cursor App

## Why this exists

Cursor (the AI IDE) is an Electron-based VS Code fork. It has a known,
Cursor-acknowledged memory leak: the renderer process accumulates tool-call
state (diffs, file contexts) during long agent sessions and never frees it,
especially in the Agents window. The UI gets laggy, then freezes. The only
reliable recovery is a full restart — that is what this skill does, end to
end: snapshot → kill → relaunch → before/after report.

## How Cursor runs

One main process at `/Applications/Cursor.app/Contents/MacOS/Cursor` plus
helper processes (Renderer, GPU, extension host, network service, crashpad)
that all live under the `/Applications/Cursor.app` bundle path.

## Safety rules

- Match processes ONLY by the bundle path `/Applications/Cursor.app` —
  never by the bare word "cursor".
- Do NOT touch `CursorUIViewService` — despite the name it is a macOS
  system text-input service, not part of the Cursor app.
- Warn the user first if you have reason to think an important agent run is
  in flight; killing Cursor kills its local agent sessions.
- The macbook-metrics collector OWNS `cursor-metrics.sqlite3`. Read it
  ONLY with `sqlite3 -readonly`. Never write to it.
- The snapshot is best-effort: if the DB is missing or a query fails,
  note that in the log and continue — never block the nuke on it.

## Procedure

### 1. Snapshot BEFORE killing

```bash
DB="$HOME/Library/Application Support/macbook-metrics/cursor-metrics.sqlite3"
LOG_DIR="$HOME/Library/Application Support/macbook-metrics/nuke-logs"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/$(date +%Y-%m-%d-%H%M).md"

# Live per-process readout — these are the "before" numbers
ps -axo pid,rss,comm | grep "/Applications/Cursor.app" | grep -v grep

# Totals for the summary line (rss is in KB on macOS)
ps -axo rss,comm | awk 'index($0, "/Applications/Cursor.app") {n++; s+=$1} END {printf "%d processes, %.1f GB", n, s/1048576; print ""}'

# Last 30 min from the collector (read-only)
sqlite3 -readonly "$DB" "SELECT datetime(timestamp,'unixepoch','localtime'), role, process_count, ROUND(cpu_percent,1), ROUND(resident_bytes/1073741824.0,2) || ' GB' FROM raw_samples WHERE timestamp > strftime('%s','now') - 1800 ORDER BY timestamp;"
sqlite3 -readonly "$DB" "SELECT datetime(timestamp,'unixepoch','localtime'), kind, role, reason, memory_pressure FROM events WHERE timestamp > strftime('%s','now') - 1800 ORDER BY timestamp;"
```

Write all four outputs into `$LOG` with headings: process list, totals,
metrics (last 30 min), events (last 30 min). The after-restart reading is
appended in step 4 — so one file tells the whole story of this nuke.

### 2. Kill every Cursor process

```bash
# Graceful quit first — lets Cursor save session state
osascript -e 'tell application "Cursor" to quit' 2>/dev/null
sleep 3

# Kill anything still alive under the bundle path
pkill -f "/Applications/Cursor.app" 2>/dev/null
sleep 1

# Verify; force-kill leftovers by PID if needed
ps -axo pid,comm | grep "/Applications/Cursor.app" | grep -v grep
# if any remain:  kill -9 <pid> ...

# Final check — must print "all Cursor processes gone"
ps -axo pid,comm | grep "/Applications/Cursor.app" | grep -v grep && echo "STILL RUNNING" || echo "all Cursor processes gone"
```

The graceful quit often fails exactly when this skill is needed — a leaked
renderer blocks the main thread — which is why the pkill/kill steps exist.
Note in the log whether graceful quit worked or force-kill was needed.

### 3. Relaunch and verify

Skip this step only if the user asked to keep Cursor closed
("nuke cursor and keep it closed").

```bash
sleep 2
open -a Cursor

# Wait up to 15 s for the main process to come back
for i in $(seq 1 15); do
  ps -axo comm | grep -q "/Applications/Cursor.app/Contents/MacOS/Cursor" && break
  sleep 1
done
ps -axo pid,comm | grep "/Applications/Cursor.app/Contents/MacOS/Cursor" | grep -v grep
```

If the poll times out, report that — never claim Cursor is back without
seeing the main process.

### 4. After-restart reading

```bash
sleep 10   # let Cursor settle and restore windows

ps -axo pid,rss,comm | grep "/Applications/Cursor.app" | grep -v grep
ps -axo rss,comm | awk 'index($0, "/Applications/Cursor.app") {n++; s+=$1} END {printf "%d processes, %.1f GB", n, s/1048576; print ""}'
```

Append both outputs to `$LOG` under an "after restart" heading.

### 5. Report to the user

End with one plain-English summary line, for example:

> Killed 14 processes using 21.3 GB. Cursor is back with 9 processes
> using 2.1 GB. Snapshot saved to nuke-logs/2026-08-14-1832.md.

Never claim success without the step 2 final check and (unless skipped)
the step 3 relaunch check.

## Known failure modes

- After a force-kill, Cursor may show a "restore windows?" dialog on
  relaunch. That is expected — tell the user to click Restore.
- If the metrics DB has no recent rows (collector stalled), say so in the
  log and the report; the `ps` readouts still give valid before/after.
