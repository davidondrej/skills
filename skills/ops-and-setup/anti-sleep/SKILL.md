---
name: anti-sleep
description: Keep the user's MacBook awake reliably with macOS caffeinate for a set duration or while a process runs. Use for "don't let my Mac sleep", "keep the screen on", "anti-sleep", "caffeinate", overnight work, or long builds. Unlike a normal background job, it survives temporary agent-shell cleanup.
---

# Anti-Sleep (macOS caffeinate)

Use the bundled launcher from this skill directory. It creates a one-shot user LaunchAgent using only built-in macOS tools.

## Required workflow

Never launch `caffeinate` with raw `&`, `nohup`, `disown`, or `launchctl submit`. Temporary execution shells can kill their descendants, and `launchctl submit` can restart a timed job.

Resolve `scripts/anti-sleep.sh` relative to this `SKILL.md`; never assume the user's current directory. Run:

1. Inspect current state:

```bash
scripts/anti-sleep.sh status
```

2. If another session is active, do not replace it without consulting the user. Otherwise start a timer:

```bash
scripts/anti-sleep.sh start 10800    # 3 hours
```

For a specific process:

```bash
scripts/anti-sleep.sh start-pid <PID>
```

3. In a **separate tool/shell call after the start command has returned**, verify:

```bash
scripts/anti-sleep.sh verify
```

Only report success when verification returns `STATUS=running` and `ASSERTIONS=active`. Confirm the PID, flags, and wall-clock expiry. If verification fails, run `stop` and do not claim the Mac is protected.

## Assertion flags

The default is `-d -i`: keep the display on and prevent idle system sleep. Pass explicit flags after the duration or PID when needed:

| Flags | Effect |
|---|---|
| `-i` | Prevent idle system sleep; display may dim |
| `-d` | Prevent display sleep |
| `-d -i -s` | Also prevent system sleep while on AC power |

Example:

```bash
scripts/anti-sleep.sh start 10800 -i
```

## Status and stop

```bash
scripts/anti-sleep.sh status
scripts/anti-sleep.sh stop
```

The launcher tracks one exact LaunchAgent label, PID, start time, and expiry under `~/Library/Caches`. It never uses broad `pkill`.

## Fallback

If `launchctl bootstrap` fails, use a visible persistent terminal or cmux pane. Read the `cmux` skill before interacting with cmux. If no persistent surface is available, tell the user instead of starting an unreliable background job.

`caffeinate` cannot keep the keyboard backlight on. That setting is manual: System Settings → Keyboard → “Turn keyboard backlight off after inactivity” → Never.
