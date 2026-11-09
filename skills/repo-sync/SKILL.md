---
name: repo-sync
description: Manage automatic Git syncing on macOS with repo-sync. Use only when the user explicitly invokes /repo-sync.
disable-model-invocation: true
---

# repo-sync

## What it does

Sync shared Git repos for team documents, notes, skills, and context on macOS. Complex software projects and pull request workflows are outside scope.

By default, after 60 seconds without local edits, repo-sync commits eligible non-ignored changes (including staged edits, renames, and deletions), rebases, and pushes. It checks remote changes every 60 seconds and starts at login without an AI agent.

Only the remote's default branch syncs (`origin/HEAD`, falling back to `main`). Feature branches and detached HEAD are skipped; branches are never switched.

## Check first

```sh
command -v repo-sync
repo-sync help
```

Installed help is the command contract. Older binaries may lack `skill`, `remove`, `status`, or `version`; run `repo-sync version` when listed. Installing the skill does not install or upgrade the binary.

Default config: `~/Library/Application Support/repo-sync/config.json`. Check `ProgramArguments` in `~/Library/LaunchAgents/com.vectal-labs.repo-sync.plist` for a custom path and use the selected config throughout. Flags precede positional arguments.

Read [references/operations.md](references/operations.md) for custom settings, unsupported commands, legacy removal, upgrades, or failed checks.

## Start syncing

A request to sync a named repo authorizes automatic commits and pushes. Mention that staged changes are included; do not ask again when already authorized.

For a fresh installation:

```sh
brew install --cask vectal-labs/tap/repo-sync
repo-sync setup
repo-sync status
```

Homebrew must already be available; it installs Git and GitHub CLI. Setup checks identity/access and service health, and preserves existing registrations. Select only requested repos.

For an existing local clone:

```sh
repo-sync add "/absolute/path/to/notes"
repo-sync status
```

`add` defaults to the current repo, which needs an `origin` remote. When asked to clone a remote repo, check the destination, clone, then add it. Do not overwrite folders, create remote repos, or change remotes without authorization.

For a custom config:

```sh
repo-sync add --config "/absolute/path/to/config.json" "/absolute/path/to/notes"
repo-sync status --config "/absolute/path/to/config.json"
```

`add` may save registration despite restart failure. Check fresh status; if setup is needed, use the same config. Report registration separately from active syncing when readiness fails.

## Stop syncing one repo

When installed help lists `remove`:

```sh
repo-sync remove "/absolute/path/to/notes"
repo-sync status
```

```sh
repo-sync remove --config "/absolute/path/to/config.json" "/absolute/path/to/notes"
repo-sync status --config "/absolute/path/to/config.json"
```

`remove` defaults to the current repo. For missing or moved folders, use the old configured absolute path.

Removal unregisters the repo and restarts the matching service. Files, history, local work, and pushed data remain; teammates' syncing is unaffected. In-progress Git operations may finish during shutdown.

Verify registration is absent and the service applied the change. Removing the last repo leaves an empty running service. With no background service, only config changes; manually started `repo-sync run` processes still need restarting.

Without `remove`, follow **Legacy removal** in the reference. Do not uninstall or delete the clone instead.

## Install or maintain this skill

When help lists `skill`, use `repo-sync skill install`, then `repo-sync skill status`. The binary bundles the skill and references; no checkout or download is needed. Setup also offers installation. Start a new agent session afterward.

Homebrew upgrades refresh unchanged managed copies. After Go upgrades, rerun setup or `repo-sync skill refresh`. `repo-sync skill uninstall` removes unchanged managed copies, preserving customized folders, the program, and syncing service. See **Agent skill installation** in the reference for destinations and conflicts.

## Uninstall everything

Run `repo-sync uninstall` only on request. After confirmation, it removes the service, settings, logs, cache, program, and unchanged managed skills. Customized skills, repositories, Git history, and shared Git credentials remain. `--keep-binary` retains the program; `--yes` skips the prompt when already authorized.

## Safety and verification

- Filename protection blocks names such as `.env`, private keys, and `.npmrc`, but does not scan contents; ordinary filenames can hide secrets. Normal syncing can unstage blocked files.
- Use `repo-sync allow` only when publishing that file is explicitly authorized.
- Conflicts preserve local commits, abort repo-sync's own rebase, and retry. No automatic conflict resolution or force-push; one failing repo does not block others.
- Do not reset history, switch branches, delete lock files, or override secret protection just to clear an error.
- There is no `pause`, `resume`, or `sync now` command. Check help before using any command.
- Check exit codes and fresh status; a running service can still have repo failures. Do not create verification commits or push test files without authorization.
- Briefly report the repo, action, verification, and remaining failures.
