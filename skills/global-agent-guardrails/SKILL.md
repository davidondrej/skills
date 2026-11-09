---
name: global-agent-guardrails
description: "Configure a shared guard against catastrophic shell commands in local AI agents. Use when changing block patterns, adding an agent or machine, or investigating why a command was or wasn't blocked."
---

# Global Agent Guardrails

Block catastrophic shell commands before execution. One patterns file can feed a shared hook script or native adapter for each agent. This guards against accidents, not malicious agents (obfuscation like `python -c "shutil.rmtree(...)"` can slip past regex).

[Cloudroom](https://www.cloudroom.dev/security) ships a built-in Command Guard based on this approach, on by default.

## File map

Organize the shared guard, its pattern list, tests, and any agent-specific adapters in an appropriate local configuration directory. Keep the patterns in one source of truth where possible.

## Check installation

Check that the shared guard and pattern list are present, then run the test suite after any pattern change. All tests should pass.

## Add or tune a pattern

1. Write patterns using POSIX ERE (`grep -E`). Use `[[:space:]]`, never `\\s` — adapters can convert `[:space:]` to `\\s` for JavaScript or Python and compile in multiline mode.
2. Add block and allow cases to the test suite, then run it; all must pass.
3. Verify that the pattern compiles in each adapter's regex engine.
4. Ensure consumers re-read patterns as intended. If an agent uses a separate native blocklist, keep it synchronized with the shared patterns.

Block only catastrophic commands (irreversible data loss, disk wipes, repo deletion). Recoverable local commands (`git status`, `git clean -fdx`, `rm -rf node_modules`) stay allowed; avoid over-blocking.

## Per-agent wiring

Use each agent's supported hook or native blocking mechanism. Configure it to call the shared guard or adapter at the appropriate pre-execution event, and merge settings into existing configuration rather than overwriting it. Use absolute paths in configurations when path expansion is inconsistent.

A generic hook configuration may look like:

```json
{"hooks": {"PRE_EXECUTION": [{"matcher": "SHELL_COMMAND", "hooks": [{"type": "command", "command": "/ABSOLUTE/PATH/TO/GUARD_SCRIPT"}]}]}}
```

Adapt event names, matchers, payload fields, and block responses to the agent's public documentation.

## Gotchas

- Some agents pin trust to a hash of hook configuration. After changing hook configuration, check whether the agent requires renewed trust.
- Some background or worker environments cannot execute local hook scripts. Check the agent's documented behavior and understand whether it fails open or closed.
- Plugin manifests and enablement settings vary by agent; validate them against current public documentation.
- A hook or adapter may fail open or fail closed when it encounters an error. Choose and test the behavior deliberately.
- Native deny and block lists may have different semantics; confirm whether a match requests confirmation or prevents execution.
- Ensure the guard correctly reads command text from each agent's documented payload format.
- Adapter regexes may require multiline mode so `^` matches each shell line like `grep`.
- **False-positive class:** a harmless command whose argument text contains a dangerous-looking string (e.g. passing a prompt mentioning `git push --force` on a CLI) gets blocked. Workaround: put the text in a file and reference it.
- Some agents or hosted environments may not support local command hooks. Check public documentation for current coverage and limitations.

## E2E verification

Use a safe probe in a temporary, non-git directory to check that a deliberately blocked command is stopped by the guard. A response indicating that the command was blocked means the guard works; an unrelated command error does not verify the guard.

For direct testing, pipe a representative hook payload containing a catastrophic command to the guard script and confirm it returns the documented block status. Run the test suite after any pattern change.
