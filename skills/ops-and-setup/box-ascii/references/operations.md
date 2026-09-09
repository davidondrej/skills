# Operations and observations

Official docs were checked through DeepAPI on 2026-09-09. Treat the HTTP/CLI examples below as documented behavior; the final section records local test evidence. Recheck current docs when an operation differs. Read only the sections relevant to the task.

## Direct HTTP operations

All paths are relative to `https://ascii.dev/api/box/v1` and require bearer authentication.

- Inspect: `GET /me`, `GET /limits`, `GET /boxes`, `GET /boxes/{id}`.
- Create: `POST /boxes`, for example `{"ttlSeconds":7200,"noEnv":true}` for an isolated two-hour test. This provisions billable compute; size and TTL must fit the task and account limits.
- Stop: `POST /boxes/{id}/stop`. Resume: `POST /boxes/{id}/resume`. Fork: `POST /boxes/{id}/fork`.
- Change auto-stop: `PATCH /boxes/{id}` with `{"ttlSeconds":null}` to disable it where the account permits. Do not disable it incidentally during unrelated setup.
- Register SSH access: `POST /boxes/{id}/sshkey` with `{"key":"<public-key>"}`. Send only the public key.
- Run a command: `POST /boxes/{id}/commands` with `command`, optional `cwd`, and `timeoutSeconds`. Poll Box readiness first.
- Files: `GET /boxes/{id}/files` and `PUT /boxes/{id}/files`. Check the endpoint schema for path/content fields instead of guessing.
- Environments: `GET/POST /environments`, `PUT /environments/{environmentId}`; update fields include `name`, `isDefault`, `safeForThirdParties`, `passGithub`, `passSecrets`, `passBoxCredentials`, `passAgentsCredentials`, `envContents`, and `secretFiles`.
- Upgrade selected Boxes: `POST /environments/{environmentId}/upgrade` with `{"agentIds":["<box-id>"]}`. The field is **`agentIds`, not `boxIds`**. Omitting the list upgrades all eligible Boxes; it is not a single-Box default. Check both `upgraded` and `failed` counts, then verify the target's version.
- GitHub: `GET /repos` discovers available repositories; `POST /repos` selects a `repositoryId` and `baseBranch` for the default environment. For a named environment prefer `box env add-repo <name> owner/repo`, or verify the named-environment schema.
- Secrets: `POST /secrets` updates the default environment. It **replaces the entire collection**, not one key. Preserve all required variables/files. Prefer the granular endpoints below; they avoid rewriting other items or losing concurrent edits through a stale full collection.
- Template: `POST /named-snapshots` with `{"boxId":"<id>","name":"agent-stack"}`; create from it with `POST /boxes` and `{"from":"agent-stack","environment":"dev"}`.

Read the endpoint's current schema in the [API reference](https://docs.ascii.dev/box/api/v1#endpoint-reference) before adding fields. Do not invent a generic API route from a dashboard URL.

## Change one secret safely

- Set one variable: `PUT /environments/{environmentId}/vars/{key}` with `{"value":"<secret>"}`.
- Set one file: `PUT /environments/{environmentId}/secret-files` with `{"path":"repository/.env","contents":"<file-content>"}`. The CLI equivalent `box env set-file <name> repository/.env --from ./private/project.env` reads the file instead of exposing its contents in arguments.
- Construct request bodies in memory from an already loaded process variable or approved local secret file. Never interpolate secret values into the command text or print the request/response body.
- These endpoints return `success`, `versionId`, and `versionNumber`. `versionId` is not the environment ID; retain the original environment ID for later operations.
- Re-read the latest version before upgrading selected Boxes. An upgrade targets the latest version, so resolve unexpected concurrent edits before rolling it out. There is no revision precondition established by the schemas checked here.

