---
name: create-readonly-db-role
description: Set up read-only PostgreSQL access for agents. Use only when the user explicitly invokes /create-readonly-db-role.
disable-model-invocation: true
---

# Create a Read-Only DB Role for Agents

Prepare a SELECT-only role and protected connection. The SQL, role name, grants, denylist, RLS setting, timeouts, and connection steps are examples to adapt to your system, not live production configuration.

## Access model

1. **SELECT-only grants.** Grant no write permissions; use a denylist to exclude secrets and PII.
2. **Current and future tables.** Grant SELECT on all tables in `public`, including future tables through default privileges, then revoke denylisted tables. Never grant the `auth` schema. New sensitive tables need a manual revoke.
3. **Soft guardrails.** Set `default_transaction_read_only = on` and a short `statement_timeout` suited to the workload.

**RLS:** tables may return no rows when the role has no applicable policy. Consider `bypassrls` only if it fits your security model: it skips row filtering, while grants and the denylist still apply.

## Workflow

1. **Check the role:** `select rolname from pg_roles where rolname = 'agent_reader';`. Use your chosen name; if it exists, update rather than recreate it.
2. **Agree on the denylist with the human.** Identify secret or PII tables agents must never see, such as credentials, webhook payloads, and identity tables.
3. **Save SQL in the repo**, e.g. `docs/database/create-agent-reader-role.sql`. Comment what changes, why, and how to apply, verify, and revert. Chat-only SQL is insufficient.
4. **The human applies it. Agents never run production DDL.** In Supabase, paste the file into the SQL editor, then delete the query from its history because it contains the password. The human stores the password in a password manager.
5. **Wire the connection** through a protected secret manager or local environment configuration; never commit it. Supabase session poolers typically use `<role>.<project-ref>` on port 5432. Install `psql` if missing (Homebrew `libpq` on macOS).
6. **Run every verification check below.**
7. **Create a project-local usage skill** covering key tables, query patterns, read-only access, and never pasting PII into commits or docs.

## SQL template

```sql
-- Example only. Rename the role, timeout, and denylist for your system.

-- 1. role + soft guardrails
create role agent_reader with login password 'REPLACE_ME';
alter role agent_reader set default_transaction_read_only = on;
alter role agent_reader set statement_timeout = '10s';  -- example timeout; change as needed

-- 2. SELECT-only grants, denylist model
grant usage on schema public to agent_reader;
grant select on all tables in schema public to agent_reader;
alter default privileges for role postgres in schema public
  grant select on tables to agent_reader;   -- future tables auto-readable

-- 3. denylist: keep secrets and PII invisible (replace with your own tables)
revoke select on table public.secrets from agent_reader;
revoke select on table public.private_events from agent_reader;

-- 4. only if RLS is enabled, no policy covers this role, and bypass fits your model
alter role agent_reader bypassrls;
```

Revert: `drop owned by agent_reader; drop role agent_reader;`

## Verification

All checks must pass before declaring done:

```bash
# Load the connection URL from your secret manager or local environment configuration.
psql "<readonly-connection-url>" -X -c "select current_user;"                      # -> agent_reader
psql "<readonly-connection-url>" -X -c "show statement_timeout;"                   # -> matches your chosen timeout
psql "<readonly-connection-url>" -X -c "select count(*) from public.<big_table>;"  # -> real number, NOT 0
psql "<readonly-connection-url>" -X -c "delete from public.<any_table> where false;"
# -> ERROR: read-only transaction (soft guardrail)
psql "<readonly-connection-url>" -X -c "begin; set transaction read write; delete from public.<any_table> where false; rollback;"
# -> ERROR: permission denied (the hard wall)
psql "<readonly-connection-url>" -X -c "select * from public.<denylisted> limit 1;"         # -> ERROR: permission denied
psql "<readonly-connection-url>" -X -c "select * from auth.<identity_table> limit 1;"       # -> ERROR: permission denied
```

Verify both protections: writes fail under the read-only guardrail, and fail with `permission denied` when it is off. If any check fails, correct the configuration through the human and rerun all checks.

## Troubleshooting and maintenance

- **No rows across tables:** check RLS policies; use `bypassrls` only if appropriate.
- **Write verification succeeds:** stop. Have the human revoke the role's privileges and correct the setup, then rerun all checks.
- **Supabase authentication fails:** check the pooler username, usually `<role>.<project-ref>`.
- **Legitimate query times out:** add filters or limits before raising the timeout.
- **New sensitive table:** add `revoke select` to the denylist.
- **Password rotation:** have the human run `alter role agent_reader with password '...'` and update the stored connection secret.
- Never allow agents to write through this role. Production writes remain human-only.
