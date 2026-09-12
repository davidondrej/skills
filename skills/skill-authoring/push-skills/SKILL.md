---
name: push-skills
description: Commit and push changes to the user's skills repo, including global AGENTS.md. Use after editing skills, or when the user says "push the skill", "push skills to github", "update the skills repo", or "publish code/AGENTS.md". Covers private commits and public mirror verification; use publish-skill for skill allowlisting.
---

# Push Skills

The canonical repo is `~/.agents`, with private remote `<private-skills-repo>`. Pushes to `main` trigger the sanitized public mirror at `davidondrej/skills`. Only the pipeline pushes to the public repo.

Only commit or push when the user requests it. Editing this skill is not permission to publish it. For distributed skill edits, follow `distribute-skill-to-all-agents` before pushing.

## Always include global instructions

The user's standing scope for an authorized `/push-skills` run includes saved changes to `~/code/AGENTS.md`, unless the user explicitly excludes that file. Check it on every run, even when the latest message names a skill. Preserve the conversation's original publishing objective through skill edits, renames, and other follow-up requests.

After fetching, compare the saved `global/AGENTS.md` with `origin/main:global/AGENTS.md`. A dirty local checkout may simply lag behind an already published commit; do not use local Git status alone to decide whether the saved content is committed. Transfer genuinely new edits while preserving upstream changes.

Before declaring completion, verify the saved global instructions are committed privately and the substantive updates appear in the public root `AGENTS.md`. Report that file's result separately from any skill publication. A successful skill push does not complete an AGENTS.md publishing request.

## Choose the source file

- `~/code/AGENTS.md` is a symlink to `~/.agents/global/AGENTS.md`. Save the editor buffer and confirm the link before committing. If the link differs, inspect both files before choosing the source; do not replace the link or overwrite either file as part of publishing. The public destination is root `AGENTS.md`.
- `~/.agents/AGENTS.md` contains private repo instructions. It is a different file and stays excluded.
- Updating global instructions needs no copy, skill allowlisting, or policy version bump.
- Skill edits live under `skills/<skill-name>/`. For a newly public skill, use `publish-skill` and include its policy changes in the same commit.

## Prepare without disturbing other work

Run Git in `~/.agents`, or the temporary worktree described below. Check both staged and unstaged changes:

```bash
git status --short
git diff --cached --stat
git diff HEAD -- global/AGENTS.md
git remote -v
git fetch origin main
```

Replace `global/AGENTS.md` with the exact intended paths for a skill update. Confirm `origin` is the private repo. Review outgoing commits as well as file changes; a push includes every commit ahead of `origin/main`.

- If the checkout is clean, fast-forward `main` with `git merge --ff-only origin/main`.
- If only the intended edits are pending, commit them, then rebase those intended commits onto `origin/main` before pushing.
- If there are unrelated edits, staged files, or local commits, use a clean temporary worktree based on `origin/main`: `git worktree add --detach <temporary-path> origin/main`. Leave the original checkout and index intact. Transfer only the approved changes as a patch against their original base, using three-way application where needed. Copy only approved new files separately. Preserve upstream edits; do not overwrite a newer file with an older full copy. Resolve conflicts from both versions; ask only if intent is ambiguous.

Do not stash, reset, unstage, or commit someone else's work.

## Commit and push

Stage only the intended paths. Plain `git commit` includes every staged file, even when the preceding `git add` names only one file. Use an explicit path list:

```bash
git add -- global/AGENTS.md
git commit --only -m "Update global agent instructions" -- global/AGENTS.md
```

Adapt the paths and message for skills. Review `git show --stat HEAD` and `git diff origin/main..HEAD` before pushing. If there is nothing new to commit, check whether the intended state is already pushed and continue with verification.

```bash
git push origin HEAD:main
source_sha=$(git rev-parse HEAD)
```

If the push is rejected because `main` advanced, fetch and rebase the isolated intended commits, review again, and retry. Never force-push. Confirm the remote contains the pushed commit; do not rely on a particular push-output label. If a temporary worktree was used, report that the original checkout was left untouched.

## Verify public publication

A private push alone does not prove publication. Find the workflow for the pushed commit:

```bash
gh run list --repo <private-skills-repo> --workflow public-mirror.yml \
  --commit "$source_sha" --json databaseId,headSha,status,conclusion,url
gh run watch <run-id> --repo <private-skills-repo> --exit-status
```

Wait for that run, not an older successful run. If a newer run supersedes it, confirm that run's source contains the intended change. The workflow can add a DeepAPI sync commit, so the public commit's `Source:` may name a descendant of your pushed commit. If the run fails, is cancelled without replacement, or remains stalled, inspect its status/logs and report publication incomplete with the run link. Do not rerun indefinitely.

Read the actual published file and confirm the intended update:

```bash
gh api repos/davidondrej/skills/contents/AGENTS.md \
  -H 'Accept: application/vnd.github.raw'
```

For skills, check `skills/<category>/<skill-name>/SKILL.md`; use the committed policy and published tree to find the category. Private-only skills need only private push verification.

The mirror may rewrite or omit content. A green workflow and an existing file are not enough: inspect the content. For missing or unexpected output, inspect that run's `public-mirror-report` artifact and `~/.agents/tools/public_mirror/README.md`. Report exclusions or failures accurately; do not bypass the sanitizer or add manual approval gates. Finish with the private commit, workflow result, and public file link when published.
