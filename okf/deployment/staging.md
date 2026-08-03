---
type: Staging Workflow
title: Staging and Production
description: Staging workflow, production deployment, and rollback procedures for TokenBel Wiki
---

# Staging and Production

Deployment workflow for TokenBel Wiki, including staging validation and production cutover.

## Deployment Environments

### Local Development

**Command:** `make dev` or `make serve`

**Process:**
1. Clean existing `public/` directory
2. Run Hugo server in Docker with:
   - Live reloading
   - Draft and future content
   - Port 1313
   - Base URL: `http://localhost:1313/`

**Access:** `http://localhost:1313/`

**Use case:** Content authoring, template development, CSS changes

### Preview Deployments

**Enabled by:** `preview_urls = true` in `wrangler.toml`

**Trigger:** Push to any branch (except main)

**Process:**
1. Cloudflare Workers Builds detects push
2. Runs `npm run build` (which runs `build.sh`)
3. Deploys to preview URL
4. Preview URL: `https://<branch-hash>.tokenbel-wiki.workers.dev`

**Use case:** Review changes before merging to main

**Note:** Preview deployments are automatic and temporary. They are deleted after a period of inactivity.

### Production Deployment

**Trigger:** Push to `main` branch

**Process:**
1. Cloudflare Workers Builds detects push to main
2. Runs `npm run build` (which runs `build.sh`)
3. Deploys to production
4. Routes traffic from `wiki.tokenbel.info` to new version

**Access:** `https://wiki.tokenbel.info/`

## Deployment Scripts

### package.json Scripts

```json
{
  "scripts": {
    "build": "./build.sh",
    "deploy": "wrangler deploy",
    "deploy:dry-run": "wrangler deploy --dry-run"
  }
}
```

### build Script

Runs the complete production build:
1. Verifies Linux x86_64 platform
2. Downloads and verifies Hugo 0.164.0
3. Downloads and verifies Node.js 24.18.1
4. Installs Node.js dependencies (`npm ci`)
5. Logs versions
6. Builds site with Hugo (`--gc --minify --cleanDestinationDir --environment production`)

### deploy Script

Runs `wrangler deploy` to publish the built `public/` directory to Cloudflare.

**Process:**
1. Authenticates with Cloudflare API (using `CF_API_TOKEN` or interactive auth)
2. Validates `wrangler.toml` configuration
3. Packages `public/` directory
4. Uploads to Cloudflare
5. Activates new version

### deploy:dry-run Script

Runs `wrangler deploy --dry-run` to validate without publishing.

**Checks:**
- Configuration validity
- File existence
- Route configuration
- No actual deployment

## Makefile Targets

### cloudflare-build

```makefile
cloudflare-build:
	@npm run build
```

Runs the production build script (`build.sh`).

**Note:** Requires Linux x86_64 (enforced by `build.sh`).

### deploy-dry-run

```makefile
deploy-dry-run: cloudflare-build
	@npm run deploy:dry-run
```

Validates complete deployment:
1. Runs `cloudflare-build` (production build)
2. Runs `npm run deploy:dry-run` (wrangler validation)

**Use case:** CI validation, local testing before deployment

### deploy

```makefile
deploy: cloudflare-build
	@npm run deploy
```

Full production deployment:
1. Runs `cloudflare-build` (production build)
2. Runs `npm run deploy` (wrangler deploy)

**Use case:** Manual production deployment

## Rollback Procedures

### Automatic Rollback

Cloudflare Workers supports **automatic rollback** to the previous version if a deployment fails health checks.

**Configuration:** Not explicitly configured — uses Cloudflare defaults.

### Manual Rollback

**Option 1: Via Cloudflare Dashboard**
1. Go to Cloudflare Dashboard → Workers & Pages
2. Select `tokenbel-wiki` Worker
3. Go to Deployments
4. Find the previous successful version
5. Click "Roll back" or "Promote"

**Option 2: Via Wrangler CLI**
```bash
# List deployments
wrangler deployments list

# Roll back to previous version
wrangler rollback --message "Rolling back to previous version"
```

**Option 3: Revert Git Commit**
1. Identify the problematic commit
2. Revert it: `git revert <commit-hash>`
3. Push to main: `git push origin main`
4. Cloudflare automatically deploys the reverted commit

## Validation Checks

### make check

```makefile
check: css-check build
	@test -f static/css/tailwind.min.css
	@test -f public/index.html
	@test -f public/404.html
	@grep -q 'База знаний TokenBel' public/index.html
	@grep -q 'Страница не найдена' public/404.html
	@grep -q 'noindex, follow' public/404.html
	@printf '%s\n' 'Hugo build checks passed.'
```

**Checks:**
1. CSS files are up to date (`css-check`)
2. Site builds successfully (`build`)
3. Required files exist
4. Home page contains required text
5. 404 page contains required text and meta

**Use case:** CI validation, pre-deployment checks

### make css-check

Verifies that committed CSS files match current Tailwind CLI output.

**Fails if:** Either `output.css` or `tailwind.min.css` is stale.

## Staging Workflow

### Step 1: Create Feature Branch

```bash
git checkout -b feature/new-article
```

### Step 2: Make Changes

- Add new article to `content/`
- Update section `_index.md` if needed
- Add images to `.wiki-media/inbox/` and publish with `make media-publish`

### Step 3: Validate Locally

```bash
make css-build
make check
make dev
```

### Step 4: Commit and Push

```bash
git add .
git commit -m "Add new article"
git push origin feature/new-article
```

### Step 5: Review Preview Deployment

1. Wait for Cloudflare Workers Builds to complete
2. Visit preview URL (shown in Cloudflare dashboard)
3. Review changes

### Step 6: Merge to Main

```bash
git checkout main
git merge feature/new-article
git push origin main
```

### Step 7: Production Deployment

1. Cloudflare Workers Builds automatically deploys
2. Changes go live at `https://wiki.tokenbel.info/`

## Relationships

* [Cloudflare Worker](cloudflare-worker.md) — Runtime configuration
* [Wrangler Config](wrangler-config.md) — Deployment configuration
* [Build System](../build-system/) — Build process for deployment

## Citations

[1] `wrangler.toml:3` — preview_urls = true enables preview deployments
[2] `package.json:5-7` — Build and deploy scripts
[3] `build.sh` — Production build script
[4] `Makefile:75-82` — check target with all validations
[5] `Makefile:89-95` — Cloudflare build and deploy targets
[6] `docs/deployment.md` — Complete deployment runbook
[7] `ARCHITECTURE.md:5` — Architecture context for deployment
