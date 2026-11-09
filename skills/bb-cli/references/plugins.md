# Plugin management commands

## Plugins

- A bb plugin is a TypeScript package running inside the bb server, extending
  it with services, schedules, HTTP/RPC endpoints, settings — and `bb` CLI
  subcommands that agents run through bash like any other command.
- Use `bb plugin list` to inspect installed plugins and their current state.
- The builtin Concurrency limit plugin exposes
  `bb concurrency-limit status [--json]`,
  `bb concurrency-limit global [unlimited|<limit>] [--json]`, and
  `bb concurrency-limit host <host-id> [auto|<limit>] [--json]`. Automatic
  host limits allow one thread per available processor.
- **BB plugin catalog** (store under `/api/v1/plugin-catalog`):
  - The store lists the **BB Community marketplace** catalog: a manifest
    the server re-reads at startup and every two hours from
    `https://getbb.app/marketplace/v1/marketplace.json`
    (override with `BB_MARKETPLACE_URL`, which the server reads only at
    startup). Its entries install from their listed
    git or npm source through the normal install pipeline. A refresh only
    updates discovery metadata and icons; it never installs, updates, or runs
    plugin code, and a failed refresh keeps the last catalog bb validated.
  - `bb plugin search <query> [--json]` — search the catalog by id,
    name, description, category, or tag; status shows installed / compatible /
    requires newer bb. An **Installs** column appears once the curated
    marketplace's `stats.json` sidecar has been read (`installs` in `--json`,
    null when unknown): anonymous-telemetry install counts for published
    entries.
- **Third-party marketplaces** (routes under `/api/v1/marketplaces`):
  - `bb marketplace add <source>` — add a marketplace from an https manifest
    URL, `git:<url>[@<ref>]` (bb reads `marketplace.json` from the checkout),
    or `path:<directory>`. The CLI resolves a relative path from its current
    directory before it sends the request. BB validates the
    manifest, caches the catalog, and fetches its icons. **Adding a
    marketplace installs nothing.** The manifest's own `name` is the
    marketplace's identity, so a name collision is refused; `bb-community` is
    reserved and can be neither added nor removed.
  - `bb marketplace list [--json]` — name, source, entry count, last refresh.
  - `bb marketplace refresh [name] [--json]` — re-read one catalog or every
    one of them. Discovery metadata and icons only. A failed refresh keeps the
    last catalog bb validated and exits non-zero.
  - `bb marketplace remove <name> [--json]` — forget a marketplace. Its
    catalog rows and cached icons are deleted; every plugin it listed keeps
    running as a direct install with its full source intent and exact
    resolution, so `bb plugin outdated`/`update` keep working from the
    recorded source.
  - Install a specific marketplace's entry with
    `bb plugin install <entry-id>@<marketplace>`. A bare entry id resolves
    across every marketplace. Exactly one match installs. Several matches fail
    and list the `id@marketplace` choices.
  - Installing from a marketplace other than `bb-community` first resolves and
    prints the true source — npm package with its range or dist-tag, or git
    URL with its ref or semver range, subdirectory, and the exact release tag
    and commit that range currently lands on — plus the marketplace and the
    entry's author. `--yes` skips the prompt, not the resolution. The install
    fails if the listing or its resolved git commit changes after confirmation.
