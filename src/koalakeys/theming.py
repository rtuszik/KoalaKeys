from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from ruamel.yaml import YAML

from koalakeys.logger import get_logger

logger = get_logger()

yaml_safe = YAML(typ="safe")

PACKAGE_DIR = Path(__file__).parent
BUILTIN_THEMES_DIR = PACKAGE_DIR / "themes"

DEFAULT_THEME = "catppuccin"
MODES = ("light", "dark")
RESERVED_KEYS = {"extends", "modes", "default_mode", "font_url", "custom_css", *MODES}

COLOR_TOKENS = (
    "bg",
    "surface",
    "card",
    "card-hover",
    "key-bg",
    "keyboard-bg",
    "border",
    "border-input",
    "text",
    "text-muted",
    "accent",
    "accent-2",
    "key-text",
    "step-1",
    "step-2",
    "step-3",
    "step-4",
    "step-5",
    "step-overflow",
    "step-text",
    "shadow",
    "shadow-strong",
)
SHARED_TOKENS = (
    "font",
    "font-size",
    "line-height",
    "radius",
    "gap",
    "section-gap",
    "key-size",
    "max-width",
)

_COLOR_RE = re.compile(
    r"^(#[0-9a-fA-F]{3,8}"
    r"|rgba?\([0-9.,%\s/]+\)"
    r"|hsla?\([0-9.,%\s/]+\)"
    r"|[a-zA-Z]+)$"
)
_LENGTH_RE = re.compile(r"^(0|-?[0-9.]+(px|rem|em|%|vh|vw|vmin|vmax|ch|pt)|calc\([0-9.+\-*/%\sa-z()]+\))$")
_NUMBER_RE = re.compile(r"^[0-9.]+(px|rem|em|%)?$")
_FONT_RE = re.compile(r"^[a-zA-Z0-9\s,'\"\-]+$")
_FONT_URL_RE = re.compile(r"^https://[^\s\"'<>]+$")

_LENGTH_TOKEN_NAMES = {"radius", "gap", "section-gap", "key-size", "max-width", "font-size"}


class ThemeError(ValueError):
    """Raised when a theme cannot be loaded, resolved, or validated."""


@dataclass
class ResolvedTheme:
    """A theme reduced to concrete token values ready for CSS emission."""

    name: str
    shared: dict[str, str]
    light: dict[str, str] | None
    dark: dict[str, str] | None
    default_mode: str
    font_url: str | None = None
    custom_css: str = ""
    warnings: list[str] = field(default_factory=list)

    @property
    def both_modes(self) -> bool:
        return self.light is not None and self.dark is not None

    @property
    def default_is_dark(self) -> bool:
        return self.both_modes and self.default_mode == "dark"

    def render_token_css(self) -> str:
        primary = self.light if self.light is not None else self.dark
        root_tokens = {**self.shared, **(primary or {})}
        lines = [":root {"]
        lines += [f"\t--kk-{k}: {v};" for k, v in root_tokens.items()]
        lines.append("}")
        if self.both_modes:
            lines.append("body.dark-mode {")
            lines += [f"\t--kk-{k}: {v};" for k, v in (self.dark or {}).items()]
            lines.append("}")
        return "\n".join(lines)


def _validate_token_value(name: str, value: object) -> str:
    if not isinstance(value, (str, int, float)):
        raise ThemeError(f"Token '{name}' must be a scalar, got {type(value).__name__}")
    text = str(value).strip()
    if name == "font":
        ok = bool(_FONT_RE.match(text))
    elif name == "line-height":
        ok = bool(_NUMBER_RE.match(text))
    elif name in _LENGTH_TOKEN_NAMES:
        ok = bool(_LENGTH_RE.match(text))
    else:  # color token
        ok = bool(_COLOR_RE.match(text))
    if not ok:
        raise ThemeError(f"Invalid value for token '{name}': {text!r}")
    return text


def sanitize_css(css: str) -> str:
    if not css:
        return ""
    return re.sub(r"</\s*(style|script)", r"<\\/\1", css, flags=re.IGNORECASE)


def _validate_font_url(url: object) -> str | None:
    if url is None:
        return None
    text = str(url).strip()
    if not _FONT_URL_RE.match(text):
        raise ThemeError(f"font_url must be an https stylesheet URL, got {text!r}")
    return text


def _split_theme_doc(data: dict) -> tuple[dict[str, str], dict[str, dict[str, str]]]:
    shared: dict[str, str] = {}
    modes: dict[str, dict[str, str]] = {}
    for key, value in data.items():
        if key in RESERVED_KEYS:
            if key in MODES and value:
                modes[key] = {k: _validate_token_value(k, v) for k, v in value.items()}
            continue
        shared[key] = _validate_token_value(key, value)
    return shared, modes


def _list_user_theme_names(themes_dir: Path) -> set[str]:
    if not themes_dir.is_dir():
        return set()
    return {p.stem for p in themes_dir.glob("*.yaml")}


def _load_raw(path: Path) -> dict:
    try:
        with path.open(encoding="utf-8") as f:
            data = yaml_safe.load(f)
    except FileNotFoundError as e:
        raise ThemeError(f"Theme file not found: {path}") from e
    except Exception as e:
        raise ThemeError(f"Error reading theme file '{path}': {e}") from e
    if not isinstance(data, dict):
        raise ThemeError(f"Theme file '{path}' must be a mapping")
    return data


