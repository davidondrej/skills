---
name: repo-sync
description: Manage repo-sync on macOS for shared documents and team context. Use when asked what repo-sync does, to automatically sync a repo, add a repo to repo-sync, stop syncing or un-sync a repo, check sync health, configure repo-sync, or uninstall it. Ordinary one-time Git pulls and pushes do not need this skill.
---

# repo-sync

## What it does

repo-sync keeps shared Git repos in sync on macOS. It is for team documents, notes, skills, and context. Complex software projects and pull request workflows are outside its intended scope.

By default, after 60 seconds without local edits, it commits eligible non-ignored changes, rebases on the remote, and pushes. This includes staged edits, renames, and deletions. It checks remote changes every 60 seconds, starts at login, and runs without an AI agent.

Only the remote's default branch syncs (`origin/HEAD`, with `main` as fallback). Feature branches and detached HEAD are skipped. It never switches branches.

## Check first

```sh
command -v repo-sync
repo-sync help
```

Use the installed help as the command contract. Older binaries may lack `remove`, `status`, or `version`. Run `repo-sync version` when listed. Installing this skill does not install or upgrade the binary.

The default config is `~/Library/Application Support/repo-sync/config.json`. Check the installed service's `ProgramArguments` in `~/Library/LaunchAgents/com.vectal-labs.repo-sync.plist` for a custom path. Use that config throughout. Put flags before positional arguments.

Read [references/operations.md](references/operations.md) for custom settings, unsupported commands, legacy removal, upgrades, or failed checks.

## Start syncing

A request to sync a named repo authorizes its automatic commits and pushes. Briefly explain that staged changes are included. Use existing authorization without asking again.

For a fresh installation:

```sh
brew install --cask vectal-labs/tap/repo-sync
repo-sync setup
repo-sync status
```

Homebrew installs Git and GitHub CLI. Setup checks Git identity and access, lets you choose repos, and verifies the service. Select only repos within the request. Repeating setup keeps existing registrations. Homebrew itself must already be available.

For an existing local clone:

```sh
repo-sync add "/absolute/path/to/notes"
repo-sync status
```

`add` without a path uses the current repo. The clone needs an `origin` remote. If the request names a remote repo and asks for a local clone, check the destination, clone it there, then add it. Do not overwrite folders, create remote repositories, or change remotes unless authorized.

For a custom config:

```sh
repo-sync add --config "/absolute/path/to/config.json" "/absolute/path/to/notes"
repo-sync status --config "/absolute/path/to/config.json"
```

`add` can save a registration even when the service restart fails. Verify fresh status. If setup is needed, run it with the same config. Report registration and active syncing separately when readiness fails.

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

Without a path, `remove` uses the current repo. For a missing or moved folder, use its old configured absolute path.

Removal unregisters the repo and restarts the matching installed service. Files, Git history, and local work remain. A Git operation already in progress may finish during shutdown. Removal does not erase anything already pushed or stop syncing on teammates' machines.

Verify that the registration is absent and the service applied the change. Removing the last repo leaves the service running with no repos. If no background service is running, removal only updates the config; manually started `repo-sync run` processes still need restarting.

If help lacks `remove`, follow **Legacy removal** in the reference. Do not substitute uninstall or delete the clone.

## Uninstall everything

Use `repo-sync uninstall` only when the user requests uninstalling repo-sync. It removes the service, settings, logs, cache, and program after confirmation. Repositories, Git history, and shared Git credentials remain. `--keep-binary` keeps the program; `--yes` skips the CLI prompt when already authorized.

## Safety and verification

- Secrets are blocked by filename, including `.env`, private keys, and `.npmrc`. Contents are not scanned; ordinary filenames can still contain secrets. Blocked staged files can be unstaged by normal syncing.
- Use `repo-sync allow` only when publishing that file is explicitly authorized.
- Conflicts keep local commits, abort repo-sync's own rebase, and retry. There is no automatic conflict resolution or force-push. One failing repo does not block the others.
- Do not reset history, switch branches, delete lock files, or override secret protection just to clear an error.
- There is no `pause`, `resume`, or `sync now` command. Check help before using any command.
- Check exit codes and fresh status. A running service can still have repo failures. Do not create verification commits or push test files into the user's repos without authorization.
- Report the repo, action, verification result, and any remaining failure in a few short sentences.
