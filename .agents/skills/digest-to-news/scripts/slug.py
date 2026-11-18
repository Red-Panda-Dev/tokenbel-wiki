#!/usr/bin/env python3
"""Build a tokenbel-wiki news slug (leaf-bundle directory name).

Convention of published news (July 2026 onwards): lower-case transliteration
of seoTitle (ё→e, ч→ch, ш→sh), words joined with "-", then the period as
DDMMYYYY. A period of several days gets both ends, a single day — one date.

    slug.py "Портфели и облигации" 2026-11-17 --from 2026-10-15
    -> portfeli-i-obligacii-15102026-17112026
    slug.py "Финансовые отчёты и портфели" 2026-10-14
    -> finansovye-otchety-i-portfeli-14102026

Dates already present in the title ("… (15.10.2026 - 17.11.2026)") are kept
and no second date is appended.

Usage: slug.py "SEO_TITLE" TO_DATE [--from FROM_DATE]   (dates in YYYY-MM-DD)
"""

from __future__ import annotations

import argparse
import re
from datetime import date

TRANSLIT = str.maketrans(
    {
        "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e", "ж": "zh",
        "з": "z", "и": "i", "й": "i", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o",
        "п": "p", "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f", "х": "x", "ц": "c",
        "ч": "ch", "ш": "sh", "щ": "shch", "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "iu",
        "я": "ia",
    }
)  # fmt: skip
TITLE_DATE = re.compile(r"(\d{2})\.(\d{2})\.(\d{4})")


def slugify(title: str, to_date: date | None = None, from_date: date | None = None) -> str:
    text = title.lower().translate(TRANSLIT)
    has_date = bool(TITLE_DATE.search(text))
    text = TITLE_DATE.sub(r"\1\2\3", text)
    slug = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    if to_date and not has_date:
        if from_date and from_date != to_date:
            slug = f"{slug}-{from_date:%d%m%Y}"
        slug = f"{slug}-{to_date:%d%m%Y}"
    return slug


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("title")
    parser.add_argument("to_date", nargs="?", type=date.fromisoformat)
    parser.add_argument("--from", dest="from_date", type=date.fromisoformat)
    args = parser.parse_args()
    print(slugify(args.title, args.to_date, args.from_date))


if __name__ == "__main__":
    main()
