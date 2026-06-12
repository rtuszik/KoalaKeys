from koalakeys.generate_cheatsheet import (
    generate_html,
    generate_index,
    get_layout_info,
    load_layout,
    load_yaml,
    normalize_shortcuts,
    replace_shortcut_names,
    validate_and_lint,
    write_html_content,
)


class TestLoadYaml:
    def test_valid_file(self, valid_fixtures):
        result = load_yaml(valid_fixtures / "minimal.yaml")
        assert isinstance(result, dict)
        assert "title" in result

    def test_file_not_found(self, fixtures_dir):
        result = load_yaml(fixtures_dir / "nonexistent.yaml")
        assert result is None

    def test_malformed_yaml(self, invalid_fixtures):
        result = load_yaml(invalid_fixtures / "malformed.yaml")
        assert result is None

    def test_returns_correct_title(self, valid_fixtures):
        result = load_yaml(valid_fixtures / "minimal.yaml")
        assert result is not None
        assert result["title"] == "Minimal Test"

    def test_returns_shortcuts(self, valid_fixtures):
        result = load_yaml(valid_fixtures / "minimal.yaml")
        assert result is not None
        assert "shortcuts" in result
        assert "General" in result["shortcuts"]


class TestReplaceShortcutNamesWithMappings:
    def test_cmd_to_symbol(self, sample_system_mappings):
        result = replace_shortcut_names("CMD+C", sample_system_mappings)
        assert "⌘" in result or "modifier-symbol" in result

    def test_multiple_modifiers(self, sample_system_mappings):
        result = replace_shortcut_names("CMD+Shift+C", sample_system_mappings)
        assert "<sep>" in result

    def test_arrow_key_up(self):
        result = replace_shortcut_names("Ctrl+Up", {})
        assert "↑" in result

    def test_arrow_key_down(self):
        result = replace_shortcut_names("Ctrl+Down", {})
        assert "↓" in result

    def test_arrow_key_left(self):
        result = replace_shortcut_names("Ctrl+Left", {})
        assert "←" in result

    def test_arrow_key_right(self):
        result = replace_shortcut_names("Ctrl+Right", {})
        assert "→" in result

    def test_preserves_regular_keys(self):
        result = replace_shortcut_names("A+B+C", {})
        assert "A" in result
        assert "B" in result
        assert "C" in result


class TestNormalizeShortcuts:
    def test_basic_normalization(self, valid_yaml_data):
        result = normalize_shortcuts(valid_yaml_data, {})
        assert "General" in result
        keys = list(result["General"].keys())
        assert any("<sep>" in k for k in keys)

    def test_with_system_mappings(self, valid_yaml_data, sample_system_mappings):
        result = normalize_shortcuts(valid_yaml_data, sample_system_mappings)
        keys = list(result["General"].keys())
        assert len(keys) > 0

    def test_allowtext_mode_skips_processing(self):
        data = {"AllowText": True, "shortcuts": {"Commands": {"kubectl get pods": {"description": "List pods"}}}}
        result = normalize_shortcuts(data, {})
        assert "kubectl get pods" in result["Commands"]

    def test_empty_shortcuts(self):
        result = normalize_shortcuts({"shortcuts": {}}, {})
        assert result == {}

    def test_preserves_description(self, valid_yaml_data):
        result = normalize_shortcuts(valid_yaml_data, {})
        for key, details in result["General"].items():
            assert "description" in details
            assert details["description"] == "Copy"

    def test_multiple_categories(self):
        data = {
            "shortcuts": {
                "General": {"Ctrl+C": {"description": "Copy"}},
                "Navigation": {"Ctrl+N": {"description": "New"}},
            }
        }
        result = normalize_shortcuts(data, {})
        assert "General" in result
        assert "Navigation" in result


