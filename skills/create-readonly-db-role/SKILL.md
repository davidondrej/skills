---
name: create-readonly-db-role
description: Set up read-only PostgreSQL access for agents. Use only when the user explicitly invokes /create-readonly-db-role.
disable-model-invocation: true
---

# Create a Read-Only DB Role for Agents

Prepare a SELECT-only role and protected connection. The SQL, role name, grants, denylist, RLS setting, timeouts, and connection steps are examples to adapt to your system, not live production configuration.

## Access model

1. **SELECT-only grants.** Grant no write permissions; use a denylist to exclude secrets and PII.
2. **Current and future tables.** Grant SELECT on all tables in `<application_schema>`, including future tables through default privileges, then revoke denylisted tables. Never grant the `<restricted_schema>` schema. New sensitive tables need a manual revoke.
3. **Soft guardrails.** Set `default_transaction_read_only = on` and a short `statement_timeout` suited to the workload.

**RLS:** tables may return no rows when the role has no applicable policy. Treat any mechanism that bypasses row-level security as a separate, high-risk access decision; grants and denylists do not replace row filtering.

## Workflow

1. **Check the role:** use your database's role catalog to check whether `<role_name>` exists. Use your chosen name; if it exists, update rather than recreate it.
2. **Agree on the denylist with the human.** Identify secret or PII tables agents must never see, such as credentials, webhook payloads, and identity tables.
3. **Save SQL in the repo**, e.g. `docs/database/create-agent-reader-role.sql`. Comment what changes, why, and how to apply, verify, and revert. Chat-only SQL is insufficient.
4. **The human applies it. Agents never run production DDL.** Use your provider's secure workflow for applying SQL and handling query history. The human stores the password in a password manager.
5. **Wire the connection** through a protected secret manager or local environment configuration; never commit it. Follow your provider's documentation for pooler usernames and connection settings. Install `psql` if missing (Homebrew `libpq` on macOS).
6. **Run every verification check below.**
7. **Create a project-local usage skill** covering key tables, query patterns, read-only access, and never pasting PII into commits or docs.

## SQL template

```sql
-- Example only. Replace placeholders and adapt the timeout and denylist for your system.

-- 1. role + soft guardrails
create role <role_name> with login password 'REPLACE_ME';
alter role <role_name> set default_transaction_read_only = on;
alter role <role_name> set statement_timeout = '10s';  -- example timeout; change as needed

-- 2. SELECT-only grants, denylist model
grant usage on schema <application_schema> to <role_name>;
grant select on all tables in schema <application_schema> to <role_name>;
alter default privileges for role <owner_role> in schema <application_schema>
  grant select on tables to <role_name>;   -- future tables auto-readable

-- 3. denylist: keep secrets and PII invisible (replace with your own tables)
revoke select on table <application_schema>.<sensitive_table_1> from <role_name>;
revoke select on table <application_schema>.<sensitive_table_2> from <role_name>;
```

Revert by removing privileges and the role using your database's documented process.

## Verification

All checks must pass before declaring done:

```bash
# Load the connection URL from your secret manager or local environment configuration.
psql "<readonly-connection-url>" -X -c "select current_user;"                          # -> chosen read-only role
psql "<readonly-connection-url>" -X -c "show statement_timeout;"                       # -> matches your chosen timeout
psql "<readonly-connection-url>" -X -c "select count(*) from <application_schema>.<table>;"  # -> real number, NOT 0
psql "<readonly-connection-url>" -X -c "delete from <application_schema>.<table> where false;"
# -> ERROR: read-only transaction (soft guardrail)
psql "<readonly-connection-url>" -X -c "begin; set transaction read write; delete from <application_schema>.<table> where false; rollback;"
# -> ERROR: permission denied (the hard wall)
psql "<readonly-connection-url>" -X -c "select * from <application_schema>.<denylisted_table> limit 1;"  # -> ERROR: permission denied
psql "<readonly-connection-url>" -X -c "select * from <restricted_schema>.<table> limit 1;"             # -> ERROR: permission denied
```

Verify both protections: writes fail under the read-only guardrail, and fail with `permission denied` when it is off. If any check fails, correct the configuration through the human and rerun all checks.

## Troubleshooting and maintenance

- **No rows across tables:** check RLS policies; do not bypass row-level security without an appropriate security review.
- **Write verification succeeds:** stop. Have the human revoke the role's privileges and correct the setup, then rerun all checks.
- **Connection authentication fails:** check the provider's documented pooler username and connection format.
- **Legitimate query times out:** add filters or limits before raising the timeout.
- **New sensitive table:** add a revoke to the denylist.
- **Password rotation:** have the human rotate the role password using the database's documented process and update the stored connection secret.
- Never allow agents to write through this role. Production writes remain human-only.
