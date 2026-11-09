#!/bin/bash
# Run a localhost dev server as a user LaunchAgent so it outlives the agent shell.
set -euo pipefail

PREFIX="com.persistent-localhost"
DOMAIN="gui/$(/usr/bin/id -u)"
AGENTS="${HOME}/Library/LaunchAgents"
LOGS="${HOME}/Library/Logs/persistent-localhost"
STATES="${HOME}/Library/Application Support/persistent-localhost"

usage() {
  cat <<'EOF'
Usage:
  persistent-localhost.sh start --name NAME --cmd "COMMAND" [--port N] [--dir DIR] [--env K=V]... [--watch]
  persistent-localhost.sh stop NAME
  persistent-localhost.sh restart NAME
  persistent-localhost.sh status NAME
  persistent-localhost.sh logs NAME [LINES]
  persistent-localhost.sh list

--watch wraps COMMAND in `watchexec -r` (restart on file change). Never combine
with a framework that already reloads (flask --debug, vite, nodemon, uvicorn --reload).
EOF
}

die() { echo "ERROR=$*" >&2; exit 1; }
label() { echo "${PREFIX}.$1"; }
plist() { echo "${AGENTS}/$(label "$1").plist"; }
logfile() { echo "${LOGS}/$1.log"; }
statefile() { echo "${STATES}/$1.state"; }
service() { echo "${DOMAIN}/$(label "$1")"; }
state_value() { /usr/bin/awk -F= -v k="$2" '$1==k{sub(/^[^=]*=/,"");print;exit}' "$(statefile "$1")" 2>/dev/null; }
service_pid() { /bin/launchctl print "$(service "$1")" 2>/dev/null | /usr/bin/awk '$1=="pid"&&$2=="="{print $3;exit}'; }
port_owner() { /usr/sbin/lsof -nP -iTCP:"$1" -sTCP:LISTEN -t 2>/dev/null | /usr/bin/head -1; }
pid_ppid() { /bin/ps -o ppid= -p "$1" 2>/dev/null | /usr/bin/tr -d ' '; }
pid_cwd() { /usr/sbin/lsof -a -p "$1" -d cwd -Fn 2>/dev/null | /usr/bin/awk '/^n/{print substr($0,2);exit}'; }
xml() { /usr/bin/sed -e 's/&/\&amp;/g' -e 's/</\&lt;/g' -e 's/>/\&gt;/g' <<<"$1"; }

bootout() {
  /bin/launchctl print "$(service "$1")" >/dev/null 2>&1 && /bin/launchctl bootout "$(service "$1")" >/dev/null 2>&1 || true
}

# Same app on the port: our own label, or a stray process with the same working dir. Replace it.
# Different app: leave it alone and move to the next free port.
resolve_port() {
  local name="$1" port="$2" dir="$3" owner
  while owner=$(port_owner "$port"); [[ -n "$owner" ]]; do
    if [[ "$owner" == "$(service_pid "$name")" || "$(pid_ppid "$owner")" == "$(service_pid "$name")" || "$(pid_cwd "$owner")" == "$dir" ]]; then
      echo "NOTE=replacing old instance PID ${owner} on port ${port}" >&2
      bootout "$name"; kill "$owner" 2>/dev/null || true; /bin/sleep 1
    else
      echo "NOTE=port ${port} is used by another app (PID ${owner}), trying $((port + 1))" >&2
      port=$((port + 1))
    fi
  done
  echo "$port"
}

