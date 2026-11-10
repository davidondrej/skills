---
name: boat
description: Manage Boat (boat.dev, formerly Box by Ascii) cloud sandboxes via API, CLI, and SSH. Use for provisioning, environments, secrets, templates, snapshots, stop/resume/fork, or running BB and coding agents on Boat.
---

# Boat

Manage machines through the API or CLI; use SSH or the command API inside a VM. Before direct API calls, credential changes, or recovery, read [operations and observations](references/operations.md), including its authentication example.

## Box to Boat migration

Use `boat`, `https://boat.dev/api/v1`, `/sandboxes`, and `BOAT_API_KEY` for current examples. Docs live at `https://docs.boat.dev`. Existing projects may still use Box names; inspect their configuration before migrating. Renaming this skill does not authorize changing installed tools, deployed applications, or credentials. See [migration notes](references/operations.md#box-to-boat-migration).

## Identify the account and target

1. Read project instructions and operational notes. Verify the account, organization, sandbox, and repository; reuse existing mappings instead of provisioning duplicates.
2. Load `BOAT_API_KEY` from the environment or the project's documented, gitignored credentials file. Do not assume a universal path, search unrelated credential stores, or print credentials. Use the secrets skill for a new key.
3. Check authentication and state with `GET /me`, `/limits`, and `/sandboxes`, or CLI `boat status`, `boat list`, and relevant `--help`. Filter output to needed fields.
4. Check installed tools. API calls need no Boat CLI or SDK. If installation is needed, read official instructions; never execute a remote installer blindly.

Use DeepAPI to check current Boat docs for uncertain behavior or fields. Check prices, limits, model catalogs, and installation commands live. Documentation does not prove an authenticated operation succeeded.

## Local CLI

Use `command -v boat` to locate the current CLI. Older installations may only have `box`; the skill rename does not upgrade the binary or migrate credentials. Prefer the CLI for manual management/debugging; application code can use the API.

Set `BOAT_ID` to the verified target before running:

```bash
command -v boat
boat --no-update --version
boat --no-update --json status
boat --no-update --json list --all
boat --no-update --json info "$BOAT_ID"
boat --no-update ssh "$BOAT_ID"
```

Use `boat <command> --help` for options. `--json` gives structured output; `--no-update` skips update checks. Run `boat self-update` only when updating is intended.

Installation does not sign in. If signed out, send an existing approved project token through stdin to `boat login --key-stdin`, never through arguments. Browser `boat login` uses the account's existing sign-in method; get approval before opening it.

## API access

- Base: `https://boat.dev/api/v1`; bearer header: `Authorization: Bearer $BOAT_API_KEY`. JSON bodies use `Content-Type: application/json`.
- Account-wide operations require an account key; machine-scoped keys cover only their sandbox.
- Creating scoped keys requires browser sign-in or an admin-scoped token; rotating and revoking remain session-gated. Read [API keys](https://docs.boat.dev/api-keys) before credential changes.
- Do not assume provider onboarding has an API. Boat-managed provider login uses the Agents page; injecting existing agent credentials is a separate environment setting.

## Preserve the user's scope

- Write a focused assignment preserving intent, constraints, and corrections. Never invent requirements, deliverables, permissions, or approval.
- Model, machine, repository, and thread placement guide the launcher. Give each worker only its task and necessary context.
- Before sending, remove copied conversation, launcher instructions, and unrelated assignments. Never prepend the full user prompt; quote exact wording only when explicitly requested.

## Environments and templates

**Environments** hold repositories, secrets, and credential permissions. **Named snapshots/templates** hold installed tools and disk state. Combine them for repeatable startup.

Check the target and existing contents before changes:

```bash
boat env list
boat env new dev
boat env add-repo dev owner/repository --branch main
boat env set-file dev repository/.env --from ./private/project.env
boat env set dev --github true --secrets true --sandbox-credentials false --agents-credentials true
boat new --environment dev
```

- Boat clones configured branches; it does not create working branches. Let BB or the coding workflow manage branches/worktrees.
- Clones land at `/home/user/<repository-name>`. Secret file paths are relative to `/home/user`; include the repository folder for a clone's `.env`.
- `--environment dev` selects an existing named environment. Per-sandbox `--env KEY=value` overrides its value; never put real secrets in CLI arguments.
- Without selection, new sandboxes/template deploys use the default environment. Ordinary resume and fork preserve the existing/source environment version.
- Saving creates a version; existing sandboxes do not receive it automatically, even on ordinary resume. Inspect `boat info` before deliberately upgrading.
- `boat env upgrade dev` can affect many sandboxes. For one sandbox, use the API's explicit `agentIds` selection (sandbox IDs). Upgrades delete withheld secrets; re-pinning an older version does not restore deleted files.
- Shared environment edits affect future sandboxes even when only one existing sandbox is upgraded. Use sandbox-specific configuration for single-sandbox exceptions.
- Restart applications that read injected variables only at startup. Verify the running application, not just a new SSH shell.

Preinstall BB, runtimes, and dependencies in a clean template. Keep credentials in environments or inject them for the intended user after boot. Set `BOAT_ID` to the verified prepared sandbox:

```bash
boat snapshot "$BOAT_ID" agent-stack
boat new --from agent-stack --environment dev
```

Verify snapshot readiness before deployment. Re-saving a name changes future deploys, not existing machines. Still validate fresh repository state and dependency installation.

## Isolation and credentials

- Personal sandboxes should receive only required credentials/repos. For other users, select an environment with `safeForThirdParties: true` or create the sandbox with `noEnv: true`.
- Protected mode withholds the owner's managed GitHub, secrets, sandbox, and agent credentials regardless of section toggles. Explicit per-sandbox `env` values still pass through and carry into forks/template deploys unless replaced.
- Protected mode does not sanitize arbitrary disk contents. Manually added cloud, package-manager, and Docker logins may remain. Never build a shared template from a credential-filled personal machine.
- Conversion to protected mode is one-way and scrubs managed credential files, including Codex/Claude logins added by the sandbox's own user. Check ownership and recovery needs before converting an existing sandbox.
- Keep keys, auth files, enrollment codes, desktop URLs, and raw API/session logs out of prompts, commits, and user-visible output. Desktop URLs may contain access tokens.

## Verify the outcome

Inspect the changed sandbox and verify inside it. Check file presence/permissions without printing secrets. For agent setup, run a harmless task and verify the intended account, repository, output, and continued conversation.

Report the sandbox/environment ID, changes, checks that passed, and real limitations. An accepted API request, SSH-ready machine, or snapshot does not prove a working agent session.

## Official references

- [API and endpoint index](https://docs.boat.dev/api/v1)
- [CLI reference](https://docs.boat.dev/cli-reference)
- [Environments](https://docs.boat.dev/environments)
- [Setup and scripts](https://docs.boat.dev/setup)
- [Snapshots and templates](https://docs.boat.dev/snapshots)
- [Platform guide](https://docs.boat.dev/platform-guide)
