---
type: Partial Components
title: Partials
description: Reusable HTML partial components in TokenBel Wiki
---

# Partials

Partials are reusable HTML components stored in `layouts/partials/`. They are included in templates using the `{{ partial "name.html" . }}` syntax.

## Partial Directory Structure

```
layouts/partials/
├── css.html            # CSS link injection
├── footer.html         # Footer component
├── head.html           # Head meta tags and SEO
├── header.html         # Header with navigation
├── page-dates.html      # Date display for pages
├── recent-pages.html    # Recent pages block
├── section-card.html    # Section card for home page
└── (other components)
```

## Head Partial (head.html)

File: `layouts/partials/head.html`

**Responsibilities:**
- Character encoding and viewport meta
- Font preconnects (Google Fonts)
- Page title generation
- Meta description
- Canonical URL (excluded for 404 pages)
- Robots meta (noindex,follow for 404 pages)
- OpenGraph meta tags
- Favicon link
- CSS partial inclusion
- JSON-LD structured data (home page only)

**Key logic:**
```go-html-template
{{ $is404 := eq .Kind "404" }}
{{ if not $is404 }}<link rel="canonical" href="{{ .Permalink }}">{{ end }}
{{ if $is404 }}<meta name="robots" content="noindex, follow">{{ end }}
```

**Page title generation:**
- Home: `site.Title`
- Other pages: `{{ .Title }} | {{ site.Title }}`
- 404: `Страница не найдена | {{ site.Title }}`

## CSS Partial (css.html)

File: `layouts/partials/css.html`

**Responsibilities:**
- Links the committed Tailwind CSS file
- Hardcoded to `tailwind.min.css` (production)

**Content:**
```html
<link rel="stylesheet" href="{{ \"css/tailwind.min.css\" | relURL }}">
```

**Note:** `output.css` exists for development/watch purposes but is **not** linked in any template.

## Header Partial (header.html)

File: `layouts/partials/header.html`

**Responsibilities:**
- Site header with logo
- Main navigation menu
- Mobile menu toggle
- Sticky positioning

**Data consumed:**
- `site.Menus.main` — Main navigation menu items
- `site.Title` — Site title for logo
- `site.BaseURL` — Base URL for logo link

## Footer Partial (footer.html)

File: `layouts/partials/footer.html`

**Responsibilities:**
- Site footer content
- Copyright information
- Additional links

## Page Dates Partial (page-dates.html)

File: `layouts/partials/page-dates.html`

**Responsibilities:**
- Display publication and modification dates
- Uses front matter `date` and `lastmod` fields
- Formatted according to Russian locale

**Key logic:**
- Shows `date` if present
- Shows `lastmod` if present and different from `date`
- Both dates come from front matter only (not Git)

## Recent Pages Partial (recent-pages.html)

File: `layouts/partials/recent-pages.html`

**Responsibilities:**
- Display list of recently updated pages
- Exclude pages with `excludeFromRecent: true`
- Sort by last modification date
- Limit to configurable number of items

**Key logic:**
```go-html-template
{{ $recent := where site.RegularPages ".Params.excludeFromRecent" "!=" true }}
{{ $recent = $recent.ByLastmod.Reverse }}
{{ range first 5 $recent }}
```

## Section Card Partial (section-card.html)

File: `layouts/partials/section-card.html`

**Responsibilities:**
- Render section card for home page
- Display section title, description, and icon
- Link to section page

**Data consumed:**
- `.Title` — Section title
- `.Description` — Section description
- `.Params.icon` — Section icon name
- `.RelPermalink` — Section URL

**Icon mapping:**
The icon field in section front matter maps to visual icons:
- `news` — News icon
- `chart` — Chart/statistics icon
- `guide` — Guide/documentation icon
- `document` — Policy/document icon
- `info` — Information icon

## Robots.txt

File: `layouts/robots.txt`

**Content:**
```
User-agent: *
Allow: /
```

## Relationships

* [Templates](templates.md) — Templates that include these partials
* [CSS Pipeline](css-pipeline.md) — Styling for partial components

## Citations

[1] `layouts/partials/head.html` — SEO meta and title generation
[2] `layouts/partials/css.html` — Tailwind CSS link injection
[3] `layouts/partials/header.html` — Navigation header
[4] `layouts/partials/footer.html` — Site footer
[5] `layouts/partials/page-dates.html` — Date display logic
[6] `layouts/partials/recent-pages.html` — Recent pages filtering
[7] `layouts/partials/section-card.html` — Section card rendering
[8] `layouts/robots.txt` — Robots.txt content
[9] `layouts/AGENTS.md:10-30` — Partial editing rules and conventions
