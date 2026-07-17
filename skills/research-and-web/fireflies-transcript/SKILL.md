---
name: fireflies-transcript
description: 'Pull raw meeting transcripts from the user''s Fireflies.ai notetaker via its GraphQL API, using the key saved globally on this MacBook. Use when the user wants a call transcript, meeting notes, "what was said on the call", onboarding-call transcripts, or Fireflies data. Differentiator: Fireflies meeting recordings only — for YouTube videos use youtube-transcript.'
---

# Fireflies Transcript

Fetch any meeting transcript from Fireflies.ai as raw text via GraphQL. Read-only.

## Auth (state-check first)

The API key lives in `~/.fireflies/env` (mode 600, never commit or print it):

```bash
source ~/.fireflies/env   # exports FIREFLIES_API_KEY
[ -n "$FIREFLIES_API_KEY" ] || echo "MISSING KEY - stop and tell the user"
```

Every call is a POST to `https://api.fireflies.ai/graphql` with
`Authorization: Bearer $FIREFLIES_API_KEY` and a JSON body `{"query": "..."}`.

## Step 1 - find the meeting id

```bash
curl -sS -X POST https://api.fireflies.ai/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $FIREFLIES_API_KEY" \
  -d '{"query":"{ transcripts(limit: 25) { id title date duration } }"}' \
  | jq -r '.data.transcripts[] | "\(.id) | \(.title) | \(.date)"'
```

- `date` is epoch **milliseconds**. Convert on macOS: `date -r $((1784127600000/1000))`.
- The `transcripts(title:)` filter is EXACT-match — it returns `[]` for partial names.
  List recent meetings and grep locally instead.
- Ad-hoc meetings have no proper title (e.g. `david@... - Wed, 15 Jul 2026 17:00:55 CEST - Untitled`).
  Identify those by date/time, then confirm via content or speakers, not the title.
- Paginate older meetings with `skip:` (e.g. `transcripts(limit: 50, skip: 25)`).

## Step 2 - pull the raw transcript

```bash
curl -sS -X POST https://api.fireflies.ai/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $FIREFLIES_API_KEY" \
  -d '{"query":"{ transcript(id: \"MEETING_ID\") { title sentences { speaker_name text } } }"}' \
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
  Settings -> Developer settings), update `~/.fireflies/env`.

## Verify before reporting done

A pull is successful only if the sentence count is > 0 and the speakers/topic
match the meeting the user asked about — check the first few lines, don't trust the title alone.
