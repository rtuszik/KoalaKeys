from __future__ import annotations

from dataclasses import dataclass, field
from importlib.resources import files
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

EXAMPLE_FILENAME = "example.yaml"


@dataclass
class ScaffoldResult:
    target: Path
    created: list[Path] = field(default_factory=list)
    skipped: list[Path] = field(default_factory=list)


def example_yaml_text() -> str:
    return (files("koalakeys.scaffold") / EXAMPLE_FILENAME).read_text(encoding="utf-8")


def scaffold_project(target: Path, *, force: bool = False) -> ScaffoldResult:
    result = ScaffoldResult(target=target)

    cheatsheets_dir = target / "cheatsheets"
    cheatsheets_dir.mkdir(parents=True, exist_ok=True)

    example_path = cheatsheets_dir / EXAMPLE_FILENAME
    if example_path.exists() and not force:
        result.skipped.append(example_path)
    else:
        example_path.write_text(example_yaml_text(), encoding="utf-8")
        result.created.append(example_path)

    return result
