---
name: read-prod-database
description: 'Query the production Supabase Postgres read-only via psql using the SELECT-only agents_readonly role. Use when debugging prod issues, investigating a user report, checking real usage/billing/retention numbers, or verifying data actually landed in prod. Usage/PMF numbers default to customer-only scope (David & team excluded, ADR 0175) and every answer must state which scope it used. Differentiator: this is LIVE prod data, read-only; for tests use the local Docker harness (npm run test:db) instead.'
---

# Read Prod Database (read-only)

Sanctioned read-only access to the production DeepAPI Supabase Postgres (ADR 0093). Writes are impossible for this role — never attempt them.

## Quick start

```bash
# env var lives in David's ~/.zshrc. NEVER `source ~/.zshrc` (breaks agent shells).
URL=${DEEPAPI_READONLY_DB_URL:-$(rg -o 'DEEPAPI_READONLY_DB_URL="([^"]+)"' -r '$1' ~/.zshrc)}

psql "$URL" -X -c "select count(*) from public.workspaces;"
```

State-check: `select current_user;` must return `agents_readonly`. If the env var is missing entirely, stop and ask the user.

## Scope: exclude David & team by default (ADR 0175)

Every usage/customer/PMF query runs in one of two modes. Pick one, on purpose, every time:

1. **Customer-only (DEFAULT)** — excludes David, the `@davidondrej.com` team, and dogfood/test workspaces.
2. **All workspaces** — includes internal usage. Only when the user explicitly asks, or for operational load / total-spend checks.

A workspace is internal when its ID is in `src/config/internal-workspaces.ts` (copy the current UUID list from there) or any `dashboard_workspace_members` email is on `@davidondrej.com`. Bolt this onto any workspace-scoped query:

```sql
-- customer-only scope: replace <uuids> with the list from src/config/internal-workspaces.ts
where sr.workspace_id <> all (array['<uuid-1>','<uuid-2>']::uuid[])
  and not exists (
    select 1 from public.dashboard_workspace_members m
    where m.workspace_id = sr.workspace_id
      and split_part(m.email, '@', 2) = 'davidondrej.com')
```

ALWAYS tell the user which scope each number uses — label results "customer-only (David & team excluded)" or "all workspaces (internal included)". Never present unlabeled or mixed-scope numbers.

## What you can and cannot see

- SELECT on ALL `public` tables, current and future (denylist model), all rows (role has `bypassrls`).
- Denylisted, always `permission denied`: `api_keys`, `email_webhook_events`, the whole `auth` schema. This is intentional — do not ask for access, work around it (e.g. join `service_requests.api_key_id`, not `api_keys`).
- Guardrails: every session is read-only, queries are killed after 10s.

## Discover schema, then query

```bash
psql "$URL" -X -c '\dt public.*'                    # list tables
psql "$URL" -X -c '\d public.service_requests'      # columns of one table
```

Schema source of truth in the repo: `src/db/migrations/*.sql`.

Key tables: `workspaces` (tenants), `service_requests` (every API call: status, cost, provider), `service_usage_events` (usage rollups), `credit_accounts` / `credit_ledger_entries` (money, immutable ledger), `credit_reservations` (holds), `rate_limit_counters`, `waitlist_signups`, `schema_migrations` (which migrations ran).

Useful patterns:

```bash
# recent requests for one workspace (route = endpoint, e.g. /v1/research/deep)
psql "$URL" -X -c "select id, route, status, created_at from public.service_requests where workspace_id = '<id>' order by created_at desc limit 20;"

# weekly returning workspaces (retention, ADR 0069) — PMF metric: apply the customer-only scope filter above
psql "$URL" -X -c "select date_trunc('week', created_at) w, count(distinct workspace_id) from public.service_requests group by 1 order by 1 desc limit 8;"

# did migration NNNN run on prod?
psql "$URL" -X -c "select version from public.schema_migrations order by version;"
```

## Failure modes

- `permission denied for table ...` → denylisted table (expected, see above).
- `canceling statement due to statement timeout` → your query is too heavy; add filters/limits, never retry the same query in a loop.
- Empty results you didn't expect → re-check with `select current_user` and confirm the table via `\dt`; do not assume the data is missing.
- Connection refused/auth failed → the URL or password changed; ask the user (password rotates via `alter role agents_readonly with password`).

## Hard rules

- READ ONLY. No INSERT/UPDATE/DELETE/DDL, no `set default_transaction_read_only = off`, no write workarounds. Prod writes go through the user (migration + `schema_migrations` recording).
- Query results contain real user data (emails, names, usage). Use them for analysis in chat, but NEVER paste PII or bulk data dumps into commits, PRs, docs, or code.
- Setup, maintenance, and rotation details: `docs/external/supabase-readonly-agent-db-access.md`. Role SQL: `docs/database/create-agents-readonly-role.sql`.
