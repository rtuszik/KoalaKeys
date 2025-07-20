from ruamel.yaml import YAML
import sys
import os
from validate_yaml import validate_yaml, lint_yaml
from dotenv import load_dotenv
from template_renderer import render_template
from logger import get_logger
from pathlib import Path

yaml_safe = YAML(typ='safe')
yaml_rw = YAML()
yaml_rw.indent(mapping=2, sequence=4, offset=2)
yaml_rw.preserve_quotes = True
yaml_rw.width = 100

load_dotenv()

BASE_DIR = Path(__file__).parent
PROJECT_ROOT = BASE_DIR.parent

OUTPUT_DIR = Path(os.getenv('CHEATSHEET_OUTPUT_DIR') or PROJECT_ROOT / "output")
TEMPLATES_DIR = BASE_DIR / "templates"
LAYOUTS_DIR = BASE_DIR / "layouts"
CHEATSHEETS_DIR = PROJECT_ROOT / "cheatsheets"

OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

logging = get_logger()


def load_yaml(file_path: Path) -> dict | None:
    try:
        with open(file_path, "r", encoding='utf-8') as file:
            return yaml_safe.load(file)
    except FileNotFoundError:
        logging.error(f"Error: YAML file '{file_path}' not found.")
        return None
    except Exception as e:
        logging.error(f"Error reading YAML file '{file_path}': {e}")
        return None


def load_layout():
    keyboard_layouts = load_yaml(LAYOUTS_DIR / "keyboard_layouts.yaml")
    system_mappings = load_yaml(LAYOUTS_DIR / "system_mappings.yaml")
    
    if keyboard_layouts is None or system_mappings is None:
        logging.error("Failed to load configuration files.")
        return None, None
    
    return keyboard_layouts, system_mappings

def replace_shortcut_names(shortcut, system_mappings):
    arrow_key_mappings = {
        "Up": "↑",
        "Down": "↓",
        "Left": "←",
        "Right": "→"
    }
    try:
        processed_parts = []
        i = 0
        while i < len(shortcut):
            if shortcut[i] == '+':
                if i + 1 < len(shortcut) and shortcut[i + 1] == '+':
                    processed_parts.append('+')
                    i += 2
                else:
                    processed_parts.append('<sep>')
                    i += 1
            else:
                current_part = ''
                while i < len(shortcut) and shortcut[i] != '+':
                    current_part += shortcut[i]
                    i += 1
                if current_part.strip():
                    part = current_part.strip()
                    part = system_mappings.get(part.lower(), part)
                    if part in ['⌘', '⌥', '⌃', '⇧']:
                        part = f'<span class="modifier-symbol">{part}</span>'

                    part = arrow_key_mappings.get(part, part)
                    processed_parts.append(part)


        return ''.join(processed_parts)
    except Exception as e:
         logging.error(f"Error replacing shortcut names: {e}")
         return shortcut

def normalize_shortcuts(data, system_mappings):
    normalized = {}
    allow_text = data.get('AllowText', False)
    try:
        for section, shortcuts in data.get("shortcuts", {}).items():
            normalized[section] = {}
            for shortcut, details in shortcuts.items():
                if allow_text:
                    normalized[section][shortcut] = details
                else:
                    normalized_shortcut = replace_shortcut_names(shortcut, system_mappings)
                    normalized[section][normalized_shortcut] = details
    except Exception as e:
        logging.error(f"Error normalizing shortcuts: {e}")
    return normalized


def get_layout_info(data):
    layout = data.get("layout", {})
    return {
        "keyboard": layout.get("keyboard", "US"),
        "system": layout.get("system", "Darwin"),
    }

def generate_html(data, keyboard_layouts, system_mappings):
    template_path = "cheatsheets/cheatsheet-template.html"
    layout_info = get_layout_info(data)
    data["shortcuts"] = normalize_shortcuts(
        data, system_mappings.get(layout_info["system"], {})
    )
    data["layout"] = layout_info
    data["keyboard_layout"] = keyboard_layouts.get(layout_info["keyboard"], {}).get("layout")
    data["render_keys"] = data.get("RenderKeys", True)
    data["allow_text"] = data.get("AllowText", False)
    
    return render_template(template_path, data)


def validate_and_lint(yaml_file):
    validation_result = validate_yaml(yaml_file)
    warnings = lint_yaml(yaml_file)

    if not validation_result:
        logging.error(f"Validation failed for {yaml_file}")
        return False

    if warnings:
        logging.warning(f"Linting warnings in {yaml_file}:")
        for warning in warnings:
            logging.warning(f"  - {warning}")

    return True

def write_html_content(html_output, html_content):
    try:
        with open(html_output, "w", encoding='utf-8') as file:
            file.write(html_content)
    except IOError as e:
        logging.error(f"Error writing to output file: {e}")
        return False
    return True

def main(yaml_file):
    if not validate_and_lint(yaml_file):
        return None, None

    data = load_yaml(yaml_file)
    if data is None or "title" not in data:
        logging.error("Error: Invalid YAML file or missing 'title' field.")
        return None, None

    keyboard_layouts, system_mappings = load_layout()
    if keyboard_layouts is None or system_mappings is None:
        return None, None

    html_content = generate_html(data, keyboard_layouts, system_mappings)
    if html_content is None:
        return None, None

    base_filename = f"{data['title'].lower().replace(' ', '_')}_cheatsheet"
    html_output = os.path.join(OUTPUT_DIR, f"{base_filename}.html")

    if not write_html_content(html_output, html_content):
        logging.error(f"Failed to write HTML content to {html_output}")
        return None, None

    logging.info(f"Cheatsheet generated: {html_output}")

    return data["title"], os.path.basename(html_output)


def generate_index(cheatsheets):
    template_path = "index/index_template.html"
    return render_template(template_path, {"cheatsheets": cheatsheets})


if __name__ == "__main__":
    yaml_files = yaml_files = list(CHEATSHEETS_DIR.glob("*.yaml"))

    if not yaml_files:
        print("No YAML files found in the cheatsheets directory.")
        sys.exit(1)

    cheatsheets = []
    for yaml_file in yaml_files:
        title, filename = main(yaml_file)
        if title and filename:
            cheatsheets.append({"title": title, "filename": filename})

    if cheatsheets:
        OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
        
        html_content = generate_index(cheatsheets)
        if html_content:
            index_output = os.path.join(OUTPUT_DIR, "index.html")
            if write_html_content(index_output, html_content):
                logging.info(f"Index page generated: {index_output}")
                print(f"Generated cheatsheets for {len(cheatsheets)} YAML files.")
            else:
                logging.error("Failed to write index page.")
        else:
            logging.error("Failed to generate index page.")
    else:
        print("No valid cheatsheets were generated due to errors.")
