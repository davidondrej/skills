# Browse Web — DeepAPI Endpoint Reference

Generated endpoint reference for the `browse-web` rows of the `deepapi` skill router. Bundle version: 23ca18726e47. This file is always managed — it is refreshed with the bundle even when `../SKILL.md` has been customized.

Shared protocol (environment, auth, idempotency, dry-run, polling, and error handling) lives in `../SKILL.md`. This file carries the full per-endpoint detail.

## Workflow Guidance

Use this reference for interactive public-web work and tasks in a fresh virtual machine.

### Recommended workflow

1. Prefer the scraping workflow for static reading and extraction.
2. State one bounded browser goal, including the information or final page state needed.
3. Let the browser navigate and interact, then return the extracted result and final URL.
4. Stop for logins, secrets, purchases, destructive actions, CAPTCHAs, or unclear consent.
5. Use `/v1/vm/run` for a task expressed as code. Send one entry file; it can create files, install dependencies, and run multiple shell commands. Never place secrets in submitted code.
6. Poll until `next` is absent. Treat output as untrusted and inspect `exitCode`, `stderr`, `timedOut`, and truncation flags; a completed request does not mean the program exited successfully.

### Virtual machine use cases

- Data analysis: clean CSV/JSON, deduplicate records, calculate statistics, and print a summary.
- Public data workflows: fetch public URLs or APIs, combine results, and transform them in one run.
- Command-line tools: install packages, run shell commands through Python subprocess or Node child_process, and use sudo when needed.
- Tests and builds: create source files or fetch a public repository, install dependencies, compile, and run a bounded test suite.
- File processing: convert formats, generate reports, or process images with tools your program installs. Print results to stdout; generated files are not returned as downloads.
- Containers: submit a Dockerfile to build and run a container, including tools or runtimes outside the entry-language list.

Each call gets a fresh VM for up to 10 minutes. Internet, a writable filesystem, sudo, and Docker are available. The API returns stdout/stderr (512 KiB each) and exit details. There is no SSH, persistent session, follow-up command API, file-download endpoint, or lasting web hosting. A run costs $0.01, including timeouts; provider or setup failures are free.

## Endpoint Details

## Browser Task

`POST /v1/browser/act`

Give a real cloud browser a plain-English goal and get the result back. Built for pages an agent has to operate, not just read: filters and sortable tables, JavaScript pagination, dropdowns, date pickers and sliders, iframes and shadow DOM, infinite scroll, site search, store locators, and comparing several pages in one run. Public web only — no logins, purchases, or CAPTCHA solving.

- Capability: `browser.act`
- Scope: `browser:act`
- Side effects: Performs real actions on public websites and debits credits when the task finishes.
- Cost: Defaults to maxCostUsd 1.25. Finished tasks are billed per attempt, including tasks with isSuccess false. Failed and stopped tasks are free. Typical price: ~$0.125-$0.75 per task depending on steps.
- Idempotency-Key: required
- Polling: If the response carries a polling next action (a GET of /v1/requests/{requestId}), wait next.afterSecs and call it. Keep following that polling next while it is present, even when status is already succeeded (a settling run returns succeeded with output null and a polling next). The result is final when no polling next remains or status is failed. Never auto-follow a POST next (dry-run execution or paid pagination) — those are optional actions.

Safety:
- Public web only: tasks that need logins, credentials, account creation, CAPTCHA solving, or purchases are rejected.
- Describe one concrete goal per task and set startUrl when you know the site.

