from __future__ import annotations

import sys
import argparse
import traceback

from .config import find_repository_root
from .models import WikiMediaError
from .publisher import cleanup, publish, validate
from .reporting import render, write_json


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wiki-media", description="Publish TokenBel Wiki inbox images to immutable R2 URLs."
    )
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("publish", "validate"):
        command = commands.add_parser(name)
        command.add_argument("path", nargs="?")
        command.add_argument("--remote", action="store_true", help="check remote objects/CDN without Markdown changes")
        command.add_argument("--verbose", action="store_true")
        command.add_argument("--json-report")
        if name == "publish":
            command.add_argument("--dry-run", action="store_true")
    command = commands.add_parser("cleanup")
    command.add_argument("--dry-run", action="store_true")
    command.add_argument("--verbose", action="store_true")
    command.add_argument("--json-report")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        root = find_repository_root()
        if args.command == "publish":
            report = publish(root, args.path, args.dry_run, args.remote)
            status = 3 if report.get("validation_errors") else 0
        elif args.command == "validate":
            report = validate(root, args.path, args.remote)
            status = 3 if report.get("validation_errors") else 0
        else:
            report = cleanup(root, args.dry_run)
            status = 0
        write_json(getattr(args, "json_report", None), report)
        print(render(report))
        return status
    except WikiMediaError as error:
        print(f"Error: {error}", file=sys.stderr)
        if getattr(args, "verbose", False):
            traceback.print_exc()
        return error.exit_code
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        if getattr(args, "verbose", False):
            traceback.print_exc()
        return 6


if __name__ == "__main__":
    raise SystemExit(main())
