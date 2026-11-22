from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator
from pydantic.json_schema import GenerateJsonSchema

from koalakeys.theming import DEFAULT_THEME

if TYPE_CHECKING:
    from pydantic.config import JsonDict

# Printable ASCII plus the glyphs used by the bundled layouts and system mappings.
KEY_PATTERN = r"^[\x20-\x7E\s⌘⌥⌃⇧←→↑↓¡²´ºÄÖÜÑäöüñßàçèéù]+$"
_KEY_RE = re.compile(KEY_PATTERN)

Keyboard = Literal["US", "UK", "DE", "FR", "ES", "DVORAK"]
System = Literal["Darwin", "Windows", "Linux"]
NonEmptyStr = Annotated[str, StringConstraints(min_length=1, pattern=r"\S")]
# YAML reads unquoted `1:` as a number.
Key = Annotated[str, Field(strict=False, coerce_numbers_to_str=True)]


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class Shortcut(_Model):
    description: NonEmptyStr = Field(description="Human-readable description of the shortcut.")


class Layout(_Model):
    keyboard: Keyboard = Field(description="Keyboard layout.")
    system: System = Field(description="Operating system.")


Category = Annotated[dict[Key, Shortcut], Field(min_length=1)]

_ALLOW_TEXT_SET: JsonDict = {"properties": {"AllowText": {"const": True}}, "required": ["AllowText"]}

_EXAMPLE: JsonDict = {
    "title": "KoalaKeys",
    "RenderKeys": True,
    "AllowText": False,
    "layout": {"keyboard": "US", "system": "Darwin"},
    "shortcuts": {
        "General": {
            "CMD+C": {"description": "Copy selected item"},
            "CMD+Right": {"description": "Move cursor to end of line"},
        },
        "Sequential Shortcuts": {
            "Super+T>W>S": {"description": "Multi-sequence shortcut example"},
            "CTRL+K>CTRL+C": {"description": "Add line comment"},
        },
    },
}


class Cheatsheet(_Model):
    """Schema for KoalaKeys YAML cheatsheets."""

    model_config = ConfigDict(
        title="KoalaKeys Cheatsheet",
        json_schema_extra={
            "$schema": GenerateJsonSchema.schema_dialect,
            "$id": "https://rtuszik.github.io/KoalaKeys/schema/cheatsheet.schema.json",
            "allOf": [
                {
                    "description": "AllowText=true requires RenderKeys=false.",
                    "if": _ALLOW_TEXT_SET,
                    "then": {"properties": {"RenderKeys": {"const": False}}, "required": ["RenderKeys"]},
                },
                {
                    "description": "When AllowText is not true, restrict shortcut key syntax. Supports '+' for "
                    "simultaneous keys and '>' for sequential shortcuts (chords).",
                    "if": {"not": _ALLOW_TEXT_SET},
                    "then": {
                        "properties": {
                            "shortcuts": {"additionalProperties": {"propertyNames": {"pattern": KEY_PATTERN}}}
                        }
                    },
                },
            ],
            "examples": [_EXAMPLE],
        },
    )

    title: NonEmptyStr = Field(description="Title of the cheatsheet.")
    render_keys: bool = Field(
        default=True,
        alias="RenderKeys",
        description="When true (default), render keyboard layout with highlighted keys.",
    )
    allow_text: bool = Field(
        default=False,
        alias="AllowText",
        description="When true, free-form shortcut text is allowed; requires RenderKeys=false.",
    )
    theme: NonEmptyStr = Field(
        default=DEFAULT_THEME,
        description="Theme name: a built-in (e.g. 'catppuccin') or a user theme in the project's themes/ directory.",
    )
    custom_css: str = Field(
        default="",
        description="Filename of a custom CSS file (resolved from the project's styles/ directory), "
        "layered after the theme.",
    )
    custom_css_inline: str = Field(
        default="",
        description="Inline custom CSS, emitted last in the cascade so it overrides the theme and the custom CSS file.",
    )
    layout: Layout
    shortcuts: dict[Key, Category] = Field(
        min_length=1,
        description="Categories mapped to shortcut definitions. Shortcuts use '+' for simultaneous keys "
        "(e.g., 'CMD+C') and '>' for sequential keys/chords (e.g., 'Super+T>W>S').",
    )

    @model_validator(mode="after")
    def _check_text_mode(self) -> Cheatsheet:
        if self.allow_text and self.render_keys:
            raise ValueError("AllowText can only be true when RenderKeys is false")
        if not self.allow_text:
            bad = [f"{cat}.{key}" for cat, items in self.shortcuts.items() for key in items if not _KEY_RE.match(key)]
            if bad:
                raise ValueError(f"Invalid shortcut format (set AllowText for free text): {', '.join(bad)}")
        return self


if __name__ == "__main__":
    schema = json.dumps(Cheatsheet.model_json_schema(), indent=4, ensure_ascii=False)
    Path(sys.argv[1]).write_text(schema + "\n", encoding="utf-8")
