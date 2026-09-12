---
name: signal-from-expert
description: 'Compare the user''s notes with an expert''s work on a topic. Return relevant exact quotes, source locations, and at least one gap in the user''s thinking. Use only when /signal-from-expert is explicitly invoked.'
disable-model-invocation: true
triggers: [user, model]
---

# Signal from Expert

## Inputs

Require a **corpus** (files or folders of the user's thinking), **expert**, and **topic**. URLs are optional. Ask for missing inputs in one plain-text question.

## Workflow

### 1. Read the corpus

Read every named file in full with `cat -n`. Do not read other files for context.

### 2. Choose sources

Check `<repo>/essays/<expert-slug>/` for saved pieces. Load the `deepapi` skill; if the key is unset, run `source ~/.deepapi/env`. Make 5+ separate `POST /v1/search/web` calls, varying `<expert> <topic>` queries across essays, talks, interviews, and specific sub-questions. Pick the 5–8 most relevant pieces and merge with the user's URLs and saved sources.

Show titles and URLs, one per line, and ask "go?". Wait for approval before scraping.

### 3. Scrape and save

From the skill directory, fetch all URLs in one batch:

```bash
python3 scripts/fetch-sources.py --expert "Paul Graham" --out <repo>/essays/paul-graham \
  https://paulgraham.com/startupideas.html https://paulgraham.com/schlep.html
```

The helper saves each page as `NN-slug.md` with a header and verbatim text. Check every head/tail preview for the real first and last lines. Remove leftover layout junk without changing the prose.

If `<repo>/essays/AGENTS.md` is missing, copy `assets/essays-AGENTS.md` there and add the `CLAUDE.md` symlink.

### 4. Read all sources

Read every saved source in full with `cat -n` before writing; use its line numbers for citations.

### 5. Write the analysis

Use this format with 4 numbered items by default. Repeat the item block as needed, then end with the concluding paragraph:

```markdown
# DD-MM-YYYY — Signal from <Expert>

Corpus: <files>. Sources: `essays/<expert-slug>/` (N pieces). Agent analysis, not the user's words.

## 1. <Short claim; prefix with "Gap:" for a gap>

<Quote the user's relevant words and explain the connection in 1–2 lines.>

> "<Exact expert quote, 1–4 sentences>"

Full section: `essays/<expert-slug>/NN-slug.md:START-END`

**Co-founder read:** <One paragraph connecting the findings and what to do next.>
```

- Include at least one **Gap:** item showing where the expert's work challenges the user's thinking or reveals something missing, backed by a quote.
- Quote both people exactly; never paraphrase the user's reasoning. Keep expert quotes short and point to full passages in saved files.
- One claim per item. Plain English. No hedging. Exclude private personal matters unrelated to the topic.

### 6. Save and show

Save as `<corpus folder>/signal-<expert-slug>.md` (a single file's parent folder). Show the full analysis in chat. Do not commit.

## Failures

- Truncated source: rerun with a higher `--max-chars`.
- Poor search results: ask for URLs instead of guessing.
- Fewer than 3 sources: say so and ask; do not pad with weak pieces.