- Commands:
  - `bb plugin install <src>` — `<entry-id>@<marketplace>`, an HTTP(S) Git
    repository URL, a local path,
    `git:<url>[@<ref|semver-range>]`, or `npm:<package>[@<version|tag|range>]`
    (npm on PATH required for `npm:`). Repository URLs and prefixes `path:` /
    `npm:` / `git:` skip catalog resolution. To pin or
    range an npm package, install with `npm:<package>@…`.
    Omit the npm spec to track compatible stable releases; ranges and dist-tags
    track, while exact versions are pinned. Omit the Git ref to track the
    repository's default branch; explicit branches track, while tags and
    commits are pinned. A Git semver range
    (`git:github.com/acme/repo@^1.2.0`) tracks the repository's `vX.Y.Z` tags,
    picking the highest release the range allows and excluding prereleases
    unless the range names one. `--tag-prefix <prefix>` ranges over
    `<prefix>vX.Y.Z` tags instead, for a repository that versions each plugin
    on its own. bb records the selected tag and its commit and refuses to
    resolve that tag again if it moved. A bare spec that reads as a range
    resolves over tags only when no branch or tag has that literal name; when
    both exist the install fails — write `@semver:<range>` or `@ref:<name>`.
    Installs prompt for confirmation (plugins are full-trust code);
    pass `--yes` to skip. Reinstalling an already-installed managed plugin is
    refused — use `bb plugin update`. Installing a local path for an id that
    is already installed from another local path moves the plugin to the new
    directory and keeps its settings, secrets, and schedules. Plugins that
    declare a frontend (`bb.app`) are built at install time for path sources
    and git sources without a prebuilt app when their imported dependencies
    are already available;
    git/npm packages can also ship a metadata-validated prebuilt `dist/`, and
    npm packages must. Managed git/npm installs refuse `engines.bb` /
    `engines.bbPluginSdk` mismatches, manifest vs. artifact identity mismatches,
    and reserved ID mismatches.
    A `git:`/`path:` repository can hold several plugins. Install one with
    `--subdirectory <relative-path>`, or with `--plugin <name>` to resolve an
    entry of the repository's `.bb/plugins.json` collection manifest (the two
    flags are mutually exclusive, and neither applies to `npm:` sources).
    Installs from one repository and commit share a single checkout.
    A repository that has a collection manifest and is not a plugin itself
    refuses an unselected install and lists its entry names.
  - `bb plugin outdated` — check installed plugins for compatible updates
    (table; `--json` for raw results). Shows latest compatible candidate and
    any blocked incompatible newer release. Dev builds (bb `0.0.0`) annotate
    that `engines.bb` is not enforced.
  - `bb plugin update <id>` / `bb plugin update --all` — apply compatible
    updates for tracking sources, including newer tags that satisfy a Git
    semver range. Same full-trust confirmation as install (`--yes` skips;
    non-TTY refuses without it). Use `bb plugin outdated` to preview available
    updates. Changing a pinned git:/npm: source requires `bb plugin remove`
    (which deletes the plugin's settings, secrets, and schedules) and a fresh
    install. A local path plugin is never removed to change it: edit it in
    place and `bb plugin reload <id>`, or `bb plugin install path:<new dir>`
    to move it; both keep its configuration.
  - `bb plugin list` — status, background services, schedules, handler timings,
    and each plugin's contributed `bb` command.
  - `bb plugin source <id> [--json]` — requested and resolved source, the
    repository subdirectory for a nested plugin, the semver range with its tag
    prefix and resolved tag for a Git range install, engine ranges, install
    time, integrity/registry details, and recent activation history.
  - `bb plugin enable|disable <id>`, `bb plugin reload [id]` (exits 1 when a
    reloaded plugin does not come up on its current sources: the previous
    instance was kept, or it is degraded because a service ignored its abort),
    `bb plugin remove <id>` (deletes the plugin's settings, secrets, and
    schedules; managed git/npm files are deleted, and local path sources stay
    on disk).
  - `bb plugin config <id> [set <key> <value> | unset <key>]` — declared
    settings. Reload the plugin after configuring (`bb plugin reload <id>`).
  - `bb plugin token <id>` — print a short-lived bearer token for that plugin.
  - List, reload, enable, disable, config, and remove support `--json`.
  - `bb plugin logs <id> [-n N] [-f]` — the plugin's `bb.log` output.
  - `bb plugin run <id> [args...]` — explicit form; collisions log an activation
    warning and are annotated by `bb plugin list`.
  - `bb plugin new <name>` — scaffold a todo-list plugin (`server.ts`,
    `app.tsx` with a sidebar page, a `bb <name>` CLI command, a skill, and
    vendored UI components) and install its npm dependencies (scaffold sets
    `engines.bbPluginSdk` to `>=0.4.3`). The
    scaffold depends on `@get-bb/plugin-sdk`, pinned to this bb's exact SDK
    version in `devDependencies`, so the API declarations arrive with
    `npm install` at `node_modules/@get-bb/plugin-sdk/bundled-types/*.d.ts`
    (no vendored `types/`). If that version is not on npm yet, it warns and
    still scaffolds. The
    install is best-effort and verified: if npm is missing or leaves a package
    out, it says so and prints the manual `npm install --include=dev` step
    rather than reporting success; `bb plugin build [path]` —
    compile the plugin into `dist/`: the backend bundle (`server.js` +
    `server.meta.json` stamped with SDK/identity metadata; preferred by
    git/npm installs over source), when `bb.app` is declared, `app.js` +
    `app.css` + `app.meta.json`, and, when `bb.host` is declared, the
    self-contained host artifact `host.js` + `host.js.map` +
    `host.meta.json` (its digest; host daemons download and verify the bundle
    by that digest, and run it as a host RPC worker, a provider bridge, or
    both). None of it needs the server.
  - `bb plugin types [path]` — sync the plugin's `@get-bb/plugin-sdk` surface
    to the running bb (default: cwd). For a plugin that depends on the npm
    package it rewrites the exact `devDependencies` pin to this bb's SDK
    version and brings the type-only devDependencies of the packages bb shims
    at runtime (sonner, vaul, the portal radix families, @pierre/diffs, clsx,
    tailwind-merge, class-variance-authority) to this bb's versions — adding
    any an app plugin is missing and moving one out of `dependencies`
    (reporting old → new, and reminding you to `npm install`); for a
    plugin that still vendors declarations it rewrites `types/*.d.ts`, creating
    `types/` when absent. Run it in a cloned or older plugin: the SDK surface
    grows every release. `--check` writes nothing and exits non-zero on a
    mismatch (for CI). `bb plugin build` and `bb plugin dev` refresh vendored
    declarations automatically and leave npm-package plugins alone. Needs no
    server.
  - `bb plugin migrate [path] [--yes]` — convert a plugin that still vendors
    `types/` to the `@get-bb/plugin-sdk` npm package (default: cwd): add the
    exact `devDependencies` pin, raise `engines.bbPluginSdk` when this bb's SDK
    is newer than the declared floor, move an SDK entry declared in
    `dependencies` into `devDependencies`, drop the `@get-bb/plugin-sdk` (and
    pre-rename `@bb/plugin-sdk`) entries from `compilerOptions.paths` (other
    paths like `@/*` are untouched), and delete `types/bb-plugin-sdk*.d.ts`
    plus `types/` if that empties it — a `types/` still holding your own
    declarations is kept, along with the `include` entries that compile it. It
    also rewrites quoted `@bb/plugin-sdk` import/export specifiers (and their
    subpaths) in the plugin's own `.ts`/`.tsx` sources to `@get-bb/plugin-sdk`,
    skipping `node_modules/`, `dist/`, and `types/`; the path map was what made
    the old name resolve, so the imports move with it. A
    half-migrated plugin that has no vendored artifacts left but never gained
    the pin is completed the same way. It
    prints the exact plan and asks before touching anything; `--yes` is
    required when stdin is not a terminal, where it otherwise prints the plan
    and exits non-zero having changed nothing. Run `npm install` afterwards.
    The vendored layout keeps working, so nothing migrates unless you ask.
    Re-running on a migrated plugin is a no-op. Needs no server.
  - `bb plugin dev [path]` — watch loop for an installed plugin (default:
    cwd): on every change it rebuilds the frontend bundle (when `bb.app` is
    declared; unminified, unlike `bb plugin build`) and reloads the plugin;
    open app pages pick the new UI up live.
    Build/reload failures print and keep watching; Ctrl+C stops.
  - Frontend entries default-export `definePluginApp` from
    `@get-bb/plugin-sdk/app` and register UI slots (homepageSection,
    settingsSection, navPanel, threadPanelAction, fileOpener) with hooks
    (useRpc, useRealtime, useRealtimeConnectionState,
    useSettings, useBbContext,
    useBbNavigate, useComposer for scoped text editing / quote / mention /
    focus access); components are vendored shadcn source the
    plugin owns. Installed
    plugins and their settings also appear under Extensions → Plugins.
- **Writing a plugin?** Use the `bb-plugin-authoring` skill — the complete
  authoring reference for the backend `BbPluginApi` (settings, storage, sdk,
  http/rpc/realtime, background services and schedules, CLI commands, agent
  tools and context, host-rendered UI, lifecycle) and the frontend
  `@get-bb/plugin-sdk/app` contract (slots, hooks, UI kit), with working patterns
  and gotchas. `bb guide plugins` has the short walkthrough.
