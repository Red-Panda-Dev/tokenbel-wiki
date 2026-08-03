---
type: Dependency Graph
title: Dependency Graph
description: Component dependencies and architectural boundaries in TokenBel Wiki
---

# Dependency Graph

## Layer Dependency Direction

```
┌─────────────────────────────────────────────────────────────────┐
│                      CONTENT LAYER (content/)                      │
│  Markdown + Front Matter + upload: markers                        │
└─────────────────────────────┬───────────────────────────────────┘
                              │ (data contract: front matter)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER (layouts/)                    │
│  Hugo templates + Tailwind CSS + static files                     │
│  Depends on: Content Layer front matter, Site Configuration      │
└─────────────────────────────┬───────────────────────────────────┘
                              │ (templates consume .Params)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SITE BUILD TOOLCHAIN                            │
│  Hugo CLI + Makefile + build.sh                                   │
│  Depends on: Content Layer + Presentation Layer + Configuration  │
└─────────────────────────────┬───────────────────────────────────┘
                              │ (generates public/)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 CLOUDFLARE DEPLOYMENT TARGET                       │
│  Worker with Static Assets (wrangler.toml)                       │
│  Depends on: Site Build Toolchain output (public/)              │
└───────────────────────────────────────────────────────────────────┘
```

## Media Publishing Toolchain (Parallel)

```
┌─────────────────────────────────────────────────────────────────┐
│                   MEDIA PUBLISHING TOOLCHAIN                       │
│  Python CLI (wiki-media) + Cloudflare R2                           │
│  Depends on: .wiki-media/inbox/ images, content/ upload: markers   │
└─────────────────────────────┬───────────────────────────────────┘
                              │ (mutates content/ in place)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CONTENT LAYER (content/)                      │
│  upload: markers rewritten to CDN URLs                             │
└───────────────────────────────────────────────────────────────────┘
```

**Key Insight**: The Media Publishing Toolchain is the **only component** that:
- Mutates source files (`content/` Markdown)
- Requires external credentials (R2)
- Touches external infrastructure (Cloudflare R2)
- Does **not** participate in the Hugo build chain

## Architectural Boundaries

### Content Layer → Presentation Layer
- **Contract**: Front matter fields (title, description, date, lastmod, weight, icon, heroPrimary*, etc.)
- **Direction**: Content provides data, Presentation consumes it
- **Enforcement**: Hugo template rendering, `.Site.Params` access

### Presentation Layer → Build Toolchain
- **Contract**: Static file references, template partials, CSS imports
- **Direction**: Presentation provides templates, Build Toolchain processes them
- **Enforcement**: Hugo's template resolution

### Build Toolchain → Cloudflare Deployment
- **Contract**: Complete `public/` directory with all static assets
- **Direction**: Build Toolchain produces, Cloudflare consumes
- **Enforcement**: `wrangler.toml` `[assets] directory = "./public"`

### Media Publishing → Content Layer
- **Contract**: `upload:<inbox-relative-path>` markers in Markdown
- **Direction**: Media Publishing reads and rewrites Content Layer
- **Enforcement**: `wiki_media/publisher.py` scans and rewrites `upload:` markers

## Cross-Cutting Dependencies

### Site Configuration (hugo.yaml)
- **Consumed by**: Content Layer (menus), Presentation Layer (params), Build Toolchain
- **Provides**: baseURL, locale, menus, params, taxonomies
- **Never consumed by**: Media Publishing Toolchain

### Tailwind CSS Pipeline
- **Source**: `static/css/input.css`
- **Build**: `@tailwindcss/cli` via `npm run css:build`
- **Output**: `static/css/output.css` (development), `static/css/tailwind.min.css` (production)
- **Linked**: Only `tailwind.min.css` is referenced in templates

### Pinned Dependencies
- **Hugo**: 0.164.0 (standard edition) — both Docker and native
- **Node.js**: 24.18.1 (Cloudflare build only)
- **@tailwindcss/cli**: 4.3.2
- **wrangler**: 4.118.0
- **Python**: 3.11+ (Media Publishing only)
- **boto3**: 1.34-2.0 (R2 client)
- **Pillow**: 10-13 (image validation)

## Relationships

* [System Overview](system-overview.md) — High-level architecture context
* [Architectural Invariants](invariants.md) — Rules that enforce these boundaries

## Citations

[1] `ARCHITECTURE.md:2` — Dependency direction diagram and layer descriptions
[2] `hugo.yaml` — Site configuration consumed by multiple layers
[3] `layouts/partials/head.html:1-30` — Template consuming front matter and site params
[4] `wrangler.toml:5-6` — Assets directory configuration
[5] `tools/wiki-media/src/wiki_media/publisher.py` — Media publishing entry point
[6] `build.sh:70-150` — Build toolchain orchestration
[7] `Makefile:1-50` — Local build wrapper with Docker
[8] `package.json:8-12` — Tailwind CSS build scripts
