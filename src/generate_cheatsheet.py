import yaml
from jinja2 import Template, Environment, FileSystemLoader
import sys
import os
import glob
from validate_yaml import validate_yaml, lint_yaml
from dotenv import load_dotenv
import logging
import argparse

def setup_logging(debug=False):
    log_file = 'cheatsheet_generator.log'
    log_level = logging.DEBUG if debug else logging.INFO
    log_format = '%(asctime)s - %(levelname)s - %(message)s'

    # Set up file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(log_format))

    # Set up console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(log_format))

    # Set up root logger
    logging.root.setLevel(log_level)
    logging.root.addHandler(file_handler)
    if debug:
        logging.root.addHandler(console_handler)

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Generate cheatsheets')
parser.add_argument('-d', '--debug', action='store_true', help='Enable debug mode')
args = parser.parse_args()

# Set up logging
setup_logging(args.debug)

# Load environment variables
load_dotenv()

def load_yaml(file_path):
    try:
        with open(file_path, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Error: YAML file '{file_path}' not found.")
        sys.exit(1)


def load_configs():
    config_dir = os.path.join(os.path.dirname(__file__), "configs")
    keyboard_layouts = load_yaml(os.path.join(config_dir, "keyboard_layouts.yaml"))
    system_mappings = load_yaml(os.path.join(config_dir, "system_mappings.yaml"))
    return keyboard_layouts, system_mappings


def replace_shortcut_names(shortcut, system_mappings):
    arrow_key_mappings = {
        "Up": "↑",
        "Down": "↓",
        "Left": "←",
        "Right": "→"
    }
    return "+".join(
        arrow_key_mappings.get(key.strip(), system_mappings.get(key.strip(), key.strip()))
        for key in shortcut.split("+")
    )


def normalize_shortcuts(data, system_mappings):
    normalized = {}
    for section, shortcuts in data.get("shortcuts", {}).items():
        normalized[section] = {}
        for shortcut, details in shortcuts.items():
            normalized_shortcut = replace_shortcut_names(shortcut, system_mappings)
            normalized[section][normalized_shortcut] = details
    return normalized


def get_layout_info(data):
    layout = data.get("layout", {})
    return {
        "keyboard": layout.get("keyboard", "US"),
        "system": layout.get("system", "Darwin"),
    }


def generate_html(data, keyboard_layouts, system_mappings):
    template_path = os.path.join(os.path.dirname(__file__), "cheatsheet_template.html")
    try:
        with open(template_path, "r") as file:
            template = Template(file.read())
    except FileNotFoundError:
        print(f"Error: Template file '{template_path}' not found.")
        sys.exit(1)

    layout_info = get_layout_info(data)
    data["shortcuts"] = normalize_shortcuts(
        data, system_mappings[layout_info["system"]]
    )
    data["layout"] = layout_info
    data["keyboard_layout"] = keyboard_layouts[layout_info["keyboard"]]["layout"]
    return template.render(**data)


def main(yaml_file):
    # Validate and lint the YAML file
    errors = validate_yaml(yaml_file)
    warnings = lint_yaml(yaml_file)

    if errors:
        logging.error(f"Validation errors in {yaml_file}:")
        for error in errors:
            logging.error(f"  - {error}")
        return None, None

    if warnings:
        logging.warning(f"Linting warnings in {yaml_file}:")
        for warning in warnings:
            logging.warning(f"  - {warning}")

    data = load_yaml(yaml_file)

    if "title" not in data:
        logging.error("Error: 'title' field is missing in the YAML file.")
        return None, None

    keyboard_layouts, system_mappings = load_configs()
    html_content = generate_html(data, keyboard_layouts, system_mappings)

    # Use the output directory from .env if specified, otherwise use the default
    output_dir = os.getenv('CHEATSHEET_OUTPUT_DIR')
    if not output_dir:
        output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
        logging.info(f"Using default output directory: {output_dir}")
    else:
        logging.info(f"Using custom output directory from .env: {output_dir}")

    try:
        os.makedirs(output_dir, exist_ok=True)
    except OSError as e:
        logging.error(f"Error creating output directory: {e}")
        return None, None

    base_filename = f"{data['title'].lower().replace(' ', '_')}_cheatsheet"
    html_output = os.path.join(output_dir, f"{base_filename}.html")

    try:
        with open(html_output, "w") as file:
            file.write(html_content)
    except IOError as e:
        logging.error(f"Error writing to output file: {e}")
        return None, None

    logging.info(f"Cheatsheet generated: {html_output}")

    return data["title"], os.path.basename(html_output)


def generate_index(cheatsheets):
    template_path = os.path.join(os.path.dirname(__file__), "index_template.html")
    env = Environment(loader=FileSystemLoader(os.path.dirname(template_path)))
    template = env.get_template(os.path.basename(template_path))

    html_content = template.render(cheatsheets=cheatsheets)

    output_dir = os.getenv('CHEATSHEET_OUTPUT_DIR')
    if not output_dir:
        output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
        logging.info(f"Using default output directory for index: {output_dir}")
    else:
        logging.info(f"Using custom output directory from .env for index: {output_dir}")

    index_output = os.path.join(output_dir, "index.html")

    with open(index_output, "w") as file:
        file.write(html_content)

    logging.info(f"Index page generated: {index_output}")


if __name__ == "__main__":
    cheatsheet_dir = os.path.join(os.path.dirname(__file__), "..", "cheatsheets")
    yaml_files = glob.glob(os.path.join(cheatsheet_dir, "*.yaml"))

    if not yaml_files:
        print("No YAML files found in the cheatsheets directory.")
        sys.exit(1)

    cheatsheets = []
    for yaml_file in yaml_files:
        title, filename = main(yaml_file)
        if title and filename:
            cheatsheets.append({"title": title, "filename": filename})

    if cheatsheets:
        generate_index(cheatsheets)
        print(f"Generated cheatsheets for {len(cheatsheets)} YAML files.")
    else:
        print("No valid cheatsheets were generated due to errors.")
