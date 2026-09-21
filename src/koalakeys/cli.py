from __future__ import annotations

import argparse
import sys
from pathlib import Path

from koalakeys.generate_cheatsheet import generate_all
from koalakeys.scaffold import scaffold_project
from koalakeys.validate_yaml import lint_yaml, validate_yaml

DEFAULT_PROJECT_DIRNAME = "koalakeys"


def cmd_init(args: argparse.Namespace) -> int:
    in_place = args.path == "."
    target = Path(args.path) if args.path else Path.cwd() / DEFAULT_PROJECT_DIRNAME
    result = scaffold_project(target, force=args.force)

    for path in result.created:
        print(f"created  {path}")
    for path in result.skipped:
        print(f"skipped  {path} (already exists; use --force to overwrite)")

    print("\nNext steps:")
    if in_place:
        print("  koalakeys generate")
    else:
        print(f"  cd {args.path or DEFAULT_PROJECT_DIRNAME} && koalakeys generate")
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    return generate_all()


def cmd_validate(args: argparse.Namespace) -> int:
    paths = [Path(args.path)] if args.path else sorted((Path.cwd() / "cheatsheets").glob("*.yaml"))

    if not paths:
        print("No YAML files found in the cheatsheets directory. Run `koalakeys init` to create one.")
        return 1

    all_valid = True
    for path in paths:
        print(f"Validating {path}...")
        if not validate_yaml(path):
            all_valid = False
        for warning in lint_yaml(path):
            print(f"  warning: {warning}")

    return 0 if all_valid else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="koalakeys",
        description="Generate interactive HTML keyboard-shortcut cheatsheets from YAML.",
    )
    sub = parser.add_subparsers(dest="command", metavar="{init,generate,validate}")

    p_init = sub.add_parser("init", help="Scaffold a new KoalaKeys project directory")
    p_init.add_argument(
        "path",
        nargs="?",
        default=None,
        help="Target directory (default: ./koalakeys; use '.' for the current directory)",
    )
    p_init.add_argument("--force", action="store_true", help="Overwrite existing files")
    p_init.set_defaults(func=cmd_init)

    p_generate = sub.add_parser("generate", help="Generate cheatsheets from the cheatsheets/ directory")
    p_generate.set_defaults(func=cmd_generate)

    p_validate = sub.add_parser("validate", help="Validate cheatsheet YAML files")
    p_validate.add_argument(
        "path",
        nargs="?",
        default=None,
        help="A single YAML file to validate (default: all of cheatsheets/)",
    )
    p_validate.set_defaults(func=cmd_validate)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not getattr(args, "command", None):
        parser.print_help(sys.stderr)
        return 2

    return args.func(args)


def run() -> None:
    sys.exit(main())
