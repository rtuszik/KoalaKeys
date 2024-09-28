# YAML Cheatsheet Specification Guide

## TLDR

- Use `.yaml` extension
- Required top-level keys: `title`, `layout`, `shortcuts`
- `layout` specifies `keyboard` (US, UK, DE, FR, ES) and `system` (Darwin, Windows, Linux)
- `shortcuts` organized by categories
- Use all caps for key names (CMD, CTRL, SHIFT, ALT)
- Use `+` to combine keys
- For arrow keys, use Up, Down, Left, Right
- Your YAML will be validated, linted, and automatically fixed if possible

## File Structure

Each cheatsheet should be a single YAML file with the `.yaml` extension, located in the `cheatsheets` directory of the project.

## Top-Level Keys

The YAML file must contain the following top-level keys:

1. `title`: A string representing the title of the cheatsheet.
2. `layout`: An object containing keyboard and system information.
3. `shortcuts`: An object containing categories and their associated shortcuts.

### Example:

```yaml
title: "Default macOS Keyboard Shortcuts"
layout:
  keyboard: US
  system: Darwin
shortcuts:
  # Categories and shortcuts go here
```

## Title

- The `title` should be a descriptive string enclosed in quotes.
- Use title case for the cheatsheet name.

## Layout

The `layout` object must contain two keys:

1. `keyboard`: Specifies the keyboard layout.
2. `system`: Specifies the operating system.

### Keyboard Layouts

Valid values for `keyboard` are:

- `US` (United States)
- `UK` (United Kingdom)
- `DE` (German)
- `FR` (French)
- `ES` (Spanish)

### System Types

Valid values for `system` are:

- `Darwin` (for macOS)
- `Windows`
- `Linux`

## Shortcuts

The `shortcuts` object contains categories as keys, with each category containing a set of shortcuts.

### Categories

- Use quotation marks for category names containing spaces.
- Use title case for category names.

### Shortcuts

Each shortcut is represented by a key-value pair:

- The key is the shortcut combination, enclosed in quotes.
- The value is an object with a `description` key.

#### Shortcut Formatting

- Use all caps for key names (e.g., `CMD`, `CTRL`, `SHIFT`, `ALT`).
- Use `+` to combine keys in a shortcut.
- For special keys, use their full names: `Space`, `Tab`, `Enter`, `Backspace`, `Delete`, `Esc`.
- For arrow keys, use `Up`, `Down`, `Left`, `Right`.
- For function keys, use `F1`, `F2`, etc.

#### System-Specific Key Mappings

- macOS (Darwin):
  - `CMD` for Command key (⌘)
  - `CTRL` for Control key (⌃)
  - `ALT` for Option key (⌥)
  - `SHIFT` for Shift key
- Windows:
  - `Windows` for Windows key
  - `CTRL` for Control key
  - `ALT` for Alt key
  - `SHIFT` for Shift key

### Example:

```yaml
shortcuts:
  "General":
    "CMD+C":
      description: "Copy selected item"
    "CMD+V":
      description: "Paste copied or cut item"
  "Text Editing":
    "CMD+B":
      description: "Bold selected text"
    "CMD+Right":
      description: "Move cursor to end of current line"
```

## Validation, Linting, and Fixing

When you submit your YAML file, it will go through a validation, linting, and fixing process.

### Validation

The system checks for:

1. Required top-level keys (`title`, `layout`, `shortcuts`)
2. Correct data types for each key
3. Valid values for `keyboard` and `system` in the `layout` section
4. Proper structure of the `shortcuts` section

### Linting

The linting process checks for:

1. Lines longer than 100 characters
2. Inconsistent indentation (should be multiples of 2 spaces)
3. Trailing whitespace

### Automatic Fixing

The system will attempt to automatically fix some issues:

1. Replacing special characters with their text equivalents (e.g., `⌘` to `CMD`)
2. Converting lowercase special keys to uppercase (e.g., `cmd` to `CMD`)
3. Fixing indentation to be consistent (multiples of 2 spaces)
4. Removing trailing whitespace

## Full Example

Here's a minimal example of a correctly formatted YAML cheatsheet:

```yaml
title: "Example Application Shortcuts"
layout:
  keyboard: US
  system: Darwin
shortcuts:
  "File Operations":
    "CMD+S":
      description: "Save current document"
    "CMD+O":
      description: "Open a document"
  "Editing":
    "CMD+X":
      description: "Cut selected text"
    "CMD+V":
      description: "Paste text from clipboard"
  "Navigation":
    "CMD+Left":
      description: "Go to beginning of line"
    "CMD+Right":
      description: "Go to end of line"
```

By following this specification and understanding the validation and fixing processes, you can ensure that your YAML cheatsheets will be compatible with the Easy Cheatsheets project and will render correctly in the generated HTML output.
