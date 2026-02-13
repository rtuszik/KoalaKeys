from validate_yaml import (
    lint_yaml,
    validate_layout,
    validate_render_options,
    validate_required_keys,
    validate_shortcuts,
    validate_title,
    validate_yaml,
)


class TestValidateRequiredKeys:
    def test_valid_data(self, valid_yaml_data):
        assert validate_required_keys(valid_yaml_data) is True

    def test_missing_title(self):
        data = {"shortcuts": {"General": {}}}
        assert validate_required_keys(data) is False

    def test_missing_shortcuts(self):
        data = {"title": "Test"}
        assert validate_required_keys(data) is False

    def test_empty_data(self):
        assert validate_required_keys({}) is False


class TestValidateTitle:
    def test_valid_string_title(self):
        assert validate_title({"title": "My Cheatsheet"}) is True

    def test_missing_title_key(self):
        assert validate_title({}) is True

    def test_invalid_int_title(self):
        assert validate_title({"title": 123}) is False

    def test_invalid_list_title(self):
        assert validate_title({"title": ["a", "b"]}) is False


class TestValidateRenderOptions:
    def test_defaults(self):
        assert validate_render_options({}) is True

    def test_valid_render_keys_true(self):
        assert validate_render_options({"RenderKeys": True}) is True

    def test_valid_render_keys_false(self):
        assert validate_render_options({"RenderKeys": False}) is True

    def test_invalid_render_keys_string(self):
        assert validate_render_options({"RenderKeys": "true"}) is False

    def test_invalid_allow_text_string(self):
        assert validate_render_options({"AllowText": "false"}) is False

    def test_conflict_allowtext_with_renderkeys(self):
        assert validate_render_options({"AllowText": True}) is False

    def test_valid_allowtext_mode(self):
        assert validate_render_options({"RenderKeys": False, "AllowText": True}) is True


class TestValidateLayout:
    def test_missing_layout(self):
        assert validate_layout({}) is True

    def test_valid_layout(self):
        data = {"layout": {"keyboard": "US", "system": "Darwin"}}
        assert validate_layout(data) is True

    def test_valid_all_keyboards(self):
        for kb in ["US", "UK", "DE", "FR", "ES", "DVORAK"]:
            assert validate_layout({"layout": {"keyboard": kb}}) is True

    def test_valid_all_systems(self):
        for sys in ["Darwin", "Linux", "Windows"]:
            assert validate_layout({"layout": {"system": sys}}) is True

    def test_invalid_keyboard(self):
        data = {"layout": {"keyboard": "INVALID"}}
        assert validate_layout(data) is False

    def test_invalid_system(self):
        data = {"layout": {"system": "INVALID"}}
        assert validate_layout(data) is False

    def test_non_dict_layout(self):
        assert validate_layout({"layout": "US"}) is False


class TestValidateShortcuts:
    def test_missing_shortcuts(self):
        assert validate_shortcuts({}) is True

    def test_valid_shortcuts(self, valid_yaml_data):
        assert validate_shortcuts(valid_yaml_data) is True

    def test_non_dict_shortcuts(self):
        assert validate_shortcuts({"shortcuts": ["a", "b"]}) is False

    def test_non_dict_category(self):
        data = {"shortcuts": {"General": "not a dict"}}
        assert validate_shortcuts(data) is False

    def test_missing_description(self):
        data = {"shortcuts": {"General": {"Ctrl+C": {"other": "value"}}}}
        assert validate_shortcuts(data) is False

    def test_non_string_description(self):
        data = {"shortcuts": {"General": {"Ctrl+C": {"description": 123}}}}
        assert validate_shortcuts(data) is False

    def test_invalid_shortcut_format(self):
        data = {"shortcuts": {"General": {"Ctrl+@#$": {"description": "Test"}}}}
        assert validate_shortcuts(data) is False

    def test_allowtext_mode_accepts_text(self):
        data = {
            "AllowText": True,
            "RenderKeys": False,
            "shortcuts": {"Commands": {"kubectl get pods": {"description": "List pods"}}},
        }
        assert validate_shortcuts(data) is True


