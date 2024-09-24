import yaml
from jinja2 import Template
import sys


def load_yaml(file_path):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


def normalize_shortcuts(data):
    normalized = {}
    for section, shortcuts in data.get("shortcuts", {}).items():
        normalized[section] = {}
        for shortcut, details in shortcuts.items():
            normalized_shortcut = "+".join(
                key.strip().lower() for key in shortcut.split("+")
            )
            normalized[section][normalized_shortcut] = details
    return normalized


def generate_html(data):
    with open("src/cheatsheet_template.html", "r") as file:
        template = Template(file.read())

    data["shortcuts"] = normalize_shortcuts(data)
    return template.render(**data)


def main():
    if len(sys.argv) != 2:
        print("Usage: python generate_cheatsheet.py <yaml_file>")
        sys.exit(1)

    yaml_file = sys.argv[1]
    data = load_yaml(yaml_file)
    html_content = generate_html(data)

    output_file = f"output/{data['title'].lower().replace(' ', '_')}_cheatsheet.html"
    with open(output_file, "w") as file:
        file.write(html_content)

    print(f"Cheatsheet generated: {output_file}")


if __name__ == "__main__":
    main()
