# Seo — DeepAPI Endpoint Reference

Generated endpoint reference for the `seo` rows of the `deepapi` skill router. Bundle version: 4dbca805b9cf. This file is always managed — it is refreshed with the bundle even when `../SKILL.md` has been customized.

Shared protocol (environment, auth, idempotency, dry-run, polling, and error handling) lives in `../SKILL.md`. This file carries the full per-endpoint detail.

## Workflow Guidance

Use this reference to win search visibility: find what people search for, see where a domain stands, and make content that ranks and gets cited by AI answer engines.

### Match the outcome

| Outcome | Endpoint |
| --- | --- |
| What do people search, and how hard is it? | `POST /v1/seo/keyword` |
| Where does this domain rank right now? | `POST /v1/seo/rank` |
| Who else competes for this domain's keywords? | `POST /v1/seo/competitors` |
| What should I publish to rank for this keyword? | `POST /v1/seo/audit` |
| How good is this draft, and how do I improve it? | `POST /v1/seo/optimize` |

### Recommended workflow

1. Start with `/v1/seo/keyword`. Batch every candidate keyword into ONE call (up to 100) — it costs barely more than a single keyword.
2. Judge a keyword on volume, difficulty, AND intent together. High volume with the wrong intent will never convert.
3. Check the current position with `/v1/seo/rank` before claiming a change helped.
4. Use `/v1/seo/audit` to plan a new page: it reads the live top 10 and returns an outline and gaps.
5. Use `/v1/seo/optimize` on the draft, apply the edits, and re-score.

### Important constraints

- Data covers Google US English. Volumes and positions differ elsewhere.
- `monthlySearches` returns the 12 most recent months, newest first.
- `/v1/seo/audit` and `/v1/seo/optimize` are async: they answer 202, then you poll the returned `next` path until it is absent.
- `rewrite: true` on optimize returns a full improved draft up to 12,000 characters. It is the slowest call we offer; expect roughly a minute.
- Zero results are free, and failed calls are never billed.

## Endpoint Details

## SEO Keyword Metrics

`POST /v1/seo/keyword`

Look up search volume, CPC, keyword difficulty, search intent, and 12-month trend for up to 100 keywords.

- Capability: `seo.keyword`
- Scope: `seo:read`
- Side effects: Runs a paid keyword data lookup and debits credits when finished.
- Cost: Defaults to maxCostUsd 0.125, which covers a full 100-keyword batch. The final debit follows actual data cost and is reported as debitMicrousd. Typical price: ~$0.0625 per lookup, up to 100 keywords.
- Idempotency-Key: required
- Polling: This route returns a terminal envelope directly.

Safety:
- Batch related keywords into one request (up to 100); it costs barely more than one keyword.
- monthlySearches returns the 12 most recent months, newest first.
- Data covers Google US English; volumes and positions elsewhere differ.

Request body schema:
```json
{
  "type": "object",
  "required": [
    "keywords"
  ],
  "properties": {
    "keywords": {
      "type": "array",
      "minItems": 1,
      "maxItems": 100,
      "items": {
        "type": "string",
        "maxLength": 200
      },
      "description": "Keywords to look up (1-100 per request; one request fee covers the whole batch). US English data."
    },
    "maxCostUsd": {
      "type": "string",
      "pattern": "^\\d+(\\.\\d{1,6})?$",
      "default": "0.125",
      "description": "Optional customer spend cap in USD. Defaults to 0.125."
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
  "keywords": [
    "claude code",
    "ai coding agent"
  ],
  "maxCostUsd": "0.125"
}
```

## SEO Rank Check

`POST /v1/seo/rank`

Check where a domain ranks in Google organic results for a keyword, with the live top 10.

- Capability: `seo.rank`
- Scope: `seo:read`
- Side effects: Runs a paid live ranking check and debits credits when finished.
- Cost: Defaults to maxCostUsd 0.375, which covers checks at any depth. Deeper checks (higher depth) cost more. The final debit follows actual data cost and is reported as debitMicrousd. Typical price: ~$0.025 per check.
- Idempotency-Key: required
- Polling: This route returns a terminal envelope directly.

Safety:
- position is null when the domain is not in the checked depth; raise depth (up to 100) before concluding it does not rank.
- Data covers Google US English; volumes and positions elsewhere differ.

Request body schema:
```json
{
  "type": "object",
  "required": [
    "keyword",
    "domain"
  ],
  "properties": {
    "keyword": {
      "type": "string",
      "maxLength": 200,
      "description": "Search query to check rankings for."
    },
    "domain": {
      "type": "string",
      "maxLength": 253,
      "description": "Domain to look for in the results, like example.com. A full URL also works."
    },
    "depth": {
      "type": "integer",
      "minimum": 1,
      "maximum": 100,
      "default": 30,
      "description": "How many organic results to check (default 30, maximum 100). Deeper checks cost more."
    },
    "maxCostUsd": {
      "type": "string",
      "pattern": "^\\d+(\\.\\d{1,6})?$",
      "default": "0.375",
      "description": "Optional customer spend cap in USD. Defaults to 0.375."
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
  "keyword": "web scraping api",
  "domain": "deepapi.co",
  "depth": 30
}
```

## SEO Competitors

`POST /v1/seo/competitors`

Find the domains competing with a site in Google organic search, with overlap and traffic estimates.

- Capability: `seo.competitors`
- Scope: `seo:read`
- Side effects: Runs a paid competitor analysis and debits credits when finished.
- Cost: Defaults to maxCostUsd 0.3125. Enrichment blocks (include) cost more per enriched competitor; depth adapts to the cap, so raise maxCostUsd to enrich more competitors. The final debit follows actual data cost and is reported as debitMicrousd. Typical price: ~$0.0625-$0.125 per analysis, more with enrichment.
- Idempotency-Key: required
- Polling: This route returns a terminal envelope directly.

