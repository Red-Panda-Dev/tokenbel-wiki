---
type: Article Structure
title: Article Structure
description: How articles are organized as leaf bundles in TokenBel Wiki
---

# Article Structure

Articles in TokenBel Wiki use the **leaf bundle** pattern: each article is a directory containing an `index.md` file and optionally other resources.

## Leaf Bundle Pattern

```
content/<section>/<slug>/
├── index.md          # Article content with front matter
└── (other files)     # NOT RECOMMENDED - use upload: for images
```

**Rule**: Do not use article bundles with local images. All images must go through the `wiki-media` toolchain.

## Example Structure

```
content/news/lenta-sobytii-i-mcp-24062026/
└── index.md

content/statistics/statistika-rynka-tokenov-belarusi/
└── index.md
```

## Article Naming Convention

Article directories use **kebab-case** with descriptive names, often including dates:

```
content/news/daidzest-izmenenii-v-proekte-18122025-23122025/
content/news/depozity-i-kalkuliatory-10072026/
content/statistics/statistika-rynka-tokenov-belarusi/
```

**Pattern**: `<descriptive-name>-<date>` for news, `<descriptive-name>` for evergreen content

## Content Migration

The repository was migrated from BookStack. Key migration rules:

1. **Clean migration**: No `url`, `aliases`, or legacy BookStack metadata in `content/`
2. **Image references**: Old images use absolute CDN URLs: `https://cdn-wiki.tokenbel.info/wiki/assets/...`
3. **Artifacts**: Migration artifacts are git-ignored; only clean Hugo content is committed
4. **No legacy addresses**: No BookStack-style URLs or redirects

## Creating New Articles

To create a new article:

1. Use the archetype template:
   ```bash
   hugo new news/my-new-article/index.md
   ```

2. Or create manually:
   ```bash
   mkdir -p content/news/my-new-article
   touch content/news/my-new-article/index.md
   ```

3. Add front matter (see [Front Matter](front-matter.md)):
   ```yaml
   ---
   title: "My Article"
   description: "Article description"
   date: 2025-01-04
   ---
   ```

4. For images:
   - Place image in `.wiki-media/inbox/<path>/<filename>`
   - Reference with `upload:<inbox-relative-path>` in Markdown
   - Run `make media-publish` to publish and rewrite

## Article Content Format

Articles use standard Markdown with Hugo shortcodes and front matter. The content is rendered by:

- `layouts/_default/single.html` — Article page template
- `layouts/_markup/render-table.html` — Custom table rendering

## Special Front Matter for Articles

Articles in the `news` section typically include dates:

```yaml
---
title: "News Article"
date: 2025-01-04
lastmod: 2025-01-04
tags:
  - news
  - update
---
```

Articles can be excluded from the "Recent" block:

```yaml
---
title: "Permanent Page"
excludeFromRecent: true
---
```

## Relationships

* [Sections](sections.md) — How articles fit into the section structure
* [Front Matter](front-matter.md) — Required and optional fields for articles

## Citations

[1] `archetypes/default.md` — Hugo new command template
[2] `content/news/*/` — Example article directory structures
[3] `content/statistics/*/` — Example article directory structures
[4] `content/AGENTS.md:20-25` — Rules for creating new articles
[5] `layouts/_default/single.html` — Article page template
[6] `tools/wiki-media/README.md:20-30` — Image upload workflow
[7] `Makefile:60-65` — media-publish target