class TestGetLayoutInfo:
    def test_defaults(self):
        result = get_layout_info({})
        assert result["keyboard"] == "US"
        assert result["system"] == "Darwin"

    def test_custom_keyboard(self):
        result = get_layout_info({"layout": {"keyboard": "DE"}})
        assert result["keyboard"] == "DE"

    def test_custom_system(self):
        result = get_layout_info({"layout": {"system": "Linux"}})
        assert result["system"] == "Linux"

    def test_partial_layout(self):
        result = get_layout_info({"layout": {"keyboard": "FR"}})
        assert result["keyboard"] == "FR"
        assert result["system"] == "Darwin"

    def test_full_custom_layout(self):
        result = get_layout_info({"layout": {"keyboard": "DVORAK", "system": "Windows"}})
        assert result["keyboard"] == "DVORAK"
        assert result["system"] == "Windows"


class TestGenerateHtml:
    def test_returns_string(self, valid_yaml_data, sample_keyboard_layouts, sample_system_mappings):
        system_mappings = {"Darwin": sample_system_mappings}
        result = generate_html(valid_yaml_data, sample_keyboard_layouts, system_mappings)
        assert result is not None
        assert isinstance(result, str)

    def test_contains_title(self, valid_yaml_data, sample_keyboard_layouts, sample_system_mappings):
        system_mappings = {"Darwin": sample_system_mappings}
        result = generate_html(valid_yaml_data, sample_keyboard_layouts, system_mappings)
        assert valid_yaml_data["title"] in result

    def test_contains_html_structure(self, valid_yaml_data, sample_keyboard_layouts, sample_system_mappings):
        system_mappings = {"Darwin": sample_system_mappings}
        result = generate_html(valid_yaml_data, sample_keyboard_layouts, system_mappings)
        assert "<" in result and ">" in result


class TestThemeIntegration:
    def _sm(self, sample_system_mappings):
        return {"Darwin": sample_system_mappings}

    def test_injects_token_block(self, valid_yaml_data, sample_keyboard_layouts, sample_system_mappings):
        result = generate_html(dict(valid_yaml_data), sample_keyboard_layouts, self._sm(sample_system_mappings))
        assert ":root {" in result
        assert "--kk-bg:" in result
        assert "body.dark-mode {" in result  # catppuccin defines both modes

    def test_unknown_theme_returns_none(self, valid_yaml_data, sample_keyboard_layouts, sample_system_mappings):
        data = {**valid_yaml_data, "theme": "does-not-exist-xyz"}
        result = generate_html(data, sample_keyboard_layouts, self._sm(sample_system_mappings))
        assert result is None

    def test_inline_custom_css_emitted_and_sanitized(
        self, valid_yaml_data, sample_keyboard_layouts, sample_system_mappings
    ):
        data = {**valid_yaml_data, "custom_css_inline": ".x { color: red; } </style><script>evil()</script>"}
        result = generate_html(data, sample_keyboard_layouts, self._sm(sample_system_mappings))
        assert ".x { color: red; }" in result
        assert "</style><script>" not in result  # breakout neutralized

    def test_no_theme_field_defaults_catppuccin(self, valid_yaml_data, sample_keyboard_layouts, sample_system_mappings):
        result = generate_html(dict(valid_yaml_data), sample_keyboard_layouts, self._sm(sample_system_mappings))
        assert "--kk-key-text: #f38ba8;" in result  # catppuccin dark key-text

    def test_dark_only_user_theme_hides_toggle(
        self, valid_yaml_data, sample_keyboard_layouts, sample_system_mappings, tmp_path, monkeypatch
    ):
        import koalakeys.generate_cheatsheet as gc

        themes = tmp_path / "themes"
        themes.mkdir()
        (themes / "vimdark.yaml").write_text("extends: catppuccin\nmodes: [dark]\n", encoding="utf-8")
        monkeypatch.setattr(gc, "THEMES_DIR", themes)

        data = {**valid_yaml_data, "theme": "vimdark"}
        result = generate_html(data, sample_keyboard_layouts, self._sm(sample_system_mappings))
        assert 'id="dark-mode-toggle"' not in result  # single-mode: no toggle button
        assert "body.dark-mode {" not in result  # dark folded into :root


