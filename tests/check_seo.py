#!/usr/bin/env python3
"""Validate rendered SEO metadata in Hugo output without third-party packages."""

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.meta: dict[str, str] = {}
        self.title_parts: list[str] = []
        self.json_ld: list[str] = []
        self._in_title = False
        self._in_json_ld = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "meta":
            key = attributes.get("property") or attributes.get("name")
            if key:
                self.meta[key] = attributes.get("content") or ""
        elif tag == "title":
            self._in_title = True
        elif tag == "script" and attributes.get("type") == "application/ld+json":
            self._in_json_ld = True
            self.json_ld.append("")

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        elif tag == "script":
            self._in_json_ld = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)
        if self._in_json_ld:
            self.json_ld[-1] += data

    @property
    def title(self) -> str:
        return "".join(self.title_parts).strip()


def fail(errors: list[str], page: Path, message: str) -> None:
    errors.append(f"{page}: {message}")


def parse_page(path: Path) -> PageParser:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return parser


def article_pages(content_root: Path, public_root: Path) -> set[Path]:
    pages = set()
    for source in content_root.rglob("*.md"):
        if source.name == "_index.md":
            continue
        relative = source.relative_to(content_root).with_suffix("")
        if source.name == "index.md":
            relative = relative.parent
        relative = Path(*(part.lower() for part in relative.parts))
        pages.add(public_root / relative / "index.html")
    return pages


def graph_types(graph: dict[str, object]) -> set[str]:
    return {
        item.get("@type")
        for item in graph.get("@graph", [])
        if isinstance(item, dict) and isinstance(item.get("@type"), str)
    }


def graph_item(graph: dict[str, object], item_type: str) -> dict[str, object] | None:
    return next(
        (
            item
            for item in graph.get("@graph", [])
            if isinstance(item, dict) and item.get("@type") == item_type
        ),
        None,
    )


def is_absolute_production_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme == "https" and parsed.netloc in {
        "wiki.tokenbel.info",
        "cdn-wiki.tokenbel.info",
    }


def front_matter(source: Path) -> str | None:
    match = re.match(r"^---\n(.*?)\n---", source.read_text(encoding="utf-8"), re.DOTALL)
    return match.group(1) if match else None


def front_matter_value(header: str, key: str) -> str | None:
    value = re.search(
        rf"(?m)^{re.escape(key)}:\s*(?:\"(?P<double>.*)\"|'(?P<single>.*)'|(?P<bare>[^\n#]+))\s*$",
        header,
    )
    if not value:
        return None
    return next(
        part.strip()
        for part in value.group("double", "single", "bare")
        if part is not None
    )


