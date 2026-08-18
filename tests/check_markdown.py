#!/usr/bin/env python3
"""Validate generated Markdown page variants for Accept: text/markdown negotiation.

Hugo output format "Markdown" renders an `index.md` sibling next to every
content `index.html` (see `hugo.yaml` outputs and `worker.js`). Paginator
pages (`/page/N/`) and `404.html` are intentionally exempt: the Worker
falls back to HTML for them.
"""

import sys
from pathlib import Path

PAGER_SEGMENT = "page"


def is_pager_path(index_html: Path, public: Path) -> bool:
    parts = index_html.parent.relative_to(public).parts
    return len(parts) >= 2 and parts[-2] == PAGER_SEGMENT


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_markdown.py <public-dir>", file=sys.stderr)
        return 2

    public = Path(sys.argv[1])
    if not public.is_dir():
        print(f"not a directory: {public}", file=sys.stderr)
        return 2

    errors: list[str] = []
    checked = 0

    root_md = public / "index.md"
    if not root_md.is_file():
        errors.append("public/index.md is missing (home Markdown variant)")
    elif "TokenBel Wiki" not in root_md.read_text(encoding="utf-8"):
        errors.append("public/index.md does not mention 'TokenBel Wiki'")

    for index_html in sorted(public.rglob("index.html")):
        if is_pager_path(index_html, public):
            continue
        sibling_md = index_html.with_name("index.md")
        if not sibling_md.is_file():
            errors.append(f"missing Markdown variant: {sibling_md.relative_to(public)}")
            continue
        text = sibling_md.read_text(encoding="utf-8").strip()
        if not text.startswith("# "):
            errors.append(
                f"Markdown variant must start with an H1: {sibling_md.relative_to(public)}"
            )
            continue
        checked += 1

    if errors:
        print("Markdown validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print(
        f"Markdown validation passed for {checked} page variants (plus pager fallbacks)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
