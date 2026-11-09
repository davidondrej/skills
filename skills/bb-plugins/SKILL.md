---
name: bb-plugins
description: 'Build, install, and debug bb plugins. Use when the user wants a bb plugin, a sidebar panel, a bb CLI subcommand, an agent tool, a theme, a provider, or to extend bb itself. For running threads and the core bb CLI, use bb-cli instead.'
---

# bb plugins

bb plugins are TypeScript packages that run inside bb. They are how bb extends itself.

Many first-party features are plugins: GitHub, Docs, Memory, Tasks, Connect, Automations, Secrets, Keep Awake, and the coding-agent providers.

## Trust

Plugins are full-trust. Server code runs in-process. App UI is same-origin page code, not a sandbox. Host workers run as Node on enrolled machines.

Review source before installing third-party plugins. Keep credentials in `secret: true` settings.

## This skill vs others

- Use this skill to create, install, or change a plugin.
- Use `bb-cli` to operate bb (threads, projects, environments).
- For exact API signatures, read the `bb-plugin-authoring` skill if it is available, then run `bb guide plugins`. In the plugin directory, run `bb plugin types` before trusting local SDK types. Do not guess from minified `dist/` files.

## Scaffold

```sh
bb plugin new hello            # add --app for a React UI
cd bb-plugin-hello
bb plugin install . --yes
bb plugin dev                  # rebuild + reload on save
```

The manifest is the `bb` object in `package.json`. Required: `bb.name`, `bb.description`, `bb.branding.icon`, `bb.server`. Optional: `bb.app`, `bb.host`, `bb.skills`, `bb.themes`.

Plugin id is the last package-name segment with a `bb-plugin-` prefix stripped. `bb-plugin-hello` and `@acme/bb-plugin-hello` both become `hello`.

Put runtime imports in `dependencies`. Leave types and tooling in `devDependencies`. Git installs run `npm install --omit=dev`.

## What a plugin can add

A default-export factory in `server.ts` receives `BbPluginApi` and registers surfaces:

- settings, kv + SQLite storage, HTTP, RPC, realtime
- background services and cron
- one top-level `bb <name> …` command
- agent tools, `skills/` folders, extra instructions
- mention providers
- optional host workers and experimental agent providers

`app.tsx` default-exports `definePluginApp` and can add pages, thread-panel actions, composer controls, file openers, and a replacement sidebar.

Do not copy the full API into this skill. Read `bb-plugin-authoring` when implementing a surface.

## Install and ship

```sh
bb plugin install .                                 # local path
bb plugin install github                            # bundled official plugin
bb plugin install npm:bb-plugin-notes@^1.0.0
bb plugin install git:https://github.com/acme/bb-plugin-notes.git@^1.2.0
bb plugin list
bb plugin reload <id>
bb plugin logs <id> -f
```

Installs prompt because the code is full-trust. Pass `--yes` to skip.

A failed managed update rolls back. Catalog refresh never installs code.

Community listings live at https://getbb.app/marketplace/v1/marketplace.json. Submit via a PR to https://github.com/get-bb/marketplace. Use the `submit-a-plugin` skill for that workflow.

## Check the work

1. `bb plugin list` shows the plugin `running`.
2. If it added a CLI, `bb <command> --help` works.
3. If it added UI, open the page or panel in bb and confirm it loads.
4. If the factory throws, the plugin is `error`. Read `bb plugin logs <id>` and fix, then `bb plugin reload <id>`.
