---
type: Front Matter Contract
title: Front Matter
description: Required and optional front matter fields for all content types
---

# Front Matter

Front matter is YAML metadata at the top of every Markdown file. It defines the document's identity, appearance, and behavior in the rendered site.

## Universal Fields

All content types support these fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | Human-readable title, displayed in headings and navigation |
| `description` | string | Recommended | One-sentence summary, used in meta description and section cards |
| `date` | date | No | Publication date, displayed in article headers |
| `lastmod` | date | No | Last modification date, displayed in UI; used for sorting |
| `excludeFromRecent` | boolean | No | If `true`, excludes page from "Последние обновления" block |

## Section Landing Pages

Files: `content/<section>/_index.md`

**Required fields:**

```yaml
---
title: "Section Title"
description: "Section description"
weight: <10-50>
icon: <news|chart|guide|document|info>
---
```

**Example:**
```yaml
---
title: "Статистика"
description: "Аналитические данные и статистика рынка TokenBel."
weight: 20
icon: chart
---
```

## Home Page

File: `content/_index.md`

**Special fields for hero section:**

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

These fields are consumed by `layouts/home.html` to render call-to-action buttons.

## Article Pages (Leaf Bundles)

Files: `content/<section>/<slug>/index.md`

**Recommended structure:**

```yaml
---
title: "Article Title"
description: "Article summary for meta and cards"
date: 2025-01-04
tags:
  - tag1
  - tag2
---

Article content here...
```

### Image References

Articles **must not** use local image files in article bundles. Instead:

1. Place image in `.wiki-media/inbox/<path>/<filename>`
2. Reference in Markdown using `upload:` marker:

```markdown
![Alt text](upload:<inbox-relative-path>)
```

The `wiki-media` CLI will replace these with CDN URLs during publishing.

**Valid examples:**
```markdown
![График](upload:statistics/trading-volume.png)
![График](upload:statistics/trading-volume.png "Источник")
<img src="upload:statistics/trading-volume.png" alt="График">
```

**Invalid examples:**
```markdown
![График](images/trading-volume.png)  # Local file - NOT ALLOWED
![График](upload:/absolute/path.png)  # Absolute path - NOT ALLOWED
![График](upload:../parent/path.png)  # Relative path outside inbox - NOT ALLOWED
```

## Date Handling

- **Source**: Dates come **only** from front matter (`date` and `lastmod` fields)
- **Not from Git**: `enableGitInfo: false` in `hugo.yaml` means Git commit dates are ignored
- **Display**: `layouts/partials/page-dates.html` renders dates from front matter
- **Sorting**: Articles are sorted by `.ByLastmod.Reverse` in list templates

## Excluding from Recent

Pages with `excludeFromRecent: true` in front matter are **excluded** from:
- The "Последние обновления" block on the home page
- The recent pages partial rendered by `layouts/partials/recent-pages.html`

**Example:**
```yaml
---
title: "Old Article"
excludeFromRecent: true
---
```

## Taxonomies

The site defines a single taxonomy in `hugo.yaml`:

```yaml
taxonomies:
  tag: tags
```

Articles can be tagged using the `tags` field:

```yaml
---
tags:
  - statistics
  - market-data
---
```

## Language

- **Primary language**: Russian (ru-BY locale)
- **All content**: Must be in Russian
- **Configuration**: `languages.ru.locale: "ru-BY"` in `hugo.yaml`

## Relationships

* [Sections](sections.md) — How front matter drives section organization
* [Article Structure](article-structure.md) — File organization for articles

## Citations

[1] `hugo.yaml:1-10` — Site configuration including `enableGitInfo: false`
[2] `hugo.yaml:14-15` — Taxonomy definition
[3] `hugo.yaml:17-29` — Menu configuration
[4] `content/_index.md` — Home page front matter with hero fields
[5] `content/news/_index.md` — Section landing page front matter example
[6] `content/news/*/index.md` — Article front matter examples
[7] `layouts/partials/page-dates.html` — Date rendering from front matter
[8] `layouts/partials/recent-pages.html` — Recent pages filtering logic
[9] `content/AGENTS.md:20-35` — Front matter rules and conventions
[10] `tools/wiki-media/README.md:20-30` — upload: marker syntax requirements
