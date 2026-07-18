---
name: never-publish-skill
description: 'Keep a skill out of the public skills mirror by adding it to neverPublishSkills in public-mirror-policy.json. Use when the user says "never publish this skill", "keep this skill private", "add to the never-publish list", or asks how the public mirror / never-publish mechanism works. Differentiator: this is about publish exclusion — for pushing skills to GitHub use push-skill-to-github.'
---

# Never-Publish a Skill

## How the public mirror works (30 seconds)

- `~/.agents` is the private repo `<owner>/private-skills`. A GitHub Action (`.github/workflows/public-mirror.yml`) publishes a **sanitized mirror** to the public repo `davidondrej/skills`.
- It runs on every push to `main`, every 6 hours (cron), and on manual dispatch. Fully autonomous — no human gates.
- Pipeline: deterministic excludes/rewrites → AI editor pass → AI reviewer pass → deny-regex scan → publish. Unsure files get omitted (fail-closed).
- `tools/public_mirror/mirror.py` drops any skill listed in `neverPublishSkills` (in `~/.agents/public-mirror-policy.json`) **before all other steps**. This is the only hard, deterministic guarantee a skill never goes public. The AI passes are for sanitizing skills that DO publish.
- `excludePaths` in the same policy handles non-skill paths (`tools/**`, `AGENTS.md`, etc.) — not what you want for skills. Skills go in `neverPublishSkills` by name.

## Add a skill to the never-publish list

All edits happen in `~/.agents/public-mirror-policy.json`:

1. Add the skill's folder name to the `neverPublishSkills` array:

```json
"neverPublishSkills": ["youtube-polls", "copywriting", "synology-nas", "composio-cli", "todoist", "<new-skill>"],
```

2. **Bump the top-level `version` field by 1.** Mandatory — a policy-version change forces a full mirror rebuild. That full rebuild is what retracts a skill that was ALREADY published (the publish step rsyncs with `--delete`, so the skill disappears from the public repo on the next run). Incremental runs cannot retract. One bump per commit covers multiple policy edits in that commit.

3. Validate the JSON:

```bash
python3 -c "import json; p=json.load(open('$HOME/.agents/public-mirror-policy.json')); print(p['version'], p['neverPublishSkills'])"
```

4. **Commit the policy change and the skill in the SAME commit.** Never let a private skill reach `main` in a push that doesn't also carry its never-publish entry — the workflow fires on every push. Do not push unless the user says to (then follow `push-skill-to-github`).

## Verify (after the user pushes)

```bash
# Workflow ran and succeeded
gh run list --repo <owner>/private-skills --workflow "Publish public skills mirror" --limit 1

# Skill is absent from the public repo (expect 404)
gh api repos/davidondrej/skills/contents --jq '.[].name' | rg -i <skill-name> || echo "NOT PUBLIC — correct"
```

The public repo nests skills as `skills/<category>/<skill>/`, so search the whole tree, not one folder. The run's `public-mirror-report.json` artifact lists every excluded/quarantined file.

## Gotchas

- Adding to `neverPublishSkills` without the version bump = an already-published skill **stays public**. The bump is not optional.
- The list matches the skill FOLDER name under `skills/`, exactly — not the frontmatter `name`, no globs.
- New publishable skills should also be added to `skillCategoryMap` in the same policy file (see `~/.agents/AGENTS.md`). Never-published skills don't need a category entry.
- Local edits do nothing until pushed. Publishing risk only exists on push to `main` — and the 6-hour cron re-publishes from the last pushed state, so a bad push self-repeats until fixed.
