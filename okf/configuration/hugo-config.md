---
type: Hugo Configuration
title: Hugo Config
description: hugo.yaml site configuration for TokenBel Wiki
---

# Hugo Config

File: `hugo.yaml` — The **central configuration** file for the Hugo static site generator.

## Complete Configuration

```yaml
baseURL: "https://wiki.tokenbel.info/"
title: "Wiki TokenBel"
defaultContentLanguage: "ru"

languages:
  ru:
    locale: "ru-BY"
    label: "Русский"
    weight: 1

enableRobotsTXT: true
enableGitInfo: false

pagination:
  pagerSize: 12

taxonomies:
  tag: tags

params:
  description: "Справочные материалы, руководства и статистика TokenBel."
  mainSiteURL: "https://tokenbel.info/"
  dashboardURL: "https://dashboard.tokenbel.info/"
  tokensURL: "https://dashboard.tokenbel.info/tokens/"
  secondMarketURL: "https://dashboard.tokenbel.info/secondhand/"
  sharesURL: "https://dashboard.tokenbel.info/shares/"
  bondsURL: "https://dashboard.tokenbel.info/bonds/"
  repositoryURL: "https://github.com/Red-Panda-Dev/tokenbel-wiki"

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

caches:
  images:
    dir: ":cacheDir/images"
```

## Configuration Sections

### Site Identity

```yaml
baseURL: "https://wiki.tokenbel.info/"
title: "Wiki TokenBel"
defaultContentLanguage: "ru"
```

| Field | Value | Description |
|-------|-------|-------------|
| `baseURL` | `https://wiki.tokenbel.info/` | Canonical base URL for all pages |
| `title` | `Wiki TokenBel` | Site title, used in templates and meta |
| `defaultContentLanguage` | `ru` | Default language for content |

**Important:** `baseURL` must end with trailing slash.

### Language Configuration

```yaml
languages:
  ru:
    locale: "ru-BY"
    label: "Русский"
    weight: 1
```

**Single language:** The site supports only Russian (ru) with Belarus locale (ru-BY).

| Field | Value | Description |
|-------|-------|-------------|
| `locale` | `ru-BY` | Locale for date formatting and localization |
| `label` | `Русский` | Human-readable language name |
| `weight` | `1` | Language priority (only one language) |

### Global Settings

```yaml
enableRobotsTXT: true
enableGitInfo: false
```

| Field | Value | Description |
|-------|-------|-------------|
| `enableRobotsTXT` | `true` | Generate `robots.txt` file |
| `enableGitInfo` | `false` | **Disable** Git-based dates and info |

**Critical:** `enableGitInfo: false` means:
- Page dates come **only** from front matter (`date`, `lastmod`)
- `.GitInfo` is not available in templates
- `.Lastmod` resolves from front matter, not Git commits

### Pagination

```yaml
pagination:
  pagerSize: 12
```

| Field | Value | Description |
|-------|-------|-------------|
| `pagerSize` | `12` | Number of items per page in pagination |

**Usage:** Used by list templates when pagination is enabled.

### Taxonomies

```yaml
taxonomies:
  tag: tags
```

**Single taxonomy:** Only `tag` taxonomy is defined, mapped to `tags` in front matter.

**Usage:**
```yaml
---
tags:
  - statistics
  - market-data
---
```

### Site Parameters

```yaml
params:
  description: "Справочные материалы, руководства и статистика TokenBel."
  mainSiteURL: "https://tokenbel.info/"
  dashboardURL: "https://dashboard.tokenbel.info/"
  tokensURL: "https://dashboard.tokenbel.info/tokens/"
  secondMarketURL: "https://dashboard.tokenbel.info/secondhand/"
  sharesURL: "https://dashboard.tokenbel.info/shares/"
  bondsURL: "https://dashboard.tokenbel.info/bonds/"
  repositoryURL: "https://github.com/Red-Panda-Dev/tokenbel-wiki"
```

**Site description:** Used in meta tags and home page.

**External URLs:** Links to related TokenBel services, consumed by:
- `layouts/home.html` — "Полезные ссылки" section
- `layouts/partials/header.html` — Logo link (uses `mainSiteURL`)
- Templates can access via `site.Params.<field>`

### Menus

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

**Main menu:** Defines the primary navigation menu.

| Field | Description |
|-------|-------------|
| `name` | Display text for menu item |
| `pageRef` | Reference to section (must match directory name) |
| `weight` | Sort order (lower = earlier) |

**Template access:** Available via `site.Menus.main` in templates.

**Usage:**
- `layouts/partials/header.html` — Renders main navigation
- `layouts/_default/list.html` — Section navigation

### Caches

```yaml
caches:
  images:
    dir: ":cacheDir/images"
```

**Image cache:** Custom cache directory for Hugo's image processing.

| Field | Value | Description |
|-------|-------|-------------|
| `dir` | `:cacheDir/images` | Cache directory relative to Hugo cache |

**Note:** This is separate from the `.cache/hugo` directory used by `build.sh`.

## Template Access

All configuration values are accessible in Hugo templates:

```go-html-template
{{ site.BaseURL }}          <!-- "https://wiki.tokenbel.info/" -->
{{ site.Title }}           <!-- "Wiki TokenBel" -->
{{ site.Language.Lang }}   <!-- "ru" -->
{{ site.Params.description }} <!-- "Справочные материалы..." -->
{{ site.Menus.main }}      <!-- Main menu items -->
```

## Relationships

* [Content Layer](../content-layer/) — Content that uses this configuration
* [Presentation Layer](../presentation-layer/) — Templates that consume configuration

## Citations

[1] `hugo.yaml` — Complete configuration file
[2] `layouts/partials/head.html:5-10` — Usage of site.Title and site.Params
[3] `layouts/home.html:40-50` — Usage of site.Params external URLs
[4] `layouts/partials/header.html` — Usage of site.Menus.main
[5] `content/_index.md` — Usage of site.Params in front matter
[6] `ARCHITECTURE.md:5` — Architecture context for configuration
