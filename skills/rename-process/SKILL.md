---
name: rename-process
description: Coordinate project or repository renames and moves involving Git, BB, services, or multiple machines. Preserve work and history while updating operational paths. Excludes ordinary file, code-symbol, and thread-title renames.
---

# Rename process

Finish the requested rename with the smallest verified set of changes. Use one coordinator working outside the directory being renamed. Keep existing approvals; ask only for missing decisions or authorization.

## Keep the scope small

- Touch only systems affected by the changed name or path. Keep unrelated Git pulls/rebases, cleanup, dependency updates, document reconciliation, and implementation separate.
- Preserve the existing repository, local work, ignored files, credentials, stashes, worktrees, and conversation identities. A repository split requires explicit scope for the new repository and its visibility/content.
- Keep product branding, domains, runtime/plugin identities, and historical documents unchanged unless their change is requested or necessary. Avoid bulk replacement of every old-name occurrence.
- Use current supported commands. Do not build a general migration framework, launch extra agents, or require a shutdown/database migration without a concrete need.

## Execute

1. **Confirm the map.** Record old/new names, exact real paths, Git remotes, repository identities/visibility, and affected machines. Inspect existing destinations, local changes, aliases, worktrees, services, and tool references. Resolve only missing scope; do not restart an already-approved naming discussion.
2. **Prepare once.** Choose the supported update route before moving anything. Save private inventories and suitable backups. Pause affected writers and file copies; release processes that hold the old root. Stage required service/configuration edits and check their originals have not changed. If BB is affected, read [BB path migration](references/bb-cutover.md).
3. **Move and update together.** Rename the real directory in place on the same filesystem. Never overwrite an independent destination or replace the existing private checkout with a fresh clone. Update remotes, tool references, necessary aliases, and service/configuration paths. Repair linked worktrees with `git worktree repair`; preserve missing registrations rather than pruning them.
4. **Verify affected use.** Compare work, refs, stashes, ignored state, and worktree links. Check the actual tool/service workflow at the new path, not just file existence or a running process. Distinguish pre-existing failures from new ones. Once relevant checks pass, finish; broaden testing only for unresolved failures.
5. **Close out.** Update current operational notes, resume paused work, and commit/push only within the authorized scope. Report completion, final paths/repository URLs, and any real remaining blocker. Separate completed changes from prepared ones.

## Reusing the old name

For an approved split, fix and verify every old remote, alias, and dependent path before creating the new repository or checkout under that name. Check canonical repository identities: an old GitHub URL can redirect to the renamed repository. Verify the new repository's visibility and allowed contents independently; never copy private history into a fresh core repository.

## If a check fails

Keep existing data intact and repair the specific broken reference. If rollback is needed, restore folders, configurations, and tool references together, then recheck access. Do not turn the rename into unrelated repair work.
