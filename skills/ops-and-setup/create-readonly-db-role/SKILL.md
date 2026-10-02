---
name: create-readonly-db-role
description: Set up read-only PostgreSQL access for agents. Use only when the user explicitly invokes /create-readonly-db-role.
disable-model-invocation: true
---

# Create a Read-Only DB Role for Agents

Prepare a SELECT-only role and protected connection. The SQL, role name, grants, denylist, RLS behavior, timeouts, and connection steps are examples to adapt to your system, not live production configuration.

## Access model

1. **SELECT-only grants.** Grant no write permissions; use a denylist to exclude secrets and PII.
2. **Current and future tables.** Grant SELECT on all tables in `<application_schema>`, including future tables through default privileges, then revoke denylisted tables. Never grant the `<restricted_schema>` schema. New sensitive tables need a manual revoke.
3. **Soft guardrails.** Set `default_transaction_read_only = on` and a short `statement_timeout` suited to the workload.

**RLS:** tables may return no rows when the role has no applicable policy. Review row-level policies with the database administrator to ensure the role sees only the intended rows.

## Workflow

1. **Check the role:** `select rolname from pg_roles where rolname = '<reader_role>';`. Use your chosen name; if it exists, update rather than recreate it.
2. **Agree on the denylist with the human.** Identify secret or PII tables agents must never see, such as tables containing credentials, webhook payloads, and identity data.
3. **Save SQL in the repo**, e.g. `docs/<setup-file>.sql`. Comment what changes, why, and how to apply, verify, and revert. Chat-only SQL is insufficient.
4. **The human applies it. Agents never run production DDL.** In Supabase, paste the file into the SQL editor, then delete the query from its history because it contains the password. The human stores the password in a password manager.
5. **Wire the connection** through a protected secret manager or local environment configuration; never commit it. Supabase session poolers typically use `<role>.<project-ref>` on port 5432. Install `psql` if missing (Homebrew `libpq` on macOS).
6. **Run every verification check below.**
7. **Create a project-local usage skill** covering key tables, query patterns, read-only access, and never pasting PII into commits or docs.

## SQL template

```sql
-- Example only. Rename the role, schema, timeout, and denylist for your system.

-- 1. role + soft guardrails
create role <reader_role> with login password 'REPLACE_ME';
alter role <reader_role> set default_transaction_read_only = on;
alter role <reader_role> set statement_timeout = '10s';  -- example timeout; change as needed

-- 2. SELECT-only grants, denylist model
grant usage on schema <application_schema> to <reader_role>;
grant select on all tables in schema <application_schema> to <reader_role>;
alter default privileges for role <owner_role> in schema <application_schema>
  grant select on tables to <reader_role>;   -- future tables auto-readable

-- 3. denylist: keep secrets and PII invisible (replace with your own tables)
revoke select on table <application_schema>.<sensitive_table_1> from <reader_role>;
revoke select on table <application_schema>.<sensitive_table_2> from <reader_role>;
```

Revert: `drop owned by <reader_role>; drop role <reader_role>;`

## Verification

All checks must pass before declaring done:

```bash
# Load the connection URL from your secret manager or local environment configuration.
psql "<readonly-connection-url>" -X -c "select current_user;"                      # -> <reader_role>
psql "<readonly-connection-url>" -X -c "show statement_timeout;"                   # -> matches your chosen timeout
psql "<readonly-connection-url>" -X -c "select count(*) from <application_schema>.<readable_table>;"  # -> real number, NOT 0
psql "<readonly-connection-url>" -X -c "delete from <application_schema>.<any_table> where false;"
# -> ERROR: read-only transaction (soft guardrail)
psql "<readonly-connection-url>" -X -c "begin; set transaction read write; delete from <application_schema>.<any_table> where false; rollback;"
# -> ERROR: permission denied (the hard wall)
psql "<readonly-connection-url>" -X -c "select * from <application_schema>.<denylisted_table> limit 1;"  # -> ERROR: permission denied
psql "<readonly-connection-url>" -X -c "select * from <restricted_schema>.<identity_table> limit 1;"    # -> ERROR: permission denied
```

Verify both protections: writes fail under the read-only guardrail, and fail with `permission denied` when it is off. If any check fails, correct the configuration through the human and rerun all checks.

## Troubleshooting and maintenance

- **No rows across tables:** check RLS policies and consult the database administrator.
- **Write verification succeeds:** stop. Have the human revoke the role's privileges and correct the setup, then rerun all checks.
- **Supabase authentication fails:** check the pooler username, usually `<role>.<project-ref>`.
- **Legitimate query times out:** add filters or limits before raising the timeout.
- **New sensitive table:** add `revoke select` to the denylist.
- **Password rotation:** have the human run `alter role <reader_role> with password '...'` and update the stored connection secret.
- Never allow agents to write through this role. Production writes remain human-only.
