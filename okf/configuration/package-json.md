---
type: Package.json
title: Package.json
description: Node.js dependencies and scripts for TokenBel Wiki build toolchain
---

# Package.json

File: `package.json` — Node.js project configuration for the build toolchain.

## Complete Configuration

```json
{
  "name": "tokenbel-wiki",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "build": "./build.sh",
    "css:build": "NODE_ENV=production npx @tailwindcss/cli -i static/css/input.css -o static/css/output.css && NODE_ENV=production npx @tailwindcss/cli -i static/css/input.css -o static/css/tailwind.min.css --minify",
    "css:watch": "NODE_ENV=production npx @tailwindcss/cli -i static/css/input.css -o static/css/output.css --watch",
    "deploy": "wrangler deploy",
    "deploy:dry-run": "wrangler deploy --dry-run"
  },
  "devDependencies": {
    "@tailwindcss/cli": "4.3.2",
    "@tailwindcss/typography": "0.5.20",
    "tailwindcss": "4.3.3",
    "wrangler": "4.118.0"
  }
}
```

## Project Metadata

```json
{
  "name": "tokenbel-wiki",
  "version": "0.1.0",
  "private": true
}
```

| Field | Value | Description |
|-------|-------|-------------|
| `name` | `tokenbel-wiki` | Project name |
| `version` | `0.1.0` | Project version |
| `private` | `true` | Prevents accidental publishing to npm |

## Scripts

### build

```json
"build": "./build.sh"
```

**Purpose**: Production build for Cloudflare

**Process:**
1. Executes `build.sh` script
2. Downloads pinned Hugo and Node.js
3. Verifies SHA-256 checksums
4. Installs dependencies
5. Builds site with Hugo

**Environment:** Requires Linux x86_64

### css:build

```json
"css:build": "NODE_ENV=production npx @tailwindcss/cli -i static/css/input.css -o static/css/output.css && NODE_ENV=production npx @tailwindcss/cli -i static/css/input.css -o static/css/tailwind.min.css --minify"
```

**Purpose**: Regenerate both Tailwind CSS output files

**Process:**
1. Compile `input.css` → `output.css` (development, unminified)
2. Compile `input.css` → `tailwind.min.css` (production, minified)

**Environment:** `NODE_ENV=production` ensures production-optimized output

**Output files:**
- `static/css/output.css` — Development output
- `static/css/tailwind.min.css` — Production output (actually linked)

### css:watch

```json
"css:watch": "NODE_ENV=production npx @tailwindcss/cli -i static/css/input.css -o static/css/output.css --watch"
```

**Purpose**: Watch mode for CSS development

**Process:**
1. Watch `static/css/input.css` for changes
2. Recompile to `static/css/output.css` on each change
3. Does **not** generate minified output

**Use case:** Development with live CSS reloading

### deploy

```json
"deploy": "wrangler deploy"
```

**Purpose**: Deploy to Cloudflare

**Process:**
1. Authenticates with Cloudflare API
2. Validates configuration
3. Packages `public/` directory
4. Uploads to Cloudflare
5. Activates new version

**Requirements:**
- `CF_API_TOKEN` environment variable or interactive auth
- Valid `wrangler.toml` configuration
- Built `public/` directory

### deploy:dry-run

```json
"deploy:dry-run": "wrangler deploy --dry-run"
```

**Purpose**: Validate deployment without publishing

**Process:**
1. Validates configuration
2. Validates file existence
3. Checks route configuration
4. No actual deployment

**Use case:** CI validation, pre-deployment checks

## Dependencies

```json
"devDependencies": {
  "@tailwindcss/cli": "4.3.2",
  "@tailwindcss/typography": "0.5.20",
  "tailwindcss": "4.3.3",
  "wrangler": "4.118.0"
}
```

### Tailwind CSS Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `@tailwindcss/cli` | 4.3.2 | Tailwind CSS CLI for compilation |
| `@tailwindcss/typography` | 0.5.20 | Typography plugin for prose styling |
| `tailwindcss` | 4.3.3 | Tailwind CSS library |

**Pinned versions:** Ensure reproducible CSS builds across environments.

### Cloudflare Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `wrangler` | 4.118.0 | Cloudflare Workers CLI for deployment |

**Pinned version:** Matches Cloudflare's recommended version for Workers Builds.

## Usage in Makefile

The scripts are called by `Makefile` targets:

```makefile
css-build: dependencies
	@$(DOCKER_RUN) npm run css:build

css-watch: dependencies
	@$(DOCKER_RUN) npm run css:watch

cloudflare-build:
	@npm run build

deploy-dry-run: cloudflare-build
	@npm run deploy:dry-run

deploy: cloudflare-build
	@npm run deploy
```

## Usage in build.sh

The `build.sh` script calls `npm run` commands:

```bash
install_node_dependencies() {
  npm ci
}
```

**Purpose:** Install exact versions from `package-lock.json`.

## Relationships

* [Build System](../build-system/) — Build process that uses these scripts
* [Tailwind Build](../build-system/tailwind-build.md) — CSS compilation details

## Citations

[1] `package.json` — Complete configuration file
[2] `Makefile:40-41` — css-build target calling npm run css:build
[3] `Makefile:43-44` — css-watch target calling npm run css:watch
[4] `Makefile:89-95` — Cloudflare targets calling npm run build/deploy
[5] `build.sh:87-89` — install_node_dependencies using npm ci
[6] `ARCHITECTURE.md:5` — Architecture context for dependencies
