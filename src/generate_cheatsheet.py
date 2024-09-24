import yaml
from jinja2 import Template
import sys
import os


def load_yaml(file_path):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


def replace_shortcut_names(shortcut):
    replacements = {
        "cmd": "⌘",
        "command": "⌘",
        "option": "⌥",
        "alt": "⌥",
        "ctrl": "⌃",
        "shift": "⇧",
    }
    return "+".join(replacements.get(key.strip().lower(), key.strip()) for key in shortcut.split("+"))


def normalize_shortcuts(data):
    normalized = {}
    for section, shortcuts in data.get("shortcuts", {}).items():
        normalized[section] = {}
        for shortcut, details in shortcuts.items():
            normalized_shortcut = replace_shortcut_names(shortcut)
            normalized[section][normalized_shortcut] = details
    return normalized


def generate_html(data, css_path):
    with open("src/cheatsheet_template.html", "r") as file:
        template = Template(file.read())

    data["shortcuts"] = normalize_shortcuts(data)
    return template.render(css_path=css_path, **data)


def main():
    if len(sys.argv) != 2:
        print("Usage: python generate_cheatsheet.py <yaml_file>")
        sys.exit(1)

    yaml_file = sys.argv[1]
    data = load_yaml(yaml_file)

    css_path = "src/styles.css"
    html_content = generate_html(data, css_path)

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    base_filename = f"{data['title'].lower().replace(' ', '_')}_cheatsheet"
    html_output = os.path.join(output_dir, f"{base_filename}.html")

    with open(html_output, "w") as file:
        file.write(html_content)

    print(f"Cheatsheet generated: {html_output}")


if __name__ == "__main__":
    main()

