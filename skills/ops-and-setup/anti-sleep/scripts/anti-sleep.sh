#!/bin/bash
set -euo pipefail

LABEL="com.davidondrej.anti-sleep"
DOMAIN="gui/$(/usr/bin/id -u)"
SERVICE="${DOMAIN}/${LABEL}"
STATE_DIR="${HOME}/Library/Caches/${LABEL}"
PLIST="${STATE_DIR}/job.plist"
STATE="${STATE_DIR}/state"
LOCK_DIR="${STATE_DIR}/lock"

usage() {
  cat <<'EOF'
Usage:
  anti-sleep.sh start SECONDS [FLAGS...]
  anti-sleep.sh start-pid PID [FLAGS...]
  anti-sleep.sh verify
  anti-sleep.sh status
  anti-sleep.sh stop

FLAGS default to: -d -i
Allowed flags: -d -i -m -s -u
EOF
}

die() {
  echo "ERROR=$*" >&2
  exit 1
}

release_lock() {
  /bin/rmdir "$LOCK_DIR" >/dev/null 2>&1 || true
}

acquire_lock() {
  local now
  local modified

  /bin/mkdir -p "$STATE_DIR"
  /bin/chmod 700 "$STATE_DIR"

  if ! /bin/mkdir "$LOCK_DIR" 2>/dev/null; then
    now=$(/bin/date +%s)
    modified=$(/usr/bin/stat -f %m "$LOCK_DIR" 2>/dev/null || echo "$now")
    if [[ "$modified" =~ ^[0-9]+$ ]] && (( now - modified > 30 )); then
      /bin/rmdir "$LOCK_DIR" 2>/dev/null ||
        die "another anti-sleep operation is in progress"
      /bin/mkdir "$LOCK_DIR" 2>/dev/null ||
        die "another anti-sleep operation is in progress"
    else
      die "another anti-sleep operation is in progress"
    fi
  fi

  trap release_lock EXIT
  trap 'exit 130' HUP INT TERM
}

service_loaded() {
  /bin/launchctl print "$SERVICE" >/dev/null 2>&1
}

service_pid() {
  /bin/launchctl print "$SERVICE" 2>/dev/null |
    /usr/bin/awk '$1 == "pid" && $2 == "=" { print $3; exit }'
}

process_is_caffeinate() {
  local pid="${1:-}"
  local command

  [[ "$pid" =~ ^[0-9]+$ ]] || return 1
  kill -0 "$pid" 2>/dev/null || return 1
  command=$(/bin/ps -p "$pid" -o command= 2>/dev/null || true)
  [[ "$command" == /usr/bin/caffeinate* ]]
}

state_value() {
  local key="$1"

  [[ -f "$STATE" ]] || return 1
  /usr/bin/awk -F= -v key="$key" '
    $1 == key {
      sub(/^[^=]*=/, "")
      print
      exit
    }
  ' "$STATE"
}

format_epoch() {
  /bin/date -r "$1" '+%Y-%m-%d %H:%M:%S %Z'
}

validate_flags() {
  local flag

  for flag in "$@"; do
    case "$flag" in
      -d|-i|-m|-s|-u) ;;
      *) die "unsupported caffeinate flag: $flag" ;;
    esac
  done
}

bootout_loaded_job() {
  if service_loaded; then
    /bin/launchctl bootout "$SERVICE" >/dev/null ||
      die "could not remove existing LaunchAgent ${LABEL}"
  fi
}

write_plist() {
  local temp
  local argument

  temp=$(/usr/bin/mktemp "${STATE_DIR}/job.plist.XXXXXX")
  {
    cat <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${LABEL}</string>
  <key>ProgramArguments</key>
  <array>
EOF
    for argument in "$@"; do
      printf '    <string>%s</string>\n' "$argument"
    done
    cat <<'EOF'
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <false/>
</dict>
</plist>
EOF
  } >"$temp"
  /bin/chmod 600 "$temp"
  /bin/mv "$temp" "$PLIST"
}

write_state() {
  local mode="$1"
  local target="$2"
  local flags="$3"
  local pid="$4"
  local start_epoch="$5"
  local expires_epoch="$6"
  local temp

  temp=$(/usr/bin/mktemp "${STATE_DIR}/state.XXXXXX")
  {
    printf 'MODE=%s\n' "$mode"
    printf 'TARGET=%s\n' "$target"
    printf 'FLAGS=%s\n' "$flags"
    printf 'PID=%s\n' "$pid"
    printf 'START_EPOCH=%s\n' "$start_epoch"
    printf 'EXPIRES_EPOCH=%s\n' "$expires_epoch"
  } >"$temp"
  /bin/chmod 600 "$temp"
  /bin/mv "$temp" "$STATE"
}

