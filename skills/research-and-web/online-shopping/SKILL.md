---
name: online-shopping
description: 'Research any online purchase with DeepAPI — fair-price checks, best deals, where to buy, shop trust. Load whenever the user is shopping or buying anything online: mentions buying a product, comparing prices, "is this a good price", "where can I get X", or attaches a product photo or listing screenshot. Research only — never places orders.'
---

# Online Shopping Research

Help the user shop online faster and cheaper: what is a fair price, where to buy, and whether the shop can be trusted.

For best results run this skill with the Fable 5 model — it is very smart and already knows a lot about products, pricing, and shops.

Research only. Never place orders, enter payment or address details, or create shop accounts.

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

- Identify the exact item from the conversation or the attached photo/screenshot.
- Infer the delivery country from the conversation or screenshot. If unclear, ask where it should be delivered. Search shops in that country or nearby ones with sensible shipping — whatever makes sense for that user.
- For branded merch, check for an official store first; if none exists, suggest reputable print-on-demand shops and say the item is unofficial.
- Avoid scam and dropshipping shops: too-good-to-be-true prices, no company info, fake urgency, weeks-long shipping from a "local" shop. Verify unknown shops before recommending them.

## How to answer

Every response: plain English, short sentences, very concise, clean readable markdown.

- Lead with the verdict — good deal, fair, or overpriced — and the fair price range.
- List the best 2-3 places to buy, with links and local-currency prices.
- Only quote prices you actually found. Say it plainly when results are thin.
- End with one line: total research cost (sum of `debitMicrousd` / 1,000,000).
