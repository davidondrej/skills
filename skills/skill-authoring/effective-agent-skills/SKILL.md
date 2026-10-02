---
name: effective-agent-skills
description: 'Write, review, and debug agent skills. Use when creating or editing SKILL.md files, improving skill structure, or diagnosing invocation and execution problems.'
---

# Effective Agent Skills

---

## 1. What agent skills are

An Agent Skill is a folder containing a `SKILL.md` file (YAML frontmatter + markdown instructions), plus optional subfolders for scripts, references, and assets that the agent loads on demand.

```
my-skill/
├── SKILL.md          # Required: metadata + instructions
├── scripts/          # Optional: executable code (CLIs, validators, helpers)
├── references/       # Optional: detailed docs loaded only when needed
└── assets/           # Optional: templates, fonts, static files
```

Agent Skills (agentskills.io) is an open standard. The folder and `SKILL.md` format are portable; optional behavior such as invocation control can be client-specific.

---

## 2. Why use skills

Skills package procedural knowledge and context for reuse:

- **Context efficiency** — instructions load only when relevant
- **Repeatability** — multi-step procedures become auditable workflows
- **Composability** — multiple skills combine at runtime per task
- **Portability** — same files work across vendors and surfaces

---

## 3. How they work — progressive disclosure

Three levels of loading:

**Level 1 — Discovery (~100 tokens per skill, always in context):**
The agent sees `name` + `description` first to decide whether the skill applies.

**Level 2 — Activation (<5,000 tokens, loaded on match):**
When the request matches, the agent reads the full `SKILL.md` body.

**Level 3 — Execution (unbounded, on demand):**
The agent reads references (`references/foo.md`) or runs scripts (`scripts/validate.py`) as needed. Running a script need not load its source into context.

Bundled files consume context only when their contents are loaded.

---

## 4. SKILL.md anatomy

```markdown
---
name: skill-name
description: What this skill does AND when to use it. Include trigger phrases the user will say.
---

# Skill Name

## Quick start
[Minimal working example]

## Workflow
[Step-by-step procedure with checklists]

## Output format
[What the user/agent should expect back]

## Advanced
[Link to references/ for rarely-needed detail]
```

