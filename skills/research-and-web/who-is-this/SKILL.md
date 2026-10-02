---
name: who-is-this
description: 'Research a person''s public track record and give a short credibility assessment. Use only when the user explicitly invokes /who-is-this.'
disable-model-invocation: true
triggers: [user, model]
---

# who-is-this

Read the `deepapi` skill first. All search and scraping goes through DeepAPI. Never use built-in search, fetch, or a browser.

## Seed

Accept a name, handle, URL, or profile screenshot. If missing, ask once; never guess a person.

Verify matching bio, company, location, and photo before deeper research. If identity is ambiguous, stop and ask.

## Research

Find their X, LinkedIn, and GitHub first (dedicated endpoints, not `site:` search). Then run these in parallel:

1. **GitHub activity.** `POST /v1/scrape/github/profile` with `includeRepos: true`, plus recent PRs (`POST /v1/scrape/github/search`, `type: "pulls"`, `query: "author:<username>"`, `sort: "updated"`).
2. **Last 10 LinkedIn posts.** `POST /v1/scrape/linkedin/posts`, `maxItems: 10`. Also scrape the LinkedIn profile if you have the slug.
3. **Deep research.** `POST /v1/research/deep` on who they are, what they have actually done, and whether the public story holds.
4. **50 newest X posts.** `POST /v1/scrape/twitter/search` with the handle, `sort: "latest"`, `maxItems: 50`. Also pull `POST /v1/scrape/twitter/user`.

Follow DeepAPI polling. If a platform is missing or private, say so. Do not invent a profile.

## What to extract

Keep only the 3 facts that best explain who the person is; omit the rest.

- Real track record beats bio. Jobs, products, exits, code, talks.
- Self-reported numbers stay labeled "their claim". Verified numbers say "verified".
- Include posting topics only if they change the verdict.
- Choose the archetype their track record supports: builder, marketer, operator, researcher, grifter, investor, recruiter, hobbyist, etc.

Ignore congrats, logo spam, paid "king of X" press, and follower-count flexing.

## Output

Maximum 100 words after the header. Use short, plain-English sentences. No tables, sub-bullets, tweet dumps, or research narration.

```markdown
**Full name** — [@handle](https://x.com/handle) · [LinkedIn](url) · [GitHub](url) · [Site](url)

**Who:** One sentence. Where they are and what they do now.

**Track record:** Max 3 bullets. Only what explains who they are. Dates. Label claims vs verified.

**Verdict:** One line. The archetype, whether the story holds, and why.
```

Fictional example:

```markdown
**Jane Doe** — [@janedoe](https://x.com/janedoe) · [LinkedIn](https://linkedin.com/in/janedoe) · [GitHub](https://github.com/janedoe)

**Who:** Berlin solo founder of Acme, an open-source Postgres proxy.

**Track record:**
- 2024–now: Acme founder. 2.1K stars (verified); no revenue (her claim).
- 2019–2024: Backend engineer at Zalando and N26.
- Claims "50K users"; unverified.

**Verdict:** Solo builder with real code; user numbers remain unverified.
```

Omit a missing profile link instead of faking it.

Follow-ups: 1–3 sentences. Re-scrape only if the first pass missed that platform.