Sources: [one variable](https://docs.ascii.dev/box/api/reference/environments/set-environment-var), [one secret file](https://docs.ascii.dev/box/api/reference/environments/set-environment-secret-file), [targeted upgrade](https://docs.ascii.dev/box/api/reference/environments/upgrade-box-environment).

## Requests, retries, and long work

- Check HTTP status plus the endpoint's success fields. Core Box endpoints use `ok`; environment changes/upgrades document `success` instead, despite the API overview's general envelope description. On errors, retain only useful fields such as `code`, `message`, and `requestId`; redact secrets and token-bearing URLs before sharing.
- Create and fork accept `Idempotency-Key`. Persist one UUID with the exact request body before calling; reuse both after a timeout. The documented deduplication window is 24 hours.
- `409 idempotency_in_progress`: retry the same request after waiting. `409 idempotency_key_reused`: the body changed; inspect prior state rather than blindly allocating another machine.
- Poll `GET /boxes/{id}` until `ready` or `idle` before commands. A creation/stop response is not proof that provisioning/snapshotting finished. Treat `error` as failure, not another readiness poll.
- `401`: check the intended key/account. `402`: inspect billing/plan prerequisites. `403`: inspect account, organization, or machine-size restrictions. `429`: back off and inspect limits. Retry transport/5xx failures only when the operation is safe to repeat.
- Stop snapshots and archives; it is not permanent deletion. For permanent deletion, consult the documented confirmation header and background deletion operation, then verify completion under the user's authorized scope.
- Default auto-stop is one hour from creation/resume, not an activity-based idle timer. A fork does not inherit its source's TTL; set it explicitly. Trial restrictions can prevent disabling or extending it.
- Synchronous commands are documented up to 600 seconds. For longer work, use `detached: true`, then `GET /boxes/{id}/commands/{processId}`; inspect completion and exit status. Use a service for work that must restart after restore.
- Box `idle`/`running` tracks its prompt API. An agent launched over SSH or the command API can be busy while Box reports `idle`. Stop decisions must use the agent's own task state.
- The prompt API documents `codex` and `claude-code`. A preinstalled harness is not necessarily supported by that API. Run BB or other harnesses through their own process/service and interfaces.
- Native PowerShell pipelines can keep stdin open and hang command workflows. Use Python, WSL, or another documented path when reproducing that issue.

Sources: [API](https://docs.ascii.dev/box/api/v1), [CLI](https://docs.ascii.dev/box/cli-reference), [long-running tasks](https://docs.ascii.dev/box/long-running-tasks), [setup](https://docs.ascii.dev/box/setup).

## SSH, BB, and Codex

The hosted image uses SSH user `user`, home `/home/user`. Discover the current address from the Box record; do not keep a previous IP after resume without checking it.

1. Register a dedicated public key through the API. Keep its private half local with restricted permissions.
2. Verify the host key through a trusted channel. Our tests retrieved public SSH host-key material through the authenticated command API before using a dedicated known-hosts file. Do not disable host-key checking to get past a mismatch.
3. Inspect installed tools and versions. Use the bb-cli skill and current BB enrollment instructions to install/enroll the correct worker or server. Keep enrollment credentials out of logs.
4. For an authorized personal setup, transfer only the required Codex login and GitHub credentials over SSH/SCP. Codex's file is `~/.codex/auth.json`; restrict the destination to the intended user. Verify login works instead of assuming copied OAuth credentials stay valid indefinitely.
5. Prepare the intended repository, branch, context, and dependencies. Check Git access and the actual commit. If BB creates a worktree, verify that worktree's dependencies too.
6. Run the agent through BB, then check the conversation, diff, and continued task. Box's prompt API does not establish BB conversation continuity.

A laptop-to-cloud tunnel does not prove independence from the laptop. If the BB controller or required tunnel runs locally, closing the laptop can still break control. Use the project's accepted deployment design and test the actual disconnection path.

## Snapshot and recovery boundaries

- Snapshots restore files and supported system changes, not process memory. Treat resume as a reboot. Manually started agents must be restarted and their saved sessions reopened.
- Documented capture includes `/home/user`, Docker named volumes, and changes under `/etc`, `/usr`, `/opt`, `/root`, `/srv`, cron tables, and the package database. Enabled systemd services restart; machine identity and SSH host keys are not captured.
- Docker build cache and unused images do not have the same persistence guarantee as named volumes. Do not assume all of `/var/lib/docker` is restored.
- Template deploys choose the requested/default environment rather than the source's named environment. Per-Box `env` values can still carry from the source.
- `noEnv` scrubs Box-managed credential locations, not every possible credential or private file. Protection does not turn an arbitrary personal snapshot into a safe shared image.
- Restore may become usable before background hydration finishes. Measure readiness for actual agent work, not just the API response or vendor startup claim.
- A named snapshot is a fixed starting point, not an independent off-provider backup. Verify exports/restoration before promising recovery or retention; published retention terms have conflicted with product docs.

Sources: [snapshots](https://docs.ascii.dev/box/snapshots), [environments](https://docs.ascii.dev/box/environments), [terms](https://box.ascii.dev/terms).

## What we actually observed

Manual integration tests on 2026-09-09 established the observations below. Keep detailed transcripts, live machine identifiers, and account details in the owning project's private records.

- The tests used Python `urllib.request` with `BOX_API_KEY` and bearer headers. No Box-specific skill, installed SDK, or Box CLI was required for those requests.
- Authenticated account/limit/Box reads worked. A small temporary Python client also created a Box with `noEnv: true`, registered an SSH key, and called the command endpoint.
- SSH/SCP handled BB installation and credential transfer. BB's remote worker ran Codex using the existing ChatGPT subscription, cloned a GitHub project, created a worktree, and completed a harmless coding test with diff review, local commit, and conversation continuation.
- One worktree setup took 66 seconds, including 63 seconds installing dependencies. This was one observation, not a latency guarantee. It motivates preparing dependencies in templates and measuring useful-work startup.
- These tests establish the manual integration path. They do not by themselves establish automatic provisioning for every new thread, uninterrupted work after laptop disconnection, restart of the same conversation after stop/resume, or isolation under concurrent users. Verify each in the actual deployment before claiming it works.
