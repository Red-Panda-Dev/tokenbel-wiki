---
type: Template Structure
title: Templates
description: Hugo template files and their responsibilities in TokenBel Wiki
---

# Templates

The Presentation Layer uses **local Hugo templates only** — no external themes. All templates are in the `layouts/` directory.

## Template Hierarchy

```
layouts/
├── _default/           # Default templates for all content types
│   ├── baseof.html     # Base template (HTML skeleton)
│   └── list.html       # Section list template
│   └── single.html     # Single page/article template
├── _markup/           # Markdown render hooks
│   └── render-table.html  # Custom table rendering
├── home.html          # Home page template
├── 404.html           # 404 error page template
├── robots.txt         # Robots.txt template
└── partials/          # Reusable partials (see Partials)
```

## Base Template (baseof.html)

File: `layouts/_default/baseof.html`

**Responsibilities:**
- HTML5 document structure (`<html>`, `<head>`, `<body>`)
- Language attribute: `lang="{{ site.Language.Lang | default \"ru\" }}"`
- Skip-to-content link for accessibility
- Header partial inclusion
- Main content block definition
- Footer partial inclusion

**Key features:**
- Uses Tailwind CSS classes for styling
- Full-height flex column layout
- Antialiased text rendering
- Black text on light gray background

## Home Template (home.html)

File: `layouts/home.html`

**Responsibilities:**
- Hero section with call-to-action buttons
- Section cards grid (from `site.Sections.ByWeight`)
- Recent pages block
- Useful links section

**Front matter fields consumed:**
- `.Title` — Page title
- `.Description` — Page description
- `.Params.heroPrimaryLabel` — Primary CTA button text
- `.Params.heroPrimaryURL` — Primary CTA button URL
- `.Params.heroSecondaryLabel` — Secondary CTA button text
- `.Params.heroSecondaryURL` — Secondary CTA button URL

**Section iteration:**
```go-html-template
{{ range site.Sections.ByWeight }}
  {{ partial "section-card.html" . }}
{{ end }}
```

## List Template (list.html)

File: `layouts/_default/list.html`

**Responsibilities:**
- Section landing page rendering
- Article list sorted by last modification date
- Pagination support

**Key logic:**
- Iterates over `.RegularPages.ByLastmod.Reverse`
- Renders each page with title, description, and date
- Excludes pages with `excludeFromRecent: true` from recent block

## Single Template (single.html)

File: `layouts/_default/single.html`

**Responsibilities:**
- Individual article/page rendering
- Article header with title and dates
- Content rendering
- Navigation elements

## 404 Template (404.html)

File: `layouts/404.html`

**Responsibilities:**
- Custom 404 error page
- Must contain literal text `Страница не найдена`
- Must emit `noindex, follow` robots meta tag

**Validation:**
- `make check` verifies both requirements

## Markup Render Hooks

### Table Rendering (render-table.html)

File: `layouts/_markup/render-table.html`

**Responsibilities:**
- Custom table styling and rendering
- Adds Tailwind CSS classes to table elements
- Preserves Markdown table structure

## Template Inheritance

All page templates extend `baseof.html` using Hugo's block system:

```go-html-template
{{ define "main" }}
  <!-- Page-specific content -->
{{ end }}
```

The base template defines the block:
```go-html-template
{{ block "main" . }}{{ end }}
```

## Relationships

* [Partials](partials.md) — Reusable components included by templates
* [CSS Pipeline](css-pipeline.md) — Styling for templates

## Citations

[1] `layouts/_default/baseof.html` — Base template with HTML structure
[2] `layouts/home.html` — Home page template
[3] `layouts/_default/list.html` — Section list template
[4] `layouts/_default/single.html` — Single page template
[5] `layouts/404.html` — 404 error page template
[6] `layouts/_markup/render-table.html` — Custom table rendering
[7] `layouts/AGENTS.md:10-20` — Template editing rules
[8] `Makefile:50-55` — check target validates 404 requirements
