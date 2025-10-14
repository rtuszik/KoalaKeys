from jinja2 import Environment, FileSystemLoader
from logger import get_logger
from pathlib import Path

logging = get_logger()


def render_template(template_path, data):
    try:
        templates_dir = Path(__file__).parent / "templates"

        env = Environment(loader=FileSystemLoader(str(templates_dir)))

        template = env.get_template(str(template_path))
        return template.render(**data)

    except FileNotFoundError:
        logging.error(f"Error: Template file '{template_path}' not found.")
        return None
    except Exception as e:
        logging.error(f"Error reading template file: {e}")
        return None
