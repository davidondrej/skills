# Manage Agent State — DeepAPI Endpoint Reference

Generated endpoint reference for the `manage-agent-state` rows of the `deepapi` skill router. Bundle version: ee61bded3e6a. This file is always managed — it is refreshed with the bundle even when `../SKILL.md` has been customized.

Shared protocol (environment, auth, idempotency, dry-run, polling, and error handling) lives in `../SKILL.md`. This file carries the full per-endpoint detail.

## Workflow Guidance

Use this reference to preserve agent context, inspect the account, follow requests, and report product feedback.

### Recommended workflows

- Durable context: store small, reusable facts in memory under clear paths; read before overwriting and delete only on request.
- Account check: inspect balance, key details, capabilities, or usage before claiming availability or spend.
- Request follow-up: use the request log or request status when a prior operation is still running or needs auditing.
- Product feedback: send concise reproduction details and the desired outcome through the feedback endpoint.

## Endpoint Details

## List Memory

`GET /v1/memory`

List the markdown files in this workspace's hosted memory, with sizes, versions, and usage against the limits.

- Capability: `memory.list`
- Scope: `memory:read`
- Side effects: Reads memory file metadata only.
- Cost: Memory reads and writes are free.
- Idempotency-Key: not required
- Polling: This route returns a terminal envelope directly.

Safety:
- Call this first to discover what the workspace already remembers before reading or writing files.
- Use memory for durable cross-session notes: user preferences, project context, decisions, and progress. Read it at the start of a task; write back what future sessions must know.

Response schema:
```json
{
  "$ref": "#/components/schemas/PublicEnvelope"
}
```

## Write Memory

`POST /v1/memory/{path}`

Create or update one memory file. Writes replace the whole file and bump its version.

- Capability: `memory.write`
- Scope: `memory:write`
- Side effects: Stores markdown in the workspace's private hosted memory. Free — nothing is debited.
- Cost: Memory reads and writes are free.
- Idempotency-Key: not required
- Polling: This route returns a terminal envelope directly.

Safety:
- Writes replace the whole file: read the current content first, merge your changes into it, then write the full merged markdown back.
- Pass ifVersion from your last read; on memory_version_conflict re-read the file, merge again, and retry with the new version.
- Retrying the same write is safe — an identical write just stores the same content again.
- Limits: 200 files, 256 KB per file, 2 MB per workspace. Keep memory curated — prune stale notes instead of appending forever.
- Memory is private to your workspace and never published at a public URL; still, never store API keys, passwords, or other secrets in it.
- Use memory for durable cross-session notes: user preferences, project context, decisions, and progress. Read it at the start of a task; write back what future sessions must know.

Request body schema:
```json
{
  "type": "object",
  "required": [
    "content"
  ],
  "properties": {
    "content": {
      "type": "string",
      "description": "Full markdown content of the file. Writes replace the whole file. 256 KB max per file."
    },
    "ifVersion": {
      "type": "integer",
      "minimum": 1,
      "description": "Optional concurrency guard: the version from your last read. The write is rejected with memory_version_conflict if someone else wrote the file since."
    }
  },
  "additionalProperties": false
}
```

Path parameters schema:
```json
{
  "type": "object",
  "required": [
    "path"
  ],
  "properties": {
    "path": {
      "type": "string",
      "description": "Markdown file path inside the workspace memory, e.g. \"memory.md\" or \"notes/customers.md\". Must end with \".md\". Letters, digits, dots, dashes, underscores, and forward slashes only."
    }
  }
}
```

Response schema:
```json
{
  "$ref": "#/components/schemas/PublicEnvelope"
}
```

Example request body:
```json
{
  "content": "# Memory\n\n- User prefers concise answers.\n- Project X ships on Friday."
}
```

Example path params: `{"path":"memory.md"}`

## Read Memory

`GET /v1/memory/{path}`

Read one memory file: full markdown content plus its current version for safe writes.

- Capability: `memory.read`
- Scope: `memory:read`
- Side effects: Reads memory file content only.
- Cost: Memory reads and writes are free.
- Idempotency-Key: not required
- Polling: This route returns a terminal envelope directly.

Safety:
- A 404 memory_file_not_found just means nothing is stored there yet — write the file to create it.
- Keep output.version: pass it as ifVersion on your next write to that file.