verify_running() {
  local pid
  local command
  local assertions

  pid=$(service_pid || true)
  process_is_caffeinate "$pid" || return 1
  command=$(/bin/ps -p "$pid" -o command=)
  assertions=$(/usr/bin/pmset -g assertions 2>/dev/null || true)
  /usr/bin/grep -Fq "pid ${pid}(caffeinate)" <<<"$assertions" || return 1

  printf 'STATUS=running\n'
  printf 'LABEL=%s\n' "$LABEL"
  printf 'PID=%s\n' "$pid"
  printf 'COMMAND=%s\n' "$command"
  printf 'ASSERTIONS=active\n'

  if [[ -f "$STATE" ]]; then
    printf 'MODE=%s\n' "$(state_value MODE)"
    printf 'FLAGS=%s\n' "$(state_value FLAGS)"
    if [[ "$(state_value MODE)" == "timer" ]]; then
      printf 'EXPIRES=%s\n' "$(format_epoch "$(state_value EXPIRES_EPOCH)")"
    else
      printf 'UNTIL_PID=%s\n' "$(state_value TARGET)"
    fi
  fi
}

start_job() {
  local mode="$1"
  local target="$2"
  shift 2
  local flags=("$@")
  local arguments=(/usr/bin/caffeinate)
  local flags_text
  local existing_pid
  local pid
  local start_epoch
  local expires_epoch=0
  local attempt

  if [[ ${#flags[@]} -eq 0 ]]; then
    flags=(-d -i)
  fi
  validate_flags "${flags[@]}"
  acquire_lock

  existing_pid=$(service_pid || true)
  if process_is_caffeinate "$existing_pid"; then
    die "anti-sleep is already running as PID ${existing_pid}; inspect it before replacing it"
  fi

  bootout_loaded_job
  /bin/mkdir -p "$STATE_DIR"
  /bin/chmod 700 "$STATE_DIR"
  /bin/rm -f "$PLIST" "$STATE"

  arguments+=("${flags[@]}")
  if [[ "$mode" == "timer" ]]; then
    arguments+=(-t "$target")
  else
    arguments+=(-w "$target")
  fi

  write_plist "${arguments[@]}"
  start_epoch=$(/bin/date +%s)
  if [[ "$mode" == "timer" ]]; then
    expires_epoch=$((start_epoch + target))
  fi

  if ! /bin/launchctl bootstrap "$DOMAIN" "$PLIST"; then
    /bin/rm -f "$PLIST"
    die "launchctl could not start the one-shot LaunchAgent"
  fi

  pid=""
  for attempt in 1 2 3 4 5; do
    pid=$(service_pid || true)
    process_is_caffeinate "$pid" && break
    /bin/sleep 0.2
  done

  if ! process_is_caffeinate "$pid"; then
    bootout_loaded_job
    /bin/rm -f "$PLIST" "$STATE"
    die "caffeinate did not survive launch"
  fi

  flags_text="${flags[*]}"
  write_state "$mode" "$target" "$flags_text" "$pid" "$start_epoch" "$expires_epoch"

  verify_running || {
    bootout_loaded_job
    /bin/rm -f "$PLIST" "$STATE"
    die "caffeinate started without a visible power assertion"
  }
}

status_job() {
  local now
  local mode
  local expires_epoch
  local pid

  if verify_running; then
    return 0
  fi

  pid=$(service_pid || true)
  if [[ -f "$STATE" ]]; then
    mode=$(state_value MODE)
    if [[ "$mode" == "timer" ]]; then
      now=$(/bin/date +%s)
      expires_epoch=$(state_value EXPIRES_EPOCH)
      if [[ "$expires_epoch" =~ ^[0-9]+$ ]] && (( now >= expires_epoch )); then
        printf 'STATUS=expired\n'
        printf 'EXPIRED_AT=%s\n' "$(format_epoch "$expires_epoch")"
        return 0
      fi
    fi
    printf 'STATUS=failed\n'
    printf 'EXPECTED_PID=%s\n' "$(state_value PID)"
    printf 'OBSERVED_PID=%s\n' "${pid:-none}"
    return 1
  fi

  if service_loaded; then
    printf 'STATUS=inactive\n'
    printf 'LABEL=%s\n' "$LABEL"
  else
    printf 'STATUS=stopped\n'
  fi
}

stop_job() {
  acquire_lock
  bootout_loaded_job
  /bin/rm -f "$PLIST" "$STATE"
  printf 'STATUS=stopped\n'
  printf 'LABEL=%s\n' "$LABEL"
}

command="${1:-}"
case "$command" in
  start)
    duration="${2:-}"
    [[ "$duration" =~ ^[0-9]+$ ]] ||
      die "duration must be an integer of at least 5 seconds"
    duration=$((10#$duration))
    (( duration >= 5 )) ||
      die "duration must be an integer of at least 5 seconds"
    shift 2
    start_job timer "$duration" "$@"
    ;;
  start-pid)
    target_pid="${2:-}"
    [[ "$target_pid" =~ ^[0-9]+$ ]] ||
      die "PID must be a positive integer"
    target_pid=$((10#$target_pid))
    (( target_pid >= 1 )) ||
      die "PID must be a positive integer"
    kill -0 "$target_pid" 2>/dev/null ||
      die "target PID ${target_pid} is not running"
    shift 2
    start_job pid "$target_pid" "$@"
    ;;
  verify)
    verify_running || die "anti-sleep is not running with active power assertions"
    ;;
  status)
    status_job
    ;;
  stop)
    stop_job
    ;;
  -h|--help|help)
    usage
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac
