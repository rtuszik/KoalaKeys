import yaml
from jinja2 import Template
import sys

def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def generate_html(data):
    with open('cheatsheet_template.html', 'r') as file:
        template = Template(file.read())
    
    print("Debug: Data being passed to template:")
    for key, value in data.items():
        print(f"{key}: {type(value)}")
    
    return template.render(**data)

def main():
    if len(sys.argv) != 2:
        print("Usage: python generate_cheatsheet.py <yaml_file>")
        sys.exit(1)
    
    yaml_file = sys.argv[1]
    data = load_yaml(yaml_file)
    html_content = generate_html(data)
    
    output_file = f"{data['title'].lower().replace(' ', '_')}_cheatsheet.html"
    with open(output_file, 'w') as file:
        file.write(html_content)
    
    print(f"Cheatsheet generated: {output_file}")

if __name__ == "__main__":
    main()
