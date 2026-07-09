---
name: online-shopping
description: 'Research any online purchase with DeepAPI — fair-price checks, best deals, where to buy, shop trust. Load whenever the user is shopping or buying anything online: mentions buying a product, comparing prices, "is this a good price", "where can I get X", or attaches a product photo or listing screenshot. Research only — never places orders.'
---

# Online Shopping Research

The whole purpose of this skill: save the user time and money when shopping online. Answer three things: what is a fair price, where to buy, and whether the shop can be trusted.

For best results run this skill with the Fable 5 model — it is very smart and already knows a lot about products, pricing, and shops.

Research only. Never place orders, enter payment or address details, or create shop accounts.

Non-negotiable: every response to the user is very concise, clear, and formatted in nice readable markdown. The How to answer section is a hard contract — check every response against it before sending.

## Setup

- Read `DEEPAPI_API_KEY` and `DEEPAPI_API_BASE_URL` from the environment. If unset, try `source ~/.deepapi/env`; the default base URL is `https://deepapi.co`.
- If the key is missing, stop and tell the user to get one at https://deepapi.co.
- Never print, log, or expose the key.

## DeepAPI

Use DeepAPI for all shopping research — not built-in search tools. Mix the endpoints however the task needs:

| Endpoint | Use for | maxCostUsd |
|---|---|---|
| `POST /v1/search/web` | find shops, prices, deals, reviews — run ~3 query variants | `"0.05"` |
| `POST /v1/scrape/website` | read the exact product page or listing the user is checking; verify an unknown shop | `"0.20"` |
| `POST /v1/research/deep` | pricing or market questions search cannot settle | `"0.10"` |
| `POST /v1/scrape/twitter/search` | real buyer complaints about a shop | `"0.03"` |

Every request: `Authorization: Bearer $DEEPAPI_API_KEY`, `Content-Type: application/json`, a unique `Idempotency-Key` per POST, and an explicit `maxCostUsd`.

```bash
curl -sS -X POST "$DEEPAPI_API_BASE_URL/v1/search/web" \
  -H "Authorization: Bearer $DEEPAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: shop-$(uuidgen)" \
  -d '{"query": "Sony WH-1000XM5 price Germany", "maxResults": 5, "maxCostUsd": "0.05"}'
```

If `status: running`, poll `GET /v1/requests/{requestId}` after `next.afterSecs`. On HTTP 402, ask the user to top up at https://deepapi.co/credits.

## How to research

Use your judgment. The goal is a confident answer, not a fixed procedure.

Scale research effort to the item's price. A cheap item researched for minutes is this skill failing its purpose:

- **Obvious call** — the screenshot or conversation already gives you enough to judge: answer right away. Zero searches, zero scrapes.
- **Cheap (roughly under $50)**: answer from your own knowledge — you already know what everyday items cost. At most ONE quick web search, and only if genuinely unsure. Scraping and deep research are forbidden in this tier. Respect the user's time above all: answer even more quickly, clearly, and concisely than usual.
- **Mid-range**: a few searches, scrape the listing and a top competitor or two.
- **Expensive ($1,000+)**: full depth — deep research, many search variants, scrape several shops and buyer reviews.

For mid-range and expensive items, give first impressions BEFORE any deep research or scraping: a sentence or two from your own knowledge — the typical price range for this kind of item and whether the deal looks good or bad so far. For example: "Cars of this brand and year usually go for €18-25k, so this looks slightly high — running a deep check to verify." Then start the research. Never leave the user waiting minutes with nothing to read.

Then, as needed for the price tier:

- Identify the exact item from the conversation or the attached photo/screenshot.
- Infer the delivery country from the conversation or screenshot. If unclear, ask where it should be delivered. Search shops in that country or nearby ones with sensible shipping — whatever makes sense for that user.
- For branded merch, check for an official store first; if none exists, suggest reputable print-on-demand shops and say the item is unofficial.
- Avoid scam and dropshipping shops: too-good-to-be-true prices, no company info, fake urgency, weeks-long shipping from a "local" shop. Verify unknown shops before recommending them.

## How to answer

The format below is a hard rule, not a preference. Draft the response, check it against this list, and rewrite it if it fails any point:

- Very concise: the whole answer fits on one screen. Short sentences. Plain English.
- No filler, no hedging, no research narration ("I searched for...", "Let me check..."). Conclusions only.
- Nice readable markdown: a bold verdict line first, then short bullets or a small table. Never a wall of text, never long paragraphs.
- Verdict up top — good deal, fair, or overpriced — with the fair price range.
- Best 2-3 places to buy: links + local-currency prices.
- Only quote prices you actually found. Say it plainly when results are thin.
- Last line: total research cost (sum of `debitMicrousd` / 1,000,000).

Shape every answer like this:

```markdown
**Verdict: Overpriced — fair price is €280–€330, this listing asks €449.**

| Buy from | Price |
|---|---|
| [amazon.de](https://www.amazon.de/...) | €289 |
| [mediamarkt.de](https://www.mediamarkt.de/...) | €299 |

Skip shiny-deals24.shop — €99 for this item is a classic scam price.

_Research cost: $0.08_
```

Success looks like this: the user found the right product quickly and bought it from a trusted, reputable shop at a good deal — not from an overpriced reseller or dropshipping store.
