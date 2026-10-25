# End-to-end integration tests for cheatsheet generation.

from koalakeys.generate_cheatsheet import generate_index, main


class TestGenerationIntegration:
    def test_minimal_generates_valid_file(self, valid_fixtures, isolated_output):
        title, filename = main(valid_fixtures / "minimal.yaml")

        assert title == "Minimal Test"
        assert filename == "minimal_test_cheatsheet.html"

        output_file = isolated_output / filename
        assert output_file.exists(), "expected the cheatsheet file to be written"

        html = output_file.read_text(encoding="utf-8")
        assert "<html" in html.lower()
        assert "</html>" in html.lower()
        assert "Minimal Test" in html  # title rendered into the page

    def test_full_featured_renders_content_and_theme(self, valid_fixtures, isolated_output):
        title, filename = main(valid_fixtures / "full_featured.yaml")

        assert title == "Full Featured Test"
        html = (isolated_output / filename).read_text(encoding="utf-8")

        # Shortcut descriptions made it through normalization + rendering.
        assert "Copy selected item" in html
        assert "Select all" in html
        # Default catppuccin theme tokens are injected.
        assert ":root {" in html
        assert "--kk-bg:" in html

    def test_only_the_expected_file_is_written(self, valid_fixtures, isolated_output):
        _, filename = main(valid_fixtures / "minimal.yaml")

        written = [p.name for p in isolated_output.iterdir()]
        assert written == [filename]

    def test_invalid_input_writes_nothing(self, invalid_fixtures, isolated_output):
        title, filename = main(invalid_fixtures / "missing_title.yaml")

        assert (title, filename) == (None, None)
        assert list(isolated_output.iterdir()) == []


class TestIndexIntegration:
    def test_index_links_generated_cheatsheets(self, valid_fixtures, isolated_output):
        results = [
            main(valid_fixtures / "minimal.yaml"),
            main(valid_fixtures / "full_featured.yaml"),
        ]
        cheatsheets = [{"title": t, "filename": f} for t, f in results]

        index_html = generate_index(cheatsheets)

        for title, filename in results:
            assert title in index_html
            assert filename in index_html
