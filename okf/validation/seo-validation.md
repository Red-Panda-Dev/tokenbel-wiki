---
type: Validation Script
title: SEO Validation
description: Validates rendered SEO metadata in Hugo output without third-party packages
---

# SEO Validation

Python script that validates SEO metadata, structured data, and HTML correctness in Hugo-generated pages.

## Script Overview

File: `tests/check_seo.py`

**Purpose**: Ensure all pages have correct SEO metadata, canonical URLs, OpenGraph tags, and JSON-LD structured data.

**Features**:
- Validates meta tags (description, og:title, og:description, etc.)
- Checks canonical URL correctness
- Validates JSON-LD structured data
- Verifies page titles and language attributes
- HTML parsing without external dependencies

## Validation Rules

### Required Meta Tags

All pages must have:
- `og:title` — OpenGraph title
- `og:description` — OpenGraph description
- `og:url` — OpenGraph URL (canonical)
- `og:type` — OpenGraph type (website or article)
- `description` — Meta description
- `twitter:card` — Twitter card type

### Canonical URL Rules

- Must be absolute URLs starting with `https://wiki.tokenbel.info/`
- Must not contain `localhost` or port numbers
- 404 pages must NOT have canonical URLs
- Must match the page's actual URL

### JSON-LD Rules

- Home page must have `WebSite` schema
- Article pages must have `Article` or `BreadcrumbList` schemas
- JSON-LD must be valid JSON
- Must include required fields for each schema type

### Page Title Rules

- Must not be empty
- Must not exceed 60 characters (warning)
- Must include site name for non-home pages

### Language Rules

- All pages must have `lang="ru"` attribute
- Must match `languages.ru.locale: "ru-BY"` in `hugo.yaml`

## Usage

### Run Validation

```bash
# Run SEO validation
python tests/check_seo.py

# Check specific page
python tests/check_seo.py public/index.html

# Run with verbose output
python tests/check_seo.py --verbose
```

### Integration with Makefile

The SEO validation is integrated into the build process:

```makefile
# In Makefile
check: css-check build
	@test -f public/index.html
	@test -f public/404.html
	@python tests/check_seo.py
	@python tests/check_pagination.py
```

## Implementation Details

### HTML Parser

Uses Python's built-in `HTMLParser` to extract:
- Meta tags (property, name, content attributes)
- Page titles
- JSON-LD script tags
- Language attributes

### Validation Logic

1. **Page Discovery**: Scans `public/` directory for HTML files
2. **Meta Extraction**: Parses each page for meta tags
3. **Rule Checking**: Validates each page against SEO rules
4. **Error Reporting**: Collects and reports all validation errors
5. **Exit Code**: Returns non-zero if any validation fails

### Special Page Handling

**Home Page (`index.html`)**:
- Must have `WebSite` JSON-LD
- Title must contain "База знаний TokenBel"
- Must have canonical URL

**404 Page (`404.html`)**:
- Must NOT have canonical URL
- Must have `noindex, follow` robots meta
- Must contain literal text "Страница не найдена"

**Article Pages**:
- Must have `Article` JSON-LD
- Must have publication date in schema
- Must have proper OpenGraph article tags

## Error Messages

Common validation errors:
- `MISSING_OG_TITLE`: Missing og:title meta tag
- `MISSING_DESCRIPTION`: Missing description meta tag
- `INVALID_CANONICAL`: Canonical URL is invalid
- `NO_CANONICAL`: Missing canonical URL (except 404)
- `INVALID_JSON_LD`: JSON-LD is not valid JSON
- `EMPTY_TITLE`: Page title is empty

## Relationships

* [Pagination Validation](pagination-validation.md) — Validates pagination in list pages
* [Build System](../build-system/) — Build process that runs validation
* [Presentation Layer](../presentation-layer/) — Templates that generate the validated output

## Citations

[1] `tests/check_seo.py` — Complete SEO validation script
[2] `Makefile:75-82` — check target that runs validation
[3] `layouts/partials/head.html` — SEO meta tags generation
[4] `hugo.yaml` — Site configuration affecting SEO
[5] `ARCHITECTURE.md:5` — Architecture context for validation
[6] `content/_index.md` — Home page with required text
[7] `layouts/404.html` — 404 page with required text and meta
