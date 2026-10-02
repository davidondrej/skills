# bb theme authoring reference

How to write a good bb app theme: the design model, the full design-token
reference (what every CSS variable drives), and how to set colors and fonts.
Read this before authoring or editing a built-in theme or a custom stylesheet.

The *palette* is global and server-stored; light/dark *mode* is a separate
per-client setting that the palette layers on top of. You ship one stylesheet
that handles both modes.

## Contents

- [Where themes live](#where-themes-live)
- [Model](#model)
- [Stylesheet structure](#stylesheet-structure)
- [What to set (quick start)](#what-to-set-quick-start)
- [Token reference — what each variable drives](#token-reference)
- [Changing fonts](#changing-fonts)
- [Worked example](#worked-example)
- [Applying a theme](#applying-a-theme)

## Where themes live

A custom theme is a folder under the app data dir:
`<bb-data-dir>/theme/<name>/theme.css` (the packaged app uses `~/.bb/theme/…`).
The folder name is the theme id. Run `bb theme dir` to print the exact directory
rather than guessing it. Always put custom app-theme CSS here — not in a stray
`.css` file elsewhere in a repo. To edit a theme, change its `theme.css` in place
and re-run `bb theme set <name>` (or just re-select it) to re-apply.

## Model

The app's colors flow through CSS custom properties. The whole **neutral ramp**
(backgrounds, cards, borders, sidebar, hover/active states, inset surfaces) is
**derived from two anchors** — `--canvas` (the base surface) and `--ink` (the
base text color) — by mixing `--ink` into `--canvas` at increasing percentages
(higher % = more contrast / further from the surface). Accent-tinted surfaces
(focus ring, selection, destructive surfaces) derive from `--primary` /
`--destructive`. So you mostly set the **anchors + accent + text tiers +
semantic** tokens, and everything else follows automatically.

A custom theme is a plain CSS file that overrides these tokens. It is injected as
the last stylesheet, so its rules win.

## Stylesheet structure

Provide two blocks using these exact selectors — `:root, .light` for light mode
and `.dark` for dark:

```css
:root, .light { /* light overrides */ }
.dark { /* dark overrides */ }
```

`:root` matches in both modes, so anything you put only in `:root, .light`
applies to dark too. Use that for mode-independent things (the `color-mix` text
tiers, the ANSI palette, fonts): the `.dark` block then only needs to re-set the
anchors, accent, and semantic colors.

The stylesheet is capped at ~256 KB.

## What to set (quick start)

Set tokens in this order:

1. **The two anchors — `--canvas` and `--ink`.** Nearly everything derives from
   them. Keep them high-contrast — aim for ≥ 4.5:1 between `--ink` and
   `--canvas`.
2. **The accent — `--primary` and `--primary-foreground`** (text/icons drawn on
   the accent). The focus ring, selection highlight, and sidebar ring derive from
   `--primary`.
3. **The secondary text tiers — `--muted-foreground`, `--subtle-foreground`,
   `--readback-foreground`.** These do NOT derive by default; derive them from the
   anchors so contrast tracks the theme:
   ```css
   --muted-foreground: color-mix(in oklch, var(--ink) 70%, var(--canvas));
   --subtle-foreground: color-mix(in oklch, var(--ink) 58%, var(--canvas));
   --readback-foreground: color-mix(in oklch, var(--ink) 64%, var(--canvas));
   ```
4. **Semantic + accent colors** (also not derived): `--destructive`,
   `--destructive-text` (a text-legible variant), `--warning`, `--warning-text`,
   `--attention`, `--success`, `--diff-added`, `--diff-removed`, `--pr-merged`,
   and `--file-accent` (file-path tint).
5. **Terminal palette (optional): `--ansi-0` … `--ansi-15`.** If you remap these,
   also set `--ansi-bg-fg-0` … `--ansi-bg-fg-15` — the readable text color
   (usually black or white) drawn on top of each ANSI color when used as a
   background.

## Token reference

What each variable drives. You mainly set the **anchors + accent + text tiers +
semantic** tokens; the rest derive.

**Anchors — set first; everything below keys off them:**

| token | drives |
|---|---|
| `--canvas` | base surface: page/content background, cards, popovers, sidebar, and (via mixes) every neutral fill, border, and chrome surface |
| `--ink` | base text/foreground color, and the strength of every neutral fill/border (ink mixed into canvas) |

**Surfaces & chrome — auto-derive from `--canvas`/`--ink`; leave alone unless you want one element to differ:**

| token | drives | derives |
|---|---|---|
| `--background` | main content-area background | `= --canvas` |
| `--card`, `--popover` | card surfaces; dropdown/menu/popover/tooltip surfaces | `= --canvas` |
| `--secondary`, `--accent` | subtle fills: secondary buttons, hovered list rows, highlights | ink 8% |
| `--muted` | muted fill: badges, chips, inset blocks | ink 11% |
| `--border` | default component borders (cards, dividers) | ink 14% |
| `--border-hairline` | the finest 1px separators | ink ~15% |
| `--border-seam` | resizable app-shell boundaries: sidebar↔content, split panes, and side panels | ink ~10% |
| `--border-seam-vertical` | compatibility alias for `--border-seam`; prefer the orientation-neutral token | `= --border-seam` |
| `--input` | input/control field borders | ink ~30% |
| `--surface-recessed` | sunken inset wells (code/diagram backgrounds) | translucent ink |
| `--surface-raised` | faintly lifted panels | translucent ink |
| `--surface-scrim` | **frosted top bars** — the thread/page header (`bg-surface-scrim`, blurred) | canvas 92% |
| `--state-hover`, `--state-active` | translucent hover / pressed overlays on rows & buttons | translucent ink |
| `--sidebar`, `--sidebar-foreground`, `--sidebar-accent`, `--sidebar-border` | left sidebar surface, its text, hovered items, borders | canvas/ink mixes |

**Accent — set `--primary` (+ foreground); these follow it:**

| token | drives | derives |
|---|---|---|
| `--primary` | primary buttons, active/accent states, links, focus ring, selection | set |
| `--primary-foreground` | text/icons drawn on a `--primary` fill | set |
| `--ring`, `--sidebar-ring` | keyboard focus outline | `= --primary` |
| `--surface-selected`, `--surface-selected-border` | selected-row tint and its outline | primary 16% / 35% |
| `--file-accent` | file-path titles in the timeline (the one tint in otherwise-neutral text) | set |

**Text tiers — set these (they do NOT auto-derive; use the `color-mix` recipe so contrast tracks the anchors):**

| token | drives |
|---|---|
| `--foreground` | primary body text (auto `= --ink`; usually leave it) |
| `--muted-foreground` | secondary text: metadata, timestamps, labels (highest-contrast secondary tier) |
| `--subtle-foreground` | low-emphasis text: captions, hints, placeholders |
| `--readback-foreground` | settled/closed-turn machinery text (recede tier between muted and subtle) |

**Semantic / status — set each to a recognizable hue (these carry meaning; don't flatten them to neutral):**

| token | drives |
|---|---|
| `--destructive` | destructive buttons/fills (delete; failing/closed PR) |
| `--destructive-foreground` | text/icons on a `--destructive` fill |
| `--destructive-text` | text-only destructive (must clear ~4.5:1 on the canvas — give dark mode a lighter value) |
| `--surface-destructive`, `--surface-destructive-border` | destructive-tinted surfaces/outlines (auto-derive from `--destructive`) |
| `--warning`, `--warning-text` | warning fills / warning text |
| `--attention` | attention indicator (amber dot) |
| `--success` | success states: passing checks, open PR |
| `--diff-added`, `--diff-removed` | added/removed line colors in diffs |
| `--pr-merged` | merged-PR purple (the universal merged color) |

**Terminal — set only if remapping:** `--ansi-0` … `--ansi-15` (the 16 ANSI
colors) and `--ansi-bg-fg-0` … `--ansi-bg-fg-15` (the readable text drawn on each
ANSI color when used as a background).

**Non-color (optional):** `--radius` (corner rounding) and `--shadow-*`
(elevation); fonts are below. Decorative `--pill-*` (prompt mention chips) are
fixed literals — override only if needed.

## Changing fonts

Three font tokens, overridden the same way as colors. Fonts are mode-independent,
so set them in the `:root, .light` block only. Always end the stack with a
generic family (`sans-serif` / `monospace` / `serif`) as a fallback.

| token | drives |
|---|---|
| `--font-sans` | the entire app UI / body text (`body` uses it) |
| `--font-mono` | code blocks, diffs, file paths and previews, terminal-style text |
| `--font-serif` | serif prose (rarely used in the UI) |

The browser must be able to load the family. Three ways:

1. **A system or already-bundled font** — just name it. Inter is bundled (always
   available); common OS fonts like `Menlo`, `"SF Mono"`, `Consolas`, `Georgia`
   work by name:
   ```css
   :root, .light {
     --font-sans: "Helvetica Neue", system-ui, sans-serif;
     --font-mono: "SF Mono", Menlo, monospace;
   }
   ```
2. **A web font via `@import`** — the `@import` must be the VERY FIRST statement
   in the file (an `@import` after any other rule is ignored), then reference it:
   ```css
   @import url("https://fonts.googleapis.com/css2?family=JetBrains+Mono&family=Sora&display=swap");
   :root, .light {
     --font-sans: "Sora", sans-serif;
     --font-mono: "JetBrains Mono", monospace;
   }
   ```
3. **A self-hosted font via `@font-face`**:
   ```css
   @font-face {
     font-family: "My Font";
     src: url("https://example.com/myfont.woff2") format("woff2");
     font-display: swap;
   }
   :root, .light { --font-sans: "My Font", sans-serif; }
   ```

Options 2–3 fetch the font over the network when the theme applies, so keep the
generic fallback in the stack so text still renders if the font is slow or fails.

## Worked example

A complete Nord-like theme. Note the text tiers in `:root, .light` recompute from
whichever anchors are active, so the `.dark` block only re-sets anchors, accent,
and semantics:

```css
:root, .light {
  --canvas: #eceff4;
  --ink: #2e3440;
  --primary: #5e81ac;
  --primary-foreground: #eceff4;
  --muted-foreground: color-mix(in oklch, var(--ink) 70%, var(--canvas));
  --subtle-foreground: color-mix(in oklch, var(--ink) 58%, var(--canvas));
  --readback-foreground: color-mix(in oklch, var(--ink) 64%, var(--canvas));
  --destructive: #bf616a;
  --destructive-text: #a1343d;
  --success: #6f9655;
  --file-accent: #5e81ac;
}
.dark {
  --canvas: #2e3440;
  --ink: #d8dee9;
  --primary: #88c0d0;
  --primary-foreground: #2e3440;
  --destructive: #bf616a;
  --destructive-text: #d6868d;
  --success: #a3be8c;
  --file-accent: #88c0d0;
}
```

## Applying a theme

1. `bb theme dir` — print the custom-theme directory (e.g. `~/.bb/theme`).
2. Write your stylesheet to `<that-dir>/<name>/theme.css`. Start the name with
   a letter or digit. Use at most 64 letters, digits, dots, underscores, or
   hyphens.
3. `bb theme set <name>` — activate it. To edit later, change the file in place
   and re-run `bb theme set <name>`.

## Code themes (diffs and file previews)

Code colors follow the active UI palette. Built-in palettes use the matching
Shiki pair. A custom or plugin theme may declare Pierre / VS Code JSON; if it
does not, diffs use `pierre-dark` / `pierre-light`.

A custom theme folder may ship Pierre / VS Code theme JSON:

```text
<bb-data-dir>/theme/my-theme/
  theme.css
  pierre-dark.json
  pierre-light.json
```

Or name the files in `theme.json`:

```json
{
  "codeTheme": {
    "dark": "pierre-dark.json",
    "light": "github-light"
  }
}
```

Each side is a bundled Shiki / Pierre name, or a folder-relative `.json` file
with `{ name, type, colors, tokenColors }`. See https://diffs.com/theme.

There is no separate code-theme setting. `bb theme show` prints the resolved
Pierre names for the active palette.

Changes apply live to every open window — no reload needed.
