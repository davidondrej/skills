# cmux viewers

Follow the main skill's workspace, ownership, and focus rules.

## Browser workflow

Open → wait → snapshot → act → re-snapshot. Browser surfaces use WKWebView; do not assume CDP or Playwright feature parity.

```bash
cmux_browser_surface=$(cmux --json browser open https://example.com --focus false | jq -r .result.surface_ref)
cmux browser "$cmux_browser_surface" wait --load-state complete --timeout-ms 15000
cmux browser "$cmux_browser_surface" snapshot --interactive  # element refs: e1, e2, …
cmux browser "$cmux_browser_surface" fill e1 "<email-address>"
cmux browser "$cmux_browser_surface" click e2 --snapshot-after
cmux browser "$cmux_browser_surface" wait --selector "#ready" --timeout-ms 10000
cmux browser "$cmux_browser_surface" wait --url-contains "/dashboard" --timeout-ms 10000
```

With the same `cmux browser "$cmux_browser_surface"` prefix:

- Navigate: `goto URL`, `back`, `forward`, `reload`.
- Inspect: `get url`, `get title`, `get text body`, `get value "#email"`, `get count ".row"`, `eval 'return document.title'`.
- Session: `cookies get`, `cookies set --name foo --value bar`, `state save /tmp/auth.json`, `state load /tmp/auth.json`.
- Diagnose: `console list`, `errors list`, `screenshot`.

Check `cmux browser --help` for build-specific support for viewport, geolocation/offline emulation, tracing, network interception, and raw input. Handle `not_supported` responses rather than assuming those operations work.

## Markdown workflow

`cmux markdown open` live-renders Markdown; `cmux open file.pdf` selects its viewer. Flags: `--workspace`, `--surface`, `--window`, `--direction <right|down|left|up>`, `--focus <true|false>`. **No `--pane`.** `--surface` selects where to split from; verify the layout.

### Add a document tab to the helper pane

Find the caller's right helper pane. Open relative to an existing Markdown surface there; if this creates a new pane, move the fresh surface into the helper and verify. Without a helper, open once with `--direction right --focus false`.

```bash
cmux list-panes --workspace "$CMUX_WORKSPACE_ID"
cmux list-pane-surfaces --workspace "$CMUX_WORKSPACE_ID" --pane pane:10
cmux markdown open /abs/path/file.md --workspace "$CMUX_WORKSPACE_ID" --surface surface:12 --focus false
# If a new pane was created, move only the newly opened surface:
cmux move-surface --surface surface:NEW --pane pane:10 --focus false
cmux list-panes --workspace "$CMUX_WORKSPACE_ID"  # verify no stray pane remains
```

### Replace the document in the single helper pane

**Close the previous Markdown surface first, then open the new file fresh.** Opening first and closing later, or moving an existing viewer, can leave the pane blank.

```bash
cmux list-panes --workspace "$CMUX_WORKSPACE_ID"
cmux list-pane-surfaces --workspace "$CMUX_WORKSPACE_ID" --pane pane:10
cmux close-surface --surface surface:PREV
cmux markdown open /abs/path/new.md --workspace "$CMUX_WORKSPACE_ID" --direction right --focus false
```

**Blank viewer recovery:** close it and reopen the file fresh; move only the fresh surface if necessary. `surface-health` can report healthy while the viewer is blank, and `refresh-surfaces` usually does not fix it.

**Verification:** `read-screen` cannot read Markdown; browser screenshots capture only WKWebView surfaces. Confirm rendering with the user. A browser preview can inspect the file but does not prove the Markdown pane rendered.
