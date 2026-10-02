---
name: online-shopping
description: 'Research online purchases, prices, and shop trust. Use for buying advice, subscriptions, or shopping photos, links, and checkout screens.'
---

# Online Shopping Research

Auto-invoke for online purchases. Do not add `disable-model-invocation` or Codex `allow_implicit_invocation: false`.

Find a fair price, trusted places to buy, and legal checkout tax savings. Fable 5 is the preferred model for this skill.

**Research only.** Never place orders, create shop accounts, or enter payment, address, company, or VAT/tax details. Remind the user to enter them; never save those values in this skill or any file.

Keep every response concise and readable. Check it against **How to answer** before sending.

## Setup

- Read the API key and API base URL from the environment. If unset, follow the documented setup instructions; the default base URL is `https://deepapi.co`.
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

Every request: `Authorization: Bearer $API_KEY`, `Content-Type: application/json`, a unique `Idempotency-Key` per POST, and an explicit `maxCostUsd`.

```bash
curl -sS -X POST "$API_BASE_URL/v1/search/web" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: shop-$(uuidgen)" \
  -d '{"query": "Sony WH-1000XM5 price Germany", "maxResults": 5, "maxCostUsd": "0.05"}'
```

If `status: running`, poll `GET /v1/requests/{requestId}` after `next.afterSecs`. On HTTP 402, ask the user to top up at https://deepapi.co/credits.

## VAT and sales tax

On checkout, subscription, or SaaS plan screens—especially Stripe or a VAT/GST/tax line—remind the user **before paying**:

- If they have a company, buy as a business and enter its VAT ID (EU VAT number, Polish NIP, GSTIN, or local equivalent). For eligible EU B2B digital purchases, reverse charge can remove VAT from checkout.
- Look for “purchasing as a business”, “VAT number”, “tax ID”, or “add billing details”. Currency changes do **not** remove VAT.
- If tax is already $0 with a VAT ID, skip the reminder. If tax remains, check business status and VAT ID; do not promise removal without checking eligibility.
- Never suggest a VPN, fake address, or borrowed card.

Treat tax as a possible legal saving; do not dismiss a valid business VAT option as “unavoidable tax”.

## How to research

1. **Give first impressions before any research**, whatever the price. In 1–2 sentences, react to the screenshot, link, or description: apparent value, seller reputation, or a rough price range. Make clear these are preliminary. For a checkout with VAT, include the company VAT ID reminder, unless tax is already $0.
2. **Identify the exact item and buying intent:** what it is for, who it is for, and whether price, quality, or delivery matters most. Infer from context; ask one short question only if uncertainty would change the recommendation.
3. **Scale research to the price:**
   - **Obvious call:** the screenshot or conversation is enough to judge; answer immediately, without searches or scrapes.
   - **Cheap (roughly under $50):** answer from existing knowledge. At most one quick web search if unsure; no scraping or deep research. Keep it especially brief.
   - **Mid-range:** a few searches; scrape the listing and one or two top competitors.
   - **Expensive ($1,000+):** deep research, several search variants, and scrapes of several shops and buyer reviews.

Use judgment within these limits. As needed for the price tier:

- Infer the delivery country; ask if unclear. Find shops there or nearby with sensible shipping.
- For branded merch, check the official store first. If none exists, suggest reputable print-on-demand shops and label the item unofficial.
- Avoid scam and dropshipping shops. Verify unknown shops before recommending them. Watch for implausibly low prices, missing company info, fake urgency, and weeks-long shipping from a “local” shop.

## How to answer

Draft, check, and revise against this format:

- Fit on one screen: short sentences, plain English, readable Markdown.
- Start with a **bold verdict**—good deal, fair, or overpriced—and the fair price range.
- Use short bullets or a small table with the **best 2–3 places to buy**, links, and local-currency prices.
- On checkout/subscription screens, add one short company VAT ID reminder when applicable.
- Quote only prices actually found; clearly label preliminary estimates and say when results are thin.
- Give conclusions without filler, hedging, or research narration. Report research costs only if asked.

Example:

```markdown
**Verdict: Overpriced — fair price is €280–€330, this listing asks €449.**

| Buy from | Price |
|---|---|
| [amazon.de](https://www.amazon.de/...) | €289 |
| [mediamarkt.de](https://www.mediamarkt.de/...) | €299 |

Skip shiny-deals24.shop — €99 for this item is a classic scam price.

VAT: if you have a company, tick business and enter the VAT ID before paying.
```
