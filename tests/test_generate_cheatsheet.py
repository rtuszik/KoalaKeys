import pytest

from koalakeys.generate_cheatsheet import (
    generate_html,
    generate_index,
    load_and_lint,
    load_layout,
    load_yaml,
    normalize_shortcuts,
    replace_shortcut_names,
    write_html_content,
)
from koalakeys.models import Cheatsheet

LAYOUT = {"keyboard": "US", "system": "Darwin"}


def sheet(**overrides):
    return Cheatsheet.model_validate({"title": "T", "layout": LAYOUT, **overrides})


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


class TestShortcutHtmlEscaping:
    def test_key_parts_are_escaped(self):
        result = replace_shortcut_names("<img src=x onerror=alert(1)+&", {})
        assert result == "&lt;img src=x onerror=alert(1)<sep>&amp;"

    def test_modifier_symbol_span_is_kept(self):
        assert replace_shortcut_names("cmd", {"cmd": "⌘"}) == '<span class="modifier-symbol">⌘</span>'

    def test_rendered_page_has_no_raw_key_markup(self):
        html = generate_html(
            sheet(shortcuts={"General": {"<img src=x onerror=alert(1)+A": {"description": "Test"}}}),
            {"US": {"layout": []}},
            {"Darwin": {}},
        )
        assert html is not None
        assert "<img src=x" not in html
        assert "&lt;img src=x onerror=alert(1)" in html


class TestNormalizeShortcuts:
    def test_basic_normalization(self, valid_yaml_data):
        result = normalize_shortcuts(Cheatsheet.model_validate(valid_yaml_data), {})
        assert "General" in result
        keys = list(result["General"].keys())
        assert any("<sep>" in k for k in keys)

    def test_with_system_mappings(self, valid_yaml_data, sample_system_mappings):
        result = normalize_shortcuts(Cheatsheet.model_validate(valid_yaml_data), sample_system_mappings)
        assert any("modifier-symbol" in k for k in result["General"])

    def test_allowtext_mode_skips_processing(self):
        data = sheet(
            AllowText=True,
            RenderKeys=False,
            shortcuts={"Commands": {"kubectl get pods": {"description": "List pods"}}},
        )
        result = normalize_shortcuts(data, {})
        assert "kubectl get pods" in result["Commands"]

    def test_preserves_description(self, valid_yaml_data):
        result = normalize_shortcuts(Cheatsheet.model_validate(valid_yaml_data), {})
        for details in result["General"].values():
            assert details.description == "Copy"

    def test_multiple_categories(self):
        data = sheet(
            shortcuts={
                "General": {"Ctrl+C": {"description": "Copy"}},
                "Navigation": {"Ctrl+N": {"description": "New"}},
            }
        )
        result = normalize_shortcuts(data, {})
        assert list(result) == ["General", "Navigation"]

    def test_does_not_mutate_sheet(self, valid_yaml_data):
        data = Cheatsheet.model_validate(valid_yaml_data)
        normalize_shortcuts(data, {})
        assert list(data.shortcuts["General"]) == ["CMD+C"]


class TestGenerateHtml:
    def test_returns_string(self, valid_yaml_data, sample_keyboard_layouts, sample_system_mappings):
        system_mappings = {"Darwin": sample_system_mappings}
        result = generate_html(Cheatsheet.model_validate(valid_yaml_data), sample_keyboard_layouts, system_mappings)
        assert result is not None
        assert isinstance(result, str)

    def test_contains_title(self, valid_yaml_data, sample_keyboard_layouts, sample_system_mappings):
        system_mappings = {"Darwin": sample_system_mappings}
        result = generate_html(Cheatsheet.model_validate(valid_yaml_data), sample_keyboard_layouts, system_mappings)
        assert result is not None
        assert valid_yaml_data["title"] in result

    def test_contains_html_structure(self, valid_yaml_data, sample_keyboard_layouts, sample_system_mappings):
        system_mappings = {"Darwin": sample_system_mappings}
        result = generate_html(Cheatsheet.model_validate(valid_yaml_data), sample_keyboard_layouts, system_mappings)
        assert result is not None
        assert "<" in result and ">" in result


