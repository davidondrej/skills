# Manage Agent State — DeepAPI Endpoint Reference

Generated endpoint reference for the `manage-agent-state` rows of the `deepapi` skill router. Bundle version: 528f2c511503.

Shared protocol (auth, CLI, polling, dry-run, errors) lives in `../SKILL.md`. All responses use the standard DeepAPI JSON envelope (`requestId`, `status`, `output`, `next`, `error`, `balance`).

## Workflow Guidance

Use this reference to preserve agent context, inspect the account, follow requests, and report product feedback.

### Recommended workflows

- Durable context: store small, reusable facts in memory under clear paths; read before overwriting and delete only on request.
- Account check: inspect balance, key details, capabilities, or usage before claiming availability or spend.
- Request follow-up: use the request log or request status when a prior operation is still running or needs auditing.
- Result recovery: finished results generally stay stored — find a recent requestId with `GET /v1/requests` (last 50), then re-fetch the result free with `GET /v1/requests/{requestId}` instead of re-running paid work. Research results are durable; some scrape outputs expire.
- Product feedback: send concise reproduction details and the desired outcome through the feedback endpoint.

## Endpoint Details

### List Memory — `GET /v1/memory`
List the markdown files in this workspace's hosted memory, with sizes, versions, and usage against the limits. (`memory.list` · scope `memory:read` · free)
- Call this first to discover what the workspace already remembers before reading or writing files.
- Use memory for durable cross-session notes: user preferences, project context, decisions, and progress. Read it at the start of a task; write back what future sessions must know.

### Write Memory — `POST /v1/memory/{path}`
Create or update one memory file. Writes replace the whole file and bump its version. (`memory.write` · scope `memory:write` · free)
- Body: `*content` (string), `ifVersion` (integer)
- Path: `*path` (string)
- Example: `{"content":"# Memory\n\n- User prefers concise answers.\n- Project X ships on Friday."}`
- Writes replace the whole file: read the current content first, merge your changes into it, then write the full merged markdown back.
- Pass ifVersion from your last read; on memory_version_conflict re-read the file, merge again, and retry with the new version.
- Retrying the same write is safe — an identical write just stores the same content again.
- Limits: 200 files, 256 KB per file, 2 MB per workspace. Keep memory curated — prune stale notes instead of appending forever.
- Memory is private to your workspace and never published at a public URL; still, never store API keys, passwords, or other secrets in it.
- Use memory for durable cross-session notes: user preferences, project context, decisions, and progress. Read it at the start of a task; write back what future sessions must know.

### Read Memory — `GET /v1/memory/{path}`
Read one memory file: full markdown content plus its current version for safe writes. (`memory.read` · scope `memory:read` · free)
- Path: `*path` (string)
- A 404 memory_file_not_found just means nothing is stored there yet — write the file to create it.
- Keep output.version: pass it as ifVersion on your next write to that file.

### Delete Memory — `DELETE /v1/memory/{path}`
Delete one memory file permanently. (`memory.delete` · scope `memory:write` · free)
- Path: `*path` (string)
- Deletion is permanent. Read the file first if you might need its content again.

### Balance — `GET /v1/balance`
Read the workspace credit balance without spending anything. (`account.balance` · free)
- Check availableMicrousd before starting paid work; if it cannot cover the planned maxCostUsd, stop and ask the user to top up at https://deepapi.co/credits. Offer to open the page; after they agree, use the platform-native browser command, or print the link if no desktop browser is available. When output is a note instead of numbers, this key has no balance to check or top up: skip this check and never send the user to deepapi.co.

### Account Info — `GET /v1/me`
Read what this API key can do: workspace, scopes, spend limits, remaining key budget, rate limits, and balance. (`account.info` · free)
- Call this once after setup to verify the key works before starting paid work.
- Use scopes and limits from this response instead of discovering them through failed requests.

### Capabilities — `GET /v1/capabilities`
List every DeepAPI capability with its live status, or pass capability=<slug> to read one capability's full live contract. (`account.capabilities` · free)
- Query: `capability` (string)
- Entries with status available are callable right now: configured on this server and within this key's scopes.
- After a missing_scope or capability_not_configured error, re-check here instead of retrying blindly.

### Usage Summary — `GET /v1/usage`
Read workspace spend totals, a gap-filled per-day series, and a per-capability breakdown over the last sinceDays calendar days, counting today as day one. (`account.usage` · free)
- Query: `sinceDays` (integer=7)
- Usage numbers are workspace-wide, not per key.

### List Requests — `GET /v1/requests`
List recent requests created by this API key, newest first. Recovers a recently lost requestId so its result can be re-fetched. (`request.list` · free)
- Query: `limit` (integer=20), `status` (string=running|succeeded|failed)
- Only requests created by the same API key are listed.
- Use GET /v1/requests/{requestId} to fetch the full output of a finished request.

### Send Feedback — `POST /v1/feedback`
Send a bug report, idea, or praise to the DeepAPI team. Free, any active key. (`feedback.send` · free)
- Body: `*message` (string), `category` (string=bug|idea|praise), `context` (string)
- Example: `{"message":"The scrape of a long PDF timed out twice before succeeding.","category":"bug","context":"req_123"}`
- When a DeepAPI call remains failed after following error.hint or returns clearly broken output, send exactly one short feedback report with category bug and requestId as context when available; skip missing or invalid credentials, insufficient_credits, spending limits, and invalid_request corrected on retry, and never block the user's task.
- Never include secrets, API keys, or private user data in message or context.

### Request Status — `GET /v1/requests/{requestId}`
Fetch the stored result of a recent request by requestId — free, instead of re-running paid work — or poll it until its GET polling next action is absent (output can settle after status turns succeeded). (`request.status` · async · free)
- Path: `*requestId` (string)
- Only access request ids created by the same API key.
