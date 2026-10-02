---
name: fireflies-transcript
description: Fetch raw Fireflies.ai meeting transcripts. Use only when the user explicitly invokes /fireflies-transcript; for YouTube, use youtube-transcript.
disable-model-invocation: true
---

# Fireflies Transcript

Fetch any meeting transcript from Fireflies.ai as raw text via GraphQL. Read-only.

## Auth (state-check first)

Configure your Fireflies API credential using the documented method (never commit or print it):

```bash
source "<credential-file>"   # exports API_KEY
[ -n "$API_KEY" ] || echo "MISSING KEY - stop and tell the user"
```

Every call is a POST to `https://api.fireflies.ai/graphql` with authentication configured according to Fireflies' API documentation and a JSON body `{"query": "..."}`.

## Step 1 - find the meeting id

```bash
curl -sS -X POST https://api.fireflies.ai/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ transcripts(limit: 25) { id title date duration } }"}' \
  | jq -r '.data.transcripts[] | "\(.id) | \(.title) | \(.date)"'
```

- `date` is epoch **milliseconds**. Convert on macOS: `date -r $((1784127600000/1000))`.
- The `transcripts(title:)` filter is EXACT-match — it returns `[]` for partial names.
  List recent meetings and grep locally instead.
- Ad-hoc meetings have no proper title (e.g. `Untitled - Wed, 15 Jul 2026 17:00:55 CEST`).
  Identify those by date/time, then confirm via content or speakers, not the title.
- Paginate older meetings with `skip:` (e.g. `transcripts(limit: 50, skip: 25)`).

## Step 2 - pull the raw transcript

```bash
QUERY='{ transcript(id: "MEETING_ID") { title sentences { speaker_name text } } }'
curl -sS -X POST https://api.fireflies.ai/graphql \
  -H "Content-Type: application/json" \
  -d "$(jq -nc --arg query "$QUERY" '{query: $query}')" \
  > /tmp/ff.json

# speaker-labeled raw text (usual deliverable)
jq -r '.data.transcript.sentences[] | "\(.speaker_name): \(.text)"' /tmp/ff.json

# bare text only
jq -r '.data.transcript.sentences[].text' /tmp/ff.json
```

Transcripts run to hundreds of sentences — save to a file, never dump to stdout/chat.

Optional extras on the same `transcript(id:)` query: `summary { overview short_summary keywords }`,
`participants`, `duration`, `meeting_link`.

## Failure modes

- `sentences: null` — recording still processing or no audio captured; nothing to pull.
- `errors[]` in the response instead of `data` — usually a bad field name; fix the query.
- 401/invalid key — key was rotated; ask the user for a new one (Fireflies dashboard:
  Settings -> Developer settings), update the configured credential file.

## Verify before reporting done

A pull is successful only if the sentence count is > 0 and the speakers/topic
match the meeting the user asked about — check the first few lines, don't trust the title alone.
