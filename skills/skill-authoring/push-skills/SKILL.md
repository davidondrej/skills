---
name: push-skills
description: Push skills and global AGENTS.md to the private repo and verify the public mirror. Use only when the user explicitly invokes /push-skills.
disable-model-invocation: true
---

# Push Skills

Canonical repo: `<skills-repo>`. Private remote: `OWNER/PRIVATE_REPO`. Pushing `main` triggers the sanitized mirror at `davidondrej/skills`; only the configured publishing process pushes there.

Only commit or push when the user requests it. Editing this skill is not permission to publish it. For distributed skill edits, follow `distribute-skill-to-all-agents` before pushing.

## Always include global instructions

The user's standing scope for an authorized `/push-skills` run includes saved changes to `<workspace>/AGENTS.md`, unless they explicitly exclude that file. Check it on every run, even when the latest message names a skill. Preserve the conversation's original publishing objective through skill edits, renames, and other follow-up requests.

After fetching, compare saved `global/AGENTS.md` with `origin/main:global/AGENTS.md`. Local dirt may already be published; Git status alone cannot tell. Transfer new edits while preserving upstream changes.

Verify saved global instructions are committed privately and substantive updates appear in public root `AGENTS.md`. Report this separately; successful skill publication does not complete an AGENTS.md request.

## Choose the source file

- `<workspace>/AGENTS.md` should link to `<skills-repo>/global/AGENTS.md`. Save the editor buffer and verify the link. If it differs, inspect both files before choosing; do not replace the link or overwrite either file. Public destination: root `AGENTS.md`.
- `<skills-repo>/AGENTS.md` is a separate, private repo-instruction file and stays excluded.
- Updating global instructions needs no copy, skill allowlisting, or policy version bump.
- Skills live under `skills/<skill-name>/`. Use `publish-skill` for newly public skills; include policy changes in the same commit.

## Prepare without disturbing other work

Run Git in `<skills-repo>` or the temporary worktree below. Check staged and unstaged changes:

```bash
git status --short
git diff --cached --stat
git diff HEAD -- global/AGENTS.md
git remote -v
git fetch origin main
```

For skills, substitute the intended paths. Confirm `origin` is private. Review outgoing commits as well as files: every commit ahead of `origin/main` will push.

- Clean checkout: fast-forward `main` with `git merge --ff-only origin/main`.
- Only intended edits pending: commit, then rebase those commits onto `origin/main`.
- Unrelated edits, staged files, or local commits: use `git worktree add --detach <temporary-path> origin/main`. Preserve the original checkout and index. Transfer approved changes as a patch against their original base, using three-way application when needed; copy approved new files separately. Preserve newer upstream edits instead of overwriting with an old copy. Resolve conflicts from both versions; ask only when intent is ambiguous.

Do not stash, reset, unstage, or commit someone else's work.

## Commit and push

Stage only intended paths. Plain `git commit` includes all staged files regardless of the preceding `git add`; use an explicit path list:

```bash
git add -- global/AGENTS.md
git commit --only -m "Update global agent instructions" -- global/AGENTS.md
```

Adapt paths and message for skills. Review `git show --stat HEAD` and `git diff origin/main..HEAD` before pushing. If nothing needs committing, check whether the intended state is already pushed, then verify it.

```bash
git push origin HEAD:main
source_sha=$(git rev-parse HEAD)
```

If `main` advanced, fetch, rebase the isolated intended commits, review, and retry. Never force-push. Verify the remote contains the commit instead of relying on push-output labels. Report when a temporary worktree kept the original checkout untouched.

## Verify public publication

Find the publication workflow for the pushed commit; a private push alone does not prove publication:

```bash
gh run list --repo "$PRIVATE_REPO" --workflow "$PUBLISH_WORKFLOW" \\
  --commit "$source_sha" --json databaseId,headSha,status,conclusion,url
gh run watch <run-id> --repo "$PRIVATE_REPO" --exit-status
```

Wait for the matching run. If superseded, verify the newer source contains your change. The publishing process may add an automated sync commit, so public `Source:` can name a descendant of your commit. For failure, cancellation without replacement, or a stall, inspect status/logs and report incomplete publication with the run link. Do not rerun indefinitely.

Read the published file and confirm the intended update:

```bash
gh api repos/davidondrej/skills/contents/AGENTS.md \\
  -H 'Accept: application/vnd.github.raw'
```

Find skill categories from the committed policy and published tree, then check `skills/<category>/<skill-name>/SKILL.md`. Private-only skills need only private push verification.

The mirror may rewrite or omit content; green CI and file existence do not prove correctness. For missing or unexpected content, inspect the matching publication report artifact and the mirror tooling documentation in `<skills-repo>/tools/`. Report exclusions/failures accurately. Never bypass the sanitizer or add manual approval gates. Finish with the private commit, workflow result, and published file link.