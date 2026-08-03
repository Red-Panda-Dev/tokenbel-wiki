---
type: Architectural Invariants
title: Architectural Invariants
description: Rules and constraints that must not be violated in TokenBel Wiki
---

# Architectural Invariants

These are the **non-negotiable rules** that define the system's architectural boundaries and constraints.

## Hugo Edition

- **Rule**: Use Hugo **standard** edition, not Extended
- **Rationale**: Tailwind CSS 4 uses plain CSS source; no Sass/SCSS compilation needed
- **Enforcement**: `build.sh` downloads `hugo_${HUGO_VERSION}_linux-amd64.tar.gz` (standard edition)
- **Signals**: Absence of `theme/` directory, `.scss` files, or Dart Sass dependencies

## CSS Pipeline

- **Rule**: Tailwind CSS 4 compiles from single plain-CSS source
- **Rationale**: Keeps Hugo standard edition while preserving reproducible CSS build
- **Enforcement**: `make css-build` regenerates committed static output; `make css-check` detects stale CSS
- **Signals**: `static/css/input.css` (source), `static/css/output.css` (dev), `static/css/tailwind.min.css` (prod)

## Page Dates

- **Rule**: Dates come **only** from front matter, never from Git history
- **Rationale**: Decouples rendered dates from commit history
- **Enforcement**: `enableGitInfo: false` in `hugo.yaml`
- **Signals**: `layouts/partials/page-dates.html` resolves `.Lastmod` from front matter only

## Canonical Domain

- **Rule**: Canonical URL is **always** `https://wiki.tokenbel.info/`
- **Rationale**: SEO consistency across local, staging, and production
- **Enforcement**: `baseURL` in `hugo.yaml` and matching routes in `wrangler.toml`
- **Signals**: `layouts/partials/head.html` emits `.Permalink` for canonical URLs
- **Constraint**: Never use `localhost` or port numbers in canonical URLs or links

## 404 Page Contract

- **Rule**: 404 page must emit `noindex, follow` and literal text `Страница не найдена`
- **Rationale**: Required SEO and copy contracts
- **Enforcement**: `make check` greps `public/404.html` for both strings
- **Signals**: `layouts/404.html` contains the required text; `layouts/partials/head.html` sets robots meta

## Home Page Contract

- **Rule**: Home page must contain `База знаний TokenBel`
- **Rationale**: Required copy for validation
- **Enforcement**: `make check` greps `public/index.html`
- **Signals**: `content/_index.md` title and description

## Section Assembly

- **Rule**: Sections are auto-assembled from `content/` directory structure
- **Rationale**: Single source of truth for navigation
- **Enforcement**: `home.html` and `_default/list.html` iterate `.Sections.ByWeight`
- **Signals**: Menu order declared in `menus.main` in `hugo.yaml`

## Static-Only Deployment

- **Rule**: Deployed unit is **static only** — no Worker script, bindings, or KV
- **Rationale**: Operational simplicity and zero runtime cost
- **Enforcement**: `wrangler.toml` has no `main`, bindings, or secrets; sets `[assets] directory = "./public"`
- **Signals**: `.gitignore` excludes `public/`, `resources/`, `.cache/`, `.wrangler/`

## Pinned Cloudflare Builds

- **Rule**: Cloudflare builds use pinned, checksum-verified tooling
- **Rationale**: Reproducible production builds
- **Enforcement**: `build.sh` requires Linux x86_64, performs SHA-256 checks, pins Hugo 0.164.0 / Node 24.18.1 / Wrangler 4.118.0
- **Signals**: `build.sh` `require_linux_x64` check and checksum verification

## R2 Immutable Objects

- **Rule**: R2 media objects are content-addressed and **immutable**
- **Rationale**: Deduplication, durability, and safe re-publishing
- **Enforcement**: `r2.py` refuses mismatched overwrite, never deletes, always verifies remote SHA-256
- **Signals**: Object key format: `wiki/media/images/<sha[:2]>/<sha><canonical-extension>`

## Upload Marker Contract

- **Rule**: `upload:` markers are **strictly** inbox-relative
- **Rationale**: Safe, local-first media authoring
- **Enforcement**: `images.py` `resolve_inbox_path` rejects absolute/`..`/`~`/URI/symlink
- **Signals**: `.wiki-media/inbox/` is the only valid source directory

## Media Publishing Isolation

- **Rule**: Media Publishing Toolchain runs in separate Python/uv runtime
- **Rationale**: Isolates external-credentialed, repo-mutating tool from static build
- **Enforcement**: `tools/wiki-media/pyproject.toml` has own dependencies, `requires-python >=3.11`
- **Signals**: Media Publishing **never** performs Git commits; `.gitignore` excludes `.wiki-media/`

## No External Themes

- **Rule**: No external Hugo themes or Sass dependencies
- **Rationale**: Keep build reproducible and self-contained
- **Enforcement**: All templates in `layouts/`, all CSS in `static/css/`
- **Signals**: Absence of `theme` directory or theme references in `hugo.yaml`

## Build Output Exclusion

- **Rule**: Build artifacts are **never** committed
- **Rationale**: Generated files should not be versioned
- **Enforcement**: `.gitignore` excludes `public/`, `resources/`, `.cache/`, `.hugo_build.lock`
- **Signals**: These directories are git-ignored and regenerated on each build

## Relationships

* [System Overview](system-overview.md) — Architecture context for these invariants
* [Dependency Graph](dependency-graph.md) — How components interact within these boundaries

## Citations

[1] `ARCHITECTURE.md:5` — Architectural invariants and constraints section
[2] `hugo.yaml:11` — `enableGitInfo: false` configuration
[3] `build.sh:1-10` — Pinned versions and platform requirements
[4] `build.sh:80-110` — SHA-256 checksum verification for Hugo
[5] `build.sh:110-140` — SHA-256 checksum verification for Node.js
[6] `wrangler.toml:5-6` — Static assets configuration without script
[7] `.gitignore` — Excluded build artifact directories
[8] `tools/wiki-media/src/wiki_media/r2.py` — Immutable R2 object handling
[9] `tools/wiki-media/src/wiki_media/images.py` — Inbox-relative path validation
[10] `Makefile:40-50` — CSS freshness checking via `css-check`
[11] `layouts/partials/head.html:10-15` — Canonical URL and robots meta emission
[12] `layouts/404.html` — 404 page with required text
[13] `content/_index.md` — Home page with required text
