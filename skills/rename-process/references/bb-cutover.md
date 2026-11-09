# BB path migration

Read only when the rename affects BB projects, environments, threads, plugin paths, or the controller itself. Use the available bb-cli skill and current CLI help; resolve IDs from live state rather than copying an earlier migration.

## Choose the route before moving folders

- BB project/environment roots must be real directories. Compatibility aliases may serve other tools, but must not become BB roots.
- Updating a project source does not update existing environments or thread attachments. Inspect the saved remote, source paths, shared/archived environments, thread references, terminals, plugin paths, and affected background services together.
- For an individual running thread, use the supported self-directory switch and end that turn after success. Check current support for bulk and archived-thread operations. A tested offline migration of shared environment references can cover many threads without individual switches; prove this from the installed version's code and tests.
- Prefer supported administration. If required metadata cannot be updated through it, prepare one complete guarded offline migration. Never guess daemon endpoints or assume an old SQL file matches the current schema.

## Only if an offline migration is necessary

1. Prepare the complete change and rollback against a consistent disposable database copy. Test shared and archived thread resolution, retained provider IDs, worktree paths, repeat application, unexpected-state rejection, and rollback. Preserve history, credentials, archive state, and unrelated projects; do not rewrite historical event paths.
2. Obtain only missing approval for shutdown and database changes. Before stopping BB, verify an independent terminal and direct remote access. Arrange a maintenance runner outside BB that survives shutdown, records progress privately, restarts services/BB, and continues the same coordinator thread.
3. Pause all writers to the shared controller, including other projects when necessary. Preserve queued messages; release affected loaded runtimes and close affected terminals. Save which services were running and stop only those requiring maintenance. Coordinate resuming interrupted work.
4. Stop BB normally and verify that its database has no open writers. Take a fresh consistent backup outside the renamed directories. Pass the complete rehearsal on a copy of this final backup before applying the approved SQL offline. A changed-state guard failure requires inspection, not weaker checks.
5. Follow the tested order for physical moves, aliases, configurations, worktree repair, and metadata. Restart only previously running affected services and verify access before accepting normal work.

## Verify and recover

Check BB sources/environments and existing thread identities at the new roots. Exercise an archived thread through supported recovery and restore its archived state afterward. Check plugin calls and cloud setup readiness, including `bb cloud-repos` when that plugin exists. If stale host errors remain after the move, reload the existing plugin and recheck; a running label alone is insufficient. Preserve plugin identity and state rather than removing/reinstalling it.

Rollback before new traffic must restore the fresh maintenance backup, folders, aliases, configurations, and worktree links together. Never restore an old whole database over newer conversations. Once new writes have occurred, use a scoped forward repair.
