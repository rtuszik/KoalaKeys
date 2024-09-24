# easy-cheatsheets

Create and manage your collection of interactive keyboard shortcut cheatsheets with ease!

## Overview

easy-cheatsheets is a powerful tool designed to help you create, organize, and view a collection of interactive HTML cheatsheets for keyboard shortcuts. Whether you're a developer, designer, or power user, this tool will help you keep all your essential shortcuts at your fingertips.

## Features

- Generate beautiful, interactive HTML cheatsheets from simple YAML files
- Create a collection of cheatsheets for different applications or workflows
- Interactive keyboard layout with real-time highlighting
- Categorized shortcuts with descriptions for easy reference
- Clickable shortcuts that highlight corresponding keys on the keyboard
- Index page for quick access to all your cheatsheets
- Search and sort functionality to find the right cheatsheet quickly
- Responsive design for both cheatsheets and index page
- Support for different keyboard layouts and system mappings
- Dark mode toggle for comfortable viewing in any environment

## Requirements

- Python 3.x
- PyYAML
- Jinja2

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/easy-cheatsheets.git
   cd easy-cheatsheets
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Create YAML files for your cheatsheets in the `cheatsheets` directory at the root of the project. Use the following format:

   ```yaml
   title: Your Cheatsheet Title
   layout:
     keyboard: QWERTY
     system: Darwin
   shortcuts:
     Category Name:
       "Shortcut Keys":
         description: "Shortcut Description"
   ```

2. Run the script to generate your cheatsheet collection:

   ```
   python src/generate_cheatsheet.py
   ```

3. Find your generated HTML cheatsheets in the `output` directory.
4. Open `output/index.html` in your browser to view and navigate your cheatsheet collection.

## Customization

Customize the look and feel of your cheatsheets by modifying:

- `src/cheatsheet_template.html`: Individual cheatsheet template
- `src/index_template.html`: Index page template
- `src/styles.css`: Styles for cheatsheets and index

## Contributing

We welcome contributions! Feel free to submit issues, feature requests, or pull requests.

## License

This project is open source and available under the [MIT License](LICENSE).

## Get Started

Start building your ultimate cheatsheet collection today with easy-cheatsheets!