class TestCustomCssFile:
    def test_loads_and_sanitizes_file(self, tmp_path, monkeypatch):
        import koalakeys.generate_cheatsheet as gc

        styles = tmp_path / "styles"
        styles.mkdir()
        (styles / "extra.css").write_text(".x { color: red; } </style>", encoding="utf-8")
        monkeypatch.setattr(gc, "STYLES_DIR", styles)

        out = gc.load_custom_css_file("extra.css")
        assert ".x { color: red; }" in out
        assert "</style>" not in out

    def test_missing_file_logs_and_returns_empty(self, tmp_path, monkeypatch):
        import koalakeys.generate_cheatsheet as gc

        monkeypatch.setattr(gc, "STYLES_DIR", tmp_path / "styles")
        assert gc.load_custom_css_file("nope.css") == ""

    def test_empty_filename_returns_empty(self):
        from koalakeys.generate_cheatsheet import load_custom_css_file

        assert load_custom_css_file("") == ""
        assert load_custom_css_file(None) == ""


class TestValidateAndLint:
    def test_valid_file_returns_true(self, valid_fixtures):
        assert validate_and_lint(valid_fixtures / "minimal.yaml") is True

    def test_valid_full_featured_returns_true(self, valid_fixtures):
        assert validate_and_lint(valid_fixtures / "full_featured.yaml") is True

    def test_invalid_file_returns_false(self, invalid_fixtures):
        assert validate_and_lint(invalid_fixtures / "missing_title.yaml") is False

    def test_malformed_file_returns_false(self, invalid_fixtures):
        assert validate_and_lint(invalid_fixtures / "malformed.yaml") is False


class TestLoadLayout:
    def test_load_layout_returns_tuple(self):
        keyboard_layouts, system_mappings = load_layout()
        assert keyboard_layouts is not None
        assert system_mappings is not None
        assert isinstance(keyboard_layouts, dict)
        assert isinstance(system_mappings, dict)

    def test_load_layout_contains_us_keyboard(self):
        keyboard_layouts, _ = load_layout()
        assert "US" in keyboard_layouts

    def test_load_layout_contains_darwin_mappings(self):
        _, system_mappings = load_layout()
        assert "Darwin" in system_mappings


class TestWriteHtmlContent:
    def test_write_html_content_success(self, tmp_path):
        output_file = tmp_path / "test.html"
        content = "<html><body>Test</body></html>"

        result = write_html_content(output_file, content)

        assert result is True
        assert output_file.exists()
        assert output_file.read_text() == content

    def test_write_html_content_creates_file(self, tmp_path):
        output_file = tmp_path / "new_file.html"
        content = "<html>Content</html>"

        write_html_content(output_file, content)

        assert output_file.exists()


class TestGenerateIndex:
    def test_generate_index_returns_html(self):
        cheatsheets = [
            {"title": "Test1", "filename": "test1.html"},
            {"title": "Test2", "filename": "test2.html"},
        ]

        result = generate_index(cheatsheets)

        assert result is not None
        assert isinstance(result, str)

    def test_generate_index_contains_titles(self):
        cheatsheets = [
            {"title": "VS Code Shortcuts", "filename": "vscode.html"},
        ]

        result = generate_index(cheatsheets)

        assert "VS Code Shortcuts" in result

    def test_generate_index_empty_list(self):
        result = generate_index([])

        assert result is not None


class TestMainFunction:
    def test_main_with_valid_file(self, valid_fixtures, isolated_output):
        from koalakeys.generate_cheatsheet import main

        title, filename = main(valid_fixtures / "minimal.yaml")

        assert title == "Minimal Test"
        assert filename is not None
        assert filename.endswith(".html")

    def test_main_with_invalid_file(self, invalid_fixtures):
        from koalakeys.generate_cheatsheet import main

        title, filename = main(invalid_fixtures / "missing_title.yaml")

        assert title is None
        assert filename is None

    def test_main_with_nonexistent_file(self, invalid_fixtures):
        from koalakeys.generate_cheatsheet import main

        title, filename = main(invalid_fixtures / "empty.yaml")

        assert title is None
        assert filename is None