Safety:
- sharedKeywords counts keywords where both domains rank; use it to judge how direct a competitor is.
- gapKeywords are keywords the competitor ranks for and the target domain does not — content opportunities.
- Data covers Google US English; volumes and positions elsewhere differ.

Request body schema:
```json
{
  "type": "object",
  "required": [
    "domain"
  ],
  "properties": {
    "domain": {
      "type": "string",
      "maxLength": 253,
      "description": "Domain to find organic search competitors for, like example.com."
    },
    "limit": {
      "type": "integer",
      "minimum": 1,
      "maximum": 25,
      "default": 10,
      "description": "Optional cap on returned competitors. Defaults to 10, maximum 25."
    },
    "include": {
      "type": "array",
      "maxItems": 2,
      "items": {
        "type": "string",
        "enum": [
          "topPages",
          "gapKeywords"
        ]
      },
      "description": "Optional enrichment blocks for up to 3 strongest competitors: topPages (their best pages) and gapKeywords (keywords they rank for that your domain does not). Requested blocks are all-or-nothing; a cap too small for every block is rejected before spend."
    },
    "maxCostUsd": {
      "type": "string",
      "pattern": "^\\d+(\\.\\d{1,6})?$",
      "default": "0.3125",
      "description": "Optional customer spend cap in USD. Defaults to 0.3125."
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
  "domain": "deepapi.co",
  "limit": 10
}
```

## SEO Audit

`POST /v1/seo/audit`

One keyword in, a ranking plan out: live metrics, the current top 10, an analysis of what those pages cover, and a concrete outline to beat them.

- Capability: `seo.audit`
- Scope: `seo:read`
- Side effects: Starts a paid analysis (keyword data, live results, page fetches, and an AI planning step) and debits credits when finished.
- Cost: Defaults to maxCostUsd 1.25. Dropping recommendations from include skips the page analysis and costs a fraction. The final debit follows actual usage and is reported as debitMicrousd. Typical price: ~$0.375-$0.75 per audit.
- Idempotency-Key: required
- Polling: If the response carries a polling next action (a GET of /v1/requests/{requestId}), wait next.afterSecs and call it. Keep following that polling next while it is present, even when status is already succeeded (a settling run returns succeeded with output null and a polling next). The result is final when no polling next remains or status is failed. Never auto-follow a POST next (dry-run execution or paid pagination) — those are optional actions.

Safety:
- This runs for up to a few minutes: poll the returned next action until the result is final.
- Use include to skip blocks you do not need; recommendations is the expensive one.
- Data covers Google US English; volumes and positions elsewhere differ.

Request body schema:
```json
{
  "type": "object",
  "required": [
    "keyword"
  ],
  "properties": {
    "keyword": {
      "type": "string",
      "maxLength": 200,
      "description": "Keyword to build a ranking plan for."
    },
    "domain": {
      "type": "string",
      "maxLength": 253,
      "description": "Optional: your domain. The plan then includes where you currently rank and your highest-leverage first moves."
    },
    "include": {
      "type": "array",
      "maxItems": 4,
      "items": {
        "type": "string",
        "enum": [
          "metrics",
          "serp",
          "competitors",
          "recommendations"
        ]
      },
      "description": "Optional output blocks. Defaults to all four. Dropping recommendations skips the page analysis and costs much less."
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
  "keyword": "web scraping api",
  "domain": "deepapi.co"
}
```

## SEO Optimize

`POST /v1/seo/optimize`

Score a draft (or live page) against a target keyword for SEO and AI-answer-engine visibility, with prioritized edits and an optional rewrite.

- Capability: `seo.optimize`
- Scope: `seo:read`
- Side effects: Starts a paid analysis (keyword data, an optional page fetch, and an AI scoring step) and debits credits when finished.
- Cost: Defaults to maxCostUsd 0.625. rewrite: true roughly doubles the analysis cost. The final debit follows actual usage and is reported as debitMicrousd. Typical price: ~$0.25-$0.50 per analysis.
- Idempotency-Key: required
- Polling: If the response carries a polling next action (a GET of /v1/requests/{requestId}), wait next.afterSecs and call it. Keep following that polling next while it is present, even when status is already succeeded (a settling run returns succeeded with output null and a polling next). The result is final when no polling next remains or status is failed. Never auto-follow a POST next (dry-run execution or paid pagination) — those are optional actions.

Safety:
- Provide exactly one of text or url.
- This runs for up to a minute or two: poll the returned next action until the result is final.
- Scores are rubric-based (0-100, strict): treat 80+ as competitive rather than aiming for 100.
- Data covers Google US English; volumes and positions elsewhere differ.

Request body schema:
```json
{
  "type": "object",
  "required": [
    "keyword"
  ],
  "properties": {
    "keyword": {
      "type": "string",
      "maxLength": 200,
      "description": "Target keyword the content should rank for."
    },
    "text": {
      "type": "string",
      "maxLength": 30000,
      "description": "The draft content to score and improve. Provide exactly one of text or url."
    },
    "url": {
      "type": "string",
      "description": "A live page to fetch and score instead of pasting text. Provide exactly one of text or url."
    },
    "rewrite": {
      "type": "boolean",
      "default": false,
      "description": "When true, also return rewrittenText: the full improved draft with the edits applied, up to 12,000 characters."
    },
    "maxCostUsd": {
      "type": "string",
      "pattern": "^\\d+(\\.\\d{1,6})?$",
      "default": "0.625",
      "description": "Optional customer spend cap in USD. Defaults to 0.625."
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
  "keyword": "web scraping api",
  "text": "# The complete guide to web scraping APIs\n\nWeb scraping APIs let agents...",
  "rewrite": true
}
```
