# Operations and troubleshooting

## Inspect service and configuration

```sh
repo-sync status
/usr/bin/plutil -extract ProgramArguments json -o - "$HOME/Library/LaunchAgents/com.vectal-labs.repo-sync.plist"
```

Use `--config "/absolute/path/to/config.json"` for the path selected in the plist. A missing plist means no standard installation was found. Do not assume another config controls the running service.

Status checks readiness and repository health without committing or pushing. Newer binaries also report installed/running versions and cached update information. A nonzero exit may describe a repo failure, stale settings, version mismatch, or update failure. Read the reason.

Logs are in `~/Library/Logs/repo-sync/`. Read only what the task needs. Redact credentials and private content before reporting output. Runtime status lives in `~/Library/Caches/repo-sync/`; do not edit it to make checks pass.

The config contains:

- `idle_debounce`: positive duration string; default `"1m"`.
- `fetch_interval`: positive duration string; default `"1m"`.
- `repositories`: entries with unique `name`, absolute `path`, `remote`, and optional `allow` patterns.

For authorized setting changes, resolve config symlinks, preserve unrelated fields, and write atomically. Recheck the original contents immediately before writing; do not overwrite concurrent edits. The daemon reads settings at startup. Apply changes with `repo-sync setup --config "/absolute/path/to/config.json"`, then verify status with that config. For removing repos, prefer `remove` and use the legacy procedure below only when unavailable.

## Legacy removal

Use this only if installed help lacks `remove`. An available upgrade may add the command, but never assume it does. Installing the skill alone does not change CLI capabilities.

1. Find the exact registration and installed config using the plist. Match the configured absolute repo path, resolving symlinks when possible. For a missing folder, use its recorded path. If no registration matches, make no changes.
2. Inspect the service and record its PID before stopping it:

   ```sh
   /bin/launchctl print "gui/$(id -u)/com.vectal-labs.repo-sync"
   ```

   Treat only an explicit missing-service response as absent. For other inspection errors, stop and report the error. Verify the installed service uses the config being edited. If it uses another config, resolve that mismatch before proceeding.
3. If loaded, stop it gracefully:

   ```sh
   /bin/launchctl bootout "gui/$(id -u)/com.vectal-labs.repo-sync"
   ```

   Verify that the service is absent and its recorded PID has exited. Wait up to 45 seconds; a Git operation may finish during that time. If shutdown cannot be verified, leave the config unchanged and report the failure. Do not force-kill processes.
4. Remove only the requested entry from `repositories`. Preserve other settings, file permissions, and any config symlink. Use an atomic write to the resolved target, checking for concurrent changes first. Never delete the clone, `.git`, its remote, or unrelated registrations. If saving fails after shutdown, report that the service is stopped and the removal was not saved.
5. If the service was loaded and other registrations remain, restart the same plist:

   ```sh
   /bin/launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.vectal-labs.repo-sync.plist"
   ```

   Verify `repo-sync status` with the same config. If the binary lacks `status`, verify a fresh service PID and fresh startup logs showing the expected repositories; clearly state that this older binary lacks the normal health check.
6. If no registrations remain, keep the service unloaded. Re-read the saved config and verify service absence again after saving. If an updater restarted it, recheck its config and stop it gracefully again before claiming completion. Older daemons cannot report readiness when empty, and older `setup` exits without restarting an empty configuration. Keep settings and the plist so the user can add repos later.
7. If the service was absent, report only removal from the config. Any foreground `repo-sync run` process must be stopped by its owner or restarted within explicit authorization. Do not claim all syncing stopped from a config edit alone.

If restart or verification fails, report that the removal was saved and remaining repos may not be syncing. Do not silently restore the removed registration. These steps affect only this Mac.

## Common failures

- **Identity or authentication:** follow the named CLI failure. Use existing identity and credentials. Setup checks fetch and dry-run push access; real server hooks or branch protection can still reject a later push.
- **Feature branch or detached HEAD:** report the skipped branch. Do not switch branches automatically.
- **Conflict:** repo-sync keeps local commits and aborts its own failed rebase. Resolve the conflict only when authorized.
- **Missing folder:** the registration stays; other repos continue. Returning the folder triggers recovery. Remove its registration when the user wants permanent un-syncing.
- **Offline:** automatic retries continue without offline notifications.
- **Other failures:** retries start at 1 minute and double up to 30 minutes. Persistent failures notify after 10 minutes.
- **Blocked files or held pushes:** inspect named paths and unpublished commits without revealing secret contents. repo-sync does not rewrite those commits for you.

Inside the relevant repo, `repo-sync allow "relative/path"` overrides filename protection for an explicitly approved file. Recheck readiness afterward because older `allow` commands can save settings despite a failed restart.

## Updates and unsupported commands

Check installed help first. Newer releases support:

```sh
repo-sync version
repo-sync update
repo-sync updates off
repo-sync updates on
```

`update` checks and upgrades a Homebrew installation. `updates off` disables automatic installation while keeping update notifications. Change this preference only when requested.

For older Homebrew installs, an authorized upgrade uses `brew upgrade --cask repo-sync`. For Go installs, update the binary through the original installation method, then rerun setup. After an upgrade, check help, version when available, and service status. If the needed command is still absent, explain the installed release's limitation.

## Sources

- [Repository and installation](https://github.com/vectal-labs/repo-sync)
- [Detailed behavior](https://github.com/vectal-labs/repo-sync/blob/main/docs/behavior.md)

These pages may describe a newer release. Installed help takes precedence for available commands.