write_plist() {
  local name="$1" cmd="$2" dir="$3" port="$4"; shift 4
  local env_entries="" kv
  for kv in "$@"; do
    env_entries+="    <key>$(xml "${kv%%=*}")</key><string>$(xml "${kv#*=}")</string>
"
  done
  /bin/mkdir -p "$AGENTS" "$LOGS" "$STATES"
  cat >"$(plist "$name")" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$(label "$name")</string>
  <key>ProgramArguments</key><array><string>/bin/bash</string><string>-c</string><string>$(xml "$cmd")</string></array>
  <key>WorkingDirectory</key><string>$(xml "$dir")</string>
  <key>EnvironmentVariables</key><dict>
    <key>PATH</key><string>$(xml "$PATH")</string>
    <key>PORT</key><string>${port}</string>
${env_entries}  </dict>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><dict><key>SuccessfulExit</key><false/></dict>
  <key>ThrottleInterval</key><integer>5</integer>
  <key>StandardOutPath</key><string>$(xml "$(logfile "$name")")</string>
  <key>StandardErrorPath</key><string>$(xml "$(logfile "$name")")</string>
</dict></plist>
EOF
}

cmd_start() {
  local name="" cmd="" port="" dir="$PWD" watch=0 envs=()
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --name) name="$2"; shift 2 ;;
      --cmd) cmd="$2"; shift 2 ;;
      --port) port="$2"; shift 2 ;;
      --dir) dir="$(cd "$2" && pwd)"; shift 2 ;;
      --env) envs+=("$2"); shift 2 ;;
      --watch) watch=1; shift ;;
      *) die "unknown option $1" ;;
    esac
  done
  [[ "$name" =~ ^[A-Za-z0-9._-]+$ ]] || die "--name must be letters, digits, dot, dash, underscore"
  [[ -n "$cmd" ]] || die "--cmd is required"
  [[ -z "$port" || "$port" =~ ^[0-9]+$ ]] || die "--port must be a number"
  if (( watch )); then
    command -v watchexec >/dev/null || die "--watch needs watchexec: brew install watchexec"
    cmd="watchexec -r -w . -- ${cmd}"
  fi
  [[ -n "$port" ]] && port=$(resolve_port "$name" "$port" "$dir")
  bootout "$name"
  write_plist "$name" "$cmd" "$dir" "$port" "${envs[@]+"${envs[@]}"}"
  /bin/launchctl bootstrap "$DOMAIN" "$(plist "$name")" || die "launchctl bootstrap failed"
  printf 'NAME=%s\nCMD=%s\nDIR=%s\nPORT=%s\nPLIST=%s\nLOG=%s\nSTARTED=%s\n' \
    "$name" "$cmd" "$dir" "$port" "$(plist "$name")" "$(logfile "$name")" "$(/bin/date '+%Y-%m-%d %H:%M:%S')" >"$(statefile "$name")"
  wait_ready "$name" "$port"
  cmd_status "$name"
}

# Block until the port listens (or 60s), so callers never race the server.
wait_ready() {
  local name="$1" port="$2" i
  for i in $(seq 1 60); do
    if [[ -n "$port" ]]; then [[ -n "$(port_owner "$port")" ]] && return
    else [[ -n "$(service_pid "$name")" ]] && (( i >= 3 )) && return; fi
    /bin/sleep 1
  done
  if [[ -n "$port" ]]; then
    echo "STATUS=failed (nothing listening on port ${port} after 60s). Last log lines:" >&2
    /usr/bin/tail -n 20 "$(logfile "$name")" >&2 || true
    exit 1
  fi
}

cmd_status() {
  local name="$1" pid port
  [[ -f "$(statefile "$name")" ]] || die "no server named ${name}"
  pid=$(service_pid "$name"); port=$(state_value "$name" PORT)
  if [[ -n "$pid" ]]; then echo "STATUS=running"; else echo "STATUS=stopped"; fi
  echo "PID=${pid:-none}"
  if [[ -n "$port" ]]; then
    [[ -n "$(port_owner "$port")" ]] && echo "URL=http://localhost:${port}" || echo "URL=http://localhost:${port} (not listening)"
  fi
  /bin/cat "$(statefile "$name")"
}

cmd_stop() {
  local name="$1"
  bootout "$name"
  /bin/rm -f "$(plist "$name")" "$(statefile "$name")"
  echo "STATUS=stopped"; echo "NAME=${name}"
}

cmd_restart() {
  local name="$1"
  [[ -f "$(plist "$name")" ]] || die "no server named ${name}"
  /bin/launchctl kickstart -kp "$(service "$name")" >/dev/null || die "kickstart failed"
  /bin/sleep 1
  wait_ready "$name" "$(state_value "$name" PORT)"
  cmd_status "$name"
}

cmd_list() {
  local f name
  for f in "${STATES}"/*.state; do
    [[ -f "$f" ]] || { echo "no servers"; return; }
    name=$(/usr/bin/basename "$f" .state)
    printf '%-24s %-8s port=%-6s %s\n' "$name" "$([[ -n "$(service_pid "$name")" ]] && echo running || echo stopped)" \
      "$(state_value "$name" PORT)" "$(state_value "$name" DIR)"
  done
}

case "${1:-}" in
  start) shift; cmd_start "$@" ;;
  stop) cmd_stop "${2:?NAME required}" ;;
  restart) cmd_restart "${2:?NAME required}" ;;
  status) cmd_status "${2:?NAME required}" ;;
  logs) /usr/bin/tail -n "${3:-50}" "$(logfile "${2:?NAME required}")" ;;
  list) cmd_list ;;
  -h|--help|help) usage ;;
  *) usage >&2; exit 2 ;;
esac
