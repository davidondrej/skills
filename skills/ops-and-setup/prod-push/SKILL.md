---
name: prod-push
description: 'Push to GitHub main and babysit the change until it is verifiably live in production, fixing CI and deploy failures along the way. Use when the user says "push", "push to github", "push to prod", "ship it", or "deploy". Differentiator: pushing requires the user''s explicit go-ahead; this is the procedure for AFTER they give it (this repo''s CI gate + Vercel promotion).'
---

# Prod Push

Only run this after the user explicitly told you to push. Never push on your own.

## How shipping works here

- Direct pushes to `main`. No PRs, no side branches.
- GitHub Actions `CI` (`.github/workflows/ci.yml`) always reports required `verify`. Typecheck and lint run for code; generated, browser, DB, and Windows checks run only for relevant paths. The full suite runs nightly.
- Vercel (project `deep-api`) owns the production build and builds EVERY `main` push — docs-only commits included (ADR 0161 removed the ignored-build rule; do not reconnect it). It promotes to Production only when `verify` is green. Prod serves `deepapi.co`.
- New CI runs on the same branch cancel in-progress ones (`cancel-in-progress: true`).

## Landing work from a worktree

Agents build in linked worktrees (`cursor/*`, `agent/*` branches); the loop below refuses to run there. To ship worktree work:

1. In the worktree: commit everything on your own branch. Never commit to `main` from a worktree.
2. In the primary checkout (`~/code/DeepAPI`): the tree must be clean (`git status --porcelain --untracked-files=no` prints nothing). If it is dirty with WIP that is not yours, stop and tell the user — never stash around it.
3. `git pull --rebase origin main`, then land YOUR branch: `git merge <branch>` (fast-forwards when possible), or cherry-pick its commits if the branch history is messy. One branch at a time — never land two agent branches in one pass.
4. Resolve any conflicts here in the hub, rerun the relevant checks, then continue the loop below at step 2.
5. After the push is verified live, leave the worktree and its branch in place — deleting them is always the user's decision, never yours.

## The loop

Repeat until the exact change is live.

```bash
# 0. Fail closed before touching Git. Ship only from the primary main checkout:
#    linked worktrees use their own branch's hook and may carry stale safety code.
[ "$(git branch --show-current)" = "main" ] || { echo "prod-push: not on main" >&2; exit 1; }
git_dir=$(git rev-parse --path-format=absolute --git-dir)
git_common_dir=$(git rev-parse --path-format=absolute --git-common-dir)
[ "$git_dir" = "$git_common_dir" ] || { echo "prod-push: linked worktree pushes are forbidden" >&2; exit 1; }
if git config --local --get-regexp '^user\.(name|email)$' >/dev/null; then
  echo "prod-push: unexpected local Git identity override" >&2
  exit 1
fi
if [ "$(git config user.name)" != "David Ondrej" ] || [ "$(git config user.email)" != "<email-address>" ]; then
  echo "prod-push: unexpected effective Git identity" >&2
  exit 1
fi
# If an incident is active and you are not the named recovery owner, STOP.
# Follow docs/runbooks/incident-response.md if you are the owner.
npm run incident:status

# 1. commit ONLY your files. WIP belongs in worktrees, never parked in this
#    primary checkout — it must be clean between pushes. Never `git add -A`,
#    `git add .`, or `commit -a`. If a file you touched also carries someone
#    else's unfinished edits, copy it aside (outside the repo), strip their
#    part, commit yours — and restore the copy only AFTER the push, because
#    step 2 requires a clean tree.
git add <your files> && git commit
[ "$(git log -1 --format='%an <%ae>')" = "David Ondrej <<email-address>>" ] || { echo "prod-push: unexpected commit author" >&2; exit 1; }

# 2. sync + push (other agents also commit to main)
# The pull requires a CLEAN tree. --autostash is BANNED here: replaying
# dirty edits onto fresh upstream commits creates UU conflicts and orphaned
# autostash entries (this bit us on 2026-07-25). If tracked dirt remains
# that is not yours, stop and tell the user — never stash around it.
[ -z "$(git status --porcelain --untracked-files=no)" ] || { echo "prod-push: tree not clean; commit yours or stop" >&2; exit 1; }
# The pre-push hook typechecks the EXACT pushed commit in a clean worktree.
# Incident recovery pushes still run the full suite. Never use `--no-verify`.
git pull --rebase origin main
git push origin main
if git config --local --get-regexp '^user\.(name|email)$' >/dev/null; then
  echo "prod-push: push introduced a local Git identity override; stop" >&2
  exit 1
fi
SHA=$(git rev-parse HEAD)

# 3. Find the CI run immediately, then let GitHub stream it to completion
RUN_ID=""
for attempt in 1 2 3 4 5 6; do
  RUN_ID=$(gh run list --workflow=ci.yml --branch=main --limit=10 \
    --json headSha,databaseId --jq ".[] | select(.headSha==\"$SHA\") | .databaseId")
  [ -n "$RUN_ID" ] && break
  sleep 5
done
[ -n "$RUN_ID" ] || { echo "prod-push: CI run not found" >&2; exit 1; }
gh run watch "$RUN_ID" --exit-status

# 4. CI green -> confirm Vercel promoted this exact commit.
# EVERY main push deploys (ADR 0161), docs-only commits included — always
# verify the deployment; never skip this on a "docs-only" judgment call.
gh api "repos/davidondrej/DeepAPI/commits/$SHA/status" \
  --jq '{state, vercel_logs: [.statuses[] | select(.context=="Vercel") | .target_url][0]}'
DEP=$(gh api "repos/davidondrej/DeepAPI/deployments?sha=$SHA&environment=Production&per_page=1" --jq '.[0].id')
gh api "repos/davidondrej/DeepAPI/deployments/$DEP/statuses" --jq '.[0].state'
# If promotion is still pending, poll every 10 seconds.

# 5. confirm prod is serving
curl -sS -m 15 https://deepapi.co/v1/health
```

