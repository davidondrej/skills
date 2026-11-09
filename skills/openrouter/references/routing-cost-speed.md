# Routing, cost, and speed

## Model fallbacks versus provider failover

`models: ["author/primary", "author/backup"]` tries models in priority order. If `model` is also present, it is tried first. Provider failover selects another host for a model; it is separate from model fallback. The returned `model` tells you which model actually served the request. [Model fallback contract](https://openrouter.ai/docs/guides/routing/model-fallbacks)

A successful but unusable answer needs application validation and explicit recovery. Do not assume an HTTP 200 that fails your JSON validator automatically advances to the next model.

All entries in one request share its fields. Verify each candidate's required schema/tool/media support, output limit, reasoning control, price, and privacy rules. If they require different parameters, make separate bounded attempts. Do not substitute a more expensive fallback that defeats the user's cost goal.

## Provider object

These fields live inside `provider`, not at the request root. Discover actual endpoint/provider slugs from the model's endpoints API or Providers page.

- `order: ["provider-a", "provider-b"]`: prefer these hosts in order. Other eligible hosts remain available unless `allow_fallbacks: false`.
- `only: ["provider-a"]`: restrict the candidate set. Account restrictions still apply.
- `ignore: ["provider-b"]`: exclude a host; combines with account exclusions.
- `allow_fallbacks`: permit fallback hosts beyond the preferred `order`. Setting false trades availability for control; it is not a substitute for validating model fallbacks.
- `require_parameters: true`: only route to endpoints advertising support for requested parameters. Essential schema/tool features still need local validation; parameter support is not a quality guarantee.
- `sort: "price" | "latency" | "throughput"`: sort eligible hosts by the selected metric. Default routing balances price and recent health; it is not strictly cheapest.
- `sort: {"by": "price", "partition": "model"}` preserves model priority. `partition: "none"` pools endpoints across models, so it can select the backup ahead of the primary. Do not use that when strict primary-first behavior matters.
- `max_price`: hard provider **unit-price** filter. `prompt` and `completion` are USD per **million tokens**; `request` is USD/request; `image` is USD/image. This does not cap a job's total bill.
- `data_collection: "deny"` and `zdr: true`: distinct data-policy filters. Check account/guardrail policy and plugins too.
- `quantizations`: restrict serving precision only when the task requires it; shrinking the pool can reduce availability.

Base provider slugs generally match regional/variant endpoints; full slugs narrow the match. Service-tier endpoints require tier eligibility. A provider name alone does not guarantee geographic residency. [Full routing contract and exact field values](https://openrouter.ai/docs/guides/routing/provider-selection)

Example provider configuration for price-sensitive work (replace the placeholder exclusion with a verified slug):

```json
{
  "provider": {
    "sort": "price",
    "ignore": ["provider-to-exclude"],
    "allow_fallbacks": true,
    "require_parameters": true
  }
}
```

Choose numerical price ceilings from current endpoint prices and the user's budget; do not copy a universal ceiling.

## Choose the speed metric deliberately

- **Lowest unit price:** `sort: "price"`. Measure cost per validated result, including reasoning, retries, cache writes, and plugins.
- **Lowest TTFT:** `sort: "latency"`. Measure time to the first **visible answer** too: an early reasoning token or SSE heartbeat is not the user's answer.
- **Fastest long output:** `sort: "throughput"`. This optimizes tokens/second, not necessarily TTFT or total latency.
- **`model:nitro`:** throughput sorting plus eligibility for supported priority-tier endpoints. A priority route can cost more. Use plain throughput sorting when you do not want this additional eligibility.
- **`model:floor`:** price sorting plus eligibility for flex-tier endpoints. Regular hosts remain eligible as backups. This differs from explicitly requesting flex-only service.

Suffixes are routing shortcuts, not new trained models. Actual served tier controls billing; recheck current tier availability and prices. [Nitro](https://openrouter.ai/docs/guides/routing/model-variants/nitro), [Floor](https://openrouter.ai/docs/guides/routing/model-variants/floor), [performance](https://openrouter.ai/docs/guides/best-practices/latency-and-performance)

`preferred_max_latency` (seconds) and `preferred_min_throughput` (tokens/second) are **soft preferences**, inside `provider`. Endpoints that miss them remain fallbacks. Numbers mean p50; percentile objects can specify p50/p75/p90/p99. Historical metrics are not promises. Set application deadlines separately. [Threshold semantics](https://openrouter.ai/docs/guides/routing/provider-selection)

## Cheap improvements before changing models

Reduce duplicated input and unnecessarily long output. Reuse stable system prefixes and tool definitions. Cache only where current provider rules and privacy policy permit it. Benchmark bounded concurrency; more workers can increase rate limits and retries.

Prompt caching varies by model/provider: minimum prefix, read/write price, TTL, and automatic versus explicit activation. Do not promise universal discounts. Keep cacheable prefixes stable; timestamps and reordered tool definitions defeat reuse. Track reported cached tokens and total cost.

OpenRouter's best-effort sticky routing can preserve a prompt-cache host; explicit `provider.order` overrides it. An explicit `session_id` can group a conversation and support stickiness where eligible. Use opaque IDs, not personal data; do not assume it stores conversation history. Price-sort hopping may cost more overall if cache reuse is lost. Prompt caching differs from caching an entire application response. [Prompt caching and session rules](https://openrouter.ai/docs/guides/best-practices/prompt-caching)
