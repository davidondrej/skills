# Reasoning and output

## Discover before configuring

Read each model's live `reasoning` metadata: `supported_efforts`, `default_effort`, `default_enabled`, `mandatory`, and `supports_max_tokens`. Missing metadata is not proof that a dynamic router's selected model cannot reason. `supported_efforts: null` means no gateway effort allowlist; an omitted field means effort selection is not exposed. Do not assume all accepted values produce distinct native behavior. [Reasoning guide](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens)

Use one deliberate control:

- `reasoning: {"effort": "low"}` is an example **only if this model supports low and the task permits it**. Other effort levels and defaults are model-dependent.
- `reasoning: {"max_tokens": 2048}` is an example for a model with verified token-budget support. Some providers map this to an effort level; it is not universally a precise reasoning ceiling.
- Disable reasoning only when supported, with the documented control. Never send `enabled: false` or `effort: "none"` to a mandatory reasoning model.
- `exclude: true` only suppresses returned reasoning. Hidden reasoning still consumes tokens and is billed. Avoid suppressing blocks needed for a tool continuation.
- Prefer effort **or** reasoning budget. The guide's introductory example says not to combine them, while its capability notes allow combinations on some models. Unless the exact endpoint is verified, send one control and avoid legacy/native duplicates such as both `reasoning_effort` and `reasoning.effort`.

Effort is not a universal token percentage. The guide's percentage-to-budget mapping applies to budget-based implementations; native effort models choose their own token consumption. Gemini thinking levels, for example, do not provide an exact reasoning-token ceiling. Recheck the specific model instead of carrying assumptions across model families. [Provider-specific reasoning](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens#provider-specific-reasoning-implementation)

## Output budget

The Chat API supports `max_completion_tokens`; the generated request schema marks `max_tokens` deprecated, although many guide examples still use it. Preserve a working integration's supported field or intentionally migrate it. Send one ceiling, not competing aliases. For Responses, inspect `max_output_tokens` in that endpoint's schema. [Chat request contract](https://openrouter.ai/docs/api/api-reference/chat/create-a-chat-completion), [parameters](https://openrouter.ai/docs/api_reference/parameters)

Budget reasoning **plus the final answer**, within both endpoint output capacity and remaining context. Where the provider requires an explicit thinking budget, the output ceiling must exceed it. Include tool definitions and multimodal input in context accounting. Do not assign every request the largest advertised cap: large reservations can cause credit errors and do not make a small task faster.

For large edits, estimate the required returned text. Chunk at meaningful boundaries only when each chunk retains the context needed for correctness and safety; retain a whole-artifact check where required. Never treat partial output as a fully sanitized artifact.

## Ordered fallback with the Python OpenAI SDK

This template uses externally configured, verified values. It assumes all candidates accept the same effort, output ceiling, and schema. `extra_body` is an SDK argument; it is not a JSON field on the wire. Disable SDK retries here so the application's one retry policy owns the budget.

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
    timeout=60.0,
    max_retries=0,
)

schema = {
    "type": "object",
    "properties": {"answer": {"type": "string"}},
    "required": ["answer"],
    "additionalProperties": False,
}
response = client.chat.completions.create(
    model=os.environ["OPENROUTER_PRIMARY_MODEL"],
    messages=[{"role": "user", "content": "Return an answer to: What is 2 + 2?"}],
    max_completion_tokens=int(os.environ["OPENROUTER_OUTPUT_LIMIT"]),
    response_format={
        "type": "json_schema",
        "json_schema": {"name": "answer", "strict": True, "schema": schema},
    },
    extra_body={
        "models": [os.environ["OPENROUTER_FALLBACK_MODEL"]],
        "reasoning": {"effort": os.environ["OPENROUTER_REASONING_EFFORT"]},
        "provider": {"require_parameters": True, "allow_fallbacks": True},
    },
)
# Next: record safe metadata, classify stop/errors, then parse and validate.
# Never blindly index content and call the request successful.
```

The SDK `model` is tried first, then the `models` list. With raw HTTP, a `models: [primary, fallback]` array is sufficient. Automatic model fallback reacts to API errors; a successful response that fails your local validator requires an application decision. [Fallbacks and SDK examples](https://openrouter.ai/docs/guides/routing/model-fallbacks)

## Validate before accepting

1. Inspect top-level errors, choices, and `finish_reason` before parsing text. Expected Chat reasons include `stop`, `length`, `tool_calls`, `content_filter`, and `error`.
2. Handle valid tool calls as tool calls. For a text contract, require a nonempty string; do not coerce null, arrays, or reasoning into the answer. For multimodal output, use its documented output fields.
3. `json_object` requests JSON syntax. `json_schema` plus `strict: true` requests the schema, but enforcement varies by provider. Parse locally, validate the schema, then validate task semantics.
4. Optional `plugins: [{"id": "response-healing"}]` can repair formatting for non-streaming `json_object` or `json_schema` responses. It cannot restore content cut off by a token limit or prove the answer is correct. Keep your validator.

Sources: [response contract](https://openrouter.ai/docs/api_reference/overview), [structured outputs](https://openrouter.ai/docs/guides/features/structured-outputs), [response healing](https://openrouter.ai/docs/guides/features/plugins/response-healing).

## Retry with evidence

A non-text answer alone does not prove reasoning exhaustion. Collect finish/native finish reason, requested cap, completion and reasoning counts, actual model/provider, and generation ID. Missing counts are unknown, not zero.

- **Transient network/provider failure:** bounded backoff, respecting Retry-After and the total deadline.
- **Confirmed length/output exhaustion:** reserve enough answer room; consider less reasoning if quality permits, a smaller task, or a larger supported cap within budget. A lower effort may help; test it rather than promising it will.
- **Invalid JSON or task validation failure:** one bounded corrective attempt or an explicitly chosen compatible fallback; never a blind infinite retry loop.
- **Unsupported configuration, auth, credit, or policy error:** fix the cause; do not retry unchanged or silently relax restrictions.

Different fallback reasoning controls require separate application requests. Keep each candidate's explicit configuration and the same acceptance checks. This is an implementation recommendation, not a promise that OpenRouter changes parameters for each entry in `models`.
