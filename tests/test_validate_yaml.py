import json
import subprocess
import sys
from pathlib import Path

import pytest

from koalakeys.models import Cheatsheet, Shortcut
from koalakeys.validate_yaml import CheatsheetError, lint_yaml, load_cheatsheet, validate_yaml

SCHEMA_FILE = Path(__file__).parent.parent / "docs" / "schema" / "cheatsheet.schema.json"
LAYOUT = {"keyboard": "US", "system": "Darwin"}
SHORTCUTS = {"General": {"CMD+C": {"description": "Copy"}}}


def problems(tmp_path, text):
    sheet = tmp_path / "sheet.yaml"
    sheet.write_text(text, encoding="utf-8")
    with pytest.raises(CheatsheetError) as exc:
        load_cheatsheet(sheet)
    return exc.value.problems


def validate(**fields):
    return Cheatsheet.model_validate({"title": "T", "layout": LAYOUT, "shortcuts": SHORTCUTS, **fields})


def error_locs(**fields):
    from pydantic import ValidationError

    with pytest.raises(ValidationError) as exc:
        validate(**fields)
    return [".".join(map(str, e["loc"])) for e in exc.value.errors()]


class TestCheatsheetModel:
    def test_defaults(self):
        sheet = validate()
        assert sheet.render_keys is True
        assert sheet.allow_text is False
        assert sheet.theme == "catppuccin"
        assert sheet.custom_css == ""
        assert sheet.custom_css_inline == ""

    def test_aliases_populate_fields(self):
        sheet = validate(RenderKeys=False, AllowText=True)
        assert sheet.render_keys is False
        assert sheet.allow_text is True

    @pytest.mark.parametrize("field", ["title", "layout", "shortcuts"])
    def test_required_fields(self, field):
        data = {"title": "T", "layout": LAYOUT, "shortcuts": SHORTCUTS}
        del data[field]
        with pytest.raises(ValueError, match=field):
            Cheatsheet.model_validate(data)

    @pytest.mark.parametrize("title", ["", "   ", 123, ["a"]])
    def test_invalid_title(self, title):
        assert error_locs(title=title) == ["title"]

    @pytest.mark.parametrize(("field", "value"), [("RenderKeys", "true"), ("AllowText", "false"), ("RenderKeys", 1)])
    def test_bools_are_strict(self, field, value):
        assert error_locs(**{field: value}) == [field]

    def test_allow_text_requires_render_keys_false(self):
        with pytest.raises(ValueError, match="AllowText can only be true when RenderKeys is false"):
            validate(AllowText=True)

    @pytest.mark.parametrize("theme", ["", "  ", 123])
    def test_invalid_theme(self, theme):
        assert error_locs(theme=theme) == ["theme"]

    @pytest.mark.parametrize("field", ["custom_css", "custom_css_inline"])
    def test_css_fields_must_be_strings(self, field):
        assert error_locs(**{field: ["a.css"]}) == [field]

    def test_unknown_top_level_key_rejected(self):
        assert error_locs(colour="red") == ["colour"]

    @pytest.mark.parametrize("keyboard", ["US", "UK", "DE", "FR", "ES", "DVORAK"])
    def test_all_keyboards(self, keyboard):
        assert validate(layout={"keyboard": keyboard, "system": "Darwin"}).layout.keyboard == keyboard

    @pytest.mark.parametrize("system", ["Darwin", "Linux", "Windows"])
    def test_all_systems(self, system):
        assert validate(layout={"keyboard": "US", "system": system}).layout.system == system

    @pytest.mark.parametrize(
        ("layout", "loc"),
        [
            ({"keyboard": "INVALID", "system": "Darwin"}, "layout.keyboard"),
            ({"keyboard": "US", "system": "INVALID"}, "layout.system"),
            ({"keyboard": "US"}, "layout.system"),
            ({"keyboard": "US", "system": "Darwin", "extra": 1}, "layout.extra"),
        ],
    )
    def test_invalid_layout(self, layout, loc):
        assert error_locs(layout=layout) == [loc]

    def test_non_dict_layout(self):
        assert error_locs(layout="US") == ["layout"]

    @pytest.mark.parametrize(
        ("shortcuts", "loc"),
        [
            ({}, "shortcuts"),
            (["a", "b"], "shortcuts"),
            ({"General": "not a dict"}, "shortcuts.General"),
            ({"General": {}}, "shortcuts.General"),
            ({"General": {"Ctrl+C": {"other": "value"}}}, "shortcuts.General.Ctrl+C.description"),
            ({"General": {"Ctrl+C": {"description": 123}}}, "shortcuts.General.Ctrl+C.description"),
            ({"General": {"Ctrl+C": {"description": ""}}}, "shortcuts.General.Ctrl+C.description"),
        ],
    )
    def test_invalid_shortcuts(self, shortcuts, loc):
        assert loc in error_locs(shortcuts=shortcuts)

    def test_invalid_shortcut_format_names_key(self):
        with pytest.raises(ValueError, match=r"General\.Ctrl\+日"):
            validate(shortcuts={"General": {"Ctrl+日": {"description": "Test"}}})

    @pytest.mark.parametrize("key", ["~", "_", ";", "{", "}", "$", "^", "'", "Ctrl+!", "Shift+@#%&*()", "ß", "Ä", "é"])
    def test_accepts_layout_and_shifted_symbol_keys(self, key):
        assert key in validate(shortcuts={"General": {key: {"description": "Test"}}}).shortcuts["General"]

    @pytest.mark.parametrize("key", ["Ctrl+\x00", "Ctrl+🙂"])
    def test_rejects_control_and_unsupported_characters(self, key):
        with pytest.raises(ValueError, match="Invalid shortcut format"):
            validate(shortcuts={"General": {key: {"description": "Test"}}})

    def test_allowtext_mode_accepts_text(self):
        sheet = validate(
            AllowText=True,
            RenderKeys=False,
            shortcuts={"Commands": {"kubectl get pods": {"description": "List pods"}}},
        )
        assert "kubectl get pods" in sheet.shortcuts["Commands"]

    def test_model_is_frozen(self):
        sheet = validate()
        with pytest.raises(ValueError, match="frozen"):
            sheet.title = "changed"  # pyrefly: ignore[read-only]


