from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError
import re
from logger import get_logger

logger = get_logger()

yaml_safe = YAML(typ='safe')
yaml_rw = YAML()
yaml_rw.indent(mapping=2, sequence=4, offset=2)
yaml_rw.preserve_quotes = True
yaml_rw.width = 100

def validate_required_keys(data):
    required_keys = ['title', 'shortcuts']
    for key in required_keys:
        if key not in data:
            logger.error(f"Missing required top-level key: '{key}'")
            return False
    return True

def validate_title(data):
    if 'title' in data and not isinstance(data['title'], str):
        logger.error("Title must be a string")
        return False
    return True

def validate_render_options(data):
    is_valid = True
    render_keys = data.get('RenderKeys', True)
    allow_text = data.get('AllowText', False)

    if 'RenderKeys' in data and not isinstance(render_keys, bool):
        logger.error("RenderKeys must be a boolean value (true/false)")
        is_valid = False

    if 'AllowText' in data and not isinstance(allow_text, bool):
        logger.error("AllowText must be a boolean value (true/false)")
        is_valid = False

    if allow_text and render_keys:
        logger.error("AllowText can only be true when RenderKeys is false")
        is_valid = False

    return is_valid

def validate_layout(data):
    if 'layout' not in data:
        return True

    if not isinstance(data['layout'], dict):
        logger.error("Layout must be a dictionary")
        return False

    valid_keyboards = ['US', 'UK', 'DE', 'FR', 'ES']
    valid_systems = ['Darwin', 'Linux', 'Windows']
    is_valid = True
    
    if 'keyboard' in data['layout'] and data['layout']['keyboard'] not in valid_keyboards:
        logger.error(f"Invalid keyboard layout. Must be one of: {', '.join(valid_keyboards)}")
        is_valid = False
    
    if 'system' in data['layout'] and data['layout']['system'] not in valid_systems:
        logger.error(f"Invalid system. Must be one of: {', '.join(valid_systems)}")
        is_valid = False

    return is_valid

def validate_shortcuts(data):
    if 'shortcuts' not in data:
        return True

    if not isinstance(data['shortcuts'], dict):
        logger.error("Shortcuts must be a dictionary")
        return False

    allow_text = data.get('AllowText', False)
    is_valid = True
    
    for category, shortcuts in data['shortcuts'].items():
        if not isinstance(shortcuts, dict):
            logger.error(f"Category '{category}' must contain a dictionary of shortcuts")
            is_valid = False
            continue

        for shortcut, details in shortcuts.items():
            if not isinstance(details, dict) or 'description' not in details:
                logger.error(f"Shortcut '{shortcut}' in category '{category}' must have a 'description' key")
                is_valid = False
            elif not isinstance(details['description'], str):
                logger.error(f"Description for shortcut '{shortcut}' in category '{category}' must be a string")
                is_valid = False
            
            if not allow_text:
                if not re.match(r'^[A-Za-z0-9+⌘⌥⌃⇧←→↑↓\s\-\|\[\],.:/`"?<>=\\⌃]+$', shortcut):
                    logger.error(f"Invalid shortcut format: '{shortcut}' in category '{category}'")
                    is_valid = False

    return is_valid

def validate_yaml(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = yaml_safe.load(file)
    except YAMLError as e:
        logger.error(f"YAML parsing error in {file_path}: {str(e)}")
        return False
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error reading {file_path}: {str(e)}")
        return False
    
    if data is None:
        logger.error(f"Empty YAML file: {file_path}")
        return False

    is_valid = True

    if not validate_required_keys(data):
        is_valid = False
    if not validate_title(data):
        is_valid = False
    if not validate_render_options(data):
        is_valid = False
    if not validate_layout(data):
        is_valid = False
    if not validate_shortcuts(data):
        is_valid = False

    if is_valid:
        logger.info(f"YAML validation successful: {file_path}")
    else:
        logger.error(f"YAML validation failed: {file_path}")

    return is_valid

def lint_yaml(file_path):
    warnings = []

    with open(file_path, 'r', encoding="utf-8") as file:
        lines = file.readlines()

    for i, line in enumerate(lines, start=1):
        if len(line.rstrip()) > 100:
            warnings.append(f"Line {i} is longer than 100 characters")

        indent = len(line) - len(line.lstrip())
        if indent % 2 != 0:
            warnings.append(f"Line {i} has inconsistent indentation")

        if line.rstrip() != line.rstrip('\n'):
            warnings.append(f"Line {i} has trailing whitespace")

    return warnings

def fix_yaml(file_path):
    with open(file_path, 'r', encoding="utf-8") as file:
        content = file.read()

    fixes = []

    special_chars = {'⌘': 'CMD', '⌃': 'CTRL', '⌥': 'ALT', '⇧': 'SHIFT'}
    for char, replacement in special_chars.items():
        if char in content:
            content = content.replace(char, replacement)
            fixes.append(f"Replaced '{char}' with '{replacement}'")

    lowercase_keys = ['cmd', 'ctrl', 'alt', 'shift']
    for key in lowercase_keys:
        pattern = re.compile(r'\b' + key + r'\b', re.IGNORECASE)
        content = pattern.sub(key.upper(), content)
        if pattern.search(content):
            fixes.append(f"Converted '{key}' to uppercase")

    # Fix indentation
    lines = content.split('\n')
    fixed_lines = []
    for line in lines:
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        fixed_indent = (indent // 2) * 2
        if fixed_indent != indent:
            fixes.append(f"Fixed indentation in line: {line.strip()}")
        fixed_lines.append(' ' * fixed_indent + stripped.rstrip())

    fixed_content = '\n'.join(fixed_lines)

    with open(file_path, 'w', encoding="utf-8") as file:
        file.write(fixed_content)

    return fixes

def format_yaml(file_path):
    yaml = YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.preserve_quotes = True
    yaml.width = 100

    with open(file_path, 'r', encoding='utf-8') as file:
        data = yaml.load(file)

    with open(file_path, 'w', encoding='utf-8') as file:
        yaml.dump(data, file)

    return "YAML file has been formatted for improved readability."

def process_yaml(file_path):
    print(f"Processing {file_path}...")
    
    errors = validate_yaml(file_path)
    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"- {error}")
    else:
        print("Validation passed.")

    warnings = lint_yaml(file_path)
    if warnings:
        print("Linting warnings:")
        for warning in warnings:
            print(f"- {warning}")
    else:
        print("Linting passed.")

    fixes = fix_yaml(file_path)
    if fixes:
        print("Fixes applied:")
        for fix in fixes:
            print(f"- {fix}")
    else:
        print("No fixes were necessary.")

    format_message = format_yaml(file_path)
    print(format_message)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python validate_yaml.py <path_to_yaml_file>")
        sys.exit(1)
    
    yaml_file = sys.argv[1]
    process_yaml(yaml_file)
