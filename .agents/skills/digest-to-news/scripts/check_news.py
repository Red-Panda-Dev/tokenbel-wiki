#!/usr/bin/env python3
"""Validate a TokenBel news article in content/news/<slug>/index.md.

Mechanical checks only: front matter, file location, structure, length,
banned phrases, jargon outside «Технически», brand spelling, repeated sentence
openers, internal links, images and leftovers that would leak into the
Hugo-generated index.md. Word lists come from ../references/glossary.md.

Usage: check_news.py FILE [FILE ...] [--strict] [--repo PATH]
Exit code 1 on errors (or on warnings with --strict).
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
GLOSSARY = SKILL_DIR / "references" / "glossary.md"
DEFAULT_REPO = SKILL_DIR.parents[2]
REQUIRED_KEYS = ("title", "seoTitle", "description", "date", "lastmod", "draft", "tags")
ALLOWED_H2 = {"Введение", "Главное", "Вехи", "Что стало удобнее", "Исправили", "Технически", "Что дальше"}
ALLOWED_H3 = {"Для инвесторов", "Для компаний и эмитентов", "Для данных и страниц", "Для AI-агентов и разработчиков"}
PARAGRAPH_SECTIONS = {"Введение", "Главное", "Вехи"}
MAX_BULLETS = {"Исправили": 4, "Технически": 3, "Что дальше": 3}
DEFAULT_MAX_BULLETS = 5
PLACEHOLDER = re.compile(r"<[A-ZА-ЯЁ][^>]*>|\[(?:Короткое|Что |Какую|Как |Изменения)|\{\{|\bTODO\b|\bXXX\b")
COMMIT_OR_PATH = re.compile(r"\b(?=[0-9a-f]*\d)(?=[0-9a-f]*[a-f])[0-9a-f]{9,40}\b|\b(?:src|tests|sql_views|cf_workers)/[\w/.-]+")
LINK_URL = re.compile(r"\]\([^)]*\)|https?://\S+|`[^`]*`|<!--.*?-->")
SENTENCE_SPLIT = re.compile(r"(?<=[.!?…])\s+(?=[«\"*]*[А-ЯЁA-Z])")
INTERNAL_LINK = re.compile(r"\]\((/[^)\s#?]*)[^)]*\)")
IMAGE = re.compile(r"!\[([^\]]*)\]\(<?([^)>\s]+)>?[^)]*\)")
CDN_IMAGE = re.compile(r"^https://cdn-wiki\.tokenbel\.info/wiki/(?:media|assets)/images/")
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*-\d{8}(?:-\d{8})?$")
SHORT_OPENERS_TO_CHECK = {"мы"}
FALLBACK_TAGS = {"новости", "портфель", "графики", "техобновление", "акции", "облигации", "уведомления"}


@dataclass
class Section:
    title: str
    line: int
    lines: list[tuple[int, str]] = field(default_factory=list)

    @property
    def text(self) -> str:
        return "\n".join(t for _, t in self.lines)

    @property
    def bullets(self) -> list[tuple[int, str]]:
        return [(n, t) for n, t in self.lines if re.match(r"^\s*[-*] ", t)]

    @property
    def words(self) -> int:
        return len(re.findall(r"\w+", LINK_URL.sub(" ", self.text)))


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, line: int | None, msg: str) -> None:
        self.errors.append(f"ERROR{f' line {line}' if line else ''}: {msg}")

    def warn(self, line: int | None, msg: str) -> None:
        self.warnings.append(f"WARN{f' line {line}' if line else ''}: {msg}")


def glossary_terms(heading: str) -> list[str]:
    """Backticked first-column terms from a glossary.md table section."""
    if not GLOSSARY.exists():
        return []
    block = re.search(rf"^## {heading}\n(.*?)(?=^## |\Z)", GLOSSARY.read_text(encoding="utf-8"), re.M | re.S)
    if not block:
        return []
    return re.findall(r"^\|\s*`([^`]+)`\s*\|", block[1], re.M)


def parse_front_matter(lines: list[str], report: Report) -> tuple[dict[str, object], int]:
    if not lines or lines[0].strip() != "---":
        report.error(1, "front matter missing")
        return {}, 0
    meta: dict[str, object] = {}
    key = None
    for idx, raw in enumerate(lines[1:], start=1):
        if raw.strip() == "---":
            return meta, idx + 1
        item = re.match(r"""^\s+-\s+["']?(.*?)["']?\s*$""", raw)
        if item and key:
            meta.setdefault(key, [])
            if isinstance(meta[key], list):
                meta[key].append(item[1])  # type: ignore[union-attr]
            continue
        pair = re.match(r"""^(\w+):\s*["']?(.*?)["']?\s*$""", raw)
        if pair:
            key, value = pair[1], pair[2]
            meta[key] = value if value else []
    report.error(1, "front matter is not closed with ---")
    return meta, len(lines)


def known_tags(news_dir: Path, current: Path) -> set[str]:
    tags = set(FALLBACK_TAGS)
    for index in news_dir.glob("*/index.md"):
        if index.resolve() != current.resolve():
            tags.update(re.findall(r"""^\s+-\s+["']([^"']+)["']""", index.read_text(encoding="utf-8"), re.M))
    return tags


def check_meta(meta: dict[str, object], report: Report, tags_vocab: set[str]) -> None:
    for key in REQUIRED_KEYS:
        if key not in meta or meta[key] in ("", []):
            report.error(None, f"front matter: '{key}' is missing or empty")
    for key in ("date", "lastmod"):
        if key in meta and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(meta[key])):
            report.error(None, f"front matter: '{key}' must be YYYY-MM-DD")
    if str(meta.get("lastmod", "")) < str(meta.get("date", "")):
        report.error(None, "front matter: 'lastmod' is earlier than 'date'")
    if str(meta.get("draft", "")) not in ("false", "true"):
        report.error(None, "front matter: 'draft' must be true or false")
    for forbidden in ("url", "aliases", "slug", "weight"):
        if forbidden in meta:
            report.error(None, f"front matter: '{forbidden}' is not used in news")
    title, seo = str(meta.get("title", "")), str(meta.get("seoTitle", ""))
    if re.search(r"\d{2}\.\d{2}\.\d{4}", title):
        report.warn(None, "title carries dates; current convention is title == seoTitle, dates live in slug/description")
    if seo and (":" in seo or re.search(r"\d", seo) or not 2 <= len(seo.split()) <= 6):
        report.warn(None, "seoTitle should be 2–6 words, no colon, no dates")
    if title and seo and title != seo and not title.startswith(seo):
        report.warn(None, "title and seoTitle differ — keep them identical")
    desc = str(meta.get("description", ""))
    if desc and not 100 <= len(desc) <= 220:
        report.warn(None, f"description is {len(desc)} chars; aim for 100–220")
    if desc and not desc.startswith("Дайджест TokenBel за "):
        report.warn(None, "description should start with «Дайджест TokenBel за <период>: …»")
    raw_tags = meta.get("tags")
    tags: list[str] = [str(t) for t in raw_tags] if isinstance(raw_tags, list) else []
    if tags and (tags[0] != "новости" or tags[-1] != "техобновление"):
        report.warn(None, "tags: start with «новости» and end with «техобновление»")
    for tag in tags:
        if tag not in tags_vocab:
            report.warn(None, f"tag «{tag}» is new — reuse an existing tag if one fits")
    if not 4 <= len(tags) <= 10:
        report.warn(None, f"{len(tags)} tags; keep 4–10")


