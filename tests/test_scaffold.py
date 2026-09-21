from ruamel.yaml import YAML

from koalakeys.scaffold import example_yaml_text, scaffold_project
from koalakeys.validate_yaml import validate_yaml


class TestScaffoldProject:
    def test_creates_example_cheatsheet_that_validates(self, tmp_path):
        result = scaffold_project(tmp_path / "proj")

        example = tmp_path / "proj" / "cheatsheets" / "example.yaml"
        assert example.exists()
        assert example in result.created
        assert validate_yaml(example)

    def test_skips_existing_example_without_force(self, tmp_path):
        example = tmp_path / "cheatsheets" / "example.yaml"
        example.parent.mkdir(parents=True)
        example.write_text("title: Mine\nshortcuts: {}\n", encoding="utf-8")

        result = scaffold_project(tmp_path)

        assert example in result.skipped
        assert example not in result.created
        assert example.read_text(encoding="utf-8") == "title: Mine\nshortcuts: {}\n"

    def test_force_overwrites_existing_example(self, tmp_path):
        example = tmp_path / "cheatsheets" / "example.yaml"
        example.parent.mkdir(parents=True)
        example.write_text("title: Mine\nshortcuts: {}\n", encoding="utf-8")

        result = scaffold_project(tmp_path, force=True)

        assert example in result.created
        assert example not in result.skipped
        assert "Mine" not in example.read_text(encoding="utf-8")


class TestExampleYamlText:
    def test_returns_parseable_non_empty_content(self):
        text = example_yaml_text()

        assert text.strip()
        data = YAML(typ="safe").load(text)
        assert "title" in data
        assert "shortcuts" in data
