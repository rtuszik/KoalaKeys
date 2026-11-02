# Theme token contract

The stylesheet consumes only these `--kk-*` semantic tokens. A theme supplies their
values; the component CSS never references palette-specific variables.

## Built-in themes

Set with `theme: <name>` in a cheatsheet (default `catppuccin`). All live in
`src/koalakeys/themes/`.

| Name | Modes | Source |
|---|---|---|
| `catppuccin` | light + dark | Catppuccin Latte / Mocha (default) |
| `rose-pine` | light + dark | Rosé Pine Dawn / Main |
| `gruvbox` | light + dark | Gruvbox light / dark |
| `solarized` | light + dark | Solarized light / dark |
| `nord` | dark only | Nord (toggle hidden) |
| `dracula` | dark only | Dracula (toggle hidden) |

To add a user theme, drop `<name>.yaml` in the project's `themes/` directory with
`extends: <built-in>` and override the tokens you want.

Built-in palettes are derived from MIT-licensed projects; see
[THIRD_PARTY_LICENSES.md](../THIRD_PARTY_LICENSES.md) for attribution.

## Tokens

### Color tokens — defined per **Mode** (`light:` / `dark:` blocks)

| Token | Drives |
|---|---|
| `--kk-bg` | Page background |
| `--kk-surface` | Section / panel background |
| `--kk-card` | Shortcut card background, category-nav background |
| `--kk-card-hover` | Shortcut card hover background |
| `--kk-key-bg` | Keyboard key background, nav-toggle button |
| `--kk-keyboard-bg` | Keyboard tray background |
| `--kk-border` | Key borders |
| `--kk-border-input` | Search-box border |
| `--kk-text` | Primary text |
| `--kk-text-muted` | Subtext, layout info, key separators |
| `--kk-accent` | Title (h1), brand color |
| `--kk-accent-2` | Section headings, nav hover, search focus |
| `--kk-key-text` | Shortcut-key glyph text (catppuccin: mauve light / red dark) |
| `--kk-step-1` … `--kk-step-5` | Sequence highlight colors for chord steps 1–5 |
| `--kk-step-overflow` | Highlight color for steps beyond 5 |
| `--kk-step-text` | Text color on an active (highlighted) key |
| `--kk-shadow` | Box-shadow color, normal elevation (rgba; alpha differs per mode) |
| `--kk-shadow-strong` | Box-shadow color, raised/hover elevation |

The surface set is intentionally split (`surface`/`card`/`key-bg`/`keyboard-bg`) so the
built-in `catppuccin` theme reproduces today's per-element shades exactly — in dark mode
cards (`surface1`) and keys (`surface0`) deliberately differ.

### Typography tokens — shared (mode-agnostic; may be overridden per mode)

| Token | Drives |
|---|---|
| `--kk-font` | `font-family` stack |
| `--kk-font-size` | Base font size; headings/key/description sizes are rem multiples of this |
| `--kk-line-height` | Base line height |

### Geometry tokens — shared (mode-agnostic; may be overridden per mode)

| Token | Drives |
|---|---|
| `--kk-radius` | General corner radius (sections, cards, keyboard) |
| `--kk-gap` | Grid gap between shortcut cards |
| `--kk-section-gap` | Vertical gap between sections |
| `--kk-key-size` | Base key dimension; `key__wide/wider/...` derive as ratios |
| `--kk-max-width` | Content max width |

Headings, description sizes, and the `key__*` width variants are **not** individual
tokens — they are derived as relative multiples so the contract stays small.

## Theme file format

User themes live in `themes/<name>.yaml` and `extends` exactly one built-in.

```yaml
# themes/my-vim.yaml
extends: catppuccin          # required for user themes; built-in parent
modes: [dark]                # optional: narrow inherited modes (hides the toggle)
font_url: "https://…/Font.css"   # optional: emits a <link>; inherited if omitted

# shared tokens (mode-agnostic)
font: "'JetBrains Mono', monospace"
radius: "8px"
gap: "10px"

dark:                        # per-mode color overrides
  accent: "#82aaff"
  key-text: "#c792ea"

# optional structural CSS bundled with the theme (sanitized, emitted in the theme layer)
custom_css: |
  .key { border-width: 2px; }
```

Notes:

- Token keys in the file drop the `--kk-` prefix (`accent`, not `--kk-accent`).
- A **built-in** theme defines every token in both relevant modes (CI-validated complete).
- Resolution is build-time, single parent only: `built-in → user overrides`. No chains.
- Color/length values are pattern-validated; `font_url` must be an https stylesheet URL.

## Cheatsheet usage

```yaml
title: "Vim"
theme: my-vim                # optional; defaults to "catppuccin"
custom_css: extra.css        # optional file (resolved from styles/) and/or:
custom_css_inline: |         # optional inline block
  h1 { letter-spacing: 0.05em; }
```

Emission cascade (later wins on equal specificity):
`base stylesheet → theme tokens → theme custom_css → cheatsheet custom_css file → cheatsheet inline`.
