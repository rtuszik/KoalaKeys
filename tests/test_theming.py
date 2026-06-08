import pytest

from koalakeys.theming import (
    BUILTIN_THEMES_DIR,
    COLOR_TOKENS,
    DEFAULT_THEME,
    SHARED_TOKENS,
    ResolvedTheme,
    ThemeError,
    resolve_theme,
    sanitize_css,
)


def write_theme(themes_dir, name, body):
    themes_dir.mkdir(parents=True, exist_ok=True)
    (themes_dir / f"{name}.yaml").write_text(body, encoding="utf-8")


class TestBuiltinCompleteness:
    """CI guard: every shipped built-in must resolve and be complete."""

    def test_all_builtins_resolve_and_complete(self):
        builtins = list(BUILTIN_THEMES_DIR.glob("*.yaml"))
        assert builtins, "expected at least one built-in theme"
        for path in builtins:
            theme = resolve_theme(path.stem)
            for mode_name in ("light", "dark"):
                mode = getattr(theme, mode_name)
                if mode is None:
                    continue
                missing = [t for t in COLOR_TOKENS if t not in mode]
                assert not missing, f"{path.stem}/{mode_name} missing {missing}"
            missing_shared = [t for t in SHARED_TOKENS if t not in theme.shared]
            assert not missing_shared, f"{path.stem} missing shared {missing_shared}"

    def test_default_theme_exists(self):
        assert (BUILTIN_THEMES_DIR / f"{DEFAULT_THEME}.yaml").is_file()


class TestResolveBuiltin:
    def test_catppuccin_both_modes(self):
        theme = resolve_theme("catppuccin")
        assert theme.both_modes is True
        assert theme.default_is_dark is True
        assert theme.font_url and theme.font_url.startswith("https://")

    def test_default_when_none(self):
        assert resolve_theme(None).name == DEFAULT_THEME

    def test_exact_token_values_preserved(self):
        theme = resolve_theme("catppuccin")
        assert theme.light["bg"] == "#eff1f5"
        assert theme.dark["bg"] == "#1e1e2e"
        assert theme.dark["card"] == "#45475a"
        assert theme.dark["key-bg"] == "#313244"
        assert theme.dark["key-text"] == "#f38ba8"
        assert theme.shared["radius"] == "6px"

    def test_render_token_css_structure(self):
        css = resolve_theme("catppuccin").render_token_css()
        assert ":root {" in css
        assert "body.dark-mode {" in css
        assert "--kk-bg: #eff1f5;" in css  # light in :root
        assert "--kk-bg: #1e1e2e;" in css  # dark in toggle block
        assert "--kk-font:" in css

    def test_unknown_theme_raises(self):
        with pytest.raises(ThemeError, match="Unknown theme"):
            resolve_theme("nope")


