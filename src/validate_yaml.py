import yaml
from yaml.parser import ParserError
from yaml.scanner import ScannerError
import re
from ruamel.yaml import YAML

def validate_yaml(file_path):
    errors = []

    try:
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
    except (ParserError, ScannerError) as e:
        return [f"YAML parsing error: {str(e)}"]

    # Check for required top-level keys
    required_keys = ['title', 'shortcuts']
    for key in required_keys:
        if key not in data:
            errors.append(f"Missing required top-level key: '{key}'")

    # Validate title
    if 'title' in data and not isinstance(data['title'], str):
        errors.append("Title must be a string")

    # Validate RenderKeys and AllowText if present
    render_keys = data.get('RenderKeys', True)
    allow_text = data.get('AllowText', False)

    if 'RenderKeys' in data and not isinstance(render_keys, bool):
        errors.append("RenderKeys must be a boolean value (true/false)")

    if 'AllowText' in data and not isinstance(allow_text, bool):
        errors.append("AllowText must be a boolean value (true/false)")

    # Check if AllowText is only enabled when RenderKeys is false
    if allow_text and render_keys:
        errors.append("AllowText can only be true when RenderKeys is false")

    # Validate layout (if present)
    if 'layout' in data:
        if not isinstance(data['layout'], dict):
            errors.append("Layout must be a dictionary")
        else:
            valid_keyboards = ['US', 'UK', 'DE', 'FR', 'ES']
            valid_systems = ['Darwin', 'Linux', 'Windows']
            
            if 'keyboard' in data['layout'] and data['layout']['keyboard'] not in valid_keyboards:
                errors.append(f"Invalid keyboard layout. Must be one of: {', '.join(valid_keyboards)}")
            
            if 'system' in data['layout'] and data['layout']['system'] not in valid_systems:
                errors.append(f"Invalid system. Must be one of: {', '.join(valid_systems)}")

    # Validate shortcuts
    if 'shortcuts' in data:
        if not isinstance(data['shortcuts'], dict):
            errors.append("Shortcuts must be a dictionary")
        else:
            for category, shortcuts in data['shortcuts'].items():
                if not isinstance(shortcuts, dict):
                    errors.append(f"Category '{category}' must contain a dictionary of shortcuts")
                else:
                    for shortcut, details in shortcuts.items():
                        if not isinstance(details, dict) or 'description' not in details:
                            errors.append(f"Shortcut '{shortcut}' in category '{category}' must have a 'description' key")
                        elif not isinstance(details['description'], str):
                            errors.append(f"Description for shortcut '{shortcut}' in category '{category}' must be a string")
                        
                        # Only validate shortcut format if AllowText is false
                        if not allow_text:
                            if not re.match(r'^[A-Za-z0-9+⌘⌥⌃⇧←→↑↓\s\-\|\[\],.:/`"?<>=\\⌃]+$', shortcut):
                                errors.append(f"Invalid shortcut format: '{shortcut}' in category '{category}'")

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
