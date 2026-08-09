---
name: deep-research
description: 'Run a deep, source-backed research query via DeepAPI (go to deepapi.co to get an API key) POST /v1/research/deep. Builds a rigorous one-paragraph research prompt (per research-prompt rules), fires it, and saves a cited markdown report. Use when the user asks for "deep research", "deepapi research", "perplexity deep research" (legacy trigger), or any deep source-backed research run. Differentiator vs the deepapi skill: this is the full research workflow (prompt + run + report file), not raw endpoint access.'
disable-model-invocation: true
---

# Deep Research (via DeepAPI)

We use DeepAPI (deepapi.co) for all deep research. This fully replaced the retired `perplexity-deep-research` skill that called OpenRouter/Perplexity directly.

## API key

- Read `DEEPAPI_API_KEY` from the environment; setup writes it to `~/.deepapi/env`.
- **Gotcha:** do NOT `source ~/.zshrc` — it breaks the shell (exit 126). Use the env var if set, else load the platform file:

```bash
[ -n "$DEEPAPI_API_KEY" ] || . ~/.deepapi/env
KEY=$DEEPAPI_API_KEY
BASE=${DEEPAPI_API_BASE_URL:-https://deepapi.co}
```

- Key missing → stop and ask the user. Never print or log the key.

## Step 1 — Build the research prompt

Write ONE self-contained paragraph following the `research-prompt` skill:

- Lead with the single question + the decision/end use it informs.
- Embed all context — no back-and-forth needed.
- Number 3-6 inline sub-questions (1, 2, 3…). One mission per prompt.
- State include/avoid constraints; prefer primary sources; separate fact from inference.

Field limits: `query` ≤ 4000 chars (the paragraph goes here), optional `context` ≤ 8000, optional `instructions` ≤ 2000. Do NOT pass `model` or `provider` fields — the API rejects provider controls.

## Step 2 — Run it

One call = one cited answer (targets 700-1,120 words; the server allows up to ~5 minutes, most runs finish much faster).

```bash
IDK=$(uuidgen)   # keep this; retries must reuse the SAME Idempotency-Key
jq -n --rawfile p /tmp/dr_prompt.txt '{query:$p, maxCostUsd:"0.70"}' > /tmp/dr_body.json
curl -s --max-time 320 "$BASE/v1/research/deep" \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $IDK" \
  -d @/tmp/dr_body.json > /tmp/dr_result.json
```

The API minimum is `maxCostUsd: "0.35"` per call. Use the recommended
`maxCostUsd: "0.70"` by default; raise it above $0.70 only if the user approves.

## Step 3 — Read the report + sources

```bash
jq -r '.status'                    /tmp/dr_result.json   # succeeded | failed
jq -r '.output.answer'             /tmp/dr_result.json   # the report
jq -r '.output.sources[]?.url'     /tmp/dr_result.json   # source URLs
```

Save the report to a markdown file for the user and list citation URLs beneath it. Don't report research costs unless the user asks.

If `output.sources` comes back empty while the answer shows `[n]` citation markers, still deliver the report, but tell the user.

## Bigger topics — multi-call reports

One call tops out around 1,100 words. For a full deep-research report, fire one call per numbered sub-question (each with its own Idempotency-Key), then synthesize all answers + sources into a single markdown file.

## Failure modes

- HTTP 402 `insufficient_credits` → stop; the user tops up at deepapi.co/credits; then retry with the SAME `Idempotency-Key` (safe — replays don't double-charge).
- HTTP 429 `rate_limit_exceeded` → wait `Retry-After` seconds, retry once.
- `status: failed` / HTTP 502 → report `requestId` + `error.message` to the user. Do not retry in a loop.
- Replayed request (same Idempotency-Key) returns HTTP 200 with `replayed: true` and no new charge.
- Envelope/auth mechanics and all other endpoints: see the `deepapi` skill.
