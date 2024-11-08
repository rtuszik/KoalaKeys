from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError
import re

# Create YAML instances once
yaml_safe = YAML(typ='safe')
yaml_rw = YAML()
yaml_rw.indent(mapping=2, sequence=4, offset=2)
yaml_rw.preserve_quotes = True
yaml_rw.width = 100

def validate_required_keys(data):
    """Validate presence of required top-level keys."""
    errors = []
    required_keys = ['title', 'shortcuts']
    for key in required_keys:
        if key not in data:
            errors.append(f"Missing required top-level key: '{key}'")
    return errors

def validate_title(data):
    """Validate title field."""
    if 'title' in data and not isinstance(data['title'], str):
        return ["Title must be a string"]
    return []

def validate_render_options(data):
    """Validate RenderKeys and AllowText options."""
    errors = []
    render_keys = data.get('RenderKeys', True)
    allow_text = data.get('AllowText', False)

    if 'RenderKeys' in data and not isinstance(render_keys, bool):
        errors.append("RenderKeys must be a boolean value (true/false)")

    if 'AllowText' in data and not isinstance(allow_text, bool):
        errors.append("AllowText must be a boolean value (true/false)")

    if allow_text and render_keys:
        errors.append("AllowText can only be true when RenderKeys is false")

    return errors

def validate_layout(data):
    """Validate keyboard layout configuration."""
    errors = []
    if 'layout' not in data:
        return errors

    if not isinstance(data['layout'], dict):
        return ["Layout must be a dictionary"]

    valid_keyboards = ['US', 'UK', 'DE', 'FR', 'ES']
    valid_systems = ['Darwin', 'Linux', 'Windows']
    
    if 'keyboard' in data['layout'] and data['layout']['keyboard'] not in valid_keyboards:
        errors.append(f"Invalid keyboard layout. Must be one of: {', '.join(valid_keyboards)}")
    
    if 'system' in data['layout'] and data['layout']['system'] not in valid_systems:
        errors.append(f"Invalid system. Must be one of: {', '.join(valid_systems)}")

    return errors

def validate_shortcuts(data):
    """Validate shortcuts structure and content."""
    errors = []
    if 'shortcuts' not in data:
        return errors

    if not isinstance(data['shortcuts'], dict):
        return ["Shortcuts must be a dictionary"]

    allow_text = data.get('AllowText', False)
    
    for category, shortcuts in data['shortcuts'].items():
        if not isinstance(shortcuts, dict):
            errors.append(f"Category '{category}' must contain a dictionary of shortcuts")
            continue

        for shortcut, details in shortcuts.items():
            if not isinstance(details, dict) or 'description' not in details:
                errors.append(f"Shortcut '{shortcut}' in category '{category}' must have a 'description' key")
            elif not isinstance(details['description'], str):
                errors.append(f"Description for shortcut '{shortcut}' in category '{category}' must be a string")
            
            if not allow_text:
                if not re.match(r'^[A-Za-z0-9+⌘⌥⌃⇧←→↑↓\s\-\|\[\],.:/`"?<>=\\⌃]+$', shortcut):
                    errors.append(f"Invalid shortcut format: '{shortcut}' in category '{category}'")

    return errors

def validate_yaml(file_path):
    """Validate YAML file structure and content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = yaml_safe.load(file)
    except YAMLError as e:
        return [f"YAML parsing error: {str(e)}"]
    
    if data is None:
        return ["Empty YAML file"]

    # Collect all validation errors
    errors = []
    errors.extend(validate_required_keys(data))
    errors.extend(validate_title(data))
    errors.extend(validate_render_options(data))
    errors.extend(validate_layout(data))
    errors.extend(validate_shortcuts(data))

    return errors

def lint_yaml(file_path):
    warnings = []

    with open(file_path, 'r') as file:
        lines = file.readlines()

    for i, line in enumerate(lines, start=1):
        # Check for lines longer than 100 characters
        if len(line.rstrip()) > 100:
            warnings.append(f"Line {i} is longer than 100 characters")

        # Check for inconsistent indentation
        indent = len(line) - len(line.lstrip())
        if indent % 2 != 0:
            warnings.append(f"Line {i} has inconsistent indentation")

        # Check for trailing whitespace
        if line.rstrip() != line.rstrip('\n'):
            warnings.append(f"Line {i} has trailing whitespace")

    return warnings

def fix_yaml(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    fixes = []

    # Replace special characters and convert to uppercase
    special_chars = {'⌘': 'CMD', '⌃': 'CTRL', '⌥': 'ALT', '⇧': 'SHIFT'}
    for char, replacement in special_chars.items():
        if char in content:
            content = content.replace(char, replacement)
            fixes.append(f"Replaced '{char}' with '{replacement}'")

    # Convert lowercase special keys to uppercase
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
        fixed_indent = (indent // 2) * 2  # Round down to nearest even number
        if fixed_indent != indent:
            fixes.append(f"Fixed indentation in line: {line.strip()}")
        fixed_lines.append(' ' * fixed_indent + stripped.rstrip())

    fixed_content = '\n'.join(fixed_lines)

    # Write fixed content back to file
    with open(file_path, 'w') as file:
        file.write(fixed_content)

    return fixes

def format_yaml(file_path):
    yaml = YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.preserve_quotes = True
    yaml.width = 100

    with open(file_path, 'r') as file:
        data = yaml.load(file)

    with open(file_path, 'w') as file:
        yaml.dump(data, file)

    return "YAML file has been formatted for improved readability."

def process_yaml(file_path):
    print(f"Processing {file_path}...")
    
    # Validate
    errors = validate_yaml(file_path)
    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"- {error}")
    else:
        print("Validation passed.")

    # Lint
    warnings = lint_yaml(file_path)
    if warnings:
        print("Linting warnings:")
        for warning in warnings:
            print(f"- {warning}")
    else:
        print("Linting passed.")

    # Fix
    fixes = fix_yaml(file_path)
    if fixes:
        print("Fixes applied:")
        for fix in fixes:
            print(f"- {fix}")
    else:
        print("No fixes were necessary.")

    # Format
    format_message = format_yaml(file_path)
    print(format_message)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python validate_yaml.py <path_to_yaml_file>")
        sys.exit(1)
    
    yaml_file = sys.argv[1]
    process_yaml(yaml_file)
