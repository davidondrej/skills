# bb app settings reference

Server-backed preferences in Settings. They are persisted on the server, so
every window and client sees the same value.

## Setting values

- `bb settings general <key> <value>` accepts any key listed under
  `generalSettings` in `bb settings show`. Boolean preferences take `true`,
  `false`, `on`, or `off`; `null` clears a preference that can be unset.
- Unknown keys and values of the wrong shape are rejected; the error names the
  keys bb knows.

## Keyboard shortcuts

- `showKeyboardHints` defaults to true. Set it with
  `bb settings keyboard hints <true|false|on|off>` to control whether
  delayed shortcut badges appear while holding Command or Control. It does not
  disable the shortcuts themselves.
- Settings → Keyboard records sparse per-command chord overrides. `Mod` means
  Command on macOS and Control on Windows/Linux.
- Reset removes the override and follows bb's current default. Clear stores an
  explicit disabled value.
- Bindings for non-native actions apply in browser and desktop clients. Command
  contexts and native-only availability remain server-owned. Reusing a chord
  can be intentional when contexts do not overlap; the UI identifies reuse.
- New Thread, New Window, New Tab, Close, and Settings in the desktop menu use
  the same resolved shortcuts as renderer commands.
- The complete default table is in `docs/configuration.md` in the bb source
  repository.

## Unhandled provider events

- `showUnhandledProviderEvents` defaults to false. Set it with
  `bb settings general showUnhandledProviderEvents <true|false|on|off>`.
- When enabled, packaged builds show raw provider events that bb has persisted
  but does not yet understand. These diagnostic payloads can be noisy.
- Development builds always show unhandled provider events regardless of the
  saved preference.

## Active-thread Enter behavior

- `steerActiveThreadOnEnter` defaults to true for a new install. An earlier
  install with saved settings or work keeps false. Set it with
  `bb settings general steerActiveThreadOnEnter <true|false|on|off>`.
- Outside an open composer typeahead menu, disabling it makes Enter queue a
  follow-up and Command+Enter steer the active turn. When enabled, those
  actions are reversed.
- Shift+Enter inserts a newline. On coarse-pointer touch devices, the
  software-keyboard Return path stays a newline; iPadOS WebKit preserves the
  Enter shortcuts for a connected Magic Keyboard.

## Streamer mode

- `streamerMode` defaults to false. Set it with
  `bb settings general streamerMode <true|false|on|off>`.
- When enabled, every `customModels` entry from `~/.bb/config.json` is hidden
  in all model lists: the pickers, `bb provider models`, and
  `sdk.providers.models`. Use it during a screen share so a private or
  early-access model id does not appear.
- The entries stay in `config.json`. A thread request that names a hidden model
  explicitly still runs with it, and default model resolution for a new thread
  keeps the full list.
- A composer whose stored selection is a hidden model falls back to the
  provider default, and the next send records that default. Select the custom
  model again after you turn streamer mode off.

## Provider order and default

- `providerOrder` defaults to `[]`. Set it to a JSON array of provider IDs.
- `defaultProviderId` defaults to `null`. Set a provider ID or use `null` to
  clear it.

## Message edits

- The `editMessages` experiment defaults to true. It controls edits of
  eligible accepted root user messages.

## Provider session release

- BB releases restorable provider sessions after 30 idle minutes.
- Active turns, commands, agents, workflows, and monitors keep sessions loaded.

## Mobile app

- The `mobileApp` experiment defaults to false while the bb mobile app is in
  early access.
- Enable it with `bb settings experiment mobileApp true`. It shows the
  **Add mobile device** card under Settings → Remote access.

## Changelog preview

- The `changelogPreview` experiment defaults to false.
- Enable it with `bb settings experiment changelogPreview true` to show the
  latest release notes on Settings → Updates.

## Timeline windowing

- The `timelineWindowing` experiment defaults to false.
- Enable it with `bb settings experiment timelineWindowing true`.
- It keeps stable timeline wrappers while mounting only rows near the active
  main or nested detail scrollport.