def main() -> int:
    public_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("public")
    content_root = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("content")
    errors: list[str] = []
    articles = article_pages(content_root, public_root)
    pages = sorted(public_root.rglob("*.html"))

    for source in content_root.rglob("*.md"):
        header = front_matter(source)
        if header is None:
            continue
        description = front_matter_value(header, "description")
        if description is None:
            fail(
                errors,
                source,
                "front matter description is missing or must be a single-line scalar",
            )
        elif not 120 <= len(description) <= 155:
            fail(
                errors,
                source,
                f"front matter description length is {len(description)}, expected 120–155",
            )
        if source != content_root / "_index.md":
            seo_title = front_matter_value(header, "seoTitle") or front_matter_value(
                header, "title"
            )
            if not seo_title or len(seo_title) > 44:
                fail(
                    errors,
                    source,
                    "SEO title must be present and no longer than 44 characters before the site suffix",
                )

    if not (public_root / "og-default.png").is_file():
        errors.append("public/og-default.png: missing social-image fallback")

    required_social = {
        "og:title",
        "og:description",
        "og:type",
        "og:url",
        "og:site_name",
        "og:locale",
        "og:image",
        "og:image:alt",
        "og:image:type",
        "og:image:width",
        "og:image:height",
        "twitter:card",
        "twitter:title",
        "twitter:description",
        "twitter:image",
        "twitter:image:alt",
    }

    for page in pages:
        parser = parse_page(page)
        is_404 = page.name == "404.html"
        if is_404:
            if parser.meta.get("robots") != "noindex, follow":
                fail(errors, page, "404 must keep noindex, follow")
            continue

        if not parser.title or len(parser.title) > 60:
            fail(errors, page, f"title length is {len(parser.title)}, expected 1–60")
        description = parser.meta.get("description", "")
        if not 120 <= len(description) <= 155:
            fail(
                errors,
                page,
                f"description length is {len(description)}, expected 120–155",
            )
        missing = sorted(key for key in required_social if not parser.meta.get(key))
        if missing:
            fail(errors, page, f"missing social metadata: {', '.join(missing)}")
            continue
        if parser.meta["og:site_name"] != "TokenBel Wiki":
            fail(errors, page, "og:site_name must be TokenBel Wiki")
        if parser.meta["og:locale"] != "ru_BY":
            fail(errors, page, "og:locale must be ru_BY")
        if parser.meta["twitter:card"] != "summary_large_image":
            fail(errors, page, "twitter:card must be summary_large_image")
        expected_image_metadata = {
            "og:image:type": "image/png",
            "og:image:width": "1200",
            "og:image:height": "630",
        }
        for key, expected in expected_image_metadata.items():
            if parser.meta[key] != expected:
                fail(errors, page, f"{key} must be {expected}")
        if not is_absolute_production_url(parser.meta["og:url"]):
            fail(errors, page, "og:url must be an absolute production URL")
        for key in ("og:image", "twitter:image"):
            if not is_absolute_production_url(parser.meta[key]):
                fail(errors, page, f"{key} must be an absolute approved URL")
        if parser.meta["og:image"] != parser.meta["twitter:image"]:
            fail(errors, page, "Open Graph and Twitter image must match")

        expected_type = "article" if page in articles else "website"
        if parser.meta["og:type"] != expected_type:
            fail(
                errors,
                page,
                f"og:type is {parser.meta['og:type']}, expected {expected_type}",
            )

        if len(parser.json_ld) != 1:
            fail(errors, page, "expected exactly one JSON-LD graph")
            continue
        try:
            graph = json.loads(parser.json_ld[0])
        except json.JSONDecodeError as exc:
            fail(errors, page, f"invalid JSON-LD: {exc.msg}")
            continue
        if graph.get("@context") != "https://schema.org":
            fail(errors, page, "JSON-LD context must be schema.org")
        types = graph_types(graph)
        organization = graph_item(graph, "Organization")
        expected_organization_id = "https://tokenbel.info/#organization"
        expected_same_as = [
            "https://t.me/tokenbel",
            "https://github.com/Red-Panda-Dev",
        ]
        if not organization or organization.get("@id") != expected_organization_id:
            fail(errors, page, "Organization must use the shared TokenBel @id")
        elif organization.get("url") != "https://tokenbel.info/":
            fail(errors, page, "Organization URL must point to the main TokenBel site")
        elif organization.get("sameAs") != expected_same_as:
            fail(errors, page, "Organization sameAs must list official TokenBel pages")

        if page == public_root / "index.html":
            website = graph_item(graph, "WebSite")
            if not website:
                fail(errors, page, "home graph must contain WebSite")
            elif website.get("@id") != "https://wiki.tokenbel.info/#website":
                fail(errors, page, "WebSite must use the wiki-specific @id")
            elif website.get("inLanguage") != "ru-BY":
                fail(errors, page, "WebSite inLanguage must be ru-BY")
            elif website.get("publisher") != {"@id": expected_organization_id}:
                fail(
                    errors,
                    page,
                    "WebSite publisher must reference the shared Organization",
                )
            continue

        expected_types = {"WebPage", "BreadcrumbList", "Organization"}
        if page in articles:
            expected_types.add("Article")
        if not expected_types.issubset(types):
            fail(
                errors, page, f"JSON-LD missing types: {sorted(expected_types - types)}"
            )
            continue
        breadcrumb = graph_item(graph, "BreadcrumbList")
        webpage = graph_item(graph, "WebPage")
        if not breadcrumb or not breadcrumb.get("itemListElement"):
            fail(errors, page, "JSON-LD breadcrumb must contain items")
        if not webpage or webpage.get("publisher") != {"@id": expected_organization_id}:
            fail(
                errors, page, "WebPage publisher must reference the shared Organization"
            )
        if page in articles:
            article = graph_item(graph, "Article")
            required_article = {
                "headline",
                "description",
                "datePublished",
                "dateModified",
                "author",
                "publisher",
                "mainEntityOfPage",
                "image",
                "inLanguage",
            }
            if not article or not required_article.issubset(article):
                fail(errors, page, "Article is missing required fields")
            elif webpage.get("mainEntity") != {"@id": article.get("@id")}:
                fail(errors, page, "WebPage.mainEntity must reference Article")
            elif article.get("author") != {"@id": expected_organization_id}:
                fail(
                    errors,
                    page,
                    "Article author must reference the shared Organization",
                )
            elif article.get("publisher") != {"@id": expected_organization_id}:
                fail(
                    errors,
                    page,
                    "Article publisher must reference the shared Organization",
                )

    nested_article = public_root / "guides/kak-eto-rabotaet/stranica-akcii/index.html"
    if nested_article.is_file():
        parser = parse_page(nested_article)
        graph = json.loads(parser.json_ld[0])
        breadcrumb = graph_item(graph, "BreadcrumbList") or {}
        items = breadcrumb.get("itemListElement", [])
        expected = [
            "https://wiki.tokenbel.info/",
            "https://wiki.tokenbel.info/guides/",
            "https://wiki.tokenbel.info/guides/kak-eto-rabotaet/",
            "https://wiki.tokenbel.info/guides/kak-eto-rabotaet/stranica-akcii/",
        ]
        actual = [item.get("item") for item in items if isinstance(item, dict)]
        if actual != expected:
            fail(
                errors,
                nested_article,
                f"breadcrumb path is {actual}, expected {expected}",
            )

    if errors:
        print("SEO validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print(f"SEO validation passed for {len(pages)} rendered HTML pages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
