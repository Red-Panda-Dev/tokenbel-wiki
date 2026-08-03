---
type: Makefile
title: Makefile
description: Docker-based local development and build wrapper for TokenBel Wiki
---

# Makefile

The `Makefile` provides a **Docker-based** wrapper for local development, building, and validation. It uses the `hugomods/hugo:0.164.0` Docker image to ensure consistent Hugo versions across development environments.

## Docker Configuration

```makefile
HUGO_VERSION ?= 0.164.0
HUGO_IMAGE ?= hugomods/hugo:$(HUGO_VERSION)
PORT ?= 1313
LOCAL_URL ?= http://localhost:$(PORT)/
PYTHON ?= python3

DOCKER_RUN_BASE = docker run --rm \
	--user "$$(id -u):$$(id -g)" \
	--volume "$(CURDIR):/src" \
	--workdir /src

DOCKER_RUN = $(DOCKER_RUN_BASE) $(HUGO_IMAGE)
DOCKER_DEV = $(DOCKER_RUN_BASE) --publish $(PORT):$(PORT) $(HUGO_IMAGE)
```

**Key features:**
- Runs as current user (`--user "$$(id -u):$$(id -g)"`) for file permission consistency
- Mounts current directory as `/src` in container
- Uses Hugo 0.164.0 standard edition via Docker

## Targets

### help

```makefile
help:
	@printf '%s\n' \
		'make dependencies  Install pinned Node.js build dependencies in Docker' \
		'make css-build     Regenerate committed Tailwind output.css and tailwind.min.css' \
		'make css-watch     Watch Tailwind input and refresh output.css' \
		'make dev           Run the live-reloading local server' \
		'make build         Build the production site into public/' \
		'make check         Verify committed CSS and run output checks' \
		... (other targets)
```

Displays all available make targets with descriptions.

### version

```makefile
version:
	@$(DOCKER_RUN) hugo version
```

Prints the Hugo version from the Docker image.

### dependencies

```makefile
dependencies:
	@$(DOCKER_RUN) npm ci --include=optional --os=linux --cpu=x64 --libc=musl
```

Installs Node.js dependencies inside Docker for Tailwind CSS build.

**Options:**
- `--include=optional` — Include optional dependencies
- `--os=linux --cpu=x64 --libc=musl` — Target Linux x64 musl platform (matches Cloudflare environment)

### css-build

```makefile
css-build: dependencies
	@$(DOCKER_RUN) npm run css:build
```

Regenerates both Tailwind CSS output files (`output.css` and `tailwind.min.css`).

**Prerequisite**: `dependencies` target must run first to install Node.js packages.

### css-watch

```makefile
css-watch: dependencies
	@$(DOCKER_RUN) npm run css:watch
```

Watches `static/css/input.css` for changes and regenerates `output.css` (not minified).

**Use case**: Development workflow with live CSS reloading.

### css-check

```makefile
css-check: dependencies
	@$(DOCKER_SHELL) -ec 'output=$$(mktemp); minified=$$(mktemp); ... diff ...'
```

Verifies that committed CSS files match current Tailwind CLI output:

1. Creates temporary files for fresh CLI output
2. Runs Tailwind CLI to generate both outputs
3. Compares against committed files: `static/css/output.css` and `static/css/tailwind.min.css`
4. **Fails** if either file differs, with error message

**Used by**: `make check` target

### dev / serve

```makefile
dev: clean
	@$(DOCKER_DEV) hugo server \
		--buildDrafts \
		--buildFuture \
		--bind 0.0.0.0 \
		--port $(PORT) \
		--baseURL $(LOCAL_URL) \
		--appendPort=false

serve: dev
```

Runs Hugo's live-reloading development server:

- `--buildDrafts` — Render draft pages
- `--buildFuture` — Render pages with future dates
- `--bind 0.0.0.0` — Accessible from network (not just localhost)
- `--port $(PORT)` — Default 1313
- `--baseURL $(LOCAL_URL)` — Local development URL
- `--appendPort=false` — Don't append port to baseURL

