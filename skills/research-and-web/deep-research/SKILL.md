---
name: deep-research
description: Run a deep, source-backed research query via DeepAPI (David's own product) POST /v1/research/deep. Builds a rigorous one-paragraph research prompt (per research-prompt rules), fires it, and saves a cited markdown report. Use when the user asks for "deep research", "deepapi research", "perplexity deep research" (legacy trigger), or any deep source-backed research run. Differentiator vs the deepapi skill: this is the full research workflow (prompt + run + report file), not raw endpoint access.
disable-model-invocation: true
---

# Deep Research (via DeepAPI)

We use DeepAPI (deepapi.co) for all deep research. This fully replaced the retired `perplexity-deep-research` skill that called OpenRouter/Perplexity directly.

## API key

- Key lives in `~/.zshrc` as `DEEPAPI_API_KEY`.
- **Gotcha:** do NOT `source ~/.zshrc` — it breaks the shell (exit 126). Use the env var if set, else read just the key line:

```bash
KEY=${DEEPAPI_API_KEY:-$(rg -o 'DEEPAPI_API_KEY=\S+' ~/.zshrc | head -1 | cut -d= -f2)}
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

One call = one cited answer (~700 words max, finishes or fails within ~60s server-side).

```bash
IDK=$(uuidgen)   # keep this; retries must reuse the SAME Idempotency-Key
jq -n --rawfile p /tmp/dr_prompt.txt '{query:$p, maxCostUsd:"0.10"}' > /tmp/dr_body.json
curl -s --max-time 120 "$BASE/v1/research/deep" \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $IDK" \
  -d @/tmp/dr_body.json > /tmp/dr_result.json
```

Default spend cap is `maxCostUsd: "0.10"` per call; raise it only if the user approves.

## Step 3 — Read the report + sources

```bash
jq -r '.status'                    /tmp/dr_result.json   # succeeded | failed
jq -r '.output.answer'             /tmp/dr_result.json   # the report
jq -r '.output.sources[]?.url'     /tmp/dr_result.json   # source URLs
jq -r '.debitMicrousd'             /tmp/dr_result.json   # cost in micro-USD (100000 = $0.10)
```

Save the report to a markdown file for the user, list citation URLs beneath it, and report the cost in dollars.

If `output.sources` comes back empty while the answer shows `[n]` citation markers, that's a DeepAPI regression (fixed 2026-07-05) — still deliver the report, but tell the user.

## Bigger topics — multi-call reports

One call is capped at ~700 words. For a full deep-research report, fire one call per numbered sub-question (each with its own Idempotency-Key), then synthesize all answers + sources into a single markdown file. Report the summed cost.

## Failure modes

- HTTP 402 `insufficient_credits` → stop; the user tops up at deepapi.co/credits; then retry with the SAME `Idempotency-Key` (safe — replays don't double-charge).
- HTTP 429 `rate_limit_exceeded` → wait `Retry-After` seconds, retry once.
- `status: failed` / HTTP 502 → report `requestId` + `error.message` to the user. Do not retry in a loop.
- Replayed request (same Idempotency-Key) returns HTTP 200 with `replayed: true` and no new charge.
- Envelope/auth mechanics and all other endpoints: see the `deepapi` skill.
