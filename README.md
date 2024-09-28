# Easy Cheatsheets

A simple tool to create and manage interactive keyboard shortcut cheatsheets.

> **Demo**: Check out the [live demo](https://rtuszik.github.io/easy-cheatsheets-collection/) to see a small collection of cheatsheets created with this project.

## Overview

Easy Cheatsheets helps generate and organize interactive HTML cheatsheets for keyboard shortcuts. It's designed for developers, designers, and power users who want to keep their essential shortcuts easily accessible.

> **Quick Start**: To create a cheatsheet, add a YAML file to the `cheatsheets` directory and run `python src/generate_cheatsheet.py`. For detailed YAML formatting instructions, see the [YAML Cheatsheet Specification Guide](yaml_cheatsheet_specification.md).

## Features

- Generate HTML cheatsheets from YAML files
- Interactive keyboard layout with real-time highlighting
- Categorized shortcuts with descriptions
- Index page for quick access to all cheatsheets
- Search functionality
- Support for different keyboard layouts and system mappings

## Demo and Examples

A live demo instance is available, showcasing a selection of cheatsheets:

- **Demo Site**: [https://rtuszik.github.io/easy-cheatsheets-collection/](https://rtuszik.github.io/easy-cheatsheets-collection/)
- **Demo Repository**: [https://github.com/rtuszik/easy-cheatsheets-collection](https://github.com/rtuszik/easy-cheatsheets-collection)

Explore the demo to see how Easy Cheatsheets works and to get ideas for creating custom cheatsheets. The demo repository also contains example YAML files that can be used as templates for new cheatsheets.

## Available Systems and Keyboards

### Systems

- Darwin (macOS)
- Linux
- Windows

### Keyboard Layouts

- US
- UK
- DE (German)
- FR (French)
- ES (Spanish)

## Requirements

- Python 3.8+

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/easy-cheatsheets.git
   cd easy-cheatsheets
   ```

2. Create and activate a virtual environment (optional):

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Set up the output directory:
   Create a `.env` file in the project root with:
   ```
   CHEATSHEET_OUTPUT_DIR=path/to/your/output/directory
   ```

## Usage

1. Create YAML files for your cheatsheets in the `cheatsheets` directory. For detailed instructions on how to format YAML files, please refer to the [YAML Cheatsheet Specification Guide](yaml_cheatsheet_specification.md).

2. Generate cheatsheets:

   ```
   python src/generate_cheatsheet.py
   ```

3. Find the HTML cheatsheets in the specified output directory.

4. Open `index.html` to view the cheatsheet collection.

## Contributing

Contributions are welcome! Feel free to submit issues, feature requests, or pull requests.

## License

This project is licensed under the terms of the [GPLv3](LICENSE).
