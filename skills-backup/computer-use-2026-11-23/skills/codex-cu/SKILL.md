---
name: codex-cu
description: Control the user's signed-in Brave browser and Mac apps from Claude Code through Codex Computer Use (the codex-cu MCP tools). Use when a Claude Code task needs real browser or desktop UI work via codex-cu, or when codex-cu is missing or broken.
---

# codex-cu

Claude Code's bridge to Codex Computer Use from the ChatGPT app. Claude Code only; Codex has its own native version.

## Tools

- `mcp__codex-cu__js` runs JavaScript with the `cua` API.
- `mcp__codex-cu__js_reset` clears the JS session. Tabs and apps stay as they are.

If they are deferred, load them with ToolSearch `select:mcp__codex-cu__js,mcp__codex-cu__js_reset`.

## Use

1. Make the first call exactly one API call, nothing else. It returns the full API docs. Read them.
   ```js
   await cua.getState();  // browsers, tabs, apps
   // or open a tab directly:
   let tab = await cua.createBrowserTab(browserId, url, { sessionName: "🔎 Task" });
   ```
2. Take browser IDs from `getState()`; don't hardcode them. The user's browser is Brave with the Codex extension.
3. Print text with `nodeRepl.write(...)`. `cua` calls print their own output.
4. Finish browser work within one reply. When your reply ends, the Stop hook ends the turn and closes tabs you opened.
   - `tab.markDeliverable()` keeps a tab the user should see.
   - `tab.markHandoff()` keeps a tab you will continue in a later turn.
5. Site permission prompts are the user's call. Never approve them on the user's behalf.
6. Don't run while a Codex agent drives the same browser.

## How it works

Files live in `<codex-cu-dir>/`; its README has status and commands.

- User MCP `codex-cu` in `~/.claude.json` runs `proxy.mjs` with the ChatGPT app's node, in front of Codex's `cua-repl.mjs`.
- The proxy adds `_meta["x-codex-turn-metadata"]` (`session_id`, `turn_id`) to every tool call. The browser side rejects calls without it.
- It hides the internal `turn_ended` and `js_add_node_module_dir` tools.
- It remembers the apps you allow in this Claude session and answers repeat "Allow Computer Use to use X?" prompts itself. Codex only remembers approvals for its own conversations.
- It listens on `~/.claude/codex-cu/<claude pid>.sock`.
- `stop-hook.sh`, a Stop hook in `~/.claude/settings.json`, walks up parent PIDs to that socket and sends `turn_ended`. The proxy calls the `turn_ended` tool, which releases this session's tabs, and starts a new `turn_id`.

## Troubleshooting

- **No codex-cu tools:** the session started before setup, or the entry is gone. Check `jq '.mcpServers["codex-cu"]' ~/.claude.json`, then start a new session.
- **"Missing required Codex turn metadata":** the entry bypasses the proxy. Its args must start with the path to `proxy.mjs`.
- **Broken after a ChatGPT app update:** re-register from the newest plugin version. If the folder is missing, ask the user to restart the ChatGPT app.
  ```sh
  d=$(ls -d ~/.codex/plugins/cache/openai-bundled/unified-computer-use/*/ | sort -V | tail -1)
  json=$(jq -c --arg proxy "<codex-cu-dir>/proxy.mjs" '.mcpServers.cua_repl | {type:"stdio", command, args: ([$proxy, .command] + .args), env}' "$d/.mcp.json")
  claude mcp remove codex-cu -s user && claude mcp add-json codex-cu "$json" -s user
  ```
- **Tabs never close:** the Stop hook is missing from `~/.claude/settings.json`.
- **Test without a new session.** This runs the js, fires the Stop hook, and shows the `turn_id` before and after:
  ```sh
  cd <codex-cu-dir> && /Applications/ChatGPT.app/Contents/Resources/cua_node/bin/node test-client.mjs run 'await cua.getState();'
  ```
