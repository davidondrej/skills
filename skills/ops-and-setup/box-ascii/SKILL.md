---
name: box-ascii
description: Operate Box by Ascii cloud VMs through its REST API, CLI, and SSH. Use for Box provisioning, environments, secrets, templates, snapshots, stop/resume/fork, or running BB and coding agents on box.ascii.dev. This is for Ascii's compute service, not Box.com file storage.
---

# Box by Ascii

Use Box's API or CLI for machine management and SSH or the command API for work inside a VM. Read [operations and observations](references/operations.md) before direct API calls, credential changes, or recovery work.

## Start with the actual account and machine

1. Read the current project's instructions and operational notes. Identify the intended account, organization, Box, and repository; retain existing mappings instead of provisioning duplicates.
2. Load `BOX_API_KEY` from the environment or the project's documented, gitignored credentials file. Read its location from the project's setup instructions; do not assume a universal path. Do not search unrelated credential stores or print their contents. Use the secrets skill if a new key is needed.
3. For operations, check authentication and state with `GET /me`, `/limits`, and `/boxes`. If the CLI is available, inspect `box status`, `box list`, and the relevant `--help` instead. Filter output to the fields needed for the task.
4. Check which tools are already installed. An API workflow does not require the Box CLI or an SDK. Read the official install instructions if installation is needed; do not execute a remote installer blindly.

Use the DeepAPI skill to read current Box docs when behavior or request fields are uncertain. Prices, limits, model catalogs, and install commands must be checked live. A documentation lookup is not evidence that an authenticated operation succeeded.

## API access

- Base URL: `https://ascii.dev/api/box/v1`.
- Authentication: `Authorization: Bearer $BOX_API_KEY`.
- JSON bodies: `Content-Type: application/json`.
- Use an account API key for account-wide operations. A machine-scoped key is restricted to its Box.
- Key creation, rotation, and revocation require a browser sign-in session, even through `box api-key`. An existing API key cannot create another key.
- Do not assume provider onboarding has an API. The documented Box-managed provider login flow uses the Agents page; injecting already configured agent credentials is a separate environment setting.

This read-only example checks authentication without printing account details or credentials. Load the key into the process environment first:

```python
import json
import os
import urllib.error
import urllib.request

request = urllib.request.Request(
    "https://ascii.dev/api/box/v1/me",
    headers={"Authorization": "Bearer " + os.environ["BOX_API_KEY"]},
)
try:
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.load(response)
        print({"status": response.status, "ok": data.get("ok")})
except urllib.error.HTTPError as error:
    print({"status": error.code})
    raise SystemExit(1)
```

Python's standard library worked in our tests. Use the official TypeScript or Python SDK when the surrounding application benefits from typed clients; do not introduce a client abstraction just to make a few requests.

## Environments and templates

An **environment** holds repositories, secrets, and credential permissions. A **named snapshot/template** holds installed tools and disk state. Use both for repeatable startup.

Common CLI operations, after checking the target and current contents:

```bash
box env list
box env new dev
box env add-repo dev owner/repository --branch main
box env set-file dev repository/.env --from ./private/project.env
box env set dev --github true --secrets true --box-credentials false --agents-credentials true
box new --environment dev
```

- Repository branches are cloned as configured; Box does not create a working branch. Let the coding workflow or BB manage branches/worktrees.
- Repositories land at `/home/user/<repository-name>`. Secret file paths are relative to `/home/user`; include the repository folder to place a `.env` inside its clone.
- `--environment dev` selects the environment. `--env KEY=value` sets a variable for one Box; it overrides the environment value. Never put real secrets in CLI arguments.
- Named environments must already exist. Omitted selection uses the default for a new Box/template deploy; ordinary resume and fork preserve the existing/source environment version.
- Saving an environment creates a version. Existing Boxes do not automatically receive it, including on ordinary resume. Inspect `box info` and upgrade deliberately.
- `box env upgrade dev` can affect many Boxes. For one Box, use the API's explicit `agentIds` selection (the schema calls Box IDs "agent" IDs). Withheld secrets are deleted on upgrade; re-pinning an older version does not restore deleted secret files.
- Editing an environment also changes what future Boxes receive, even if only one existing Box is upgraded. For an exception intended for one Box alone, use Box-specific configuration instead of changing a shared environment.
- After injection, restart the consuming application if it reads variables only at process start. Check the running application's behavior, not only a new SSH shell.

Preinstall BB, required runtimes, and dependencies in a clean template. Keep credentials in environments or inject them for the intended user after boot. Set `BOX_ID` to the verified prepared Box's identifier before these commands.

```bash
box snapshot "$BOX_ID" agent-stack
box new --from agent-stack --environment dev
```

Verify the saved snapshot is ready before deploying it. Re-saving the same name changes future deploys, not existing machines. Fresh repository state and successful dependency installation still need validation.

## Isolation and credentials

- For personal Boxes, inject only the credentials and repos the task needs. For Boxes driven by other users, use an environment marked `safeForThirdParties: true` or `noEnv: true`.
- Protected mode withholds the owner's managed GitHub, secrets, Box, and agent credentials regardless of the section toggles. Explicit per-Box `env` values still pass through.
- Do not promise that protected mode sanitizes arbitrary disk contents. Manually added cloud, package-manager, and Docker logins may remain in a template or snapshot.
- Never build a shared template from a credential-filled personal machine. Per-Box variables also carry into forks/template deploys unless replaced.
- Conversion to protected mode scrubs managed credential files, including Codex/Claude logins that the Box's own user may have added. Conversion is one-way. Check ownership and recovery needs before applying it to an existing Box.
- Keep keys, auth files, enrollment codes, desktop URLs, and raw API/session logs out of prompts, committed files, and user-visible output. Desktop URLs can contain access tokens.

## Verify the requested outcome

After a change, inspect the specific Box and verify the result inside it. Check file presence/permissions without printing secrets. For agent setup, run a harmless task and verify the intended account, repository, output, and continued conversation.

Report the Box/environment identifier, what changed, what actually passed, and any real limitation. Do not equate an accepted API request, an SSH-ready machine, or a snapshot with a working agent session.

## Official references

- [API and endpoint index](https://docs.ascii.dev/box/api/v1)
- [CLI reference](https://docs.ascii.dev/box/cli-reference)
- [Environments](https://docs.ascii.dev/box/environments)
- [Setup and scripts](https://docs.ascii.dev/box/setup)
- [Snapshots and templates](https://docs.ascii.dev/box/snapshots)
- [Platform guide](https://docs.ascii.dev/box/platform-guide)
