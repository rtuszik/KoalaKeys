# Easy Cheatsheets

Create and manage your collection of interactive keyboard shortcut cheatsheets with ease!

## Overview

Easy Cheatsheets is a powerful tool designed to help you create, organize, and view a collection of interactive HTML cheatsheets for keyboard shortcuts. Whether you're a developer, designer, or power user, this tool will help you keep all your essential shortcuts at your fingertips.

## Features

- Generate beautiful, interactive HTML cheatsheets from simple YAML files
- Create a collection of cheatsheets for different applications or workflows
- Interactive keyboard layout with real-time highlighting
- Categorized shortcuts with descriptions for easy reference
- Clickable shortcuts that highlight corresponding keys on the keyboard
- Index page for quick access to all your cheatsheets
- Search functionality to find shortcuts quickly
- Responsive design for both cheatsheets and index page
- Support for different keyboard layouts and system mappings
- Dark mode toggle for comfortable viewing in any environment

## Requirements

- Python 3.7+

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/easy-cheatsheets.git
   cd easy-cheatsheets
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Unix or MacOS:
     ```
     source venv/bin/activate
     ```
   - On Windows:
     ```
     venv\Scripts\activate
     ```

4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Set up environment variables:
   Create a `.env` file in the project root and add the following:
   ```
   CHEATSHEET_OUTPUT_DIR=path/to/your/output/directory
   ```
   Replace `path/to/your/output/directory` with the desired output location for generated cheatsheets.

## Usage

1. Create YAML files for your cheatsheets in the `cheatsheets` directory. Use the following format:

   ```yaml
   title: Your Cheatsheet Title
   layout:
     keyboard: US
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

3. Find your generated HTML cheatsheets in the directory specified by the `CHEATSHEET_OUTPUT_DIR` environment variable (or in the `output` directory if not set).

4. Open the `index.html` file in your browser to view and navigate your cheatsheet collection.

## Customization

Customize the look and feel of your cheatsheets by modifying:

- `src/cheatsheet_template.html`: Individual cheatsheet template
- `src/index_template.html`: Index page template

## Contributing

We welcome contributions! Please feel free to submit issues, feature requests, or pull requests.

## License

This project is open source and available under the [MIT License](LICENSE).

## Get Started

Start building your ultimate cheatsheet collection today with Easy Cheatsheets!
