---
name: github-outside-sandbox
description: Run Git and GitHub CLI commands through the host context when sandboxing blocks Keychain authentication, network access, or .git writes. Use for gh auth, repository or PR operations, and git index.lock or permission failures. Handles execution context only, not GitHub workflow design.
---

# GitHub Outside Sandbox

1. Start normally. Escalate only the blocked command and only within the user's authorization.
2. If sandboxed `gh auth status` fails, rerun it outside the sandbox before claiming authentication is broken. Never expose or copy tokens.
3. Run GitHub CLI network operations outside the sandbox when required: `gh repo ...`, `gh pr ...`, and related `gh` commands.
4. Run Git writes outside the sandbox when `.git` is outside writable roots or errors mention `index.lock` or `Operation not permitted`: `git add`, `git commit`, and `git push`.
5. Use the harness's official host-execution mechanism. In Codex, set `sandbox_permissions: "require_escalated"`, give a concrete `justification`, and use only a narrow safe `prefix_rule` when appropriate.
6. Never use shell wrappers, credential copying, or broad approval prefixes to bypass the sandbox.
7. Verify from the host context with `git status -sb`, `git remote -v`, and the relevant `gh ... view` command. Ask the user to authenticate only if the host-context check also fails.
