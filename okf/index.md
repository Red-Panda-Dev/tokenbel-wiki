---
okf_version: "0.1"
---

# Knowledge Bundle: TokenBel Wiki

Russian-language static knowledge base for TokenBel, built with Hugo and deployed as Cloudflare Worker with Static Assets.

## Core Domains

* [Architecture](architecture/) — System layers, dependency graph, and architectural invariants
* [Content Layer](content-layer/) — Markdown content organization, front matter contracts, and section structure
* [Presentation Layer](presentation-layer/) — Hugo templates, partials, and Tailwind CSS pipeline
* [Build System](build-system/) — Local Docker builds, pinned Cloudflare builds, and validation
* [Media Publishing](media-publishing/) — Isolated Python CLI for image publishing to Cloudflare R2
* [Deployment](deployment/) — Cloudflare Worker configuration and deployment workflow
* [Configuration](configuration/) — Hugo, Node, and toolchain configuration files

## Quick Reference

| Component | Technology | Purpose |
|-----------|------------|---------|
| Static Site | Hugo 0.164.0 (standard) | Markdown → HTML generation |
| CSS | Tailwind CSS 4 | Styling via committed static files |
| Media | Python 3.11+ CLI | Image publishing to R2/CDN |
| Deployment | Cloudflare Worker | Static asset hosting |
| Runtime | None | Pure static serving |

## Repository Roots

- Repository root: `/home/homer/Documents/Prog/RedPandaDev/tokenbel-wiki`
- Canonical URL: `https://wiki.tokenbel.info/`
- Content root: `content/`
- Layouts root: `layouts/`
- Static files: `static/`
- Tools: `tools/wiki-media/`
