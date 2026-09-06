---
name: online-shopping
description: 'Research any online purchase with DeepAPI — fair-price checks, best deals, where to buy, shop trust, and VAT/tax savings. Load on ANY shopping, buying, purchasing, checkout, subscribe, SaaS plan, software subscription, Stripe/payment page, or "is this a good price" moment — including product photos and listing or checkout screenshots. Differentiator: research-only shopping help plus a company VAT-number reminder; never places orders.'
---

# Online Shopping Research

Auto-invoke this skill. Do not add `disable-model-invocation` (or Codex `allow_implicit_invocation: false`). Models must load it on their own whenever the user is buying anything online.

The whole purpose of this skill: save the user time and money when shopping online. Answer three things: what is a fair price, where to buy, and whether the shop can be trusted. On checkout, also save tax.

For best results run this skill with the Fable 5 model — it is very smart and already knows a lot about products, pricing, and shops.

Research only. Never place orders, enter payment, address, or VAT/tax IDs, or create shop accounts. Remind the user; do not type those details for them.

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

## VAT and sales tax

Treat extra VAT/GST/sales tax as money to save, not as a dead end.

On any checkout, subscribe, or SaaS/plan screen — especially Stripe, and especially when VAT/GST/tax is a line item — remind the user **before they pay**:

- If they have a company, buy as a business.
- Enter the company VAT ID (EU VAT number, Polish NIP, GSTIN, or the local equivalent). For EU B2B digital goods this is reverse charge: VAT at checkout often drops to $0.
- Look for "purchasing as a business", "VAT number", "tax ID", or "add billing details". Currency toggles (USD vs local) do **not** remove VAT.
- Never suggest a VPN, a fake address, or a borrowed card.
- Never fill in the VAT ID, company name, or card yourself. Never write those values into this skill or any file.
- If tax is already $0 with a VAT ID, do not nag. If tax is still added, tell them to tick business + VAT ID.

Do not tell the user they "cannot avoid VAT" when a company VAT ID is the normal legal fix.

## How to research

Use your judgment. The goal is a confident answer, not a fixed procedure.

ALWAYS open with first impressions — before ANY web search, scrape, or deep research, no matter the item or its price. In one or two sentences, react to whatever the user provided (screenshot, link, description) from your own knowledge: does it look like a good deal, is the seller reputable, what is the typical price range — anything useful that comes to mind. The user must never sit waiting with nothing to read. If the screenshot is a checkout with VAT, say so in that first impression and remind them about the company VAT ID.

Extract the shopping intent early. Right after first impressions, make sure you know why the user is buying: what the item is for, who it's for, and what matters most to them (price, quality, delivery speed). Infer it from the conversation or screenshot when you can; if it's unclear and would change your recommendation, ask one short question. Knowing the real intent is how you help the user make the best possible purchase — not just find the lowest price.

Then scale research effort to the item's price. A cheap item researched for minutes is this skill failing its purpose:

- **Obvious call** — the screenshot or conversation already gives you enough to judge: answer right away. Zero searches, zero scrapes.
- **Cheap (roughly under $50)**: answer from your own knowledge — you already know what everyday items cost. At most ONE quick web search, and only if genuinely unsure. Scraping and deep research are forbidden in this tier. Respect the user's time above all: answer even more quickly, clearly, and concisely than usual.
- **Mid-range**: a few searches, scrape the listing and a top competitor or two.
- **Expensive ($1,000+)**: full depth — deep research, many search variants, scrape several shops and buyer reviews.

First impression example: "Cars of this brand and year usually go for €18-25k, so this looks slightly high — running a deep check to verify."

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
- On checkout/subscribe screens, one short VAT line: use a company VAT ID if they have one.
- Only quote prices you actually found. Say it plainly when results are thin.
- Don't report research costs unless the user asks.

Shape every answer like this:

```markdown
**Verdict: Overpriced — fair price is €280–€330, this listing asks €449.**

| Buy from | Price |
|---|---|
| [amazon.de](https://www.amazon.de/...) | €289 |
| [mediamarkt.de](https://www.mediamarkt.de/...) | €299 |

Skip shiny-deals24.shop — €99 for this item is a classic scam price.

VAT: if you have a company, tick business and enter the VAT ID before paying.
```

Success looks like this: the user found the right product quickly and bought it from a trusted, reputable shop at a good deal — not from an overpriced reseller or dropshipping store — and did not pay extra VAT they could legally reverse-charge.
