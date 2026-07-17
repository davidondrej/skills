---
name: vps-server-management
description: Use when the user wants to manage his VPS servers and the AI agents running inside them — connecting, deploying, monitoring, restarting, and operating remote hosts and their agents. Triggers on VPS, server management, remote host, SSH into server, manage my servers, agents on the server.
---

# VPS Server Management

Source of truth: `~/Documents/infrastructure.md` (read it for the latest — details change).

## Servers (Hostinger VPS) — 3 total

| Server | OS | Purpose |
|---|---|---|
| OpenClaw server | Ubuntu 24.04 (Dokploy) | OpenClaw — personal instance |
| n8n server | Ubuntu 24.04 (n8n) | All n8n workflow automations (primary) |
| Hermes server | Ubuntu 24.04 | Hermes Agent — Discord gateway |

SSH as `root@<IP>`.

## Access levels (never share higher than needed)

1. **App login** — e.g. an app-specific subdomain login page. Build/edit workflows, no server access. Safest to share.
2. **VPS SSH** — `root@<IP>`. Docker, files, system config. Trusted technical people only.
3. **Hostinger hPanel** — `hpanel.hostinger.com`. Billing, reboot, OS reinstall. Exposes SSH creds + browser terminal, so it grants server access too. The user only.

## Managing a VPS via an agent

For multi-step or exploratory work, **SSH into the box first and launch the agent ON the VPS** (e.g. `codex --yolo`), then talk to that local-on-server agent — it has full filesystem/process context and avoids fragile SSH round-trips. For short command sequences (update, config change, restart), driving an existing SSH session directly (e.g. via a cmux pane) is fine.

When checking on a remote/on-box agent, send the user one concise status line each time: what it is doing and whether it is on track.

Claude Code cmux note: after Claude finishes, it may prefill a predicted next user message; that draft is Claude, not the user speaking.

## Agents on servers

- **OpenClaw** → the OpenClaw server (managed via Dokploy).
- **Hermes** → the Hermes server (Discord gateway). Setup/config docs in the Hermes documentation folder.
- **n8n** → the n8n server.

## Hermes ops (on the Hermes server)

```bash
hermes --version            # shows version + commits behind
hermes update               # auto-snapshots, updates deps, rebuilds web UI, restarts gateway itself
hermes gateway status|restart
journalctl --user -u hermes-gateway --since '5 min ago' --no-pager   # gateway logs (systemd USER service)
```

- **Default model** lives in `~/.hermes/config.yaml` under `model.provider` + `model.default` — NOT in `.env`. Change via `hermes model` (interactive) or edit the yaml directly, then `hermes gateway restart` to propagate to gateways.
- npm `EBADENGINE` warnings during update (deps want Node >=24, box runs v22) are non-blocking — do not "fix" them.
- Deeper docs (Discord/Slack/WhatsApp setup, file structure, vision config): the Hermes documentation folder.
