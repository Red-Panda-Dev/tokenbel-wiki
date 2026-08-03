---
type: Tailwind Build
title: Tailwind Build
description: CSS compilation workflow for TokenBel Wiki
---

# Tailwind Build

The Tailwind CSS 4 compilation workflow that generates static CSS files committed to the repository.

## Build Process

Tailwind CSS 4 uses a **pre-build** approach where CSS is compiled **before** Hugo processes the site. Hugo simply copies the committed static files to the `public/` directory.

### Development Build

Command: `npm run css:build`

```json
{
  "css:build": "NODE_ENV=production npx @tailwindcss/cli -i static/css/input.css -o static/css/output.css && NODE_ENV=production npx @tailwindcss/cli -i static/css/input.css -o static/css/tailwind.min.css --minify"
}
```

**Process:**
1. Compile `static/css/input.css` → `static/css/output.css` (development, unminified)
2. Compile `static/css/input.css` → `static/css/tailwind.min.css` (production, minified)

**Environment**: `NODE_ENV=production` ensures production-optimized output

### Watch Mode

Command: `npm run css:watch`

```json
{
  "css:watch": "NODE_ENV=production npx @tailwindcss/cli -i static/css/input.css -o static/css/output.css --watch"
}
```

**Process:**
- Watches `static/css/input.css` for changes
- Recompiles to `static/css/output.css` on each change
- Does **not** generate minified output
- Ideal for development with live reloading

## Committed Outputs

Both generated files are **committed to the repository**:

### static/css/output.css

- **Purpose**: Development reference output
- **Minified**: No
- **Used by**: `make css-check` for validation
- **Linked in templates**: No (not referenced by any template)

### static/css/tailwind.min.css

- **Purpose**: Production minified output
- **Minified**: Yes
- **Used by**: All templates via `layouts/partials/css.html`
- **Linked in templates**: Yes (only CSS file actually served)

## Validation

The `make css-check` target verifies that committed CSS files match the current Tailwind CLI output:

```bash
# Inside css-check target
output=$$(mktemp)
minified=$$(mktemp)
NODE_ENV=production npx @tailwindcss/cli -i static/css/input.css -o $$output >/dev/null
NODE_ENV=production npx @tailwindcss/cli -i static/css/input.css -o $$minified --minify >/dev/null
diff -q static/css/output.css $$output >/dev/null && diff -q static/css/tailwind.min.css $$minified >/dev/null
```

**Behavior:**
- Creates temporary files for fresh CLI output
- Runs both development and production builds
- Compares against committed files using `diff -q`
- **Fails** if either file differs
- **Error message**: "Tailwind output is stale; run make css-build and commit static/css/output.css and static/css/tailwind.min.css."

## Source File Structure

File: `static/css/input.css`

```css
@import "tailwindcss";

@theme {
  --font-family-sans: 'Manrope', sans-serif;
  /* Custom theme values */
}

/* Custom semantic classes */
.wiki-card { @apply ... }
.wiki-button-primary { @apply ... }
.wiki-button-secondary { @apply ... }
.active-a { @apply ... }
.eyebrow { @apply ... }
```

**Key features:**
- `@import "tailwindcss"` — Tailwind CSS v4 import
- `@theme` — Custom theme configuration
- `@apply` — Semantic class definitions (recommended over inline classes)

## Custom Theme Configuration

The `@theme` directive defines custom design tokens:

```css
@theme {
  --font-family-sans: 'Manrope', sans-serif;
  /* Add other custom tokens as needed */
}
```

**Purpose**: Override Tailwind defaults with project-specific values.

## Semantic Classes

For reusable wiki components, the project uses **semantic classes** defined via `@apply`:

```css
/* Card styling */
.wiki-card {
  @apply p-4 sm:p-6 bg-white rounded-lg shadow-sm;
}

/* Primary button */
.wiki-button-primary {
  @apply inline-flex items-center rounded-lg px-4 py-2 bg-blue-600 text-white font-semibold hover:bg-blue-700 transition;
}

/* Secondary button */
.wiki-button-secondary {
  @apply inline-flex items-center rounded-lg px-4 py-2 bg-gray-200 text-black font-semibold hover:bg-gray-300 transition;
}

/* Active link styling */
.active-a {
  @apply text-blue-600 hover:text-blue-800 underline underline-offset-2;
}

/* Eyebrow text (small label above heading) */
.eyebrow {
  @apply text-sm font-semibold text-gray-500 tracking-wide uppercase;
}
```

**Rule**: Use semantic classes for repeated patterns; use inline Tailwind classes for one-off styling.

**Constraint**: Do **not** form Tailwind class names dynamically in templates.

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

**Pinned versions:**
- `@tailwindcss/cli`: 4.3.2 — Tailwind CSS CLI
- `@tailwindcss/typography`: 0.5.20 — Typography plugin
- `tailwindcss`: 4.3.3 — Tailwind CSS library

## Relationships

* [Makefile](makefile.md) — Build targets that call CSS compilation
* [Build Script](build-script.md) — Production build that includes CSS compilation

## Citations

[1] `package.json:8-9` — css:build script definition
[2] `package.json:10` — css:watch script definition
[3] `package.json:14-17` — Tailwind CSS dependencies
[4] `static/css/input.css` — Tailwind CSS source
[5] `static/css/output.css` — Development output (committed)
[6] `static/css/tailwind.min.css` — Production output (committed)
[7] `Makefile:46-60` — css-check validation logic
[8] `Makefile:40-41` — css-build target
[9] `Makefile:43-44` — css-watch target
[10] `layouts/partials/css.html` — CSS link partial (references tailwind.min.css only)
