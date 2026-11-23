# Seo — DeepAPI Endpoint Reference

Generated endpoint reference for the `seo` rows of the `deepapi` skill router. Bundle version: 528f2c511503.

Shared protocol (auth, CLI, polling, dry-run, errors) lives in `../SKILL.md`. All responses use the standard DeepAPI JSON envelope (`requestId`, `status`, `output`, `next`, `error`, `balance`).

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

### SEO Keyword Metrics — `POST /v1/seo/keyword`
Look up search volume, CPC, keyword difficulty, search intent, and 12-month trend for up to 100 keywords. (`seo.keyword` · scope `seo:read` · ~$0.0625 per lookup, up to 100 keywords, cap $0.125)
- Body: `*keywords` (array)
- Example: `{"keywords":["claude code","ai coding agent"],"maxCostUsd":"0.125"}`
- Batch related keywords into one request (up to 100); it costs barely more than one keyword.
- monthlySearches returns the 12 most recent months, newest first.
- Data covers Google US English; volumes and positions elsewhere differ.

### SEO Rank Check — `POST /v1/seo/rank`
Check where a domain ranks in Google organic results for a keyword, with the live top 10. (`seo.rank` · scope `seo:read` · ~$0.025 per check, cap $0.375)
- Body: `*keyword` (string), `*domain` (string), `depth` (integer=30)
- Example: `{"keyword":"web scraping api","domain":"deepapi.co","depth":30}`
- position is null when the domain is not in the checked depth; raise depth (up to 100) before concluding it does not rank.
- Data covers Google US English; volumes and positions elsewhere differ.

### SEO Competitors — `POST /v1/seo/competitors`
Find the domains competing with a site in Google organic search, with overlap and traffic estimates. (`seo.competitors` · scope `seo:read` · ~$0.0625-$0.125 per analysis, more with enrichment, cap $0.3125)
- Body: `*domain` (string), `limit` (integer=10), `include` (array)
- Example: `{"domain":"deepapi.co","limit":10}`
- sharedKeywords counts keywords where both domains rank; use it to judge how direct a competitor is.
- gapKeywords are keywords the competitor ranks for and the target domain does not — content opportunities.
- Data covers Google US English; volumes and positions elsewhere differ.

### SEO Audit — `POST /v1/seo/audit`
One keyword in, a ranking plan out: live metrics, the current top 10, an analysis of what those pages cover, and a concrete outline to beat them. (`seo.audit` · scope `seo:read` · async · ~$0.375-$0.75 per audit, cap $1.25)
- Body: `*keyword` (string), `domain` (string), `include` (array)
- Example: `{"keyword":"web scraping api","domain":"deepapi.co"}`
- This runs for up to a few minutes: poll the returned next action until the result is final.
- Use include to skip blocks you do not need; recommendations is the expensive one.
- Data covers Google US English; volumes and positions elsewhere differ.

### SEO Optimize — `POST /v1/seo/optimize`
Score a draft (or live page) against a target keyword for SEO and AI-answer-engine visibility, with prioritized edits and an optional rewrite. (`seo.optimize` · scope `seo:read` · async · ~$0.25-$0.50 per analysis, cap $0.625)
- Body: `*keyword` (string), `text` (string), `url` (string), `rewrite` (boolean=false)
- Example: `{"keyword":"web scraping api","text":"# The complete guide to web scraping APIs\n\nWeb scraping APIs let agents...","rewrite":true}`
- Provide exactly one of text or url.
- This runs for up to a minute or two: poll the returned next action until the result is final.
- Scores are rubric-based (0-100, strict): treat 80+ as competitive rather than aiming for 100.
- Data covers Google US English; volumes and positions elsewhere differ.