def check_location(path: Path, repo: Path, meta: dict[str, object], report: Report) -> None:
    try:
        rel = path.resolve().relative_to((repo / "content" / "news").resolve())
    except ValueError:
        report.warn(None, "file is outside content/news/ — run again after saving it to content/news/<slug>/index.md")
        return
    if len(rel.parts) != 2 or rel.name != "index.md":
        report.error(None, "news must be a leaf bundle: content/news/<slug>/index.md")
        return
    slug = rel.parts[0]
    if not SLUG.match(slug):
        report.warn(None, f"slug «{slug}» does not follow <translit-seoTitle>-DDMMYYYY[-DDMMYYYY] (scripts/slug.py)")
    to = str(meta.get("date", ""))
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", to) and not slug.endswith(f"{to[8:10]}{to[5:7]}{to[0:4]}"):
        report.warn(None, f"slug «{slug}» does not end with the 'date' {to} as DDMMYYYY")


def split_sections(lines: list[str], start: int, report: Report) -> list[Section]:
    sections: list[Section] = []
    for number, raw in enumerate(lines[start:], start=start + 1):
        if raw.startswith("# "):
            report.error(number, "no H1 in the body — Hugo renders the title from front matter")
        if raw.startswith("#### "):
            report.warn(number, "H4+ headings are the old manual format; use ## sections and ### audience groups")
        sub = re.match(r"^### (.+?)\s*$", raw)
        if sub and sections and sections[-1].title == "Что стало удобнее" and sub[1] not in ALLOWED_H3:
            report.warn(number, f"unexpected group «{sub[1]}»; allowed: {', '.join(sorted(ALLOWED_H3))}")
        heading = re.match(r"^## (.+?)\s*$", raw)
        if heading:
            sections.append(Section(heading[1], number))
        elif sections:
            sections[-1].lines.append((number, raw))
        elif raw.strip():
            report.error(number, "text before the first ## section — start with «## Введение»")
    return sections


