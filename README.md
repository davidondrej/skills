# Agent Skills

Open-source [Agent Skills](https://agentskills.io) by David Ondrej, for Claude Code,
Codex, Pi, and any agent that loads `SKILL.md` files.

Run them on cloud agents with [Cloudroom](https://www.cloudroom.dev), free and open source.

## Install

Requires Node.js. Run from your project, or add `-g` to install globally:

```bash
npx skills add davidondrej/skills                       # pick from all skills
npx skills add davidondrej/skills --skill deepapi -a claude-code
```

Or copy any `skills/<name>/` folder into your agent's skills directory.

## Layout

```text
skills/<name>/SKILL.md     instructions, with name + description frontmatter
skills/<name>/references/  optional docs the agent loads on demand
skills/<name>/scripts/     optional helper scripts
AGENTS.md                  David's global agent instructions
```

## Skills

- [`4x4`](skills/4x4/) — Pull 16 fast decisions out of the user with 4 sets of 4 open questions, then present an implementation plan.
- [`adr-verbatim`](skills/adr-verbatim/) — Record concise ADRs that preserve the user's decisions without conversational noise.
- [`anti-sleep`](skills/anti-sleep/) — Keep a Mac awake for a set duration or while a process runs.
- [`ask-then-build`](skills/ask-then-build/) — Clarify a feature, change, or refactor through questions, then write a build prompt for another agent.
- [`bb-cli`](skills/bb-cli/) — Use this when controlling bb.
- [`bb-plugins`](skills/bb-plugins/) — Build, install, and debug bb plugins.
- [`before-building`](skills/before-building/) — Fire the moment the user proposes a build.
- [`better-prompt`](skills/better-prompt/) — Rewrite a prompt into a deeper version of the same task, the way a top professional would approach it.
- [`boat`](skills/boat/) — Manage Boat (boat.dev, formerly Box by Ascii) cloud sandboxes via API, CLI, and SSH.
- [`browser-harness`](skills/browser-harness/) — Direct browser control via CDP.
- [`browser-use`](skills/browser-use/) — Direct browser control via CDP for web interaction: automation, scraping, testing, screenshots, and site/app work.
- [`cmux`](skills/cmux/) — Control the cmux macOS terminal app: workspaces, panes, surfaces, browsers, notifications, settings, and hooks.
- [`codex-subagent`](skills/codex-subagent/) — Launch OpenAI Codex CLI as a subagent (ChatGPT subscription auth, no API key).
- [`cua-driver`](skills/cua-driver/) — Use Cua Driver for desktop or browser tasks that are awkward or unavailable through Bash/APIs, or when the user explicitly wants GUI interaction: app testing, visual bug reproduction, form filling, calendar entry, screenshots, and demo recording.
- [`decisions`](skills/decisions/) — Ask the agent to list all choices it made during the current work that it is not confident of.
- [`deep-research`](skills/deep-research/) — Run deep research through DeepAPI and save a report with sources.
- [`deep-scrape`](skills/deep-scrape/) — Build sourced JSON dossiers on people, companies, or topics with DeepAPI.
- [`deepapi`](skills/deepapi/) — Use DeepAPI for all web search, deep research, and web scraping (websites, LinkedIn, GitHub, X/Twitter, YouTube, Instagram) instead of built-in search, research, fetch, or browser tools.
- [`designs`](skills/designs/) — Show 4 better, new design options as separate real image renders of the actual app UI.
- [`domain-checker`](skills/domain-checker/) — Check domain registration in batches using public RDAP APIs, without keys or login.
- [`effective-agent-skills`](skills/effective-agent-skills/) — Write, review, and debug agent skills.
- [`fable-review`](skills/fable-review/) — Launch an independent Fable code review and return it verbatim.
- [`fable-safe-prompt`](skills/fable-safe-prompt/) — Make minimal prompt edits to reduce false-positive refusals from Fable.
- [`file-tree`](skills/file-tree/) — Manually-invoked skill that prints a nice file tree of the current topic in a code block.
- [`fireflies-transcript`](skills/fireflies-transcript/) — Fetch raw Fireflies.ai meeting transcripts.
- [`gemini-review`](skills/gemini-review/) — Launch an independent Gemini 4 Carbon code review through Cursor at High reasoning and return it verbatim.
- [`git-worktree`](skills/git-worktree/) — Use Git worktrees to isolate parallel coding tasks.
- [`github-outside-sandbox`](skills/github-outside-sandbox/) — Run Git and GitHub CLI commands on the host when sandboxing blocks Keychain auth, network access, or .git writes.
- [`global-agent-guardrails`](skills/global-agent-guardrails/) — Configure the shared guard against catastrophic shell commands in local AI agents.
- [`goal-loop`](skills/goal-loop/) — Draft /goal prompts and explain persistent agent loops.
- [`gpt-review`](skills/gpt-review/) — Launch an independent GPT-6-Astra code review and return it verbatim.
- [`handoff`](skills/handoff/) — Capture session context for a fresh agent.
- [`herdr`](skills/herdr/) — Operate and coordinate AI agents in Herdr workspaces in Ghostty.
- [`image-prompt`](skills/image-prompt/) — Write four distinct prompts for AI image models.
- [`keep-track`](skills/keep-track/) — Keep track of open topics and decisions.
- [`kimi-review`](skills/kimi-review/) — Launch an independent Kimi K3.1 Pro Max code review and return it verbatim, falling back across harnesses and routes until one works.
- [`larp-detector`](skills/larp-detector/) — Skeptical review of outside contributions to public repos.
- [`muse-review`](skills/muse-review/) — Launch an independent Meta Muse Wonder Max code review through Pi and OpenRouter, and return it verbatim.
- [`nagent`](skills/nagent/) — Launch a new bb worker thread with the right project, model, worktree, and task brief.
- [`occams-razor`](skills/occams-razor/) — Stop overthinking and answer with what we actually know for sure, how you know, and a confidence %.
- [`openrouter`](skills/openrouter/) — Design, build, debug, and optimize OpenRouter API integrations.
- [`persistent-localhost`](skills/persistent-localhost/) — Manage persistent dev servers, APIs, and other local processes on a port using macOS LaunchAgents.
- [`prompt-for-others`](skills/prompt-for-others/) — Write a prompt teammates can give their AI agents to apply a fix, upgrade, or setup change.
- [`read-all-adrs`](skills/read-all-adrs/) — Read every ADR markdown file in the project's docs/adr/ folder so you have full context on past decisions.
- [`remind`](skills/remind/) — Rewrite the last response simpler and shorter in plain English, prefixed with a 3-5 sentence TLDR of the conversation so far.
- [`rename`](skills/rename/) — Manually-invoked skill that renames the current thread or session to 2-5 lowercase descriptive words.
- [`rename-process`](skills/rename-process/) — Coordinate project or repository renames and moves involving Git, BB, services, or multiple machines.
- [`repo-sync`](skills/repo-sync/) — Manage automatic Git syncing on macOS with repo-sync.
- [`risky-changes`](skills/risky-changes/) — Verify assumptions before implementing large or risky changes to APIs, provider data, billing, pricing, quotas, or defaults.
- [`self-archive`](skills/self-archive/) — Archive the current Cloudroom thread and release its runtime.
- [`setup-help`](skills/setup-help/) — Guide setup one step at a time and show what remains.
- [`state`](skills/state/) — Manually-invoked skill that recaps what the current thread is doing and how far along it is.
- [`stop-overthinking`](skills/stop-overthinking/) — Manually-invoked skill that stops overthinking and forces a short, practical decision.
- [`total-review`](skills/total-review/) — Run five independent max-effort reviews (Fable 5.1, Opus 5.5, GPT-6 Astra, GPT-6.1 Sol, Muse Wonder), merge their findings, and fix only what the user approves.
- [`varied-search`](skills/varied-search/) — Research a topic across the web, GitHub, and X/Twitter with DeepAPI and produce a concise Markdown report.

## Contributing

This repo is generated from a private source repo and overwritten on every publish,
so pull requests can't be merged.

## License

[MIT](LICENSE)
