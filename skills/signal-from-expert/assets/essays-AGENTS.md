# Rules for essays/

Local contract for this folder. See the root `AGENTS.md` for repo-wide rules.

## What lives here

- Full raw text of classic essays the user wants their team and future trainees to read. Reference material, not the user's words.
- One subfolder per author, e.g. `paul-graham/`. One file per essay, numbered in reading order: `NN-essay-slug.md`.
- Each file starts with the title, source URL, author and scrape date, then the unedited text.

## Rules

- Never edit, summarize or trim the essay text. It is a verbatim copy of the source.
- The user's own takeaways from an essay go in `daily/` or `lessons/`, never in the essay file.
- Add essays with the `deepapi` skill (`POST /v1/scrape/website`), one call for all URLs.