Frontmatter constraints:
- `name` is lowercase, hyphens only, 1–64 chars, **exactly matches the parent folder name**
- Avoid `<` and `>` in frontmatter (they can inject into the system prompt)
- Invalid YAML silently prevents loading
- **Never put `: ` (colon + space) inside an unquoted `description`** — strict YAML parsers (e.g. Pi's) reject it as a nested mapping ("Nested mappings are not allowed in compact mappings"), even though lenient parsers (Claude Code) accept it. If the text needs a mid-sentence colon, single-quote the whole value and double any inner apostrophes: `description: 'Differentiator: finds gaps in the user''s knowledge.'`

### Manual-only invocation is client-specific

`disable-model-invocation: true` is **not** part of the core Agent Skills specification. It is a client extension supported by Claude Code and VS Code/Copilot. In those clients, put it in `SKILL.md` frontmatter to prevent automatic invocation while keeping explicit invocation available.

OpenAI Codex uses a separate file at `agents/openai.yaml` inside the skill:

```yaml
policy:
  allow_implicit_invocation: false
```

For a manual-only skill shared across Claude Code, VS Code/Copilot, and Codex, include both configurations. Never assume a client-specific frontmatter field works in every Agent Skills implementation; verify each target client's documentation and test implicit invocation in each runtime.

---

## 5. Two design philosophies

### Pattern A — Capability primitives (tool wrappers)
The skill is a thin wrapper over a deterministic CLI or script. Logic lives in code. SKILL.md teaches the agent how to invoke it.

- **Adds**: new capabilities (search, email, browser, API access)
- **Reliability via**: shell tools, not prompts
- **Typical length**: 30–80 lines, mostly command examples
- **Use when**: the bottleneck is "the agent can't do X"

### Pattern B — Process primitives (cognitive disciplines)
The skill encodes a methodology the agent should follow. Pure prompt engineering — no scripts needed.

- **Adds**: structured workflows (TDD, code review, design alignment, debugging loops)
- **Reliability via**: explicit procedure, checklists, validation loops
- **Use when**: the bottleneck is "the agent's output quality or process is bad"

---

## 6. How to write effective skills — do this

### Write descriptions for skill selection
The agent sees the name and description before loading the body. Describe **what the skill does + concrete tasks that should trigger it**.

- Aim for one or two short sentences. The 1,024-character limit is a ceiling, not a target.
- Put the main use case and important terms first; hosts may shorten descriptions.
- Name tasks, inputs, or file types users actually mention. Match intent, not just keywords.
- Add a boundary only when it prevents confusion with related skills.
- Keep workflow steps in the body. Avoid vague claims, catchalls, and lists of synonyms.

Pattern: `"[Capability]. Use when [specific tasks or situations]."`

Sources: [Agent Skills](https://agentskills.io/skill-creation/optimizing-descriptions) · [OpenAI](https://developers.openai.com/codex/build-skills).

### Keep SKILL.md lean
- Beyond a certain length, you're usually encoding logic that should be in a script or referenced file

### Bash-first, prose-second
Prefer concrete command examples with inline comments to lengthy prose.

### Push determinism into code
Anything fragile, repetitive, or where variation is a bug → script. Use markdown only for tasks requiring judgment.

### Match strictness to task fragility (degrees of freedom)
Scale instruction rigidity to how costly a wrong move is:
- **Loose natural-language heuristics** when many approaches are valid (e.g. code review).
- **Pseudocode or templates** when there's a preferred pattern but variation is acceptable (e.g. report format).
- **Exact scripts and strict step lists** when the workflow is fragile, error-prone, or consistency-critical (e.g. migrations, document patching).

### Build validation loops
State a verify → fix → re-verify loop explicitly.

- Document skills: visual QA pass before delivery
- Code skills: tests pass + zero type errors before completion
- Data skills: schema validation before output

### State-check before action
Don't assume setup is done. Instruct the agent to verify state, then branch:
```
First check if X is configured: [command]
If not, walk the user through setup: [steps]
```

### Just-in-time loading with explicit pointers
Tell the agent exactly when to read each referenced file:
```
For standard cases, follow the steps below.
For [specific edge case], read references/edge-cases.md first.
```

### Keep references one level deep
Link references directly from SKILL.md; nested chains risk partial reads and missed instructions. Add a table of contents to references longer than 100 lines.

### Document output formats
Show structured output examples so other tools can parse them reliably.

### Defer to --help for completeness
Show common operations in SKILL.md; use `tool --help` for the rest.

### Compose primitives, don't bundle workflows
Keep each skill to one capability or discipline; compose focused skills for larger workflows.

### Cite established principles when applicable
Name the source of established methods such as TDD, DDD, or red-green-refactor so agents and users can verify the intended approach.

### Persistent artifacts for cross-session memory
Skills can keep durable context in repo files (CONTEXT.md, ADRs, decision logs) for future sessions.

---

## 7. What not to do — anti-patterns

### Don't re-teach what the model already knows
Provide context the model lacks. Skip basic Python or Git tutorials; make every paragraph earn its place.

### Don't include human-facing docs
No README.md, no CHANGELOG.md, no INSTALLATION_GUIDE.md inside the skill folder. Skills are for agents.

### Don't write vague descriptions
- Bad: "A helpful skill for documents"
- Good: "Fill PDF form fields, extract form data, flatten completed PDFs. Use when the user mentions PDF forms, fillable forms, or programmatic field population."

### Don't bundle library code
If you need a parsing library, install via npm/pip. Don't paste source into the skill.

### Don't write monolithic mega-skills
Split skills that bundle design, planning, implementation, testing, and deployment.

### Don't assume the agent will infer
Be explicit about every step that matters.
- Bad: "Then deploy it."
- Good: "Run `npm run deploy:staging` and wait for HTTP 200 from /healthz before reporting success."

### Don't write style-only variants
A skill that just changes tone or formatting belongs in user preferences or a system prompt, not a skill.

### Don't ignore failure modes
For each fallible step, describe how to recognize failure and what to do.

### Don't include time-sensitive information
"As of Q4 2024..." rots fast. Fetch live data via script or omit.

### Don't use absolute paths
Always relative. Forward slashes regardless of OS. Use runtime placeholders for skill-directory references.

### Don't trust unfamiliar skills
Skills can run code, steer behavior, and leak data. Audit scripts, references, names, and access scope before use; follow the security checklist below.

---

## 8. Authoring workflow

1. **Identify the gap.** Run your agent on real tasks. Where does it consistently fail or need re-prompting? That's a skill candidate.
2. **Decide the pattern.** Capability primitive (need new tools) or process primitive (need better methodology)?
3. **Draft the description first.** What + when; add a boundary only if it prevents likely confusion.
4. **Write the smallest body that works.** Add only when testing reveals gaps.
5. **Move detail to references/ once SKILL.md grows too long.**
6. **Test triggering.** Use realistic requests and near-misses without naming the skill. Verify that its body actually loads.
7. **Test execution.** Invoke explicitly. If output is wrong, fix the body.
8. **Adversarial test.** Have another LLM ask: "What edge cases break this skill?" Patch the gaps.
9. **Version control.** Treat skills as code. Tag, branch, review.

---

## 9. Testing and debugging

- **Verify actual activation.** Inspect whether the runtime loaded `SKILL.md`; valid YAML or an agent's self-report is not proof.
- **Wrong or missed activation.** Check discovery and invocation settings, then adjust description scope and trigger wording.
- **Execution fails → body problem.** Add explicit steps, examples, or validation.
- **Use fresh sessions for trigger tests.** Some clients snapshot skills at startup.
- **Test against the weakest model you'll deploy on.** Stronger models forgive vague skills; weaker models expose them.
- **Test both directions.** Include realistic requests and near-misses sharing keywords that should not activate the skill. Repeat ambiguous cases and test new prompts to avoid overfitting.

---

## 10. Composition

Agents can combine skills for one task:

- **One skill = one concern.** Resist bundling.
- **Define interfaces between skills.** If skill A produces artifacts that skill B consumes, document the shape.
- **Share repo-level context.** Files such as AGENTS.md, CONTEXT.md, or settings.json can coordinate multiple skills without explicit handoffs.
- **Connect skills into useful workflows** such as align → spec → build → verify → refactor.

---

## 11. Security checklist

Before installing any third-party skill:

- Read every file in the folder
- Audit `scripts/` for outbound network calls, file access outside expected scope, command execution
- Check references for prompt injection ("ignore previous instructions...")
- Verify the skill name isn't typosquatting a popular one
- Run in a sandboxed environment first
- Pin to a specific version/commit, not `latest`

---

## 12. Ship checklist

Before publishing a skill:

- [ ] Frontmatter `name` matches folder name
- [ ] Description is concise, with capability and concrete triggers first
- [ ] Boundaries distinguish related skills where needed
- [ ] No human-facing docs inside the skill folder
- [ ] No time-sensitive information
- [ ] Relative paths only
- [ ] State-check before action where applicable
- [ ] Validation loop documented
- [ ] Output format documented if relevant
- [ ] Tested with weak and strong models
- [ ] Tested for both correct triggering and correct execution
- [ ] Skill does one thing
- [ ] Composes cleanly with related skills
- [ ] Version controlled
