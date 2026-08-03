#!/usr/bin/env python3
"""Validate Hugo list pagination in rendered output."""

import math
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


class ListPageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.article_count = 0
        self.pagination = False
        self.pagination_links: set[str] = set()
        self._in_pagination = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "article":
            self.article_count += 1
        if tag == "nav" and attributes.get("aria-label") == "Постраничная навигация":
            self.pagination = True
            self._in_pagination = True
        if tag == "a" and self._in_pagination:
            href = attributes.get("href")
            if href:
                self.pagination_links.add(href)

    def handle_endtag(self, tag: str) -> None:
        if tag == "nav" and self._in_pagination:
            self._in_pagination = False


def parse_page(path: Path) -> ListPageParser:
    parser = ListPageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return parser


def pager_size(config_path: Path) -> int:
    config = config_path.read_text(encoding="utf-8")
    match = re.search(r"(?m)^\s*pagerSize:\s*(\d+)\s*$", config)
    if match is None:
        raise ValueError("hugo.yaml must configure pagination.pagerSize")
    return int(match.group(1))


def list_directories(content_root: Path) -> list[Path]:
    return sorted(path.parent for path in content_root.rglob("_index.md"))


def direct_articles(directory: Path) -> list[Path]:
    return sorted(
        child
        for child in directory.iterdir()
        if child.is_dir() and (child / "index.md").is_file()
    )


def output_path(
    public_root: Path, content_root: Path, directory: Path, page: int
) -> Path:
    relative = directory.relative_to(content_root)
    base = public_root / relative
    if page == 1:
        return base / "index.html"
    return base / "page" / str(page) / "index.html"


def fail(errors: list[str], path: Path, message: str) -> None:
    errors.append(f"{path}: {message}")


def main() -> int:
    public_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("public")
    content_root = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("content")
    config_path = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("hugo.yaml")
    size = pager_size(config_path)
    errors: list[str] = []

    for directory in list_directories(content_root):
        articles = direct_articles(directory)
        if not articles:
            continue

        expected_pages = math.ceil(len(articles) / size)
        first_page_alias = (
            output_path(public_root, content_root, directory, 1).parent
            / "page"
            / "1"
            / "index.html"
        )
        if first_page_alias.is_file():
            fail(errors, first_page_alias, "must not generate a first-page alias")
        for page_number in range(1, expected_pages + 1):
            path = output_path(public_root, content_root, directory, page_number)
            if not path.is_file():
                fail(errors, path, "missing generated pager output")
                continue

            parser = parse_page(path)
            expected_articles = min(size, len(articles) - (page_number - 1) * size)
            if parser.article_count != expected_articles:
                fail(
                    errors,
                    path,
                    f"contains {parser.article_count} article cards, expected {expected_articles}",
                )
            if expected_pages > 1:
                if not parser.pagination:
                    fail(errors, path, "missing pagination navigation")
                relative = directory.relative_to(content_root).as_posix()
                base_url = "/" if relative == "." else f"/{relative}/"
                expected_href = f"{base_url}page/2/"
                if page_number == 1 and expected_href not in parser.pagination_links:
                    fail(errors, path, f"missing path-based link {expected_href}")
            elif parser.pagination:
                fail(errors, path, "must not render pagination navigation")

    if errors:
        print("Pagination validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("Pagination validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