Path parameters schema:
```json
{
  "type": "object",
  "required": [
    "path"
  ],
  "properties": {
    "path": {
      "type": "string",
      "description": "Markdown file path inside the workspace memory, e.g. \"memory.md\" or \"notes/customers.md\". Must end with \".md\". Letters, digits, dots, dashes, underscores, and forward slashes only."
    }
  }
}
```

Response schema:
```json
{
  "$ref": "#/components/schemas/PublicEnvelope"
}
```

Example path params: `{"path":"memory.md"}`

## Delete Memory

`DELETE /v1/memory/{path}`

Delete one memory file permanently.

- Capability: `memory.delete`
- Scope: `memory:write`
- Side effects: Permanently deletes the stored file. There is no undo.
- Cost: Memory reads and writes are free.
- Idempotency-Key: not required
- Polling: This route returns a terminal envelope directly.

Safety:
- Deletion is permanent. Read the file first if you might need its content again.

Path parameters schema:
```json
{
  "type": "object",
  "required": [
    "path"
  ],
  "properties": {
    "path": {
      "type": "string",
      "description": "Markdown file path inside the workspace memory, e.g. \"memory.md\" or \"notes/customers.md\". Must end with \".md\". Letters, digits, dots, dashes, underscores, and forward slashes only."
    }
  }
}
```

Response schema:
```json
{
  "$ref": "#/components/schemas/PublicEnvelope"
}
```

Example path params: `{"path":"notes/customers.md"}`

## Balance

`GET /v1/balance`

Read the workspace credit balance without spending anything.

- Capability: `account.balance`
- Scope: `none - any active API key`
- Side effects: Reads the balance only.
- Cost: Read route returns debitMicrousd 0.
- Idempotency-Key: not required
- Polling: This route returns a terminal envelope directly.

Safety:
- Check availableMicrousd before starting paid work; if it cannot cover the planned maxCostUsd, stop and ask the user to top up at https://deepapi.co/credits. Offer to open the page; after they agree, use the platform-native browser command, or print the link if no desktop browser is available.

Response schema:
```json
{
  "$ref": "#/components/schemas/PublicEnvelope"
}
```

## Account Info

`GET /v1/me`

Read what this API key can do: workspace, scopes, spend limits, remaining key budget, rate limits, and balance.

- Capability: `account.info`
- Scope: `none - any active API key`
- Side effects: Reads key and workspace state only.
- Cost: Read route returns debitMicrousd 0.
- Idempotency-Key: not required
- Polling: This route returns a terminal envelope directly.

Safety:
- Call this once after setup to verify the key works before starting paid work.
- Use scopes and limits from this response instead of discovering them through failed requests.

Response schema:
```json
{
  "$ref": "#/components/schemas/PublicEnvelope"
}
```

## Capabilities

`GET /v1/capabilities`

List every DeepAPI capability with its live status, or pass capability=<slug> to read one capability's full live contract.

- Capability: `account.capabilities`
- Scope: `none - any active API key`
- Side effects: Reads live capability availability only.
- Cost: Read route returns debitMicrousd 0.
- Idempotency-Key: not required
- Polling: This route returns a terminal envelope directly.

Safety:
- Entries with status available are callable right now: configured on this server and within this key's scopes.
- After a missing_scope or capability_not_configured error, re-check here instead of retrying blindly.

Query parameters schema:
```json
{
  "type": "object",
  "properties": {
    "capability": {
      "type": "string",
      "example": "search.web",
      "description": "Optional capability slug. When present, returns that capability's full live contract instead of the discovery list."
    }
  },
  "additionalProperties": false
}
```

Response schema:
```json
{
  "$ref": "#/components/schemas/PublicEnvelope"
}
```

## Usage Summary

`GET /v1/usage`

Read workspace spend totals, a gap-filled per-day series, and a per-capability breakdown over the last sinceDays calendar days, counting today as day one.

- Capability: `account.usage`
- Scope: `none - any active API key`
- Side effects: Reads usage rollups only.
- Cost: Read route returns debitMicrousd 0.
- Idempotency-Key: not required
- Polling: This route returns a terminal envelope directly.

Safety:
- Usage numbers are workspace-wide, not per key.

Query parameters schema:
```json
{
  "type": "object",
  "properties": {
    "sinceDays": {
      "type": "integer",
      "minimum": 1,
      "maximum": 90,
      "default": 7,
      "description": "How many calendar days the summary covers, counting today as day one."
    }
  },
  "additionalProperties": false
}
```

