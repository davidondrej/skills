---
name: pi-web-search
description: ONLY for Pi Agents — all other agents have their own web tools. How Pi accesses the web via the pi-web-access package — search, fetch URLs/PDFs/YouTube/GitHub. Use whenever a Pi task needs current info, docs, news, prices, or content from a specific URL.
---

# Web Search

The `pi-web-access` package is installed globally. Zero-config via Exa MCP (no API key), with fallback Exa → Perplexity → Gemini.

## CRITICAL: always pass `workflow: "none"`

Every `web_search` call MUST include `workflow: "none"`. This skips the interactive browser curator popup (the user does not want it opening). No exceptions — single query or batched `queries`, always set `workflow: "none"`.

```
web_search({ queries: ["query 1", "query 2"], workflow: "none" })
```

## Tools

- `web_search` — search the web; returns synthesized answers with citations. Can be called many times per turn. **Always pass `workflow: "none"`.**
- `code_search` — zero-key Exa code-context. Use for library/API/code lookups instead of generic `web_search`.
- `fetch_content` — fetch URL(s) → markdown; handles PDFs, YouTube, GitHub.
- `get_search_content` — big pages (>30k chars) are truncated in responses but stored in full; call this to pull the rest on demand so they don't blow context.

## fetch_content specifics

- **GitHub URLs are cloned, not scraped** — you get real files + a local path to explore with `read`/`bash` (private repos need the `gh` CLI). Use this for dev work.
- **PDFs** → auto-extracted to markdown in `~/Downloads/`, readable in sections (text-only, no OCR).
- **YouTube/video** → full raw transcripts + frame extraction. Needs a `GEMINI_API_KEY` (not zero-config); frame extraction also needs `ffmpeg`/`yt-dlp`.

## Routing — match the user's phrasing

Always use the `web_search` tool. These counts are HARD MINIMUMS — count your queries before answering and do not stop short:

- **"web search"** → **at least 2** queries, varied keywords/angles, then synthesize.
- **"extensive web research"** → **at least 4** queries, totally different keywords and angles.
- **"deep research"** → **at least 8** queries, totally different keywords and angles, run across 2–3 successive batches (refine angles after each batch), to learn as much as possible about the topic.

A single batched `web_search` call counts each query in `queries[]` toward the total. If your first batch is under the minimum, fire another batch before synthesizing.

## Fallback / alternative: DeepAPI web search

If the Exa → Perplexity → Gemini chain fails, or you need ranked results with URLs:

```bash
KEY=${DEEPAPI_API_KEY:-$(rg -o 'DEEPAPI_API_KEY=\S+' ~/.zshrc | head -1 | cut -d= -f2)}
curl -s --max-time 60 "https://deepapi.co/v1/search/web" \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -H "Idempotency-Key: $(uuidgen)" \
  -d '{"query": "your search terms", "maxResults": 5, "maxCostUsd": "0.05"}'
```

Results are in `.output` (title, url, snippet per item). Query under 500 chars. Full details: `deepapi` skill.