**Access**: `http://localhost:1313/`

### build / production

```makefile
build production: clean
	@$(DOCKER_RUN) hugo --gc --minify --environment production
```

Builds the production site into `public/` directory:

- `--gc` — Garbage collect unused files
- `--minify` — Minify output HTML/CSS/JS
- `--environment production` — Set environment to production
- `--cleanDestinationDir` — Clean public/ before build

**Output**: Complete `public/` directory ready for deployment

### check

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

**Comprehensive validation** that runs:

1. `css-check` — Verifies CSS files are up to date
2. `build` — Builds the production site
3. **File existence checks**:
   - `static/css/tailwind.min.css` exists
   - `public/index.html` exists
   - `public/404.html` exists
4. **Content validation**:
   - Home page contains `База знаний TokenBel`
   - 404 page contains `Страница не найдена`
   - 404 page contains `noindex, follow`

**Purpose**: CI-equivalent validation before deployment.

### clean

```makefile
clean:
	@$(DOCKER_CLEAN) -c 'rm -rf /src/public /src/resources /src/.hugo_build.lock /src/.cache'
```

Removes generated Hugo files:
- `public/` — Built site output
- `resources/` — Hugo processing cache
- `.hugo_build.lock` — Hugo build lock file
- `.cache/` — Hugo cache directory

**Note**: Uses root user (`--user 0:0`) to ensure cleanup works regardless of file permissions.

### cloudflare-build

```makefile
cloudflare-build:
	@npm run build
```

Runs the Cloudflare production build script (`build.sh`).

**Note**: This runs `build.sh` natively (not in Docker), so it requires Linux x86_64.

### deploy-dry-run

```makefile
deploy-dry-run: cloudflare-build
	@npm run deploy:dry-run
```

Validates Cloudflare deployment without actually publishing:
1. Runs `cloudflare-build` (which runs `build.sh`)
2. Runs `npm run deploy:dry-run` (which runs `wrangler deploy --dry-run`)

### deploy

```makefile
deploy: cloudflare-build
	@npm run deploy
```

Publishes to Cloudflare:
1. Runs `cloudflare-build` (which runs `build.sh`)
2. Runs `npm run deploy` (which runs `wrangler deploy`)

### Media Publishing Targets

```makefile
media-install:
	@$(PYTHON) -m pip install -e tools/wiki-media

media-publish:
	@$(PYTHON) -m wiki_media publish $(MEDIA_PATH)

media-publish-dry-run:
	@$(PYTHON) -m wiki_media publish $(MEDIA_PATH) --dry-run

media-validate:
	@$(PYTHON) -m wiki_media validate $(MEDIA_PATH)
```

Wrapper targets for the `wiki-media` CLI:

- `media-install` — Installs the wiki-media package in editable mode
- `media-publish` — Publishes images (optional `MEDIA_PATH` argument)
- `media-publish-dry-run` — Dry run of publish (no actual uploads)
- `media-validate` — Validates media markers and images

**Note**: These run natively using `$(PYTHON)` (default: `python3`), not in Docker.

## Relationships

* [Build Script](build-script.md) — Cloudflare production build (called by `cloudflare-build`)
* [Tailwind Build](tailwind-build.md) — CSS compilation (called by `css-build`)
* [Media Publishing](../media-publishing/) — Image publishing toolchain

## Citations

[1] `Makefile:1-15` — Docker configuration and variables
[2] `Makefile:17-30` — Target definitions and help text
[3] `Makefile:32-35` — version target
[4] `Makefile:37-38` — dependencies target
[5] `Makefile:40-41` — css-build target
[6] `Makefile:43-44` — css-watch target
[7] `Makefile:46-60` — css-check target with validation logic
[8] `Makefile:62-70` — dev/serve targets
[9] `Makefile:72-73` — build/production targets
[10] `Makefile:75-82` — check target with all validations
[11] `Makefile:84-87` — clean target
[12] `Makefile:89-110` — Cloudflare and media targets