Response schema:
```json
{
  "$ref": "#/components/schemas/PublicEnvelope"
}
```

Example query: `sinceDays=7`

## List Requests

`GET /v1/requests`

List recent requests created by this API key, newest first. Recovers lost requestIds.

- Capability: `request.list`
- Scope: `none - any active API key`
- Side effects: Reads request history only.
- Cost: Read route returns debitMicrousd 0.
- Idempotency-Key: not required
- Polling: This route returns a terminal envelope directly.

Safety:
- Only requests created by the same API key are listed.
- Use GET /v1/requests/{requestId} to fetch the full output of a finished request.

Query parameters schema:
```json
{
  "type": "object",
  "properties": {
    "limit": {
      "type": "integer",
      "minimum": 1,
      "maximum": 50,
      "default": 20,
      "description": "How many recent requests to return."
    },
    "status": {
      "type": "string",
      "enum": [
        "running",
        "succeeded",
        "failed"
      ],
      "description": "Optional status filter."
    }
  },
  "additionalProperties": false
}
```

Response schema:
```json
{
  "$ref": "#/components/schemas/PublicEnvelope"
}
```

Example query: `limit=20`

## Send Feedback

`POST /v1/feedback`

Send a bug report, idea, or praise to the DeepAPI team. Free, any active key.

- Capability: `feedback.send`
- Scope: `none - any active API key`
- Side effects: Stores the feedback and notifies the team.
- Cost: Free route returns debitMicrousd 0.
- Idempotency-Key: required
- Polling: This route returns a terminal envelope directly.

Safety:
- When a DeepAPI call remains failed after following error.hint or returns clearly broken output, send exactly one short feedback report with category bug and requestId as context when available; skip missing or invalid credentials, insufficient_credits, spending limits, and invalid_request corrected on retry, and never block the user's task.
- Never include secrets, API keys, or private user data in message or context.

Request body schema:
```json
{
  "type": "object",
  "required": [
    "message"
  ],
  "properties": {
    "message": {
      "type": "string",
      "maxLength": 4000,
      "description": "The feedback itself, in plain language. What happened, what was expected, or what would help.",
      "example": "The scrape of a long PDF timed out twice before succeeding."
    },
    "category": {
      "type": "string",
      "enum": [
        "bug",
        "idea",
        "praise"
      ],
      "description": "Optional label for the feedback. Omit when unsure."
    },
    "context": {
      "type": "string",
      "maxLength": 2000,
      "description": "Optional pointer that helps reproduce the report, e.g. the requestId of a failed call.",
      "example": "req_123"
    }
  },
  "additionalProperties": false
}
```

Response schema:
```json
{
  "$ref": "#/components/schemas/PublicEnvelope"
}
```

Example request body:
```json
{
  "message": "The scrape of a long PDF timed out twice before succeeding.",
  "category": "bug",
  "context": "req_123"
}
```

## Request Status

`GET /v1/requests/{requestId}`

Poll a request by requestId until its GET polling next action is absent (output can settle after status turns succeeded).

- Capability: `request.status`
- Scope: `same key that created the request`
- Side effects: Reads or refreshes request status.
- Cost: Status polling does not create a new debit.
- Idempotency-Key: not required
- Polling: If the response carries a polling next action (a GET of /v1/requests/{requestId}), wait next.afterSecs and call it. Keep following that polling next while it is present, even when status is already succeeded (a settling run returns succeeded with output null and a polling next). The result is final when no polling next remains or status is failed. Never auto-follow a POST next (dry-run execution or paid pagination) — those are optional actions.

Safety:
- Only poll request ids created by the same API key.

Query parameters schema:
```json
{
  "type": "object",
  "properties": {
    "waitForFinishSecs": {
      "type": "integer",
      "minimum": 1,
      "maximum": 60,
      "description": "Optional long-poll wait while the request is running."
    }
  }
}
```

Path parameters schema:
```json
{
  "type": "object",
  "required": [
    "requestId"
  ],
  "properties": {
    "requestId": {
      "type": "string",
      "description": "Request id returned by the original call."
    }
  }
}
```

Response schema:
```json
{
  "$ref": "#/components/schemas/PublicEnvelope"
}
```

Example query: `waitForFinishSecs=60`

Example path params: `{"requestId":"req_123"}`
