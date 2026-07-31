SHELL := /bin/sh

HUGO_VERSION ?= 0.164.0
HUGO_IMAGE ?= hugomods/hugo:$(HUGO_VERSION)
PORT ?= 1313
LOCAL_URL ?= http://localhost:$(PORT)/

DOCKER_RUN_BASE = docker run --rm \
	--user "$$(id -u):$$(id -g)" \
	--volume "$(CURDIR):/src" \
	--workdir /src

DOCKER_RUN = $(DOCKER_RUN_BASE) $(HUGO_IMAGE)
DOCKER_DEV = $(DOCKER_RUN_BASE) --publish $(PORT):$(PORT) $(HUGO_IMAGE)

DOCKER_CLEAN = docker run --rm \
	--user 0:0 \
	--volume "$(CURDIR):/src" \
	--workdir /src \
	--entrypoint /bin/sh \
	$(HUGO_IMAGE)

.PHONY: help version dev serve build production check clean cloudflare-build deploy deploy-dry-run

help:
	@printf '%s\n' \
		'make dev       Run the live-reloading local server' \
		'make build     Build the production site into public/' \
		'make check     Build and run basic output checks' \
		'make cloudflare-build  Run the pinned Cloudflare production build' \
		'make deploy-dry-run    Validate the Cloudflare deploy without publishing' \
		'make deploy            Publish the Cloudflare Worker and static assets' \
		'make version   Print the pinned Hugo version' \
		'make clean     Remove generated Hugo files'

version:
	@$(DOCKER_RUN) hugo version

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

check: build
	@test -f public/index.html
	@test -f public/404.html
	@grep -q 'База знаний TokenBel' public/index.html
	@grep -q 'Страница не найдена' public/404.html
	@grep -q 'noindex, follow' public/404.html
	@printf '%s\n' 'Hugo build checks passed.'

cloudflare-build:
	@npm run build

deploy-dry-run: cloudflare-build
	@npm run deploy:dry-run

deploy: cloudflare-build
	@npm run deploy

clean:
	@$(DOCKER_CLEAN) -c 'rm -rf /src/public /src/resources /src/.hugo_build.lock /src/.cache'
