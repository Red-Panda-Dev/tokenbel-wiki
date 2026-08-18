SHELL := /bin/sh

HUGO_VERSION ?= 0.164.0
HUGO_IMAGE ?= hugomods/hugo:$(HUGO_VERSION)
PORT ?= 1313
LOCAL_URL ?= http://localhost:$(PORT)/
PYTHON ?= python3
NODE ?= node

DOCKER_RUN_BASE=docker run --rm \
	--user "$$(id -u):$$(id -g)" \
	--volume "$(CURDIR):/src" \
	--workdir /src

DOCKER_RUN := $(DOCKER_RUN_BASE) $(HUGO_IMAGE)
DOCKER_DEV := $(DOCKER_RUN_BASE) --publish $(PORT):$(PORT) $(HUGO_IMAGE)

DOCKER_SHELL := $(DOCKER_RUN_BASE) --entrypoint /bin/sh $(HUGO_IMAGE)

DOCKER_CLEAN=docker run --rm \
	--user 0:0 \
	--volume "$(CURDIR):/src" \
	--workdir /src \
	--entrypoint /bin/sh \
	$(HUGO_IMAGE)

.PHONY: help version dependencies css-build css-watch css-check dev serve build production check clean cloudflare-build deploy deploy-dry-run media-install media-publish media-publish-dry-run media-validate

help:
	@printf '%s\n' \
		'make dependencies  Install pinned Node.js build dependencies in Docker' \
		'make css-build     Regenerate committed Tailwind output.css and tailwind.min.css' \
		'make css-watch     Watch Tailwind input and refresh output.css' \
		'make dev           Run the live-reloading local server' \
		'make build         Build the production site into public/' \
		'make check         Verify committed CSS and run output checks' \
		'make cloudflare-build  Run the pinned Cloudflare production build' \
		'make deploy-dry-run    Validate the Cloudflare deploy without publishing' \
		'make deploy            Publish the Cloudflare Worker and static assets' \
		'make media-install     Install the isolated wiki-media CLI' \
		'make media-publish     Publish upload: images (MEDIA_PATH is optional)' \
		'make media-publish-dry-run  Plan publish without writes' \
		'make media-validate    Validate media markers and images' \
		'make version   Print the pinned Hugo version' \
		'make clean     Remove generated Hugo files'

version:
	@$(DOCKER_RUN) hugo version

dependencies:
	@$(DOCKER_RUN) npm ci --include=optional --os=linux --cpu=x64 --libc=musl

css-build: dependencies
	@$(DOCKER_RUN) npm run css:build

css-watch: dependencies
	@$(DOCKER_RUN) npm run css:watch

css-check: dependencies
	@$(DOCKER_SHELL) -ec 'output=$$(mktemp); minified=$$(mktemp); trap "rm -f $$output $$minified" EXIT; NODE_ENV=production npx @tailwindcss/cli -i static/css/input.css -o $$output >/dev/null; NODE_ENV=production npx @tailwindcss/cli -i static/css/input.css -o $$minified --minify >/dev/null; diff -q static/css/output.css $$output >/dev/null && diff -q static/css/tailwind.min.css $$minified >/dev/null || { printf "%s\\n" "Tailwind output is stale; run make css-build and commit static/css/output.css and static/css/tailwind.min.css." >&2; exit 1; }'

dev: clean
	@$(DOCKER_DEV) hugo server \
		--buildDrafts \
		--buildFuture \
		--bind 0.0.0.0 \
		--port $(PORT) \
		--baseURL $(LOCAL_URL) \
		--appendPort=false

serve: dev

build production: clean
	@$(DOCKER_RUN) hugo --gc --minify --environment production

check: css-check build
	@[ -f static/css/tailwind.min.css ]
	@[ -f public/index.html ]
	@[ -f public/404.html ]
	@[ -f worker.js ]
	@[ -f public/index.md ]
	@[ -f public/llms.txt ]
	@grep -q 'База знаний TokenBel' public/index.html
	@grep -q 'Страница не найдена' public/404.html
	@grep -q 'noindex, follow' public/404.html
	@$(PYTHON) tests/check_seo.py public content
	@$(PYTHON) tests/check_pagination.py public content hugo.yaml
	@$(PYTHON) tests/check_markdown.py public
	@$(NODE) --disable-warning=MODULE_TYPELESS_PACKAGE_JSON tests/check_link_headers.mjs
	@printf '%s\n' 'Hugo build checks passed.'

cloudflare-build:
	@npm run build

deploy-dry-run: cloudflare-build
	@npm run deploy:dry-run

deploy: cloudflare-build
	@npm run deploy

media-install:
	@$(PYTHON) -m pip install -e tools/wiki-media

media-publish:
	@$(PYTHON) -m wiki_media publish $(MEDIA_PATH)

media-publish-dry-run:
	@$(PYTHON) -m wiki_media publish $(MEDIA_PATH) --dry-run

media-validate:
	@$(PYTHON) -m wiki_media validate $(MEDIA_PATH)

clean:
	@$(DOCKER_CLEAN) -c 'rm -rf /src/public /src/resources /src/.hugo_build.lock /src/.cache'