Done = green CI plus a successful Production deployment and a healthy `GET /v1/health` for the exact SHA. Then report to the user what shipped.

## Active incident lane

Only the owner named by `npm run incident:status` may use this lane. Do not mix in unrelated work.

```bash
# Exactly one minimal recovery commit. The hook verifies that exact commit.
DEEPAPI_INCIDENT_RECOVERY=1 DEEPAPI_INCIDENT_OWNER=<owner> git push origin main
SHA=$(git rev-parse HEAD)
```

Track that exact SHA through CI, Production deployment, and health using the normal loop. Do not push a second recovery attempt until the first SHA has a terminal result. The user alone decides when recovery is proven and the freeze may be cleared; use the runbook's clearance command and commit only `.github/incident-freeze.json`.

## Failure modes

CI failed — get the exact failing step and output:

```bash
gh run view <databaseId> --log-failed
```

Reproduce locally (`npm run verify`, or just the failing step, e.g. `npm run typecheck`), fix it, commit, and restart the loop. The pre-push log is authoritative for the exact commit; a manual run checks the shared working tree and may include other agents' WIP. The new push gets a new `$SHA` — track that one.

- **CI green but Vercel status `failure`** — the Vercel build itself broke. Reproduce with `npm run build`. If it is Vercel-side (env vars, platform limits), stop and give the user the `vercel_logs` link — agents have no Vercel CLI or dashboard access, on purpose.
- **CI `conclusion: cancelled`** — a newer push superseded yours; your commit will never deploy on its own. Confirm the newer sha contains your change (`git merge-base --is-ancestor $SHA <newer-sha>`) and track that sha instead.
- **CI `conclusion: cancelled` during an incident** — stop. A forbidden newer push entered `main`; tell the user and identify its SHA before taking another recovery action.
- **Health returns `{"ok":false}` (HTTP 503)** — migration drift: deployed code expects a migration not yet applied to the prod DB. The deploy itself still succeeded. Agents can never write to prod — tell the user which migration to apply and stop looping.
- **Push rejected (non-fast-forward)** — someone pushed meanwhile. `git pull --rebase origin main` and push again.

## Hard rules

- NEVER push without the user's explicit go-ahead. Never force-push. Never push side branches.
- Never bypass or weaken CI to get green: no deleting/skipping tests, no `--no-verify`, no merging around a red check.
- `npm run smoke:prod` is user-only (spends real money). Your free prod check is `GET /v1/health`.
- If the change includes a DB migration, the user applies it to prod manually — expect health to stay red until they do, and say so in your report.
