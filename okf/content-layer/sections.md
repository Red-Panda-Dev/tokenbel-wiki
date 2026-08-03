---
type: Section Structure
title: Sections
description: Auto-assembled sections and navigation structure in TokenBel Wiki
---

# Sections

The Content Layer is organized into **auto-assembled sections** that are discovered from the `content/` directory structure. These sections drive both the main navigation menu and the home page section cards.

## Section Hierarchy

```
content/
├── _index.md                    # Home page (site root)
├── news/                        # Новости (weight: 10)
│   ├── _index.md                # Section landing page
│   └── <article>/               # Leaf bundle articles
│       └── index.md
├── statistics/                  # Статистика (weight: 20)
│   ├── _index.md
│   └── <article>/
│       └── index.md
├── guides/                      # Руководство (weight: 30)
│   ├── _index.md
│   └── <article>/
│       └── index.md
├── policies/                    # Политика (weight: 40)
│   ├── _index.md
│   └── <article>/
│       └── index.md
└── about/                       # О проекте (weight: 50)
    ├── _index.md
    └── <article>/
        └── index.md
```

## Section Landing Pages

Each section has a landing page defined by `_index.md` with the following **required front matter**:

```yaml
---
title: "Section Title"
description: "One-sentence description of the section"
weight: <10-50 in increments of 10>
icon: <news|chart|guide|document|info>
---
```

### Icon Values

The `icon` field must be one of these predefined values:

| Value | Usage |
|-------|-------|
| `news` | News section |
| `chart` | Statistics section |
| `guide` | Guides section |
| `document` | Policies section |
| `info` | About section |

### Weight Values

The `weight` field determines navigation order (lower = earlier):

| Section | Weight | Menu Order |
|---------|--------|------------|
| news | 10 | 1 |
| statistics | 20 | 2 |
| guides | 30 | 3 |
| policies | 40 | 4 |
| about | 50 | 5 |

## Navigation Menu

The main navigation menu is defined in `hugo.yaml` under `menus.main`:

```yaml
menus:
  main:
    - name: "Новости"
      pageRef: "/news"
      weight: 10
    - name: "Статистика"
      pageRef: "/statistics"
      weight: 20
    - name: "Руководство"
      pageRef: "/guides"
      weight: 30
    - name: "Политика"
      pageRef: "/policies"
      weight: 40
    - name: "О проекте"
      pageRef: "/about"
      weight: 50
```

**Rule**: The `pageRef` must match the section directory name.

## Home Page

The home page is defined at `content/_index.md` with special front matter fields:

```yaml
---
title: "База знаний TokenBel"
description: "Руководства, статистика рынка и справочные материалы по работе с TokenBel."
heroPrimaryLabel: "Открыть руководство"
heroPrimaryURL: "/guides/"
heroSecondaryLabel: "Перейти к TokenBel"
heroSecondaryURL: "https://dashboard.tokenbel.info/"
---
```

These fields are consumed by `layouts/home.html` to render the hero section.

## Section Discovery

Hugo discovers sections automatically from the `content/` directory structure. The template `layouts/home.html` iterates over sections using:

```go-html-template
{{ range site.Sections.ByWeight }}
  {{ partial "section-card.html" . }}
{{ end }}
```

This renders section cards on the home page in weight order.

## Section Lists

Section landing pages (e.g., `content/statistics/_index.md`) use the list template `layouts/_default/list.html` which:

1. Displays the section title and description
2. Lists all pages in the section sorted by `.ByLastmod.Reverse`
3. Filters out pages with `excludeFromRecent: true` from the recent pages block

## Relationships

* [Front Matter](front-matter.md) — Field definitions for section landing pages
* [Article Structure](article-structure.md) — How articles within sections are organized
* [Presentation Layer](../presentation-layer/) — How sections are rendered in templates

## Citations

[1] `hugo.yaml:20-30` — Menu configuration with section references
[2] `content/_index.md` — Home page front matter with hero fields
[3] `content/news/_index.md` — News section landing page example
[4] `content/statistics/_index.md` — Statistics section landing page example
[5] `layouts/home.html:20-30` — Section iteration using `.Sections.ByWeight`
[6] `layouts/_default/list.html` — Section list template
[7] `content/AGENTS.md:20-25` — Rules for creating new sections
