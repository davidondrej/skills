# Scraping — DeepAPI Workflow Guide

Managed workflow guide for the `scraping` rows of the `deepapi` skill router. Bundle version: 1320a0ca895c. This file is always managed — it is refreshed with the bundle even when `../SKILL.md` has been customized.

Shared protocol (environment, auth, idempotency, dry-run, polling, and error handling) lives in `../SKILL.md`.

## Workflow Guidance

Use this reference to collect structured public data for research, monitoring, lead preparation, and content analysis.

### Match the business outcome

| Outcome | Start with | Continue with |
| --- | --- | --- |
| Extract a site or document | `/v1/scrape/website` or `/v1/scrape/pdf` | Follow discovered pages only when the task needs them |
| Research developers or software | `/v1/scrape/github/search` | GitHub repository, profile, issues, pulls, contents, or commits |
| Research people, companies, or hiring across sources | `/v1/scrape/deep` | Use source links to verify facts and investigate gaps |
| Research creators and content | `/v1/scrape/youtube/search` or `/v1/scrape/tiktok/search` | YouTube transcript, channel, or shorts; TikTok profile, posts, comments, or transcript |
| Monitor conversations and audience response | X/Twitter, Reddit, Instagram, or Threads endpoints | Use `/v1/scrape/threads/posts` for exact Threads post URLs |
| Research advertising | `/v1/scrape/facebook/ads` | Go deep: competitor `pages` plus keyword queries, `activeStatus: "all"`, `maxItems` 100+ (see the Meta Ads recipe below) |
| Find local businesses and places | `/v1/scrape/google/places` | Narrow by location and category; set `maxItems: 1` when looking up one specific business (much faster and cheaper) |

### Deep Scrape (`POST /v1/scrape/deep`)

Use for sponsor research, podcast guest preparation, or company profiles. Deep Scrape discovers relevant sources and combines the results into one JSON dossier. Use Deep Research for a question or comparison; use a website or platform endpoint when you only need that source.

Send `query` with the subject's name and useful identifying context. Add known public website or profile URLs in `urls` to reduce mistaken identities. Optional `sources` limits the platforms searched. Read `GET /v1/capabilities?capability=scrape.deep` for the current schema and supported fields.

Example request body (use the shared auth and Idempotency-Key headers):
```json
{ "query": "Stripe, the payments company", "urls": ["https://stripe.com"], "maxCostUsd": "0.50" }
```

- The default customer spend cap is $0.50; `maxCostUsd` is optional. The cap is a limit, not a quoted charge. `dryRun: true` previews the hold for free.
- The POST returns `202`. Wait `next.afterSecs` and poll the returned `next.path` until no polling action remains. Recover an existing result with `GET /v1/requests/{requestId}` instead of paying to run it again.
- Read `output.subject`, `profiles`, `posts`, `people`, `websites`, and `sources`. Preserve source links. Check `conflicts`, `confidence`, `errors`, and `partial` before calling the dossier complete or treating identities as certain.
- Useful partial and low-confidence results are billable at actual usage within the cap. No usable matching data means no charge. Report missing information clearly; a source link alone does not prove a fact.

### Recommended workflow

1. Define the entities and fields the final output needs.
2. For a dossier across sources, use Deep Scrape. For one platform, use its dedicated endpoint rather than open-web search.
3. For platform lists, discover identifiers first, then fan out: call the detail endpoint for every candidate that could change the answer, not just the obvious top one.
4. Size `maxItems` to the job, not to caution: on cheap per-item endpoints (Meta ads ~$0.00375 per ad) request 100+, and continue with returned page tokens whenever the task needs more.
5. Preserve source URLs and report missing, private, blocked, or partial data honestly. When a result looks wrong, blocked, or suspiciously empty, also send one free `POST /v1/feedback` with the `requestId`.

### Important constraints

- `maxCostUsd` is a spending allowance, not a charge: every scrape bills only what it actually returned and releases the unspent budget. Endpoints with a minimum cap (for example Google Places) are rejecting a too-small allowance, not quoting a price — typical calls cost far less than the floor. Preview any call's exact hold for free with `dryRun: true`.
- Do not send a GitHub token or OAuth credential; DeepAPI handles GitHub authentication server-side and returns public resources only.
- Website and PDF extraction requires public URLs. PDFs must have a readable text layer; image-only scans are not OCRed.
- Bound large pages, documents, and transcripts with `maxChars` or `maxPages`. A `truncated: true` result reached that cap.
- Continue pagination by returning `nextPageToken` unchanged as `pageToken` with the same filters. GitHub profile repository pagination additionally requires `includeRepos: true` and one username.
- Threads posts: send one URL or up to 10 URLs to `/v1/scrape/threads/posts`. Read `missingUrls` on the final response. A backup scraper retries only missing exact posts; the endpoint does not accept `maxItems`.