class TestJsonSchema:
    def test_committed_schema_is_up_to_date(self):
        committed = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
        assert committed == Cheatsheet.model_json_schema(), "run `mise run schema` to regenerate"

    def test_module_writes_schema_file(self, tmp_path):
        target = tmp_path / "schema.json"
        subprocess.run([sys.executable, "-m", "koalakeys.models", str(target)], check=True)
        assert target.read_text(encoding="utf-8") == SCHEMA_FILE.read_text(encoding="utf-8")

    def test_schema_uses_yaml_aliases(self):
        props = Cheatsheet.model_json_schema()["properties"]
        assert "RenderKeys" in props
        assert "AllowText" in props
        assert "render_keys" not in props


class TestLoadCheatsheet:
    def test_returns_model(self, valid_fixtures):
        sheet = load_cheatsheet(valid_fixtures / "full_featured.yaml")
        assert sheet.title == "Full Featured Test"
        assert list(sheet.shortcuts) == ["General", "Navigation"]

    def test_file_not_found(self, fixtures_dir):
        with pytest.raises(CheatsheetError, match="file not found"):
            load_cheatsheet(fixtures_dir / "nonexistent.yaml")

    def test_empty_file(self, invalid_fixtures):
        with pytest.raises(CheatsheetError, match="file is empty"):
            load_cheatsheet(invalid_fixtures / "empty.yaml")

    def test_malformed_yaml(self, invalid_fixtures):
        with pytest.raises(CheatsheetError, match="cannot parse YAML"):
            load_cheatsheet(invalid_fixtures / "malformed.yaml")

    def test_invalid_utf8(self, tmp_path):
        sheet = tmp_path / "broken.yaml"
        sheet.write_bytes(b"title: \xff\xfe\n")
        with pytest.raises(CheatsheetError, match="cannot parse YAML"):
            load_cheatsheet(sheet)

    def test_problems_name_field_path(self, tmp_path):
        text = "title: T\nlayout: {keyboard: US, system: Darwin}\nshortcuts:\n  General:\n    Ctrl+C: {other: x}\n"
        result = problems(tmp_path, text)
        assert any(p.startswith("shortcuts.General.Ctrl+C.description:") for p in result)
        assert any(p.startswith("shortcuts.General.Ctrl+C.other:") for p in result)

    def test_model_error_has_no_location_prefix(self, tmp_path):
        text = (
            "title: T\nAllowText: true\nlayout: {keyboard: US, system: Darwin}\nshortcuts: {G: {a: {description: b}}}\n"
        )
        assert problems(tmp_path, text) == ["AllowText can only be true when RenderKeys is false"]

    @pytest.mark.parametrize("text", ["title: 2001-99-99\n", "a: " + "[" * 5000 + "\n"])
    def test_yaml_constructor_errors_become_cheatsheet_errors(self, tmp_path, text):
        assert problems(tmp_path, text)[0].startswith("cannot parse YAML")

    def test_numeric_keys_are_read_as_text(self, tmp_path):
        text = "title: T\nlayout: {keyboard: US, system: Darwin}\nshortcuts:\n  2024:\n    1: {description: One}\n"
        sheet = tmp_path / "sheet.yaml"
        sheet.write_text(text, encoding="utf-8")
        assert load_cheatsheet(sheet).shortcuts == {"2024": {"1": Shortcut(description="One")}}

    def test_boolean_key_error_tells_user_to_quote(self, tmp_path):
        text = "title: T\nlayout: {keyboard: US, system: Darwin}\nshortcuts:\n  G:\n    true: {description: One}\n"
        assert problems(tmp_path, text) == ["shortcuts.G.1.[key]: Input should be a valid string (quote the key)"]

    def test_non_mapping_top_level(self, tmp_path):
        assert problems(tmp_path, "- title\n- shortcuts\n")


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

    def test_non_mapping_top_level(self, tmp_path):
        sheet = tmp_path / "list.yaml"
        sheet.write_text("- title\n- shortcuts\n", encoding="utf-8")
        assert validate_yaml(sheet) is False

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
