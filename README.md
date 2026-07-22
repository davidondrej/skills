# davidondrej-skills

skills my agents actually use, synced straight from my mac.

31 agent skills across 5 categories. each one packages a repeatable workflow into instructions an agent loads when the task calls for it. they run on claude code, codex, pi, and hermes.

## how to use

1. clone the repo.
2. copy any skill folder into your agent's skills directory:
   - claude code: `~/.claude/skills/`
   - codex: `~/.codex/skills/`
   - pi: `~/.pi/agent/skills/`
3. the agent picks it up automatically. invoke by name or let it trigger from the description.

every skill is a folder with a `SKILL.md` inside. the frontmatter `description` tells the agent when to fire. some skills ship extra reference files next to the `SKILL.md`. take whatever's useful.

## the skills

### agent-orchestration

running, scheduling, delegating to, and coordinating ai coding agents.

| skill | what it does |
| --- | --- |
| [agent-self-scheduling](skills/agent-orchestration/agent-self-scheduling/) | run an agent on a schedule, loop, or interval. cron, heartbeats, recurring autonomous checks. |
| [cmux](skills/agent-orchestration/cmux/) | control cmux workspaces, panes, and surfaces. delegate to and poll agents running in panes. macos only. |
| [codex-subagent](skills/agent-orchestration/codex-subagent/) | launch openai codex cli as a subagent for self-contained coding tasks. no api key needed. |
| [delegating-to-agents](skills/agent-orchestration/delegating-to-agents/) | pick the right agent for a task (pi, codex, claude code, hermes) and hand the work off cleanly. |
| [fable-safe-prompt](skills/agent-orchestration/fable-safe-prompt/) | rewrite a prompt so claude fable 5's safety classifiers don't flag it. minimal surgical edits only. |
| [goal-loop](skills/agent-orchestration/goal-loop/) | write effective `/goal` instructions for persistent plan, act, test, review agent loops. |
| [handoff](skills/agent-orchestration/handoff/) | compact the current session into one message a fresh agent can continue from. |
| [markdown-rendering](skills/agent-orchestration/markdown-rendering/) | open markdown in a cmux right pane without the blank-render bug. |
| [run-deep-swe](skills/agent-orchestration/run-deep-swe/) | score any model on the deepswe coding-agent benchmark via openrouter. |

### skill-authoring

creating, improving, distributing, and publishing agent skills.

| skill | what it does |
| --- | --- |
| [distribute-skill-to-all-agents](skills/skill-authoring/distribute-skill-to-all-agents/) | sync a skill across codex, claude code, pi, and hermes so every agent sees it. |
| [effective-agent-skills](skills/skill-authoring/effective-agent-skills/) | how to write skills that actually work. anatomy, patterns, anti-patterns, testing, security. |
| [folder-specific-claude-and-agents-md](skills/skill-authoring/folder-specific-claude-and-agents-md/) | give a folder its own claude.md and agents.md so future agents get scoped context. |
| [push-skill-to-github](skills/skill-authoring/push-skill-to-github/) | commit and push skill changes to the skills repo after creating or updating one. |

### research-and-web

finding and pulling information from the web, research apis, browsers, and youtube.

| skill | what it does |
| --- | --- |
| [browser-harness](skills/research-and-web/browser-harness/) | direct browser control via cdp. automate, scrape, and test against your running chrome. |
| [deep-research](skills/research-and-web/deep-research/) | full deep-research workflow via deepapi. builds the prompt, runs it, saves a cited report. |
| [deepapi](skills/research-and-web/deepapi/) | raw deepapi access for scraping and safe email. |
| [pi-web-search](skills/research-and-web/pi-web-search/) | web access for pi agents. search, fetch urls, pdfs, youtube, github. |
| [research-prompt](skills/research-and-web/research-prompt/) | write a single-paragraph deep research prompt with sub-questions and output format. |
| [youtube-transcript](skills/research-and-web/youtube-transcript/) | pull the transcript of any youtube video. deepapi first, yt-dlp fallback. |

### thinking-and-docs

structured thinking, interviewing, teaching, and turning ideas into documentation.

| skill | what it does |
| --- | --- |
| [brain-to-docs](skills/thinking-and-docs/brain-to-docs/) | extract project vision and decisions from your head into a readme and adrs through q&a. |
| [copywriting](skills/thinking-and-docs/copywriting/) | how david writes. applied to any text written on his behalf. |
| [grill-me](skills/thinking-and-docs/grill-me/) | relentless interview that stress-tests a plan until every branch of the decision tree is resolved. |
| [interview-style-doc-building](skills/thinking-and-docs/interview-style-doc-building/) | build a strategic doc one question at a time, patching the file after each answer. |
| [read-all-adrs](skills/thinking-and-docs/read-all-adrs/) | read every adr in docs/adr/ for full context on past decisions. |
| [short](skills/thinking-and-docs/short/) | compress the previous answer. cut filler, keep substance. |
| [teach](skills/thinking-and-docs/teach/) | teach a skill or concept through structured missions with a persistent learning record. |

### ops-and-setup

machine, server, security, and tool setup and operations.

| skill | what it does |
| --- | --- |
| [anti-sleep](skills/ops-and-setup/anti-sleep/) | keep a macbook awake with caffeinate, for a duration or while a process runs. |
| [cyber-audit](skills/ops-and-setup/cyber-audit/) | read-only exposure audit of your machine for a cve, breach, or malicious package. writes a report. |
| [pi-custom-model](skills/ops-and-setup/pi-custom-model/) | register a custom or variant model in the pi agent so it sticks as the default. |
| [setup-help](skills/ops-and-setup/setup-help/) | step-by-step setup walkthroughs. one step at a time, remaining steps always listed. |
| [vps-server-management](skills/ops-and-setup/vps-server-management/) | connect to, deploy on, and operate vps servers and the agents running inside them. |

## layout

```
skills/
  <category>/
    <skill-name>/
      SKILL.md        <- when to use it + how it works
      *.md            <- optional reference files
```

## license

mit. see [LICENSE](LICENSE).