def _assert_complete(name: str, modes: dict[str, dict[str, str]], shared: dict[str, str]) -> None:
    if not modes:
        raise ThemeError(f"Built-in theme '{name}' defines no modes")
    missing_shared = [t for t in SHARED_TOKENS if t not in shared]
    if missing_shared:
        raise ThemeError(f"Built-in theme '{name}' missing shared tokens: {missing_shared}")
    for mode, tokens in modes.items():
        missing = [t for t in COLOR_TOKENS if t not in tokens]
        if missing:
            raise ThemeError(f"Built-in theme '{name}' mode '{mode}' missing tokens: {missing}")


def resolve_theme(
    name: str | None,
    themes_dir: Path | None = None,
    builtins_dir: Path = BUILTIN_THEMES_DIR,
) -> ResolvedTheme:
    name = name or DEFAULT_THEME
    builtin_names = {p.stem for p in builtins_dir.glob("*.yaml")}
    user_names = _list_user_theme_names(themes_dir) if themes_dir else set()

    collisions = builtin_names & user_names
    if collisions:
        raise ThemeError(
            f"User theme name(s) collide with built-ins: {sorted(collisions)}. Rename the file(s) in {themes_dir}."
        )

    if name in user_names:
        return _resolve_user_theme(name, themes_dir, builtins_dir, builtin_names)
    if name in builtin_names:
        return _resolve_builtin(name, builtins_dir)
    available = sorted(builtin_names | user_names)
    raise ThemeError(f"Unknown theme '{name}'. Available: {available}")


def _resolve_builtin(name: str, builtins_dir: Path) -> ResolvedTheme:
    data = _load_raw(builtins_dir / f"{name}.yaml")
    if "extends" in data:
        raise ThemeError(f"Built-in theme '{name}' must not use 'extends'")
    shared, modes = _split_theme_doc(data)
    _assert_complete(name, modes, shared)
    return _finalize(name, data, shared, modes)


def _narrow_modes(
    name: str,
    merged_modes: dict[str, dict[str, str]],
    narrowed: object,
) -> dict[str, dict[str, str]]:
    """Apply a user theme's `modes:` narrowing (e.g. dark-only hides the toggle)."""
    if narrowed is not None:
        if not isinstance(narrowed, list) or not set(narrowed) <= set(MODES):
            raise ThemeError(f"User theme '{name}': 'modes' must be a subset of {list(MODES)}")
        if not narrowed:
            raise ThemeError(f"User theme '{name}': 'modes' cannot be empty")
        merged_modes = {m: tokens for m, tokens in merged_modes.items() if m in narrowed}
    if not merged_modes:
        raise ThemeError(f"User theme '{name}' resolves to no modes")
    return merged_modes


def _resolve_user_theme(
    name: str,
    themes_dir: Path,
    builtins_dir: Path,
    builtin_names: set[str],
) -> ResolvedTheme:
    data = _load_raw(themes_dir / f"{name}.yaml")
    parent = data.get("extends")
    if not parent:
        raise ThemeError(f"User theme '{name}' must declare 'extends: <built-in>'")
    if parent not in builtin_names:
        raise ThemeError(f"User theme '{name}' extends unknown built-in '{parent}'. Available: {sorted(builtin_names)}")

    base = _resolve_builtin(parent, builtins_dir)
    user_shared, user_modes = _split_theme_doc(data)

    shared = {**base.shared, **user_shared}
    merged_modes: dict[str, dict[str, str]] = {}
    for mode in MODES:
        base_tokens = getattr(base, mode)
        if base_tokens is None and mode not in user_modes:
            continue
        merged_modes[mode] = {**(base_tokens or {}), **user_modes.get(mode, {})}

    merged_modes = _narrow_modes(name, merged_modes, data.get("modes"))

    # font_url / default_mode / custom_css fall back to the parent's.
    font_url = base.font_url
    if "font_url" in data:
        font_url = _validate_font_url(data.get("font_url"))

    return _finalize(name, data, shared, merged_modes, base=base, font_url=font_url)


def _finalize(
    name: str,
    data: dict,
    shared: dict[str, str],
    modes: dict[str, dict[str, str]],
    base: ResolvedTheme | None = None,
    font_url: str | None = None,
) -> ResolvedTheme:
    default_mode = data.get("default_mode") or (base.default_mode if base else None)
    if default_mode is None:
        default_mode = "dark" if "dark" in modes else next(iter(modes))
    if default_mode not in modes:
        # Narrowed away the declared default; fall back to a present mode.
        default_mode = "dark" if "dark" in modes else next(iter(modes))

    if base is None:
        font_url = _validate_font_url(data.get("font_url"))

    custom_css = sanitize_css(str(data.get("custom_css") or ""))
    if base and base.custom_css:
        custom_css = base.custom_css + ("\n" + custom_css if custom_css else "")

    return ResolvedTheme(
        name=name,
        shared=shared,
        light=modes.get("light"),
        dark=modes.get("dark"),
        default_mode=default_mode,
        font_url=font_url,
        custom_css=custom_css,
    )