class TestValidateYaml:
    def test_valid_minimal_file(self, valid_fixtures):
        assert validate_yaml(valid_fixtures / "minimal.yaml") is True

    def test_valid_full_featured_file(self, valid_fixtures):
        assert validate_yaml(valid_fixtures / "full_featured.yaml") is True

    def test_valid_allowtext_file(self, valid_fixtures):
        assert validate_yaml(valid_fixtures / "allowtext_mode.yaml") is True

    def test_file_not_found(self, fixtures_dir):
        assert validate_yaml(fixtures_dir / "nonexistent.yaml") is False

    def test_empty_file(self, invalid_fixtures):
        assert validate_yaml(invalid_fixtures / "empty.yaml") is False

    def test_malformed_yaml(self, invalid_fixtures):
        assert validate_yaml(invalid_fixtures / "malformed.yaml") is False

    def test_missing_title(self, invalid_fixtures):
        assert validate_yaml(invalid_fixtures / "missing_title.yaml") is False

    def test_missing_shortcuts(self, invalid_fixtures):
        assert validate_yaml(invalid_fixtures / "missing_shortcuts.yaml") is False

    def test_invalid_keyboard(self, invalid_fixtures):
        assert validate_yaml(invalid_fixtures / "invalid_keyboard.yaml") is False

    def test_invalid_system(self, invalid_fixtures):
        assert validate_yaml(invalid_fixtures / "invalid_system.yaml") is False

    def test_non_dict_shortcuts(self, invalid_fixtures):
        assert validate_yaml(invalid_fixtures / "non_dict_shortcuts.yaml") is False

    def test_non_dict_category(self, invalid_fixtures):
        assert validate_yaml(invalid_fixtures / "non_dict_category.yaml") is False

    def test_missing_description(self, invalid_fixtures):
        assert validate_yaml(invalid_fixtures / "missing_description.yaml") is False


class TestLintYaml:
    def test_clean_file(self, valid_fixtures):
        warnings = lint_yaml(valid_fixtures / "minimal.yaml")
        assert warnings == []

    def test_long_line_warning(self, invalid_fixtures):
        warnings = lint_yaml(invalid_fixtures / "long_lines.yaml")
        assert any("longer than 100" in w for w in warnings)

    def test_bad_indentation_warning(self, invalid_fixtures):
        warnings = lint_yaml(invalid_fixtures / "bad_indentation.yaml")
        assert any("indentation" in w for w in warnings)

    def test_trailing_whitespace_warning(self, invalid_fixtures):
        warnings = lint_yaml(invalid_fixtures / "trailing_whitespace.yaml")
        assert any("trailing whitespace" in w for w in warnings)


class TestFixYaml:
    def test_fix_special_characters(self, tmp_path):
        from validate_yaml import fix_yaml

        test_file = tmp_path / "special_chars.yaml"
        test_file.write_text('title: "Test"\nshortcuts:\n  General:\n    "⌘+C":\n      description: "Copy"')

        fixes = fix_yaml(test_file)

        content = test_file.read_text()
        assert "CMD" in content
        assert any("Replaced" in f for f in fixes)

    def test_fix_lowercase_modifiers(self, tmp_path):
        from validate_yaml import fix_yaml

        test_file = tmp_path / "lowercase.yaml"
        test_file.write_text('title: "Test"\nshortcuts:\n  General:\n    "ctrl+c":\n      description: "Copy"')

        fix_yaml(test_file)

        content = test_file.read_text()
        assert "CTRL" in content

    def test_fix_odd_indentation(self, tmp_path):
        from validate_yaml import fix_yaml

        test_file = tmp_path / "odd_indent.yaml"
        test_file.write_text('title: "Test"\n   odd_indent: true')

        fix_yaml(test_file)

        content = test_file.read_text()
        lines = content.split("\n")
        for line in lines:
            indent = len(line) - len(line.lstrip())
            assert indent % 2 == 0

    def test_no_fixes_needed(self, tmp_path):
        from validate_yaml import fix_yaml

        test_file = tmp_path / "clean.yaml"
        test_file.write_text('title: "Test"\nshortcuts:\n  General:\n    "CTRL+C":\n      description: "Copy"')

        fixes = fix_yaml(test_file)

        assert not any("Replaced" in f for f in fixes)


class TestFormatYaml:
    def test_format_yaml_returns_message(self, tmp_path):
        from validate_yaml import format_yaml

        test_file = tmp_path / "format_test.yaml"
        test_file.write_text('title: "Test"\nshortcuts:\n  General:\n    "Ctrl+C":\n      description: "Copy"')

        result = format_yaml(test_file)

        assert "formatted" in result.lower()

    def test_format_yaml_preserves_content(self, tmp_path):
        from validate_yaml import format_yaml

        test_file = tmp_path / "format_test.yaml"
        original = 'title: "Test Title"\nshortcuts:\n  General:\n    "Ctrl+C":\n      description: "Copy"'
        test_file.write_text(original)

        format_yaml(test_file)

        content = test_file.read_text()
        assert "Test Title" in content
        assert "Copy" in content