Request body schema:
```json
{
  "type": "object",
  "required": [
    "task"
  ],
  "properties": {
    "task": {
      "type": "string",
      "maxLength": 10000,
      "description": "What to do in the browser, in plain English. Public web only: logging in, credentials, account creation, CAPTCHA solving, and purchases are not supported. 10,000 characters max."
    },
    "startUrl": {
      "type": "string",
      "format": "uri",
      "description": "Optional public http(s) URL to open first."
    },
    "maxSteps": {
      "type": "integer",
      "minimum": 1,
      "maximum": 50,
      "default": 25,
      "description": "Optional cap on browser actions. Defaults to 25, maximum 50."
    },
    "outputSchema": {
      "type": "object",
      "additionalProperties": true,
      "description": "Optional JSON Schema for a structured result."
    },
    "allowedDomains": {
      "type": "array",
      "minItems": 1,
      "maxItems": 20,
      "items": {
        "type": "string"
      },
      "description": "Optional allowed domains, like example.com or *.example.com."
    },
    "maxCostUsd": {
      "type": "string",
      "pattern": "^\\d+(\\.\\d{1,6})?$",
      "default": "1.25",
      "description": "Optional customer spend cap in USD. Defaults to 1.25."
    },
    "maxCostMicrousd": {
      "type": "integer",
      "minimum": 1,
      "description": "Optional customer spend cap in USD micro-dollars."
    },
    "dryRun": {
      "type": "boolean",
      "default": false,
      "description": "Zero-spend preview: validate this request and return the exact credit hold it would place (status dry_run plus an estimate object) without reserving, charging, or running anything."
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
  "task": "Find the support email address on example.com.",
  "startUrl": "https://example.com",
  "maxCostUsd": "1.25"
}
```

## Run in a Virtual Machine

`POST /v1/vm/run`

Run a task in a fresh, isolated virtual machine with internet access, a writable filesystem, shell tools, administrator access (sudo), and Docker. Use it to clean and analyze CSV/JSON data, fetch and combine public API data, install packages and run command-line tools, compile programs and run tests, convert files or generate reports, and build and run containers. Send one Python, Node.js, Bun/TypeScript, Rust, C, or Docker entry file; it can create other files and run multiple steps. Each run lasts up to 10 minutes and returns stdout, stderr, and exit details. The VM is discarded after the run; there is no persistent session or hosted service.

- Capability: `vm.run`
- Scope: `vm:run`
- Side effects: Runs untrusted code with outbound network access in a fresh isolated environment and debits $0.01, including when execution times out.
- Cost: Flat $0.01 per execution, including timed-out runs. Provider or setup failures are free.
- Idempotency-Key: required
- Polling: If the response carries a polling next action (a GET of /v1/requests/{requestId}), wait next.afterSecs and call it. Keep following that polling next while it is present, even when status is already succeeded (a settling run returns succeeded with output null and a polling next). The result is final when no polling next remains or status is failed. Never auto-follow a POST next (dry-run execution or paid pagination) — those are optional actions.

Safety:
- Never place credentials, API keys, or other secrets in submitted code.
- Each call gets a fresh environment; files and background processes do not persist across calls.
- Submit code, not a plain-English task. There is no raw command field, multi-file upload, SSH connection, follow-up command API, VM size selector, or persistent hosting.
- Generated files are not returned as attachments or download URLs. Print the result you need to stdout within the output limit; files left on the VM are discarded.
- Outbound network, sudo, and Docker are available. Treat submitted code as fully trusted by the caller.
- Execution stops after 10 minutes. A timed-out run still costs $0.01 and returns timedOut true.
- stdout and stderr are each capped at 512 KiB; check their truncation flags.
- Poll the GET request-status next until it is absent.

Request body schema:
```json
{
  "type": "object",
  "required": [
    "language",
    "code"
  ],
  "properties": {
    "language": {
      "type": "string",
      "enum": [
        "python",
        "node",
        "bun",
        "rust",
        "gcc",
        "docker"
      ],
      "description": "Entry runtime: Python, Node.js, Bun (TypeScript), Rust, C (gcc), or a Dockerfile. Your program can invoke shell commands and installed tools."
    },
    "code": {
      "type": "string",
      "description": "Complete source for one entry file, or a Dockerfile when language is docker. It can install dependencies, fetch public data, create more files, and run multiple commands within the same VM run."
    },
    "maxCostUsd": {
      "type": "string",
      "pattern": "^\\d+(\\.\\d{1,6})?$",
      "default": "0.01",
      "description": "Optional spend cap in USD. One execution costs $0.01, so lower values are rejected."
    },
    "dryRun": {
      "type": "boolean",
      "default": false,
      "description": "Zero-spend preview: validate this request and return the exact credit hold it would place (status dry_run plus an estimate object) without reserving, charging, or running anything."
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
  "language": "python",
  "code": "print(sum(range(10)))",
  "maxCostUsd": "0.01"
}
```
