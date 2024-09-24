# Keyboard Shortcut Cheatsheet Generator

This project generates interactive HTML cheatsheets for keyboard shortcuts based on YAML configuration files. It creates visually appealing and user-friendly cheatsheets with a keyboard layout and categorized shortcuts.

## Features

- Generate HTML cheatsheets from YAML configuration files
- Interactive keyboard layout
- Categorized shortcuts with descriptions
- Clickable shortcuts that highlight corresponding keys on the keyboard

## Requirements

- Python 3.x
- PyYAML
- Jinja2

## Project Structure

```
.
├── README.md
├── example.yaml
├── neovim.yaml
├── output
│   ├── example_cheatsheet.html
├── requirements.txt
└── src
    ├── cheatsheet_template.html
    └── generate_cheatsheet.py
```

## Installation

1. Clone this repository:

   ```
   git clone https://github.com/yourusername/keyboard-shortcut-cheatsheet-generator.git
   cd keyboard-shortcut-cheatsheet-generator
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Create a YAML file with your keyboard shortcuts in the root directory. Use the following format:

   ```yaml
   title: Your Cheatsheet Title
   shortcuts:
     Category Name:
       "Shortcut Keys":
         description: "Shortcut Description"
   ```

2. Run the script with your YAML file as an argument:

   ```
   python src/generate_cheatsheet.py your_shortcuts.yaml
   ```

3. The generated HTML cheatsheet will be saved in the `output` directory with the name `your_cheatsheet_title_cheatsheet.html`.

## YAML File Structure and Key Formatting

The YAML file structure is crucial for the correct generation of the cheatsheet. Here's a detailed breakdown:

1. **Title**: The first line should be the title of your cheatsheet.

   ```yaml
   title: Your Cheatsheet Title
   ```

2. **Shortcuts**: All shortcuts are nested under the `shortcuts` key.

   ```yaml
   shortcuts:
   ```

3. **Categories**: Shortcuts are organized into categories. Each category is a key under `shortcuts`.

   ```yaml
   shortcuts:
     File Operations:
     Edit Operations:
     Window Management:
   ```

4. **Individual Shortcuts**: Each shortcut is a key-value pair under its category. The key is the shortcut combination, and the value is an object with a `description` key.

   ```yaml
   shortcuts:
     File Operations:
       "Cmd+S":
         description: "Save file"
   ```

5. **Key Formatting**:
   - Use `+` to separate different keys in a combination.
   - For function keys, use `F1`, `F2`, etc.
   - Examples of correctly formatted keys:
     - `"Cmd+S"`
     - `"cmd+s"`
     - `"Ctrl+C"`
     - `"Shift+Tab"`
     - `"Alt+F4"`
     - `"Cmd+Shift+S"`
     - `"Ctrl+Alt+Delete"`

Here's a more comprehensive example:

```yaml
title: Text Editor Shortcuts
shortcuts:
  File Operations:
    "Cmd+S":
      description: "Save file"
    "Cmd+Shift+S":
      description: "Save as"
    "Cmd+O":
      description: "Open file"
  Edit Operations:
    "Cmd+C":
      description: "Copy"
    "Cmd+V":
      description: "Paste"
    "Cmd+X":
      description: "Cut"
  Window Management:
    "Cmd+W":
      description: "Close window"
    "Cmd+Shift+F":
      description: "Full screen"
```

## Example Files

The project includes an example YAML file - `example.yaml` with a few shortcuts.

## Customization

You can customize the appearance of the cheatsheet by modifying the `src/cheatsheet_template.html` file. The template uses Jinja2 for rendering dynamic content.

## Example Outputs

The `output` directory contains an example cheatsheet:

- `example_cheatsheet.html`: Generated from `example.yaml`

You can open this file in a web browser to see how the generated cheatsheets look and function.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).
