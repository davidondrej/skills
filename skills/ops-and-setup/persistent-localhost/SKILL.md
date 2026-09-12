---
name: persistent-localhost
description: "Manage persistent dev servers, APIs, and other local processes on a port using macOS LaunchAgents. Use when starting, stopping, restarting, inspecting, or troubleshooting local servers that should survive shell exit and restart after crashes."
---

# Persistent localhost servers (macOS launchd)

One script does everything. Resolve `scripts/persistent-localhost.sh` relative to this `SKILL.md`, never from the current directory.

## Workflow

1. Check what already exists:

```bash
scripts/persistent-localhost.sh list
```

2. Start the server. `--name` is the handle. `--port` enables readiness checks and duplicate handling. `--dir` defaults to the current directory.

```bash
scripts/persistent-localhost.sh start --name myproj --port 5111 --cmd "./bin/serve"
```

The command returns only after the port is listening, or fails with the last 20 log lines. Report the printed `URL=` to the user.

3. Inspect, restart, read logs, stop:

```bash
scripts/persistent-localhost.sh status myproj
scripts/persistent-localhost.sh restart myproj   # after editing code that has no reloader
scripts/persistent-localhost.sh logs myproj 100
scripts/persistent-localhost.sh stop myproj
```

## Hot reload

Prefer the framework's own reloader in `--cmd` (`flask run --debug`, `vite`, `uvicorn --reload`, `node --watch`). If the server has none, add `--watch`. It wraps the command in `watchexec -r` on the working directory. Never use both. Requires `brew install watchexec`.

## Rules the script enforces

- Runs as `com.persistent-localhost.<name>` in the user `gui` domain via `launchctl bootstrap`. Restart uses `kickstart -kp`, stop uses `bootout`. No deprecated `load`, `start`, `stop`, no broad `pkill`.
- `KeepAlive` only on crash. A clean exit stays down. Throttle 5s so a syntax error cannot spin.
- Port already taken by the same app (our own label, or a stray process with the same working directory) is replaced. A different app is left alone and the next free port is used. Read the printed `PORT=`.
- The caller's `PATH` and a `PORT` variable are passed into the job. Add more with `--env KEY=VAL`.
- Logs: `~/Library/Logs/persistent-localhost/<name>.log`. State: `~/Library/Application Support/persistent-localhost/<name>.state`. Plist: `~/Library/LaunchAgents/`.

## Fallback

Never start servers with `nohup`, `&`, `disown`, `setsid`, or `run_in_background`. If `launchctl bootstrap` fails, report the failure and stop.
