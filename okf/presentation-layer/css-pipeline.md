---
type: CSS Pipeline
title: CSS Pipeline
description: Tailwind CSS 4 build process and committed outputs for TokenBel Wiki
---

# CSS Pipeline

TokenBel Wiki uses **Tailwind CSS 4** with a **pre-build** approach. CSS is compiled to static files before Hugo processes the site, and Hugo simply copies the committed output.

## Pipeline Overview

```
Source (static/css/input.css)
    ↓ (Tailwind CLI)
Development Output (static/css/output.css)
    ↓ (Tailwind CLI --minify)
Production Output (static/css/tailwind.min.css)
    ↓ (Hugo copy)
public/css/tailwind.min.css (served to users)
```

## Source File

File: `static/css/input.css`

**Content:** Plain CSS with Tailwind directives:

```css
@import "tailwindcss";

@theme {
  --font-family-sans: 'Manrope', sans-serif;
  /* Custom theme values */
}

/* Custom semantic classes */
.wiki-card { @apply ... }
.wiki-button-primary { @apply ... }
```

**Key features:**
- Uses `@import "tailwindcss"` for Tailwind v4
- Defines custom theme values
- Uses `@apply` for semantic classes (recommended over inline Tailwind classes)
- No Sass/SCSS — plain CSS only

## Build Commands

### Development Build

```bash
NODE_ENV=production npx @tailwindcss/cli -i static/css/input.css -o static/css/output.css
```

- **Purpose**: Development output with source maps
- **Output**: `static/css/output.css`
- **Used by**: `make css-watch` for live reloading

### Production Build

```bash
NODE_ENV=production npx @tailwindcss/cli -i static/css/input.css -o static/css/tailwind.min.css --minify
```

- **Purpose**: Minified production output
- **Output**: `static/css/tailwind.min.css`
- **Used by**: All templates via `css.html` partial

## Committed Outputs

Both output files are **committed to the repository**:

1. `static/css/output.css` — Development output (retained for reference)
2. `static/css/tailwind.min.css` — Production output (actually linked)

**Rationale**: Ensures reproducible builds without requiring Tailwind CLI at build time.

## Template Integration

File: `layouts/partials/css.html`

**Content:**
```html
<link rel="stylesheet" href="{{ \"css/tailwind.min.css\" | relURL }}">
```

**Key fact**: Only `tailwind.min.css` is linked. `output.css` is retained for:
- Development reference
- `make css-check` validation
- Watch mode (`make css-watch`)

## Makefile Targets

### css-build

```makefile
css-build: dependencies
	@$(DOCKER_RUN) npm run css:build
```

- **Purpose**: Regenerate both committed outputs
- **Dependencies**: Node.js dependencies via `npm ci`
- **Script**: `npm run css:build` (defined in `package.json`)

### css-watch

```makefile
css-watch: dependencies
	@$(DOCKER_RUN) npm run css:watch
```

- **Purpose**: Watch `input.css` and regenerate `output.css` on changes
- **Script**: `npm run css:watch`

### css-check

```makefile
css-check: dependencies
	@$(DOCKER_SHELL) -ec '... diff static/css/output.css ... diff static/css/tailwind.min.css ...'
```

- **Purpose**: Verify committed CSS matches current Tailwind CLI output
- **Behavior**: Compares committed files against fresh CLI builds
- **Fails**: If either file is stale, prints error message
- **Used by**: `make check` (runs before build validation)

## Package.json Scripts

```json
{
  "scripts": {
    "css:build": "NODE_ENV=production npx @tailwindcss/cli -i static/css/input.css -o static/css/output.css && NODE_ENV=production npx @tailwindcss/cli -i static/css/input.css -o static/css/tailwind.min.css --minify",
    "css:watch": "NODE_ENV=production npx @tailwindcss/cli -i static/css/input.css -o static/css/output.css --watch"
  }
}
```

## Dependencies

File: `package.json`

```json
{
  "devDependencies": {
    "@tailwindcss/cli": "4.3.2",
    "@tailwindcss/typography": "0.5.20",
    "tailwindcss": "4.3.3"
  }
}
```

**Pinned versions**: Ensures reproducible CSS builds across environments.

## Visual Reference

The CSS pipeline takes visual inspiration from the main TokenBel application:

- Reference files: `../tbel/src/tbel/static/css/input.css`
- Reference templates: `../tbel/src/tbel/templates/base.html`
- Reference elements: `../tbel/src/tbel/templates/elements/header.html`

**Constraint**: Do not port dashboard components, AlpineJS, or analytics from the reference.

## Custom Semantic Classes

For reusable wiki components, use semantic classes via `@apply` in `input.css`:

```css
.wiki-card {
  @apply p-4 sm:p-6 bg-white rounded-lg shadow-sm;
}

.wiki-button-primary {
  @apply inline-flex items-center rounded-lg px-4 py-2 bg-blue-600 text-white font-semibold;
}
```

**Rule**: Do not form Tailwind class names dynamically in templates.

## Relationships

* [Templates](templates.md) — Templates that link the CSS
* [Partials](partials.md) — Partials that use CSS classes

## Citations

[1] `static/css/input.css` — Tailwind CSS source file
[2] `static/css/output.css` — Development CSS output (committed)
[3] `static/css/tailwind.min.css` — Production CSS output (committed, linked)
[4] `package.json:8-10` — CSS build scripts
[5] `package.json:14-17` — Tailwind CSS dependencies
[6] `Makefile:35-45` — CSS-related make targets
[7] `layouts/partials/css.html` — CSS link partial
[8] `layouts/AGENTS.md:40-45` — CSS pipeline rules
[9] `ARCHITECTURE.md:5` — Architecture context for CSS pipeline
