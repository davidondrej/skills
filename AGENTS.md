# GLOBAL RULES
- this is a global instruction file
- it should NOT contain project-specific info

## RESPONSES
- Make ALL of your responses clear & very concise
- Use simple & easy-to-understand language
- write in short sentences, in plain English
- the User cannot see tool outputs, show him everything in text

## BEHAVIOR
- For local previews, use localhost
- for major product / architecture decisions, consult the User
- DO NOT use the multi-choice question UI. Ask the User in plain text.
- Never suggest that the user switch to Plan Mode, and never switch to it yourself

## CODE QUALITY
- NEVER mention development time (aka how long things will take)
- because of Agents, refactors & code changes that would take weeks, now take just MINUTES.
- ignore the cost of time, and instead focus on quality, simplicity, robustness, scalability
- keep the tech stack simple, popular, and maintainable
- prefer existing patterns, helpers, and conventions over new abstractions
- write simple, readable, modular code with clear ownership
- add comments only for non-obvious intent, tradeoffs, or constraints

## BUG FIXES
- When doing bug fixes, always start with reproducing the bug in an E2E setting
  as closely aligned with how an end user would experience it. This makes sure
  you find the real problem so your fix will actually solve it.
- Do not delete, skip, weaken, or narrow tests to make a task pass.
- Prefer behavior-focused tests over private implementation tests.

## DOCUMENTATION
- Keep docs concise, operational, and source-backed.
- write in plain, easy-to-understand English
- see the project’s `docs/` folder for project-specific documentation
- Do not bloat `AGENTS.md` or README files, only the user can add to them!!
- Ensure every important subfolder has its own `AGENTS.md` when it has durable
  ownership, contracts, commands, workflows, or rules that future agents need to
  follow.
- Parent `AGENTS.md` files should describe broad rules and child-doc indexes.
  Child `AGENTS.md` files should describe local contracts.

## ADRs
- Projects might have an `docs/adr/` folder
- ADRs contain important decisions for that project
- Keep ADRs short and clear. Record the context, the decision, and the
  consequences (use /adr-verbatim skill)
- follow this naming style:
  `docs/adr/0001-example-decision.md`.
- Do not rewrite old ADRs to hide history. If a decision changes, add a new ADR
  that supersedes or updates the old one
- Whenever a consequential, high-impact decision is being made, remind the User
  that it deserves a new ADR — but never write it yourself

## DATABASE
- NEVER EVER try to make any changes to the production Database yourself
- document every Database change with a clear .sql file
- save all sql migration files into `docs/database/` in that project
- in the comments, write what changed, why, how to apply, how to verify.
- if you need changes to Prod DB, ASK THE USER!

## OTHER CONTRIBUTORS
- many other Humans/Agents are working in this repo
- so DO NOT delete, revert or overwrite changes YOU did not make.
- be aware that the user is also working on this computer
- DO NOT open random browser tabs, or applications, without the user's explicit approval
- If unrelated changes appear, assume other actors made them
- When writing commit messages, NEVER EVER auto-add your agent name as co-author!

## GIT AND GITHUB
- the production branch is the "main" branch
- do not push to github by yourself
- when the User says “push to github”, do all the steps required to do so (no overthinking!)
- if you are in a worktree, you should copy the `.env` files from the Primary Checkout into the worktree

## SECRETS
- Never commit `.env` files, API keys, tokens, cookies, etc.
- Keep browser/client code limited to public or anon keys. Server-only secrets
  must stay server-side.
- Prefer project-specific `.env` files or a secrets manager for credentials.

## FINAL SELF-REVIEW
- Check the diff before declaring work done.
- Confirm the request is fully addressed and no unrelated changes were included.
- Mention any remaining risk, human decision, or follow-up that truly matters.
- make your messages simple, clear and very concise
- write in plain English

## PROJECT BASICS
- every project should have an `AGENTS.md` file at the root of that project (if missing, create it)
- each project must have a `.agents/` folder on root level of that project
- every project must also have `.claude/skills/` folder, which is an exact symlink to `.agents/skills/`
- for every single `AGENTS.md` file, there must be a `CLAUDE.md` symlink of it (if missing, create it)
- for open-source repos, add a root level `private/` folder, which is gitignored, where we can save .md files and other context that should not be visible to the public

## SPEED
- prioritize working fast & moving fast
- avoid overthinking at all cost
- encourage the User to do the obvious thing
- If something makes sense to run in parallel, to save time, RUN IT IN PARALLEL!
  Independent work runs IN PARALLEL by default. Sequential is the exception and
  needs a reason.
- if the next step is obvious, clear & safe -- JUST DO IT.
- tell the User clearly when he is your Bottleneck! be honest.

## DECISIONS vs EXECUTION
- for important Software Design or Architecture decisions, slow down, think through
  multiple alternatives
- use the "deepapi" skill to do multiple researches & scrapes, and work
  closely with the User to ensure he has complete understanding
- Execution: when the next step is obvious, do it. Do not overthink this.
- On complex topics, focus on educating & upskilling the User.

## SIMPLICITY & ANTI-BLOAT
- Aim for simplicity, elegance, and readability in code and docs.
- Prefer fewer files, lines, words, and abstractions when equally clear and correct.
- If fewer sentences communicate the same meaning, use fewer sentences.
- Every file, dependency, abstraction, and paragraph should earn its place.

## SKILLS
- global skills are in the global ~/.agents/skills folder
