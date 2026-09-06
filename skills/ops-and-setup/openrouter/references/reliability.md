# Reliability and observability

## Classify errors before retrying

Read both HTTP status and response content. OpenRouter can commit HTTP 200 after upstream headers arrive, then return an error body before any tokens appear. Do not blindly access `choices[0]`.

- Invalid request or unsupported parameter: correct configuration; retrying unchanged adds no value.
- 401/authentication: repair credentials through the approved secret flow.
- 402/payment required: inspect account/key budget and requested output allowance. Backoff alone cannot add credits. Do not silently change models or budget.
- 403/policy: report the block; never relax guardrails to make a retry succeed.
- 408/timeout, 429/rate limiting, transient 502/provider failure: bounded backoff can help. Honor `Retry-After` when present.
- 503/no eligible provider or 404/no matching endpoint: check capability/privacy/price filters as well as availability; do not blindly remove restrictions.

For upstream errors, the canonical `error_type` is more precise than lossy native codes. Chat puts it at `error.metadata.error_type`; Responses uses top-level `error_type`; Anthropic Messages uses `error.error_type`. Parse defensively. [Error contract](https://openrouter.ai/docs/api_reference/errors-and-debugging), [limits](https://openrouter.ai/docs/api_reference/limits)

## One bounded retry policy

These are application engineering recommendations, not automatic OpenRouter guarantees:

- Own retries in one layer. Account for SDK retries, gateway failover, and application retries so they do not multiply silently.
- Set a total deadline and attempt/spend ceilings. Cap concurrency, use exponential backoff with jitter, and respect Retry-After.
- Retry transient failures; change strategy for repeated deterministic failures. Stop a persistently failing route with a cooldown when workload scale justifies it.
- Never replay a completed side-effecting tool action because a later inference failed. Persist tool execution state and enforce business-level idempotency.
- Do not assume an inference `Idempotency-Key` deduplicates calls or guarantees one charge; verify support for the endpoint before relying on it.
- After an uncertain timeout, the upstream call may still run. Cancellation and billing behavior vary by provider; a client disconnect is not a universal refund.

OpenRouter may fail over before output is delivered. Once partial output reaches the client, do not expect transparent switching to another provider. Treat failed partial results according to the task contract; publishing and safety-sensitive processing must remain fail-closed. [Streaming and cancellation](https://openrouter.ai/docs/api_reference/streaming)

## Streaming correctly

Use a tested SSE parser or SDK. Network reads do not correspond to complete events. Buffer incomplete frames, handle CRLF/multiline data, ignore colon comments, and recognize `[DONE]`. A stream error may be its first and only event.

For Chat, merge deltas by choice index. Merge tool-call fragments by tool index and append argument fragments; parse only after completion. `finish_reason` belongs to the choice, not its delta. Treat `error` events and `finish_reason: "error"` as failure even under HTTP 200.

Consume the final usage frame before closing. OpenRouter's final accounting frame can contain one content-free choice repeating the terminal reason, rather than an empty `choices` array. Do not emit a second answer or invoke a tool twice. Accept only output that passes the application's completion/validation checks. [SSE contract](https://openrouter.ai/docs/api_reference/streaming)

## Safe telemetry

For each attempt record, when present:

- Local operation/attempt ID and OpenRouter generation ID.
- Requested model(s), returned model, and actual provider. A configured primary does not prove it served the request.
- Explicit effort/budget, output cap, routing policy, and served tier if reported.
- HTTP status, canonical error type, `finish_reason`, `native_finish_reason`.
- Input/output/reasoning/cache token counts; expected content type and text length, without text.
- Queue/request time, first visible answer time, duration, returned cost, and validation result.

Do not log raw `error.metadata`: moderation snippets and provider payloads may contain private input. Do not log prompts, attachments, credentials, or reasoning traces. Preserve required tool-continuation blocks in protected conversation state, separately from diagnostics.

Usage is included automatically in current Chat responses and the final streaming frame; old `usage.include` and `stream_options.include_usage` toggles are deprecated. Missing fields remain unknown. For auditing use `GET /api/v1/generation?id=GENERATION_ID`; inspect `provider_name`, `model`, `native_finish_reason`, `native_tokens_reasoning`, timing, and cost when available. Native token counts and normalized counts can differ. [Usage](https://openrouter.ai/docs/cookbook/administration/usage-accounting), [generation metadata](https://openrouter.ai/docs/api/api-reference/generations/get-request-&-usage-metadata-for-a-generation)

A blank answer is not proof of reasoning exhaustion. A plausible diagnosis needs stop reason, counts, requested limits, and the actual route. Separate confirmed evidence from inference.

## Privacy and budgets

Keep OpenRouter credentials server-side in a secret store/environment. Use application-specific keys and credit limits; never ship a shared secret in browser code. Query current key limits with `GET /api/v1/key` without printing the credential. [Authentication](https://openrouter.ai/docs/api_reference/authentication), [limits](https://openrouter.ai/docs/api_reference/limits)

No-training and zero retention are different. `provider.zdr: true` restricts inference to eligible endpoints, and account/guardrail requirements cannot be relaxed by request-level false. ZDR does not cover enabled plugins/tools and permits certain implicit in-memory caches under OpenRouter's definition. Check those services separately before sending private data. Do not promise geographic residency from provider pinning alone. [ZDR policy](https://openrouter.ai/docs/guides/features/zdr)

## Before shipping an integration

Test the serialized request and response handler at the actual SDK boundary. Cover a success, a tool/null-content response, length truncation, malformed/schema-invalid output, 200-with-error, mid-stream failure, and the approved fallback. Verify safety/privacy/cost filters remain intact on fallback. Use mocks for failure cases, then an authorized small real canary. Do not introduce unbounded paid test loops.

When changing model/provider/SDK versions, repeat representative quality and cost checks. Pin model IDs when reproducibility matters; aliases and endpoint capabilities can change. Keep enough safe telemetry to identify regressions without collecting private content.
