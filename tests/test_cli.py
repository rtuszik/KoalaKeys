from koalakeys.cli import main

VALID_SHEET = 'title: Good\nshortcuts:\n  General:\n    "CMD+C":\n      description: "Copy"\n'
INVALID_SHEET = "title: Bad\n"  # missing required 'shortcuts'


class TestBareInvocation:
    def test_no_subcommand_prints_help_and_returns_nonzero(self, capsys):
        code = main([])

        assert code != 0
        out = capsys.readouterr()
        assert "init" in (out.out + out.err)


class TestInitCommand:
    def test_init_with_path_scaffolds_and_returns_zero(self, tmp_path):
        target = tmp_path / "proj"

        code = main(["init", str(target)])

        assert code == 0
        assert (target / "cheatsheets" / "example.yaml").exists()

    def test_init_without_path_defaults_to_koalakeys_dir_in_cwd(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        code = main(["init"])

        assert code == 0
        assert (tmp_path / "koalakeys" / "cheatsheets" / "example.yaml").exists()

    def test_init_prints_next_steps_with_cd(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)

        main(["init"])

        out = capsys.readouterr().out
        assert "cd koalakeys" in out
        assert "koalakeys generate" in out

    def test_init_dot_omits_cd_from_next_steps(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)

        main(["init", "."])

        out = capsys.readouterr().out
        assert "cd " not in out
        assert "koalakeys generate" in out

    def test_init_reports_skipped_file(self, tmp_path, capsys):
        target = tmp_path / "proj"
        main(["init", str(target)])
        capsys.readouterr()  # discard first run's output

        main(["init", str(target)])

        assert "skip" in capsys.readouterr().out.lower()

    def test_init_dot_scaffolds_into_current_directory(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        code = main(["init", "."])

        assert code == 0
        assert (tmp_path / "cheatsheets" / "example.yaml").exists()
        assert not (tmp_path / "koalakeys").exists()


class TestValidateCommand:
    def _make_cheatsheets(self, tmp_path, **sheets):
        d = tmp_path / "cheatsheets"
        d.mkdir()
        for name, content in sheets.items():
            (d / f"{name}.yaml").write_text(content, encoding="utf-8")
        return d

    def test_validate_all_returns_zero_when_every_sheet_valid(self, tmp_path, monkeypatch):
        self._make_cheatsheets(tmp_path, good=VALID_SHEET)
        monkeypatch.chdir(tmp_path)

        assert main(["validate"]) == 0

    def test_validate_all_returns_nonzero_when_a_sheet_is_invalid(self, tmp_path, monkeypatch):
        self._make_cheatsheets(tmp_path, good=VALID_SHEET, bad=INVALID_SHEET)
        monkeypatch.chdir(tmp_path)

        assert main(["validate"]) != 0

    def test_validate_no_files_returns_nonzero_and_suggests_init(self, tmp_path, monkeypatch, capsys):
        (tmp_path / "cheatsheets").mkdir()
        monkeypatch.chdir(tmp_path)

        code = main(["validate"])

        assert code != 0
        assert "init" in capsys.readouterr().out

    def test_validate_single_file(self, tmp_path):
        bad = tmp_path / "bad.yaml"
        bad.write_text(INVALID_SHEET, encoding="utf-8")

        assert main(["validate", str(bad)]) != 0


class TestGenerateCommand:
    def test_generate_dispatches_to_generation(self, valid_fixtures, tmp_path, monkeypatch):
        import koalakeys.generate_cheatsheet as gc

        out = tmp_path / "output"
        monkeypatch.setattr(gc, "CHEATSHEETS_DIR", valid_fixtures)
        monkeypatch.setattr(gc, "OUTPUT_DIR", out)

        code = main(["generate"])

        assert code == 0
        assert (out / "index.html").exists()

    def test_generate_empty_dir_mentions_init(self, tmp_path, monkeypatch, capsys):
        import koalakeys.generate_cheatsheet as gc

        empty = tmp_path / "cheatsheets"
        empty.mkdir()
        monkeypatch.setattr(gc, "CHEATSHEETS_DIR", empty)

        code = main(["generate"])

        assert code != 0
        assert "init" in capsys.readouterr().out
