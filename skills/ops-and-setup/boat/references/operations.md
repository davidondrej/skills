# Operations and observations

Boat naming and API migration details were checked through DeepAPI on 2026-09-17. Operational guidance was originally checked on 2026-09-09; historical tests below remain Box-era evidence. Treat the HTTP/CLI examples below as documented behavior; the final section records local test evidence. Recheck current docs when an operation differs. Read only the sections relevant to the task.

## Box to Boat migration

- Ascii Box became Boat on September 16, 2026. The founder says legacy names/endpoints/CLI must migrate by October 31, 2026; verify current migration guidance before relying on compatibility. [Announcement](https://x.com/AniC_dev/status/2100294739413078038), [migration deadline](https://x.com/AniC_dev/status/2100294743200547123).
- Current CLI: `boat`. API base: `https://boat.dev/api/v1`. Resource routes: `/sandboxes`; API response types use `sandbox.*`. Environment examples use `BOAT_API_KEY` and `BOAT_ID`. [API](https://docs.boat.dev/api/v1), [CLI](https://docs.boat.dev/cli-reference).
- Environment credentials use `passSandboxCredentials` / `--sandbox-credentials`. Named snapshot creation takes `sandboxId`. Targeted environment upgrades still take `agentIds`; do not rename that field. [Environments](https://docs.boat.dev/environments), [snapshots](https://docs.boat.dev/api/reference/snapshots/save-named-snapshot), [upgrade](https://docs.boat.dev/api/reference/environments/upgrade-sandbox-environment).
- Published SDKs are `@boatdev/sdk` and `boat-sdk`. Do not infer that every integration package changed names. [SDK index](https://docs.boat.dev/sdks/overview).
- Keep legacy credential names only where an existing project explicitly uses them. Never rewrite token contents or assume a new key is required just because the product renamed. Verify authentication against the intended account. These doc checks did not retest live VMs or migrate local CLI state.

## Contents

- [Authentication check](#authentication-check)
- [Direct HTTP operations](#direct-http-operations)
- [Change one secret safely](#change-one-secret-safely)
- [Requests, retries, and long work](#requests-retries-and-long-work)
- [SSH, BB, and Codex](#ssh-bb-and-codex)
- [Snapshot and recovery boundaries](#snapshot-and-recovery-boundaries)
- [What we actually observed](#what-we-actually-observed)

## Authentication check

Load `BOAT_API_KEY` into the process environment first. This read-only example prints status, not account details or credentials.

```python
import json
import os
import urllib.error
import urllib.request

request = urllib.request.Request(
    "https://boat.dev/api/v1/me",
    headers={"Authorization": "Bearer " + os.environ["BOAT_API_KEY"]},
)
try:
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.load(response)
        print({"status": response.status, "ok": data.get("ok")})
except urllib.error.HTTPError as error:
    print({"status": error.code})
    raise SystemExit(1)
```

Python's standard library worked in local tests. Use an official TypeScript/Python SDK when the application benefits from typed clients; do not add a client abstraction for a few requests.

## Direct HTTP operations

All paths are relative to `https://boat.dev/api/v1` and require bearer authentication.

- Inspect: `GET /me`, `GET /limits`, `GET /sandboxes`, `GET /sandboxes/{id}`.
- Create: `POST /sandboxes`, for example `{"ttlSeconds":7200,"noEnv":true}` for an isolated two-hour test. This provisions billable compute; size and TTL must fit the task and account limits.
- Stop: `POST /sandboxes/{id}/stop`. Resume: `POST /sandboxes/{id}/resume`. Fork: `POST /sandboxes/{id}/fork`.
- Change auto-stop: `PATCH /sandboxes/{id}` with `{"ttlSeconds":null}` to disable it where the account permits. Do not disable it incidentally during unrelated setup.
- Register SSH access: `POST /sandboxes/{id}/sshkey` with `{"key":"<public-key>"}`. Send only the public key.
- Run a command: `POST /sandboxes/{id}/commands` with `command`, optional `cwd`, and `timeoutSeconds`. Poll sandbox readiness first.
- Files: `GET /sandboxes/{id}/files` and `PUT /sandboxes/{id}/files`. Check the endpoint schema for path/content fields instead of guessing.
- Environments: `GET/POST /environments`, `PUT /environments/{environmentId}`; update fields include `name`, `isDefault`, `safeForThirdParties`, `passGithub`, `passSecrets`, `passSandboxCredentials`, `passAgentsCredentials`, `envContents`, and `secretFiles`.
- Upgrade selected sandboxes: `POST /environments/{environmentId}/upgrade` with `{"agentIds":["<sandbox-id>"]}`. The field is **`agentIds`, not `sandboxIds`**. Omitting the list upgrades all eligible sandboxes; it is not a single-sandbox default. Check both `upgraded` and `failed` counts, then verify the target's version.
- GitHub: `GET /repos` discovers available repositories; `POST /repos` selects a `repositoryId` and `baseBranch` for the default environment. For a named environment prefer `boat env add-repo <name> owner/repo`, or verify the named-environment schema.
- Secrets: `POST /secrets` updates the default environment. It **replaces the entire collection**, not one key. Preserve all required variables/files. Prefer the granular endpoints below; they avoid rewriting other items or losing concurrent edits through a stale full collection.
- Template: `POST /named-snapshots` with `{"sandboxId":"<id>","name":"agent-stack"}`; create from it with `POST /sandboxes` and `{"from":"agent-stack","environment":"dev"}`.

Read the endpoint's current schema in the [API reference](https://docs.boat.dev/api/v1#endpoint-reference) before adding fields. Do not invent a generic API route from a dashboard URL.

## Change one secret safely

- Set one variable: `PUT /environments/{environmentId}/vars/{key}` with `{"value":"<secret>"}`.
- Set one file: `PUT /environments/{environmentId}/secret-files` with `{"path":"repository/.env","contents":"<file-content>"}`. The CLI equivalent `boat env set-file <name> repository/.env --from ./private/project.env` reads the file instead of exposing its contents in arguments.
- Construct request bodies in memory from an already loaded process variable or approved local secret file. Never interpolate secret values into the command text or print the request/response body.
- These endpoints return `success`, `versionId`, and `versionNumber`. `versionId` is not the environment ID; retain the original environment ID for later operations.
- Re-read the latest version before upgrading selected sandboxes. An upgrade targets the latest version, so resolve unexpected concurrent edits before rolling it out. There is no revision precondition established by the schemas checked here.

Sources: [one variable](https://docs.boat.dev/api/reference/environments/set-environment-var), [one secret file](https://docs.boat.dev/api/reference/environments/set-environment-secret-file), [targeted upgrade](https://docs.boat.dev/api/reference/environments/upgrade-sandbox-environment).

## Requests, retries, and long work

- Check HTTP status plus the endpoint's success fields. Core sandbox endpoints use `ok`; environment changes/upgrades document `success` instead, despite the API overview's general envelope description. On errors, retain only useful fields such as `code`, `message`, and `requestId`; redact secrets and token-bearing URLs before sharing.
- Create and fork accept `Idempotency-Key`. Persist one UUID with the exact request body before calling; reuse both after a timeout. The documented deduplication window is 24 hours.
- `409 idempotency_in_progress`: retry the same request after waiting. `409 idempotency_key_reused`: the body changed; inspect prior state rather than blindly allocating another machine.
- Poll `GET /sandboxes/{id}` until `ready` or `idle` before commands. A creation/stop response is not proof that provisioning/snapshotting finished. Treat `error` as failure, not another readiness poll.
- `401`: check the intended key/account. `402`: inspect billing/plan prerequisites. `403`: inspect account, organization, or machine-size restrictions. `429`: back off and inspect limits. Retry transport/5xx failures only when the operation is safe to repeat.
- Stop snapshots and archives; it is not permanent deletion. For permanent deletion, consult the documented confirmation header and background deletion operation, then verify completion under the user's authorized scope.
- Default auto-stop is one hour from creation/resume, not an activity-based idle timer. A fork does not inherit its source's TTL; set it explicitly. Trial restrictions can prevent disabling or extending it.
- Synchronous commands are documented up to 600 seconds. For longer work, use `detached: true`, then `GET /sandboxes/{id}/commands/{processId}`; inspect completion and exit status. Use a service for work that must restart after restore.
- Boat `idle`/`running` tracks its prompt API. An agent launched over SSH or the command API can be busy while Boat reports `idle`. Stop decisions must use the agent's own task state.
- The prompt API documents `codex` and `claude-code`. A preinstalled harness is not necessarily supported by that API. Run BB or other harnesses through their own process/service and interfaces.
- Native PowerShell pipelines can keep stdin open and hang command workflows. Use Python, WSL, or another documented path when reproducing that issue.

Sources: [API](https://docs.boat.dev/api/v1), [CLI](https://docs.boat.dev/cli-reference), [long-running tasks](https://docs.boat.dev/long-running-tasks), [setup](https://docs.boat.dev/setup).

## SSH, BB, and Codex

The hosted image uses SSH user `user`, home `/home/user`. Discover the current address from the sandbox record; do not keep a previous IP after resume without checking it.

1. Register a dedicated public key through the API. Keep its private half local with restricted permissions.
2. Verify the host key through a trusted channel. Our tests retrieved public SSH host-key material through the authenticated command API before using a dedicated known-hosts file. Do not disable host-key checking to get past a mismatch.
3. Inspect installed tools and versions. Use the bb-cli skill and current BB enrollment instructions to install/enroll the correct worker or server. Keep enrollment credentials out of logs.
4. For an authorized personal setup, transfer only the required Codex login and GitHub credentials over SSH/SCP. Codex's file is `~/.codex/auth.json`; restrict the destination to the intended user. Verify login works instead of assuming copied OAuth credentials stay valid indefinitely.
5. Prepare the intended repository, branch, context, and dependencies. Check Git access and the actual commit. If BB creates a worktree, verify that worktree's dependencies too.
6. Run the agent through BB, then check the conversation, diff, and continued task. Boat's prompt API does not establish BB conversation continuity.

A laptop-to-cloud tunnel does not prove independence from the laptop. If the BB controller or required tunnel runs locally, closing the laptop can still break control. Use the project's accepted deployment design and test the actual disconnection path.

## Snapshot and recovery boundaries

- Snapshots restore files and supported system changes, not process memory. Treat resume as a reboot. Manually started agents must be restarted and their saved sessions reopened.
- Documented capture includes `/home/user`, Docker named volumes, and changes under `/etc`, `/usr`, `/opt`, `/root`, `/srv`, cron tables, and the package database. Enabled systemd services restart; machine identity and SSH host keys are not captured.
- Docker build cache and unused images do not have the same persistence guarantee as named volumes. Do not assume all of `/var/lib/docker` is restored.
- Template deploys choose the requested/default environment rather than the source's named environment. Per-sandbox `env` values can still carry from the source.
- `noEnv` scrubs Boat-managed credential locations, not every possible credential or private file. Protection does not turn an arbitrary personal snapshot into a safe shared image.
- Restore may become usable before background hydration finishes. Measure readiness for actual agent work, not just the API response or vendor startup claim.
- A named snapshot is a fixed starting point, not an independent off-provider backup. Verify exports/restoration before promising recovery or retention; published retention terms have conflicted with product docs.

Sources: [snapshots](https://docs.boat.dev/snapshots), [environments](https://docs.boat.dev/environments), [terms](https://boat.dev/terms).

## What we actually observed

Manual integration tests on 2026-09-09 established the observations below. Keep detailed transcripts, live machine identifiers, and account details in the owning project's private records.

- The tests used Python `urllib.request` with an API-key environment variable and bearer headers. No Box-specific skill, installed SDK, or Box CLI was required for those requests.
- Authenticated account/limit/Box reads worked. A small temporary Python client also created a Box with `noEnv: true`, registered an SSH key, and called the command endpoint.
- SSH/SCP handled BB installation and credential transfer. BB's remote worker ran Codex, cloned a GitHub project, created a worktree, and completed a harmless coding test with diff review, local commit, and conversation continuation.
- One worktree setup took 66 seconds, including 63 seconds installing dependencies. This was one observation, not a latency guarantee. It motivates preparing dependencies in templates and measuring useful-work startup.
- These tests establish the manual integration path. They do not by themselves establish automatic provisioning for every new thread, uninterrupted work after laptop disconnection, restart of the same conversation after stop/resume, or isolation under concurrent users. Verify each in the actual deployment before claiming it works.