def first_word(text: str) -> str:
    match = re.search(r"[\wЁё]+", re.sub(r"^\s*[-*]\s+|\*\*[^*]+\*\*:?\s*", "", text))
    return match[0].lower() if match else ""


def check_openers(items: list[tuple[int, str]], report: Report, what: str) -> None:
    for (_, prev), (number, cur) in zip(items, items[1:], strict=False):
        word = first_word(cur)
        if word and word == first_word(prev) and (len(word) > 2 or word in SHORT_OPENERS_TO_CHECK):
            report.warn(number, f"two {what} in a row start with «{word}»")


def check_paragraph_openers(section: Section, report: Report) -> None:
    for number, raw in section.lines:
        if raw.strip() and not raw.lstrip().startswith(("-", "*", "[", "!", "<", "|", "#")):
            sentences = [(number, s) for s in SENTENCE_SPLIT.split(raw.strip())]
            check_openers(sentences, report, "sentences")


def check_section(section: Section, report: Report) -> None:
    if section.title not in ALLOWED_H2:
        report.warn(section.line, f"unexpected section «{section.title}»; allowed: {', '.join(sorted(ALLOWED_H2))}")
    meaningful = [t for _, t in section.lines if t.strip() and t.strip() != "---" and not t.startswith("### ")]
    if not meaningful:
        report.error(section.line, f"section «{section.title}» is empty — delete it with its --- line")
        return
    bullets = section.bullets
    if section.title in PARAGRAPH_SECTIONS and len(bullets) > 3:
        report.warn(section.line, f"«{section.title}» should be prose, found {len(bullets)} bullets")
    limit = MAX_BULLETS.get(section.title, DEFAULT_MAX_BULLETS)
    for sub in re.split(r"^### .*$", section.text, flags=re.M):
        count = len(re.findall(r"^\s*[-*] ", sub, re.M))
        if count > limit:
            report.warn(section.line, f"«{section.title}»: {count} bullets in one list, limit {limit}")
    check_openers(bullets, report, "bullets")
    check_paragraph_openers(section, report)


def check_separators(sections: list[Section], report: Report) -> None:
    for prev, cur in zip(sections, sections[1:], strict=False):
        tail = [t.strip() for _, t in prev.lines if t.strip()]
        if not tail or tail[-1] != "---":
            report.warn(cur.line, f"put a --- line before «## {cur.title}»")


def check_words(sections: list[Section], report: Report) -> None:
    canc = glossary_terms("Канцелярит")
    jargon = glossary_terms("Жаргон")
    brands = glossary_terms("Написание названий")
    for section in sections:
        for number, raw in section.lines:
            plain = LINK_URL.sub(" ", raw)
            low = plain.lower()
            for term in canc:
                if re.search(rf"(?<!\w){re.escape(term.lower())}", low):
                    report.error(number, f"канцелярит «{term}» — see references/glossary.md")
            if section.title != "Технически":
                for term in jargon:
                    if re.search(rf"(?<!\w){re.escape(term.lower())}", low):
                        report.error(number, f"jargon «{term}» outside «Технически»")
            for term in brands:
                if re.search(rf"(?<![\w.]){re.escape(term)}(?!\w)", plain):
                    report.warn(number, f"spelling «{term}» — check references/glossary.md")
            if PLACEHOLDER.search(LINK_URL.sub(" ", raw)):
                report.error(number, "template placeholder left in text")
            if COMMIT_OR_PATH.search(plain):
                report.error(number, "commit hash or source path in reader-facing text")


