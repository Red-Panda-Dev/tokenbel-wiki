---
type: Validation Script
title: Pagination Validation
description: Validates Hugo list pagination in rendered output
---

# Pagination Validation

Python script that validates pagination behavior in Hugo-generated list pages.

## Script Overview

File: `tests/check_pagination.py`

**Purpose**: Ensure pagination works correctly across all section list pages, with proper article counts, pagination links, and navigation.

**Features**:
- Validates article count per page matches `pagerSize` configuration
- Checks pagination navigation presence and correctness
- Verifies pagination links point to correct pages
- Validates pagination on all section list pages

## Pagination Configuration

The pagination size is configured in `hugo.yaml`:

```yaml
pagination:
  pagerSize: 12
```

This means each list page should contain exactly 12 articles (or fewer on the last page).

## Validation Rules

### Article Count

- Each list page must have exactly `pagerSize` articles (12 by default)
- The last page may have fewer articles
- Articles are counted by `<article>` elements in the HTML

### Pagination Navigation

- Must have a `<nav>` element with `aria-label="Постраничная навигация"`
- Must contain pagination links
- Pagination links must use Hugo's native path-based pagination (`/page/N/`)

### Pagination Links

- First page must NOT have a "previous" link
- Last page must NOT have a "next" link
- All intermediate pages must have both "previous" and "next" links
- Page numbers in links must be sequential and correct

### Path Format

Pagination must use Hugo's native path-based URLs:
- Page 1: `/section/` (no page number)
- Page 2: `/section/page/2/`
- Page 3: `/section/page/3/`
- etc.

**Not allowed**:
- Query parameter pagination (`?page=2`)
- Custom pagination schemes

## Usage

### Run Validation

```bash
# Run pagination validation
python tests/check_pagination.py

# Check specific section
python tests/check_pagination.py public/statistics/

# Run with verbose output
python tests/check_pagination.py --verbose
```

### Integration with Makefile

The pagination validation is part of the `make check` target:

```makefile
check: css-check build
	@test -f public/index.html
	@test -f public/404.html
	@python tests/check_seo.py
	@python tests/check_pagination.py
```

## Implementation Details

### HTML Parser

Uses Python's built-in `HTMLParser` to:
- Count `<article>` elements
- Find pagination `<nav>` elements
- Extract pagination links
- Verify link structure

### Page Discovery

1. Scans `public/` directory for HTML files
2. Identifies list pages (section landing pages)
3. Groups pages by section
4. Validates pagination across each section's pages

### Validation Logic

For each section with pagination:
1. Count articles on each page
2. Verify article count matches `pagerSize` (except last page)
3. Check pagination navigation exists
4. Verify pagination links are correct
5. Ensure no broken pagination sequences

## Error Messages

Common validation errors:
- `PAGER_SIZE_MISMATCH`: Article count doesn't match pagerSize
- `MISSING_PAGINATION`: Pagination navigation not found
- `INVALID_PAGINATION_LINKS`: Pagination links are incorrect
- `NON_NATIVE_PAGINATION`: Using non-native pagination scheme

## Native vs Query Parameter Pagination

### Native Pagination (Current - Required)

Uses Hugo's built-in path-based pagination:
- URL format: `/section/page/2/`
- Configured via Hugo's pagination settings
- No query parameters needed
- Better for SEO and caching

### Query Parameter Pagination (Deprecated)

Previously used query parameters:
- URL format: `/section/?page=2`
- Required custom template logic
- Less SEO-friendly
- Has been removed from the codebase

**Migration**: The repository was refactored to use native pagination exclusively (commit `01113d8`).

## Relationships

* [SEO Validation](seo-validation.md) — Validates SEO metadata on paginated pages
* [Build System](../build-system/) — Build process that runs validation
* [Content Layer](../content-layer/) — Content that gets paginated
* [Presentation Layer](../presentation-layer/) — Templates that render pagination

## Citations

[1] `tests/check_pagination.py` — Complete pagination validation script
[2] `Makefile:75-82` — check target that runs validation
[3] `hugo.yaml:11-12` — Pagination configuration (pagerSize: 12)
[4] `layouts/_default/list.html` — List template with pagination
[5] `ARCHITECTURE.md:5` — Architecture context for pagination
[6] `01113d8` — Commit that refactored to native pagination
[7] `layouts/partials/pagination.html` — Pagination partial (if exists)
