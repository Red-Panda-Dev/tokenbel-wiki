---
type: Cloudflare Worker
title: Cloudflare Worker
description: TokenBel Wiki Cloudflare Worker configuration and runtime behavior
---

# Cloudflare Worker

TokenBel Wiki is deployed as a **Cloudflare Worker with Static Assets** — a pure static hosting solution with no runtime code execution.

## Worker Type

**Static Assets Worker** — A Worker that serves pre-built static files without executing any JavaScript code.

**Key characteristics:**
- No `main` field in `wrangler.toml` (no script to execute)
- No `bindings` or `kv_namespaces` (no external resources)
- No runtime processing — pure static file serving
- Zero runtime cost (requests served from edge cache)

## Configuration File

File: `wrangler.toml`

```toml
name = "tokenbel-wiki"
compatibility_date = "2026-07-31"
preview_urls = true

[assets]
directory = "./public"
not_found_handling = "404-page"

[[routes]]
pattern = "wiki.tokenbel.info/*"
zone_name = "tokenbel.info"

[[routes]]
pattern = "wiki.tokenbel.info"
custom_domain = true

[observability]
[observability.logs]
enabled = true
head_sampling_rate = 1
invocation_logs = true
persist = true

[observability.traces]
enabled = true

[placement]
mode = "smart"
```

## Configuration Breakdown

### Basic Settings

| Field | Value | Purpose |
|-------|-------|---------|
| `name` | `tokenbel-wiki` | Worker name |
| `compatibility_date` | `2026-07-31` | Workers runtime compatibility date |
| `preview_urls` | `true` | Enable preview deployments |

### Assets Configuration

```toml
[assets]
directory = "./public"
not_found_handling = "404-page"
```

| Field | Value | Purpose |
|-------|-------|---------|
| `directory` | `./public` | Root directory of static files to serve |
| `not_found_handling` | `404-page` | Serve `404.html` with HTTP 404 status for missing paths |

**Behavior:**
- Requests are resolved against files in `public/`
- If file exists: Serve with HTTP 200
- If file doesn't exist: Serve `public/404.html` with HTTP 404
- The `404.html` file must exist in `public/`

### Routes Configuration

```toml
[[routes]]
pattern = "wiki.tokenbel.info/*"
zone_name = "tokenbel.info"

[[routes]]
pattern = "wiki.tokenbel.info"
custom_domain = true
```

**Route 1:** `wiki.tokenbel.info/*`
- Pattern: All paths under `wiki.tokenbel.info`
- Zone: `tokenbel.info` (existing Cloudflare zone)

**Route 2:** `wiki.tokenbel.info`
- Pattern: Root domain only
- Custom domain: Explicitly marked as custom domain

**Result:** Both routes point to the same Worker, handling all requests for `wiki.tokenbel.info`.

### Observability

```toml
[observability]
[observability.logs]
enabled = true
head_sampling_rate = 1
invocation_logs = true
persist = true

[observability.traces]
enabled = true
```

**Logs configuration:**
- `enabled = true` — Enable request logging
- `head_sampling_rate = 1` — Sample 100% of requests for head-based logs
- `invocation_logs = true` — Include invocation logs
- `persist = true` — Persist logs to Cloudflare Logpush

**Traces configuration:**
- `enabled = true` — Enable distributed tracing

### Placement

```toml
[placement]
mode = "smart"
```

**Smart placement:** Cloudflare automatically deploys the Worker to optimal locations worldwide based on traffic patterns.

## Request Flow

### Step 1: Request Receipt

User requests: `https://wiki.tokenbel.info/guides/getting-started`

Cloudflare edge receives the request and routes it to the `tokenbel-wiki` Worker.

### Step 2: Static Asset Resolution

Worker resolves the path against the `./public` directory:

1. Normalize path: `/guides/getting-started` → `public/guides/getting-started/index.html`
2. Check if file exists in `public/`
3. If exists: Serve file with HTTP 200

### Step 3: 404 Handling

If the file doesn't exist:

1. Look for `public/404.html`
2. If exists: Serve `404.html` with HTTP 404 status
3. The response includes the content of `404.html` but with HTTP 404 status code

### Step 4: Response Headers

All responses include:
- Standard HTTP headers
- Cache headers (configurable)
- Security headers (default Cloudflare)

**Special headers for 404:**
- `noindex, follow` robots meta tag (from `layouts/partials/head.html`)
- HTTP 404 status code (from `not_found_handling = "404-page"`)

## Build and Deploy Process

### Local Build

```bash
# Using Makefile (Docker)
make build

# Or directly
./build.sh
```

**Output:** `public/` directory with all static files.

### Cloudflare Build

Cloudflare Workers Builds runs `build.sh` automatically:

1. Check out repository
2. Run `./build.sh` (which runs `npm run build`)
3. Deploy `public/` directory

**Environment:** Linux x86_64 (required by `build.sh`)

### Package.json Scripts

```json
{
  "scripts": {
    "build": "./build.sh",
    "deploy": "wrangler deploy",
    "deploy:dry-run": "wrangler deploy --dry-run"
  }
}
```

**Commands:**
- `npm run build` — Run `build.sh` (Cloudflare build)
- `npm run deploy` — Deploy to Cloudflare (wrangler deploy)
- `npm run deploy:dry-run` — Validate deployment without publishing

## Relationships

* [Wrangler Config](wrangler-config.md) — Detailed wrangler.toml configuration
* [Build System](../build-system/) — Build process that generates public/

## Citations

[1] `wrangler.toml` — Complete Cloudflare Worker configuration
[2] `package.json:5-7` — Build and deploy scripts
[3] `build.sh` — Production build script
[4] `Makefile:89-95` — Cloudflare build and deploy targets
[5] `layouts/404.html` — 404 page content
[6] `layouts/partials/head.html:10-15` — Robots meta for 404 pages
[7] `ARCHITECTURE.md:5` — Architecture context for deployment
[8] `docs/deployment.md` — Deployment runbook
