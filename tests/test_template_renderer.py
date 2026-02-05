from template_renderer import render_template


class TestRenderTemplate:
    def test_valid_cheatsheet_template(self, valid_yaml_data, sample_keyboard_layouts):
        data = {
            **valid_yaml_data,
            "shortcuts": {"General": {"Ctrl<sep>C": {"description": "Copy"}}},
            "keyboard_layout": sample_keyboard_layouts["US"]["layout"],
            "layout": {"keyboard": "US", "system": "Darwin"},
            "render_keys": True,
            "allow_text": False,
        }
        result = render_template("cheatsheets/cheatsheet-template.html", data)
        assert result is not None
        assert isinstance(result, str)

    def test_valid_index_template(self):
        data = {
            "cheatsheets": [
                {"title": "VS Code", "filename": "vscode_cheatsheet.html"},
                {"title": "Vim", "filename": "vim_cheatsheet.html"},
            ]
        }
        result = render_template("index/index_template.html", data)
        assert result is not None
        assert "VS Code" in result
        assert "Vim" in result

    def test_missing_template_returns_none(self):
        result = render_template("nonexistent/template.html", {})
        assert result is None

    def test_template_renders_variables(self):
        data = {"cheatsheets": [{"title": "Test Title", "filename": "test.html"}]}
        result = render_template("index/index_template.html", data)
        assert "Test Title" in result

    def test_empty_cheatsheets_list(self):
        result = render_template("index/index_template.html", {"cheatsheets": []})
        assert result is not None

    def test_index_contains_html_structure(self):
        data = {"cheatsheets": [{"title": "Test", "filename": "test.html"}]}
        result = render_template("index/index_template.html", data)
        assert "<" in result and ">" in result

    def test_cheatsheet_template_contains_title(self, valid_yaml_data, sample_keyboard_layouts):
        data = {
            **valid_yaml_data,
            "shortcuts": {"General": {"Ctrl<sep>C": {"description": "Copy"}}},
            "keyboard_layout": sample_keyboard_layouts["US"]["layout"],
            "layout": {"keyboard": "US", "system": "Darwin"},
            "render_keys": True,
            "allow_text": False,
        }
        result = render_template("cheatsheets/cheatsheet-template.html", data)
        assert valid_yaml_data["title"] in result
