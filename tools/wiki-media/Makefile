#!make

SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c

UV ?= uv

.PHONY: help install install-style lint refactor test publish publish-dry-run validate cleanup
.DEFAULT_GOAL := help

help: ## Show available wiki-media commands
	@echo "Available commands:"
	@echo ""
	@echo "Setup and quality:"
	@echo "  install                 Create/sync the runtime environment with uv"
	@echo "  install-style           Install the Ruff style extra"
	@echo "  lint                    Check Python formatting and lint rules without changes"
	@echo "  refactor                Apply Ruff fixes (including unsafe fixes) and format Python code"
	@echo "  test                    Install test dependencies and run pytest"
	@echo ""
	@echo "Wiki media:"
	@echo "  publish                 Publish upload: markers; MEDIA_PATH is optional"
	@echo "  publish-dry-run         Plan a publish without writes; MEDIA_PATH is optional"
	@echo "  validate                Validate markers and images; MEDIA_PATH is optional"
	@echo "  cleanup                 Remove unreferenced inbox files; add DRY_RUN=--dry-run to preview"
	@echo ""
	@echo "Examples:"
	@echo "  make refactor"
	@echo "  make lint"
	@echo "  make publish-dry-run MEDIA_PATH=content/guides"
	@echo "  make publish MEDIA_PATH=content/guides/example/index.md"

install: ## Create/sync runtime dependencies
	$(UV) sync

install-style: ## Install Ruff style tooling
	$(UV) sync --extra style

lint: install-style ## Check formatting and lint rules without modifying source
	$(UV) run ruff format --check src/ tests/
	$(UV) run ruff check src/ tests/

refactor: install-style ## Fix imports/lint issues and format Python source
	$(UV) run ruff format src/ tests/
	$(UV) run ruff check --fix --unsafe-fixes src/ tests/
	$(UV) run ruff format src/ tests/

test: ## Install test tooling and run the test suite
	$(UV) sync --extra test
	$(UV) run pytest

publish: ## Publish media for all content or MEDIA_PATH
	$(UV) run python -m wiki_media publish $(MEDIA_PATH)

publish-dry-run: ## Show the immutable publish plan without writes
	$(UV) run python -m wiki_media publish $(MEDIA_PATH) --dry-run

validate: ## Validate all content or MEDIA_PATH
	$(UV) run python -m wiki_media validate $(MEDIA_PATH)

cleanup: ## Remove unreferenced inbox files; DRY_RUN=--dry-run previews only
	$(UV) run python -m wiki_media cleanup $(DRY_RUN)