### Meta Ads Library research recipe (`/v1/scrape/facebook/ads`)

One call is not research. Ads cost ~$0.00375 each, so depth costs cents while shallow results are worthless. For competitor or market research, fan out 3-5 calls and merge:

- Run BOTH kinds of calls: `pages` for each competitor (returns everything an advertiser runs) and keyword `query` calls (keyword search only matches ad text, so it misses ads that never mention the term).
- Always set `activeStatus: "all"` when researching: inactive ads reveal what an advertiser tested and stopped.
- Vary keywords across calls: brand name, product name, tagline, category term.
- When specific markets matter, query 2-3 key `country` codes in separate calls instead of relying on `ALL` — per-country searches can surface ads that `ALL` misses.
- Request `maxItems` 100+ per call, then dedupe the merged results by ad `id`.

### Go-deep recipes (high-value patterns)

Per-item prices are cents or fractions of cents — depth is cheap and shallow results are worthless. Default patterns:

- X/Twitter monitoring: run `sort: "latest"` AND `sort: "top"` plus 2-3 query phrasings, `maxItems` 100 each, then dedupe by tweet `id`. Enrich accounts in batches: `/v1/scrape/twitter/user` takes a handle list in one call, with optional `includeFollowers`/`includeFollowing` extraction.
- Websites: pass a URL list to fetch those exact pages in one `/v1/scrape/website` call. To crawl links from a seed, pass maxDepth above 0, or pass maxPages/includeUrls/excludeUrls without maxDepth.
- YouTube topics and creators: start with the 5-result search default; set `maxItems` to 25 only when broader coverage is useful. For channel and Shorts batches, `maxItems` applies to each channel.
- LinkedIn lists: people search exists to build lists — ask for 50+ profiles per call, fan out titles x locations variants, then enrich the shortlist with `/v1/scrape/linkedin/profile`. When researching people, set `includeDetails: true` and match on full work history, not job titles.

### Reading a `/v1/scrape/website` response

- `output` is an array of page objects. Each returned page carries the requested content (`markdown` and/or `text`, per `contentFormat`) and, when the origin reports it, a `url`. A page with no extractable content is dropped, so it never appears as a content-free result.
- Seeds-only website scrapes (no crawl) also return `urlOutcomes`: one `{url, status}` per requested URL. `returned` means that page is in `output`; `not_returned` means it produced no usable page. Do not treat a short `output` as a complete fetch — read `urlOutcomes` first. The field is omitted on crawls and other scrape endpoints.
- Per-page metadata fields are optional and present only when available: `title`, `description`, and `language` appear only when the page provides them; `truncated` and `totalChars` appear only on a page that hit the `maxChars` cap. Never assume a field exists; read defensively.
- Follow the polling `next` (a `GET` of `/v1/requests/{requestId}`) whenever it is present, regardless of `status`. A billed run whose content is still settling returns `status: "succeeded"` with `output: null`, no `list`, and a polling `next`; poll it until it is absent before treating the result as complete. Do not stop polling just because `status` is no longer `running`, and never auto-follow a `POST` `next` (dry-run execution or paid pagination).
- Read the `list.listState` signal beside `output` to tell an empty fetch from real pages: `results` (pages returned), `no_results` (the origin answered but returned nothing usable), or `source_blocked` (blocking was the dominant reason, for example an HTTP 401, 403, 407, 429, 451, or 503, or a login wall, captcha, rate limit, or access-denied notice). When the origin answers but returns nothing usable the fetch is free (`debitMicrousd: 0`) and `output` is an empty array.
- A run can also end `status: "failed"` (for example a backend failure with no working fallback). A failed run is not a free empty success; surface the error instead of treating it as no content.

### Find exact endpoint details

- `GET /v1/capabilities` lists every available capability and slug.
- `GET /v1/capabilities?capability=<slug>` returns the exact current schema, example, pricing, and availability for one endpoint.
- `https://deepapi.co/docs/reference.md` is the complete agent-readable API reference.
- `https://deepapi.co/docs/pricing.md` has current endpoint pricing.
- `https://deepapi.co/openapi.json` is the machine-readable contract; `https://deepapi.co/llms.txt` indexes all public agent docs.
