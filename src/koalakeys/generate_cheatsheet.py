from __future__ import annotations

import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
from ruamel.yaml import YAML

from koalakeys.logger import get_logger
from koalakeys.template_renderer import render_template
from koalakeys.validate_yaml import lint_yaml, validate_yaml

yaml_safe = YAML(typ="safe")
yaml_rw = YAML()
yaml_rw.indent(mapping=2, sequence=4, offset=2)
yaml_rw.preserve_quotes = True
yaml_rw.width = 100

load_dotenv()

PACKAGE_DIR = Path(__file__).parent
PROJECT_ROOT = PACKAGE_DIR.parent.parent

OUTPUT_DIR = Path(os.getenv("CHEATSHEET_OUTPUT_DIR") or PROJECT_ROOT / "output")
CHEATSHEETS_DIR = PROJECT_ROOT / "cheatsheets"
LAYOUTS_DIR = PACKAGE_DIR / "layouts"

OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

layout_file = LAYOUTS_DIR / "keyboard_layouts.yaml"
system_mapping_file = LAYOUTS_DIR / "system_mappings.yaml"

logging = get_logger()


def load_yaml(file_path: Path) -> dict | None:
    try:
        with file_path.open(encoding="utf-8") as file:
            return yaml_safe.load(file)
    except FileNotFoundError:
        logging.error(f"Error: YAML file '{file_path}' not found.")
        return None
    except Exception as e:
        logging.error(f"Error reading YAML file '{file_path}': {e}")
        return None


def load_layout():
    keyboard_layouts = load_yaml(layout_file)
    system_mappings = load_yaml(system_mapping_file)

    if keyboard_layouts is None or system_mappings is None:
        logging.error("Failed to load configuration files.")
        return None, None

    return keyboard_layouts, system_mappings


def consume_separator(shortcut: str, index: int) -> tuple[str, int]:
    current = shortcut[index]
    next_index = index + 1

    if next_index < len(shortcut):
        next_char = shortcut[next_index]
        if current == "+" and next_char == "+":
            return "<sep>+", index + 2
        if current == "+" and next_char == ">":
            return "<sep>>", index + 2
        if current == ">" and next_char == ">":
            return "<seq>>", index + 2
        if current == ">" and next_char == "+":
            return "<seq>+", index + 2

    return ("<sep>", index + 1) if current == "+" else ("<seq>", index + 1)


def format_shortcut_part(part: str, system_mappings: dict) -> str:
    arrow_key_mappings = {"Up": "↑", "Down": "↓", "Left": "←", "Right": "→"}

    mapped_part = system_mappings.get(part.lower(), part)
    if mapped_part in ["⌘", "⌥", "⌃", "⇧"]:
        mapped_part = f'<span class="modifier-symbol">{mapped_part}</span>'

    return arrow_key_mappings.get(mapped_part, mapped_part)


def replace_shortcut_names(shortcut, system_mappings):
    try:
        processed_parts = []
        i = 0
        shortcut = re.sub(r"(\+|\>)\s*(\+|\>)", r"\g<1>\g<2>", shortcut)

        while i < len(shortcut):
            if shortcut[i] in ("+", ">"):
                separator, i = consume_separator(shortcut, i)
                processed_parts.append(separator)
            else:
                current_part = ""
                while i < len(shortcut) and shortcut[i] not in ("+", ">"):
                    current_part += shortcut[i]
                    i += 1
                if current_part.strip():
                    processed_parts.append(format_shortcut_part(current_part.strip(), system_mappings))

        return "".join(processed_parts)
    except Exception as e:
        logging.error(f"Error replacing shortcut names: {e}")
        return shortcut


def normalize_shortcuts(data, system_mappings):
    normalized = {}
    allow_text = data.get("AllowText", False)
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
    data["shortcuts"] = normalize_shortcuts(data, system_mappings.get(layout_info["system"], {}))
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
        with open(html_output, "w", encoding="utf-8") as file:
            file.write(html_content)
    except OSError as e:
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
