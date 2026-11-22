from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import ValidationError
from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

from koalakeys.logger import get_logger
from koalakeys.models import Cheatsheet

if TYPE_CHECKING:
    from pathlib import Path

    from pydantic_core import ErrorDetails

logger = get_logger()

yaml_safe = YAML(typ="safe")


class CheatsheetError(ValueError):
    def __init__(self, path: Path, problems: list[str]) -> None:
        self.path = path
        self.problems = problems
        super().__init__(f"{path}: " + "; ".join(problems))


def _format_error(error: ErrorDetails) -> str:
    loc = ".".join(str(part) for part in error["loc"])
    ctx = error.get("ctx") or {}
    msg = str(ctx["error"]) if error["type"] == "value_error" and "error" in ctx else error["msg"]
    return f"{loc}: {msg}" if loc else msg


def load_cheatsheet(file_path: Path) -> Cheatsheet:
    try:
        with file_path.open(encoding="utf-8") as file:
            data = yaml_safe.load(file)
    except FileNotFoundError as e:
        raise CheatsheetError(file_path, ["file not found"]) from e
    except (OSError, UnicodeDecodeError, YAMLError) as e:
        raise CheatsheetError(file_path, [f"cannot parse YAML: {e}"]) from e

    if data is None:
        raise CheatsheetError(file_path, ["file is empty"])

    try:
        return Cheatsheet.model_validate(data)
    except ValidationError as e:
        raise CheatsheetError(file_path, [_format_error(err) for err in e.errors()]) from e


def validate_yaml(file_path: Path) -> bool:
    try:
        load_cheatsheet(file_path)
    except CheatsheetError as e:
        for problem in e.problems:
            logger.error(f"{file_path}: {problem}")
        logger.error(f"YAML validation failed: {file_path}")
        return False
    logger.info(f"YAML validation successful: {file_path}")
    return True


def lint_yaml(file_path: Path) -> list[str]:
    warnings = []

    with file_path.open(encoding="utf-8") as file:
        lines = file.readlines()

    for i, line in enumerate(lines, start=1):
        if len(line.rstrip()) > 100:
            warnings.append(f"Line {i} is longer than 100 characters")

        indent = len(line) - len(line.lstrip())
        if indent % 2 != 0:
            warnings.append(f"Line {i} has inconsistent indentation")

        if line.rstrip() != line.rstrip("\n"):
            warnings.append(f"Line {i} has trailing whitespace")

    return warnings
