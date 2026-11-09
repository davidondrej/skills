---
name: deep-research
description: Run deep research through DeepAPI and save a report with sources. Use when asked for deep research, DeepAPI research, or Perplexity deep research.
disable-model-invocation: true
triggers: [user, model]
---

# Deep Research

Use DeepAPI (`POST /v1/research/deep`) for all deep research.

## API key

Read `DEEPAPI_API_KEY` from the environment, falling back to `~/.deepapi/env`. Never source `~/.zshrc`; it breaks the shell (exit 126).

```bash
[ -n "$DEEPAPI_API_KEY" ] || . ~/.deepapi/env
KEY=$DEEPAPI_API_KEY
BASE=${DEEPAPI_API_BASE_URL:-https://deepapi.co}
```

If the key is missing, stop and ask the user. Never print or log it. Get a key at deepapi.co.

## 1. Build the prompt

Follow the `research-prompt` skill. Write one self-contained paragraph:

- Lead with the main question and the decision it informs.
- Include all context and 3-6 numbered sub-questions. Keep one mission per prompt.
- State what to include or avoid. Prefer primary sources; separate fact from inference.

Field limits: `query` ≤ 4000 characters (the prompt), optional `context` ≤ 8000, optional `instructions` ≤ 2000. Do not send `model` or `provider`; the API rejects them.

## 2. Run it

One call returns a cited answer, targeting 700-1,120 words. The server allows up to ~5 minutes.

```bash
IDK=$(uuidgen)   # keep this; retries must reuse the SAME Idempotency-Key
jq -n --rawfile p /tmp/dr_prompt.txt '{query:$p, maxCostUsd:"0.70"}' > /tmp/dr_body.json
curl -s --max-time 320 "$BASE/v1/research/deep" \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $IDK" \
  -d @/tmp/dr_body.json > /tmp/dr_result.json
```

Minimum `maxCostUsd` is `"0.35"`. Default to `"0.70"`; ask the user before raising it.

## 3. Save the report

```bash
jq -r '.status'                    /tmp/dr_result.json   # succeeded | failed
jq -r '.output.answer'             /tmp/dr_result.json   # the report
jq -r '.output.sources[]?.url'     /tmp/dr_result.json   # source URLs
```

Save a Markdown report with citation URLs beneath it. Only report costs if the user asks. If the answer has `[n]` citations but `output.sources` is empty, deliver it and tell the user.

For longer reports, run each numbered sub-question separately with its own Idempotency-Key, then combine the answers and sources into one Markdown file.

## Failures and retries

- HTTP 402 `insufficient_credits`: stop for a top-up at deepapi.co/credits, then retry with the same Idempotency-Key.
- HTTP 429 `rate_limit_exceeded`: wait `Retry-After` seconds, then retry once.
- `status: failed` / HTTP 502: report `requestId` and `error.message`. Do not retry in a loop.
- Reusing an Idempotency-Key returns HTTP 200 with `replayed: true` and no new charge.
- See the `deepapi` skill for envelope/auth details and other endpoints.
