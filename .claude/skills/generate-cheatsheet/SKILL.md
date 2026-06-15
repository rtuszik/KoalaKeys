---
name: generate-cheatsheet
description: Generate a validated KoalaKeys cheatsheet YAML from a list of shortcuts, a URL/webpage of shortcuts, or a description. Use when the user wants to create, add, or scaffold a new KoalaKeys cheatsheet for an app, tool, or CLI. Produces a file in cheatsheets/ that passes validate_yaml.
---

# Generate KoalaKeys Cheatsheet

Turn a user's shortcut source into a valid `cheatsheets/<slug>.yaml` file that passes KoalaKeys validation.

## Inputs you may receive
- **A URL** to a shortcuts/docs page (e.g. an app's keyboard-shortcut help page).
- **A pasted list** of shortcuts (any rough format).
- **A description** ("make me a Vim cheatsheet").
- Optional preferences: keyboard layout, target system, theme, key vs. text mode.

## Workflow

### 1. Gather the shortcuts
- If given a **URL**: use WebFetch to retrieve it, prompting for "all keyboard shortcuts with their action/description, grouped by the page's own categories." If the fetch is blocked or sparse, tell the user and ask them to paste the list.
- If given a **list/description**: parse it directly. Do not invent shortcuts you are unsure of — if coverage is thin, ask or note gaps rather than fabricating.
- Group shortcuts into sensible **categories** (e.g. General, Navigation, Editing). Preserve the source's grouping when it has one.

### 2. Decide the mode
- **Key shortcuts** (`CMD+C`, `Ctrl+Shift+P`): default. Keep `RenderKeys: true`, `AllowText: false`.
- **Free-form text** (CLI commands like `git rebase -i`, `kubectl get pods`): set `RenderKeys: false` and `AllowText: true`. Never mix — a single sheet is one mode.
- Pick `layout.system` from the source's platform: `Darwin` (macOS), `Linux`, or `Windows`. Pick `layout.keyboard` from US/UK/DE/FR/ES/DVORAK (default `US`). If unclear, default to `US`/`Darwin` and say so.

### 3. Normalize key syntax (for key-mode sheets)
Apply the validator's rules so the file passes on the first try:
- Modifiers UPPERCASE: `CMD`, `CTRL`, `ALT`, `SHIFT` (also `Windows`, `Super`).
- `+` joins keys pressed together: `CMD+SHIFT+P`.
- `>` joins a sequence/chord: `Ctrl+K>Ctrl+S`.
- Convert glyphs to words: `⌘→CMD`, `⌥→ALT`, `⌃→CTRL`, `⇧→SHIFT`.
- Special keys title-case: `Space`, `Tab`, `Enter`, `Esc`, `Up`/`Down`/`Left`/`Right`, `F1`–`F12`.
- Allowed key characters only (validator regex): letters, digits, `+ - | [ ] , . : / \` " ? < > = \` and arrows. Anything outside that needs `AllowText` mode.

### 4. Write the file
- Slug the title: lowercase, spaces→hyphens, e.g. "VS Code" → `cheatsheets/vs-code.yaml`.
- Use this structure (2-space indent, quote the keys and descriptions):

```yaml
title: "VS Code"
RenderKeys: true
AllowText: false
layout:
  keyboard: US
  system: Darwin
theme: catppuccin
shortcuts:
  General:
    "CMD+Shift+P":
      description: "Show command palette"
  Editing:
    "CMD+C":
      description: "Copy"
```
- `title` + `shortcuts` are the only required keys; include the rest for clarity.

### 5. Validate (required — do not skip)
Run validation, which also auto-normalizes the file:

```bash
uv run python -c "from koalakeys.validate_yaml import process_yaml; process_yaml('cheatsheets/<slug>.yaml')"
```

Then confirm a clean pass programmatically (the CLI above does NOT set an exit code):

```bash
uv run python -c "import sys; from koalakeys.validate_yaml import validate_yaml; sys.exit(0 if validate_yaml('cheatsheets/<slug>.yaml') else 1)"
```

- If validation fails, read the printed errors, fix the YAML, and re-run until both commands pass. Common fixes: lowercase modifiers, illegal characters (switch to AllowText mode), missing `description`, bad `layout` enum values, or `AllowText: true` without `RenderKeys: false`.

### 6. (Optional) Verify it generates
Only if the user wants a built preview:
```bash
uv run python src/koalakeys/generate_cheatsheet.py
```
Output HTML lands in the configured output dir (`$CHEATSHEET_OUTPUT_DIR`, default `./output`), with an `index.html`.

## Output to the user
Report: the file path created, the mode/layout/system chosen, the number of categories and shortcuts, that validation passed, and any shortcuts you couldn't confidently include (so they can review). Don't commit unless asked.

## Guardrails
- Never fabricate shortcuts to pad coverage — accuracy over completeness.
- One mode per sheet (keys OR text).
- Always end on a passing `validate_yaml`.