class TestUserTheme:
    def test_inherits_and_overrides(self, tmp_path):
        write_theme(tmp_path, "mine", "extends: catppuccin\ndark:\n  accent: '#82aaff'\n")
        theme = resolve_theme("mine", themes_dir=tmp_path)
        assert theme.dark["accent"] == "#82aaff"  # overridden
        assert theme.dark["bg"] == "#1e1e2e"  # inherited
        assert theme.light is not None  # both modes inherited
        assert theme.both_modes is True

    def test_mode_narrowing_hides_toggle(self, tmp_path):
        write_theme(tmp_path, "darkonly", "extends: catppuccin\nmodes: [dark]\ndark:\n  accent: '#82aaff'\n")
        theme = resolve_theme("darkonly", themes_dir=tmp_path)
        assert theme.both_modes is False
        assert theme.light is None
        assert theme.dark is not None
        css = theme.render_token_css()
        assert "body.dark-mode {" not in css  # dark folded into :root
        assert "--kk-accent: #82aaff;" in css

    def test_shared_override(self, tmp_path):
        write_theme(tmp_path, "round", "extends: catppuccin\nradius: '12px'\n")
        theme = resolve_theme("round", themes_dir=tmp_path)
        assert theme.shared["radius"] == "12px"
        assert theme.shared["gap"] == "12px"  # inherited

    def test_missing_extends_raises(self, tmp_path):
        write_theme(tmp_path, "bad", "dark:\n  accent: '#fff'\n")
        with pytest.raises(ThemeError, match="must declare"):
            resolve_theme("bad", themes_dir=tmp_path)

    def test_unknown_parent_raises(self, tmp_path):
        write_theme(tmp_path, "bad", "extends: nope\n")
        with pytest.raises(ThemeError, match="unknown built-in"):
            resolve_theme("bad", themes_dir=tmp_path)

    def test_collision_with_builtin_raises(self, tmp_path):
        write_theme(tmp_path, "catppuccin", "extends: catppuccin\n")
        with pytest.raises(ThemeError, match="collide"):
            resolve_theme("catppuccin", themes_dir=tmp_path)

    def test_empty_modes_narrowing_raises(self, tmp_path):
        write_theme(tmp_path, "bad", "extends: catppuccin\nmodes: []\n")
        with pytest.raises(ThemeError, match="cannot be empty"):
            resolve_theme("bad", themes_dir=tmp_path)


class TestValueValidation:
    @pytest.mark.parametrize(
        "value",
        ["red; } body { display: none", "blue<script>", "10px; color: red", "}"],
    )
    def test_injection_values_rejected(self, tmp_path, value):
        write_theme(tmp_path, "evil", f"extends: catppuccin\ndark:\n  accent: '{value}'\n")
        with pytest.raises(ThemeError, match="Invalid value"):
            resolve_theme("evil", themes_dir=tmp_path)

    @pytest.mark.parametrize("value", ["#abc", "#aabbcc", "rgba(0, 0, 0, 0.3)", "hsl(200, 50%, 50%)", "tomato"])
    def test_valid_color_values_accepted(self, tmp_path, value):
        write_theme(tmp_path, "ok", f"extends: catppuccin\ndark:\n  accent: '{value}'\n")
        assert resolve_theme("ok", themes_dir=tmp_path).dark["accent"] == value

    def test_bad_font_url_rejected(self, tmp_path):
        write_theme(tmp_path, "bad", "extends: catppuccin\nfont_url: 'http://insecure.example/f.css'\n")
        with pytest.raises(ThemeError, match="font_url"):
            resolve_theme("bad", themes_dir=tmp_path)

    def test_length_token_validation(self, tmp_path):
        write_theme(tmp_path, "bad", "extends: catppuccin\nradius: 'evil}'\n")
        with pytest.raises(ThemeError, match="Invalid value"):
            resolve_theme("bad", themes_dir=tmp_path)


class TestSanitizeCss:
    def test_neutralizes_style_breakout(self):
        out = sanitize_css("a{} </style><b>")
        assert "</style>" not in out
        assert "<\\/style>" in out

    def test_neutralizes_script_breakout(self):
        out = sanitize_css("x </SCRIPT> y")
        assert "</SCRIPT>" not in out

    def test_empty(self):
        assert sanitize_css("") == ""


class TestThemeCustomCss:
    def test_theme_custom_css_sanitized(self, tmp_path):
        write_theme(tmp_path, "withcss", "extends: catppuccin\ncustom_css: |\n  .key { border: 2px; } </style>\n")
        theme = resolve_theme("withcss", themes_dir=tmp_path)
        assert ".key { border: 2px; }" in theme.custom_css
        assert "</style>" not in theme.custom_css


class TestResolvedThemeDataclass:
    def test_single_light_mode_default_not_dark(self, tmp_path):
        write_theme(tmp_path, "lightonly", "extends: catppuccin\nmodes: [light]\n")
        theme = resolve_theme("lightonly", themes_dir=tmp_path)
        assert isinstance(theme, ResolvedTheme)
        assert theme.both_modes is False
        assert theme.default_is_dark is False
