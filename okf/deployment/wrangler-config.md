---
type: Wrangler Configuration
title: Wrangler Config
description: Detailed wrangler.toml configuration for TokenBel Wiki Cloudflare Worker
---

# Wrangler Config

File: `wrangler.toml` — The **complete configuration** for the Cloudflare Worker that serves TokenBel Wiki.

## Full Configuration

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

## Section-by-Section Analysis

### Worker Metadata

```toml
name = "tokenbel-wiki"
compatibility_date = "2026-07-31"
preview_urls = true
```

| Field | Value | Description |
|-------|-------|-------------|
| `name` | `tokenbel-wiki` | Worker name in Cloudflare dashboard |
| `compatibility_date` | `2026-07-31` | Workers runtime version; updates automatically |
| `preview_urls` | `true` | Enable preview deployments for PRs/branches |

**Preview URLs:** When enabled, each commit can have a preview URL like `https://<hash>.tokenbel-wiki.workers.dev`

### Assets Configuration

```toml
[assets]
directory = "./public"
not_found_handling = "404-page"
```

**Critical settings for static site hosting:**

| Field | Value | Description |
|-------|-------|-------------|
| `directory` | `./public` | Path to static files; must match Hugo output |
| `not_found_handling` | `404-page` | Serve custom 404 page with HTTP 404 status |

**not_found_handling options:**
- `"404-page"` — Serve `404.html` with HTTP 404 (used)
- `"null"` — Return HTTP 404 with no body
- `"single-page-app"` — Serve `index.html` for all missing paths (SPA mode)

### Routes Configuration

```toml
[[routes]]
pattern = "wiki.tokenbel.info/*"
zone_name = "tokenbel.info"

[[routes]]
pattern = "wiki.tokenbel.info"
custom_domain = true
```

**Route 1: Wildcard route**
- `pattern = "wiki.tokenbel.info/*"` — Matches all paths under the subdomain
- `zone_name = "tokenbel.info"` — Uses existing zone for tokenbel.info

**Route 2: Root route**
- `pattern = "wiki.tokenbel.info"` — Matches the root domain only
- `custom_domain = true` — Explicitly marks as custom domain

**Why both routes?**
- Wildcard route handles all subpaths (`/guides/`, `/news/`, etc.)
- Root route handles the domain apex (`wiki.tokenbel.info` without trailing slash)
- Both are needed for complete coverage

### Observability Configuration

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

**Logs section:**

| Field | Value | Description |
|-------|-------|-------------|
| `enabled` | `true` | Enable request logging |
| `head_sampling_rate` | `1` | Sample 100% of HEAD requests for logs |
| `invocation_logs` | `true` | Include Worker invocation logs |
| `persist` | `true` | Persist logs to Cloudflare Logpush |

**Traces section:**

| Field | Value | Description |
|-------|-------|-------------|
| `enabled` | `true` | Enable distributed tracing |

**Observability features:**
- Request logs with timestamps, paths, status codes
- Invocation logs showing Worker execution
- Distributed traces for debugging performance
- Log retention via Cloudflare Logpush

### Placement Configuration

```toml
[placement]
mode = "smart"
```

**Placement modes:**

| Mode | Description |
|------|-------------|
| `"smart"` | Cloudflare automatically deploys to optimal locations based on traffic (used) |
| `"off"` | Deploy to a single location (default) |
| `"regions"` | Deploy to specific regions |

**Smart placement benefits:**
- Lower latency for global users
- Automatic scaling based on traffic
- No manual region management needed

## Missing Configuration (By Design)

These fields are **intentionally absent** from `wrangler.toml`:

### No Script Entry Point

```toml
# NOT PRESENT
# main = "src/index.js"
```

**Reason**: This is a **Static Assets Worker** — no JavaScript code executes at runtime. The Worker serves pre-built files from `public/` directory.

### No Bindings

```toml
# NOT PRESENT
# [[kv_namespaces]]
# [[d1_databases]]
# [[r2_buckets]]
```

**Reason**: No external resources are accessed at runtime. All data is in the static files.

### No Variables/Secrets

```toml
# NOT PRESENT
# [vars]
# [secrets]
```

**Reason**: No runtime configuration needed. All configuration is build-time via Hugo.

### No Triggers

```toml
# NOT PRESENT
# [[triggers]]
```

**Reason**: No scheduled or event-based triggers. Worker responds to HTTP requests only.

## Validation

The configuration is validated by:

1. **wrangler validate** — Checks TOML syntax and field validity
2. **wrangler deploy --dry-run** — Validates complete deployment configuration
3. **Cloudflare dashboard** — Visual validation of Worker settings

## Relationships

* [Cloudflare Worker](cloudflare-worker.md) — Runtime behavior of the configured Worker
* [Build System](../build-system/) — Build process that generates the public/ directory

## Citations

[1] `wrangler.toml` — Complete configuration file
[2] `package.json:7` — deploy script using wrangler
[3] `package.json:6` — deploy:dry-run script
[4] `Makefile:91-95` — deploy and deploy-dry-run targets
[5] `docs/deployment.md` — Deployment documentation
[6] `ARCHITECTURE.md:5` — Architecture context for deployment
