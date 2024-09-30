from jinja2 import Template
import logging

def render_template(template_path, data):
    try:
        with open(template_path, "r") as file:
            template = Template(file.read())
    except FileNotFoundError:
        logging.error(f"Error: Template file '{template_path}' not found.")
        return None
    except Exception as e:
        logging.error(f"Error reading template file: {e}")
        return None

    try:
        return template.render(**data)
    except Exception as e:
        logging.error(f"Error rendering template: {e}")
        return None