class TestThemeIntegration:
    def _sm(self, sample_system_mappings):
        return {"Darwin": sample_system_mappings}

    def test_injects_token_block(self, valid_yaml_data, sample_keyboard_layouts, sample_system_mappings):
        result = generate_html(
            Cheatsheet.model_validate(valid_yaml_data), sample_keyboard_layouts, self._sm(sample_system_mappings)
        )
        assert result is not None
        assert ":root {" in result
        assert "--kk-bg:" in result
        assert "body.dark-mode {" in result  # catppuccin defines both modes

    def test_unknown_theme_returns_none(self, valid_yaml_data, sample_keyboard_layouts, sample_system_mappings):
        data = {**valid_yaml_data, "theme": "does-not-exist-xyz"}
        result = generate_html(
            Cheatsheet.model_validate(data), sample_keyboard_layouts, self._sm(sample_system_mappings)
        )
        assert result is None

    def test_inline_custom_css_emitted_and_sanitized(
        self, valid_yaml_data, sample_keyboard_layouts, sample_system_mappings
    ):
        data = {**valid_yaml_data, "custom_css_inline": ".x { color: red; } </style><script>evil()</script>"}
        result = generate_html(
            Cheatsheet.model_validate(data), sample_keyboard_layouts, self._sm(sample_system_mappings)
        )
        assert result is not None
        assert ".x { color: red; }" in result
        assert "</style><script>" not in result  # breakout neutralized

    def test_no_theme_field_defaults_catppuccin(self, valid_yaml_data, sample_keyboard_layouts, sample_system_mappings):
        result = generate_html(
            Cheatsheet.model_validate(valid_yaml_data), sample_keyboard_layouts, self._sm(sample_system_mappings)
        )
        assert result is not None
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
        result = generate_html(
            Cheatsheet.model_validate(data), sample_keyboard_layouts, self._sm(sample_system_mappings)
        )
        assert result is not None
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

    @pytest.mark.parametrize("absolute", [False, True])
    def test_rejects_file_outside_styles_dir(self, tmp_path, monkeypatch, absolute):
        import koalakeys.generate_cheatsheet as gc

        styles = tmp_path / "styles"
        styles.mkdir()
        secret = tmp_path / "secret.css"
        secret.write_text(".secret {}", encoding="utf-8")
        monkeypatch.setattr(gc, "STYLES_DIR", styles)

        filename = str(secret.resolve()) if absolute else "../secret.css"
        assert gc.load_custom_css_file(filename) == ""

    def test_allows_nested_file_inside_styles_dir(self, tmp_path, monkeypatch):
        import koalakeys.generate_cheatsheet as gc

        nested = tmp_path / "styles" / "sub"
        nested.mkdir(parents=True)
        (nested / "extra.css").write_text(".nested {}", encoding="utf-8")
        monkeypatch.setattr(gc, "STYLES_DIR", tmp_path / "styles")

        assert ".nested {}" in gc.load_custom_css_file("sub/extra.css")

    def test_empty_filename_returns_empty(self):
        from koalakeys.generate_cheatsheet import load_custom_css_file

        assert load_custom_css_file("") == ""
        assert load_custom_css_file(None) == ""


class TestLoadAndLint:
    def test_valid_file_returns_sheet(self, valid_fixtures):
        result = load_and_lint(valid_fixtures / "minimal.yaml")
        assert result is not None
        assert result.title == "Minimal Test"

    def test_valid_full_featured_returns_sheet(self, valid_fixtures):
        assert load_and_lint(valid_fixtures / "full_featured.yaml") is not None

    def test_invalid_file_returns_none(self, invalid_fixtures):
        assert load_and_lint(invalid_fixtures / "missing_title.yaml") is None

    def test_malformed_file_returns_none(self, invalid_fixtures):
        assert load_and_lint(invalid_fixtures / "malformed.yaml") is None

    def test_lint_warnings_do_not_fail(self, valid_fixtures, tmp_path):
        noisy = tmp_path / "noisy.yaml"
        noisy.write_text((valid_fixtures / "minimal.yaml").read_text().replace('Minimal Test"', 'Minimal Test"   '))
        result = load_and_lint(noisy)
        assert result is not None
        assert result.title == "Minimal Test"


class TestLoadLayout:
    def test_load_layout_returns_tuple(self):
        keyboard_layouts, system_mappings = load_layout()
        assert keyboard_layouts is not None
        assert system_mappings is not None
        assert isinstance(keyboard_layouts, dict)
        assert isinstance(system_mappings, dict)

    def test_load_layout_contains_us_keyboard(self):
        keyboard_layouts, _ = load_layout()
        assert keyboard_layouts is not None
        assert "US" in keyboard_layouts

    def test_load_layout_contains_darwin_mappings(self):
        _, system_mappings = load_layout()
        assert system_mappings is not None
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
        assert result is not None

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


class TestCli:
    def test_cli_with_no_yaml_files_exits_nonzero(self, tmp_path, monkeypatch):
        import koalakeys.generate_cheatsheet as gc

        empty = tmp_path / "cheatsheets"
        empty.mkdir()
        monkeypatch.setattr(gc, "CHEATSHEETS_DIR", empty)

        with pytest.raises(SystemExit) as exc_info:
            gc.cli()

        assert exc_info.value.code == 1

    def test_cli_generates_sheets_and_index(self, valid_fixtures, tmp_path, monkeypatch):
        import koalakeys.generate_cheatsheet as gc

        out = tmp_path / "output"
        monkeypatch.setattr(gc, "CHEATSHEETS_DIR", valid_fixtures)
        monkeypatch.setattr(gc, "OUTPUT_DIR", out)

        gc.cli()

        generated = list(out.glob("*.html"))
        assert (out / "index.html").exists()
        assert len(generated) > 1  # at least one sheet plus the index

    def test_cli_creates_output_dir(self, valid_fixtures, tmp_path, monkeypatch):
        import koalakeys.generate_cheatsheet as gc

        out = tmp_path / "does" / "not" / "exist"
        monkeypatch.setattr(gc, "CHEATSHEETS_DIR", valid_fixtures)
        monkeypatch.setattr(gc, "OUTPUT_DIR", out)

        gc.cli()

        assert out.is_dir()

    def test_partial_failure_returns_nonzero_and_indexes_good_sheets(
        self, valid_fixtures, invalid_fixtures, tmp_path, monkeypatch, capsys
    ):
        import shutil

        import koalakeys.generate_cheatsheet as gc

        sheets = tmp_path / "cheatsheets"
        sheets.mkdir()
        shutil.copy(valid_fixtures / "minimal.yaml", sheets)
        shutil.copy(invalid_fixtures / "missing_title.yaml", sheets)
        out = tmp_path / "output"
        monkeypatch.setattr(gc, "CHEATSHEETS_DIR", sheets)
        monkeypatch.setattr(gc, "OUTPUT_DIR", out)

        assert gc.generate_all() == 1
        assert "Minimal Test" in (out / "index.html").read_text(encoding="utf-8")
        assert "missing_title.yaml" in capsys.readouterr().out