def link_target_exists(repo: Path, url_path: str) -> bool:
    parts = [p for p in url_path.strip("/").split("/") if p]
    base = repo / "content" / Path(*parts) if parts else repo / "content"
    if (base / "index.md").exists() or (base / "_index.md").exists():
        return True
    static = repo / "static" / Path(*parts) if parts else repo / "static"
    return static.is_file() or (static / "index.html").exists()


def check_links_and_media(lines: list[str], start: int, repo: Path, report: Report) -> None:
    inbox = repo / ".wiki-media" / "inbox"
    for number, raw in enumerate(lines[start:], start=start + 1):
        if "<!--" in raw:
            report.error(number, "HTML comment — it leaks into the public index.md; replace or delete it")
        for match in INTERNAL_LINK.finditer(raw):
            target = match[1]
            if target.startswith("/news/") and target.count("/") <= 2:
                continue
            if not link_target_exists(repo, target):
                report.error(number, f"internal link {target} has no page in content/ or static/")
        for match in re.finditer(r"https?://(?:www\.)?tokenbel\.info(/[^\s)]*)?", raw):
            report.warn(number, f"{match[0]}: dashboard pages live on https://dashboard.tokenbel.info/")
        for match in IMAGE.finditer(raw):
            alt, src = match[1], match[2]
            if not alt.strip():
                report.error(number, "image without alt text")
            if src.startswith("upload:"):
                rel = src.removeprefix("upload:")
                if not (inbox / rel).is_file():
                    report.error(number, f"upload marker points to missing file .wiki-media/inbox/{rel}")
                else:
                    report.warn(number, f"unpublished image {src} — run wiki-media publish before release")
            elif not CDN_IMAGE.match(src):
                report.error(number, f"image {src}: use upload:<inbox path> or a cdn-wiki.tokenbel.info URL")


def check_balance(sections: list[Section], body_words: int, report: Report) -> None:
    if not 300 <= body_words <= 900:
        report.warn(None, f"{body_words} words; published posts are 330–840")
    by_title = {s.title: s for s in sections}
    tech, main = by_title.get("Технически"), by_title.get("Главное")
    if tech and main and tech.words >= main.words:
        report.warn(tech.line, "«Технически» is as long as «Главное» — cut it")
    for required in ("Введение", "Главное"):
        if required not in by_title:
            report.error(None, f"section «{required}» is required")
    order = [s.title for s in sections if s.title in ALLOWED_H2]
    canonical = [t for t in ("Введение", "Главное", "Вехи", "Что стало удобнее", "Исправили", "Технически", "Что дальше") if t in order]
    if order != canonical:
        report.warn(None, f"section order should be: {' → '.join(canonical)}")
    if "](/guides/" not in "\n".join(s.text for s in sections):
        report.warn(None, "no links to /guides/ — add one where a guide exists (references/guides-map.md)")


def check_file(path: Path, repo: Path) -> Report:
    lines = path.read_text(encoding="utf-8").splitlines()
    report = Report()
    meta, body_start = parse_front_matter(lines, report)
    check_meta(meta, report, known_tags(repo / "content" / "news", path))
    check_location(path, repo, meta, report)
    sections = split_sections(lines, body_start, report)
    for section in sections:
        check_section(section, report)
    check_separators(sections, report)
    check_words(sections, report)
    check_links_and_media(lines, body_start, repo, report)
    check_balance(sections, sum(s.words for s in sections), report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", type=Path, nargs="+")
    parser.add_argument("--strict", action="store_true", help="fail on warnings too")
    parser.add_argument("--repo", type=Path, default=DEFAULT_REPO, help="tokenbel-wiki root (default: auto)")
    args = parser.parse_args()

    failed = False
    for path in args.files:
        report = check_file(path, args.repo)
        for line in report.errors + report.warnings:
            print(line)
        print(f"{path}: {len(report.errors)} error(s), {len(report.warnings)} warning(s)")
        failed |= bool(report.errors or (args.strict and report.warnings))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
