from __future__ import annotations

import html
import os
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from dotenv import load_dotenv
from ruamel.yaml import YAML

from koalakeys.logger import get_logger
from koalakeys.template_renderer import render_template
from koalakeys.theming import ThemeError, resolve_theme, sanitize_css
from koalakeys.validate_yaml import CheatsheetError, lint_yaml, load_cheatsheet

if TYPE_CHECKING:
    from koalakeys.models import Cheatsheet, Shortcut

yaml_safe = YAML(typ="safe")

load_dotenv()

PACKAGE_DIR = Path(__file__).parent
PROJECT_ROOT = Path.cwd()

OUTPUT_DIR = Path(os.getenv("CHEATSHEET_OUTPUT_DIR") or PROJECT_ROOT / "output")
CHEATSHEETS_DIR = PROJECT_ROOT / "cheatsheets"
THEMES_DIR = PROJECT_ROOT / "themes"
STYLES_DIR = PROJECT_ROOT / "styles"
LAYOUTS_DIR = PACKAGE_DIR / "layouts"

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

    mapped_part = html.escape(system_mappings.get(part.lower(), part), quote=False)
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


def normalize_shortcuts(sheet: Cheatsheet, system_mappings: dict) -> dict[str, dict[str, Shortcut]]:
    if sheet.allow_text:
        return {section: dict(items) for section, items in sheet.shortcuts.items()}
    return {
        section: {replace_shortcut_names(key, system_mappings): details for key, details in items.items()}
        for section, items in sheet.shortcuts.items()
    }


def load_custom_css_file(filename):
    if not filename:
        return ""
    path = (STYLES_DIR / filename).resolve()
    if not path.is_relative_to(STYLES_DIR.resolve()):
        logging.error(f"Custom CSS file must be inside {STYLES_DIR}: {filename}")
        return ""
    try:
        return sanitize_css(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        logging.error(f"Custom CSS file not found: {path}")
        return ""
    except OSError as e:
        logging.error(f"Error reading custom CSS file '{path}': {e}")
        return ""


def styling_context(sheet: Cheatsheet) -> dict | None:
    try:
        theme = resolve_theme(sheet.theme, themes_dir=THEMES_DIR)
    except ThemeError as e:
        logging.error(f"Theme error: {e}")
        return None

    return {
        "theme_token_css": theme.render_token_css(),
        "theme_font_url": theme.font_url,
        "theme_default_is_dark": theme.default_is_dark,
        "theme_both_modes": theme.both_modes,
        "theme_custom_css": theme.custom_css,
        "custom_css_file": load_custom_css_file(sheet.custom_css),
        "custom_css_inline": sanitize_css(sheet.custom_css_inline),
    }


def generate_html(sheet: Cheatsheet, keyboard_layouts: dict, system_mappings: dict) -> str | None:
    styling = styling_context(sheet)
    if styling is None:
        return None

    context = {
        "title": sheet.title,
        "layout": sheet.layout,
        "shortcuts": normalize_shortcuts(sheet, system_mappings.get(sheet.layout.system, {})),
        "keyboard_layout": keyboard_layouts.get(sheet.layout.keyboard, {}).get("layout"),
        "render_keys": sheet.render_keys,
        "allow_text": sheet.allow_text,
        **styling,
    }
    return render_template("cheatsheets/cheatsheet-template.html", context)


def load_and_lint(yaml_file: Path) -> Cheatsheet | None:
    try:
        sheet = load_cheatsheet(yaml_file)
    except CheatsheetError as e:
        for problem in e.problems:
            logging.error(f"{yaml_file}: {problem}")
        logging.error(f"Validation failed for {yaml_file}")
        return None

    warnings = lint_yaml(yaml_file)
    if warnings:
        logging.warning(f"Linting warnings in {yaml_file}:")
        for warning in warnings:
            logging.warning(f"  - {warning}")

    return sheet


def write_html_content(html_output, html_content):
    try:
        with open(html_output, "w", encoding="utf-8") as file:
            file.write(html_content)
    except OSError as e:
        logging.error(f"Error writing to output file: {e}")
        return False
    return True


def main(yaml_file: Path, used_filenames: set[str] | None = None) -> tuple[str, str] | tuple[None, None]:
    sheet = load_and_lint(yaml_file)
    if sheet is None:
        return None, None

    keyboard_layouts, system_mappings = load_layout()
    if keyboard_layouts is None or system_mappings is None:
        return None, None

    html_content = generate_html(sheet, keyboard_layouts, system_mappings)
    if html_content is None:
        return None, None

    slug = re.sub(r"[^\w-]+", "_", sheet.title.lower()).strip("_")
    filename = f"{slug}_cheatsheet.html" if slug else "cheatsheet.html"
    if used_filenames is not None:
        if filename in used_filenames:
            logging.error(f"{yaml_file}: output file {filename} is already used by another cheat sheet")
            return None, None
        used_filenames.add(filename)
    html_output = os.path.join(OUTPUT_DIR, filename)

    if not write_html_content(html_output, html_content):
        logging.error(f"Failed to write HTML content to {html_output}")
        return None, None

    logging.info(f"Cheatsheet generated: {html_output}")

    return sheet.title, filename


def generate_index(cheatsheets):
    template_path = "index/index_template.html"
    return render_template(template_path, {"cheatsheets": cheatsheets})


def generate_all() -> int:
    yaml_files = sorted(CHEATSHEETS_DIR.glob("*.yaml"))

    if not yaml_files:
        print("No YAML files found in the cheatsheets directory. Run `koalakeys init` to create one.")
        return 1

    OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

    cheatsheets = []
    failed = []
    used_filenames: set[str] = set()
    for yaml_file in yaml_files:
        title, filename = main(yaml_file, used_filenames)
        if title and filename:
            cheatsheets.append({"title": title, "filename": filename})
        else:
            failed.append(yaml_file.name)

    if not cheatsheets:
        print("No valid cheatsheets were generated due to errors.")
        return 1

    html_content = generate_index(cheatsheets)
    if not html_content:
        logging.error("Failed to generate index page.")
        return 1

    index_output = os.path.join(OUTPUT_DIR, "index.html")
    if not write_html_content(index_output, html_content):
        logging.error("Failed to write index page.")
        return 1

    logging.info(f"Index page generated: {index_output}")
    print(f"Generated cheatsheets for {len(cheatsheets)} YAML files.")
    if failed:
        print(f"Failed to generate {len(failed)} cheatsheet(s): {', '.join(failed)}")
        return 1
    return 0


def cli():
    code = generate_all()
    if code:
        sys.exit(code)


if __name__ == "__main__":
    cli()
