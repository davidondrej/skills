---
name: git-worktree
description: Use Git worktrees to isolate parallel coding tasks. Use when setting up a task checkout, working in a shared repo, or managing existing worktrees.
disable-model-invocation: true
triggers: [user, model]
---

# Git Worktrees for Parallel Agents

## Start here

Detect where you are before editing:

```bash
[ "$(git rev-parse --path-format=absolute --git-dir)" = "$(git rev-parse --path-format=absolute --git-common-dir)" ] \
  && echo "primary checkout" || echo "worktree"
```

- **Primary checkout** → create a task-named worktree, complete the setup below, and `cd` into it before editing.
- **Worktree** (including one created by Cursor) → proceed with the task.

## Working model

Worktrees have separate working files and branches but share Git history, stashes, config, and refs.

- **One task = one worktree = one agent session.** Never share a working directory between agents.
- Keep the primary checkout on main, only for review, merging, and pushing.
- Nothing auto-merges. The human reviews each diff before merging or discarding the worktree.
- Keep task branches local and short-lived. Push only main unless the user explicitly asks to push a task branch.
- Merge one worktree at a time. If main moved, rebase the task branch before merging.

## Creating and removing

```bash
git worktree add ../myrepo-task-x          # new worktree + branch "myrepo-task-x"
git worktree add ../fix-y -b fix-y main    # explicit branch off main
git worktree list                          # see all worktrees
git worktree remove ../myrepo-task-x       # delete when merged/abandoned
git worktree prune                         # clean up stale registrations
```

A branch can be checked out in only one worktree, including main.

In Cursor, use the Agents Window or `/worktree <task>`. `/apply-worktree` applies results to the main checkout; `/delete-worktree` discards them. `/best-of-n model1,model2 <task>` runs the same task in parallel worktrees, one per model. Cursor auto-deletes older worktrees, so preserve results promptly; pushing task branches still requires explicit approval.

## Complete the setup

A fresh worktree contains tracked files only. Bootstrap it before task work:

1. **Env/secret files** — copy `.env`, `.env.local`, and similar files from the primary checkout. Never symlink them: edits would change the originals.
2. **Dependencies** — install locally (`npm ci`, `pnpm install`, `uv sync`, `bundle install`). Never symlink `node_modules` from the primary checkout: bundlers such as Next.js/Turbopack reject paths outside the worktree. If it is a symlink, remove it with `rm -f node_modules` and install normally.
3. **Databases and services** — choose shared or per-worktree state. For shared services, pin their identity to avoid duplicate instances and port conflicts. For shared Docker Compose services, pin the project name, for example with a top-level `name:`; otherwise each worktree's folder name creates a separate project. Copy or re-seed per-worktree state such as SQLite files.
4. **Ports** — run dev/test servers and debuggers one at a time, or configure separate ports per worktree.
5. **Generated files and caches** — rebuild gitignored output in the worktree (`npm run build`, codegen).
6. **Git hooks** — `core.hooksPath` and `.git/config` are shared; verify hook scripts don't assume the primary checkout's path.

## Automate setup

In Cursor, `.cursor/worktrees.json` runs setup on creation (`$ROOT_WORKTREE_PATH` is the primary checkout):

```json
{
  "setup-worktree": [
    "npm ci",
    "cp $ROOT_WORKTREE_PATH/.env.local .env.local"
  ]
}
```

Otherwise, put the checklist in `scripts/setup-worktree.sh` and run it first in each new worktree. Find the primary checkout from a worktree with:

```bash
dirname "$(git rev-parse --path-format=absolute --git-common-dir)"
```

## Merge and clean up

```bash
# from the primary checkout, after reviewing the worktree's diff:
git merge --no-ff task-branch     # or: git merge --squash task-branch
git worktree remove ../myrepo-task-x
git branch -d task-branch
```

In Cursor, use `/apply-worktree`, then review and commit.

- Delete merged worktrees to reclaim their files and dependencies.
- Rebase or restart worktrees that have stalled for days.
- Commit early and often. Deleting a worktree loses uncommitted work; commits remain in the shared repository.
