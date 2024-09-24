# YAML Cheatsheet Formatting Guide

This guide provides detailed instructions on how to format YAML files for the Keyboard Shortcut Cheatsheet Generator. Following these guidelines will ensure that your cheatsheets are generated correctly and consistently.

## Table of Contents

1. [File Structure](#file-structure)
2. [Title](#title)
3. [Layout](#layout)
4. [Shortcuts](#shortcuts)
5. [Special Characters and Formatting](#special-characters-and-formatting)
6. [Common Mistakes and How to Avoid Them](#common-mistakes-and-how-to-avoid-them)
7. [Advanced Usage](#advanced-usage)
8. [Examples](#examples)

## File Structure

Each YAML file should have the following structure:

```yaml
title: Your Cheatsheet Title
layout:
  keyboard: KEYBOARD_LAYOUT
  system: OPERATING_SYSTEM
shortcuts:
  Category1:
    "Shortcut1":
      description: "Description of Shortcut1"
    "Shortcut2":
      description: "Description of Shortcut2"
  Category2:
    "Shortcut3":
      description: "Description of Shortcut3"
```

## Title

- The title should be the first line of your YAML file.
- Use a colon (:) after "title" and provide your cheatsheet title in quotes.
- Keep the title concise but descriptive.
- Example: `title: "LazyVim Shortcuts"`

## Layout

- The layout section is optional but recommended for clarity.
- If omitted, it defaults to QWERTY keyboard layout and Darwin (macOS) system.
- Specify both `keyboard` and `system` under the `layout` key.
- Supported keyboard layouts: QWERTY, QWERTZ, AZERTY, DVORAK
- Supported systems: Darwin (macOS), Linux, Windows
- Example:
  ```yaml
  layout:
    keyboard: QWERTY
    system: Darwin
  ```

## Shortcuts

- All shortcuts must be nested under the `shortcuts` key.
- Organize shortcuts into categories.
- Each category is a key, with shortcuts nested under it.
- Format for each shortcut:
  ```yaml
  "Shortcut Keys":
    description: "Shortcut Description"
  ```
- Use quotes around the shortcut keys and description.
- Separate keys in a shortcut with a plus sign (+).
- Example:
  ```yaml
  shortcuts:
    File Operations:
      "Cmd+S":
        description: "Save file"
      "Cmd+O":
        description: "Open file"
  ```

## Special Characters and Formatting

- Use the following special character mappings for modifier keys:
  - Command (Mac): Cmd or ⌘
  - Option/Alt (Mac): Alt or ⌥
  - Control: Ctrl or ⌃
  - Shift: Shift or ⇧
- For function keys, use F1, F2, etc.
- For special keys, spell them out: Space, Enter, Backspace, Tab, Esc
- Use arrow symbols for arrow keys: ←, →, ↑, ↓
- If your shortcut includes multiple keys pressed in sequence (not simultaneously), separate them with commas.
- Example: `"Cmd+K,Cmd+S": description: "Open keyboard shortcuts"`

## Common Mistakes and How to Avoid Them

1. **Inconsistent Indentation**: 
   - Use consistent indentation (2 or 4 spaces) throughout the file.
   - Do not mix tabs and spaces.

2. **Missing Quotes**:
   - Always use quotes around shortcut keys and descriptions.
   - Correct: `"Cmd+C": description: "Copy"`
   - Incorrect: `Cmd+C: description: Copy`

3. **Incorrect Nesting**:
   - Ensure proper nesting of categories and shortcuts.
   - Use the correct number of spaces for each level.

4. **Forgetting Colons**:
   - Remember to include colons after each key.
   - Correct: `shortcuts:`
   - Incorrect: `shortcuts`

5. **Using Unsupported Characters**:
   - Avoid using unsupported special characters in shortcut keys.
   - Stick to alphanumeric characters, function keys, and supported special keys.

6. **Inconsistent Key Naming**:
   - Use consistent naming for modifier keys throughout your file.
   - Don't mix "Cmd" and "Command" or "Ctrl" and "Control" in the same file.

7. **Overcomplicating Shortcuts**:
   - Keep shortcuts simple and easy to read.
   - For complex shortcuts, consider breaking them down or using a clear, consistent format.

## Advanced Usage

1. **Multi-line Descriptions**:
   For longer descriptions, use the YAML multi-line syntax:
   ```yaml
   "Cmd+Shift+P":
     description: >
       Opens the command palette.
       This allows quick access to all available commands.
   ```

2. **Grouping Similar Shortcuts**:
   You can group similar shortcuts under a single description:
   ```yaml
   "Cmd+1, Cmd+2, Cmd+3":
     description: "Switch to tab 1, 2, or 3 respectively"
   ```

3. **Using Variables**:
   Note: The current version of the Cheatsheet Generator does not support variables. This is an example of potential future functionality.
   ```yaml
   vars:
     mod_key: Cmd
   shortcuts:
     "{{mod_key}}+C":
       description: "Copy"
   ```

## Examples

Here are some example YAML snippets for different scenarios:

1. Basic Example:
   ```yaml
   title: "Text Editor Shortcuts"
   layout:
     keyboard: QWERTY
     system: Darwin
   shortcuts:
     Text Manipulation:
       "Cmd+C":
         description: "Copy selected text"
       "Cmd+V":
         description: "Paste text"
     File Operations:
       "Cmd+S":
         description: "Save current file"
       "Cmd+O":
         description: "Open a file"
   ```

2. Complex Shortcuts:
   ```yaml
   title: "Advanced IDE Shortcuts"
   shortcuts:
     Code Navigation:
       "Ctrl+Shift+F":
         description: "Find in all files"
       "Alt+F7":
         description: "Find all usages"
     Refactoring:
       "Shift+F6":
         description: "Rename symbol"
       "Ctrl+Alt+M":
         description: "Extract method"
     Debug:
       "F5":
         description: "Start/Continue debugging"
       "Shift+F5":
         description: "Stop debugging"
   ```

3. Multi-platform Example:
   ```yaml
   title: "Cross-platform Shortcuts"
   layout:
     keyboard: QWERTY
     system: Windows
   shortcuts:
     Universal:
       "Ctrl+C (Win) / Cmd+C (Mac)":
         description: "Copy"
       "Ctrl+V (Win) / Cmd+V (Mac)":
         description: "Paste"
     Windows Specific:
       "Win+L":
         description: "Lock computer"
     Mac Specific:
       "Cmd+Space":
         description: "Open Spotlight search"
   ```

Remember to test your YAML files with a YAML validator to ensure they are correctly formatted before using them with the Cheatsheet Generator.

## File Location

Place your YAML cheatsheet files in the `cheatsheets/` directory at the root of the project, not in `src/cheatsheets/`.

## Validation and Linting

The Cheatsheet Generator includes validation and linting for your YAML files:

- Validation checks for required keys, correct data types, and valid shortcut formats.
- Linting identifies issues like lines longer than 100 characters, inconsistent indentation, and trailing whitespace.

If there are validation errors, the cheatsheet will not be generated. Linting warnings are displayed but don't prevent generation.

## Running the Generator

To generate cheatsheets, run the following command from the project root:

```bash
python src/generate_cheatsheet.py
```

This will process all YAML files in the `cheatsheets/` directory and generate HTML cheatsheets in the `output/` directory.
