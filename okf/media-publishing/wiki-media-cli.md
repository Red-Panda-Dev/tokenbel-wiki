---
type: CLI Tool
title: wiki-media CLI
description: Isolated Python CLI for TokenBel Wiki media publishing to Cloudflare R2
---

# wiki-media CLI

An **isolated Python 3.11+ CLI** for publishing images from a local inbox to Cloudflare R2 and atomically rewriting Markdown to reference the CDN URLs. It is the **only component** in the repository that:
- Mutates source files (`content/`)
- Requires external credentials (R2)
- Touches external infrastructure (Cloudflare R2)

## Project Structure

```
tools/wiki-media/
├── .env                    # R2 credentials (git-ignored)
├── .venv/                  # Python virtual environment (git-ignored)
├── AGENTS.md               # Agent operating rules
├── Makefile                # Local make targets
├── README.md               # Canonical documentation
├── pyproject.toml          # Project configuration and dependencies
├── uv.lock                 # Locked dependency versions
├── src/
│   └── wiki_media/
│       ├── __init__.py
│       ├── cli.py          # CLI entry point
│       ├── config.py       # Configuration
│       ├── discovery.py    # Repository root discovery
│       ├── images.py       # Image validation
│       ├── keys.py         # Content-addressed key generation
│       ├── markdown.py     # Markdown parsing and rewriting
│       ├── models.py       # Data models
│       ├── publisher.py    # Main publish command
│       ├── r2.py           # R2 client
│       ├── reporting.py    # JSON report generation
│       └── transaction.py  # Atomic transaction handling
└── tests/
    └── (test files)
```

## Installation

### Using uv (Recommended)

```bash
cd tools/wiki-media
uv sync
uv run python -m wiki_media publish --dry-run
```

### Using pip

```bash
python -m pip install -e tools/wiki-media
wiki-media publish --dry-run
```

**Note**: The CLI automatically discovers the repository root by searching for `.git/`, `hugo.yaml`, and `content/`.

## Makefile Targets

The `tools/wiki-media/Makefile` provides wrapper targets:

```makefile
make help              # Show available targets
make test              # Run pytest
make lint              # Run Ruff linter
make refactor          # Run Ruff fixes and formatting
make publish-dry-run   # Dry run publish
make validate          # Validate media markers
make cleanup           # Clean up unused markers
```

### refactor Target

```makefile
refactor:
	@ruff check --fix --unsafe-fixes src/ tests/
	@ruff format src/ tests/
```

- Applies `ruff check --fix --unsafe-fixes` to `src/` and `tests/`
- Applies `ruff format` to `src/` and `tests/`
- **Before committing**: Review `git diff` to verify changes

## Configuration

### pyproject.toml

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "wiki-media"
version = "0.1.0"
description = "Safe R2 media publisher for TokenBel Wiki"
requires-python = ">=3.11"
dependencies = ["boto3>=1.34,<2", "Pillow>=10,<13"]

[project.optional-dependencies]
test = ["pytest>=8,<10"]
style = ["ruff==0.16.*"]

[project.scripts]
wiki-media = "wiki_media.cli:main"

[tool.ruff]
line-length = 120
target-version = "py312"
fix = true
unsafe-fixes = false
exclude = ["__init__.py"]

[tool.ruff.lint]
select = ["I", "W292", "E4", "E7", "E9", "F", "Q"]
fixable = ["ALL"]
unfixable = []

[tool.ruff.lint.isort]
length-sort = true
known-first-party = ["resolver"]

[tool.ruff.format]
line-ending = "auto"
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
```

**Key settings:**
- Python 3.11+ required
- Dependencies: `boto3` (R2 client), `Pillow` (image validation)
- Optional: `pytest` (tests), `ruff` (linting)
- Entry point: `wiki_media.cli:main` → `wiki-media` command

### Ruff Configuration

- Line length: 120 characters
- Target Python: 3.12
- Select rules: Imports (I), W292, E4, E7, E9, F, Q
- Fix mode: Safe fixes only (unsafe-fixes = false)
- Exclude: `__init__.py` files

## Commands

### publish

```bash
wiki-media publish [content-path] [--dry-run] [--remote] [--verbose] [--json-report report.json]
```

**Purpose**: Publish images from inbox to R2 and rewrite Markdown.

**Arguments:**
- `content-path` (optional): Path to scan for upload: markers. Default: entire `content/`
- `--dry-run`: Plan the publish without actual writes or uploads
- `--remote`: Perform actual R2 uploads (requires credentials)
- `--verbose`: Enable verbose output
- `--json-report report.json`: Write detailed report to JSON file

**Scope options:**
- Entire `content/` directory (default)
- A subtree of `content/`
- A single `index.md` or `_index.md` file

**Behavior:**
1. Discover repository root
2. Resolve scope (content-path argument)
3. Scan Markdown for `upload:` markers
4. Validate each referenced image in `.wiki-media/inbox/`
5. For `--remote`: Upload missing images to R2
6. Verify remote SHA-256 for existing objects
7. Stage Markdown rewrites
8. Atomically promote rewrites to `content/`
9. Create rollback backups in `.wiki-media/run/`

**Note**: Without `--remote`, no network calls are made and no credentials are needed.

### validate

```bash
wiki-media validate [content-path] [--remote]
```

**Purpose**: Validate media markers and images without publishing.

**Arguments:**
- `content-path` (optional): Path to validate. Default: entire `content/`
- `--remote`: Verify remote R2 objects (requires credentials)

**Behavior:**
- Scans for `upload:` markers
- Validates image files exist and are valid
- With `--remote`: Verifies remote objects match local files
- Reports any issues

**Note**: Without `--remote`, no network calls are made.

### cleanup

```bash
wiki-media cleanup [--dry-run]
```

**Purpose**: Remove unused `upload:` markers from Markdown.

**Arguments:**
- `--dry-run`: Report what would be removed without actual changes

**Behavior:**
- Scans entire `content/` for `upload:` markers
- Identifies markers that reference non-existent inbox files
- Removes or reports these markers

**Note**: Always scans entire `content/`, never takes a path argument.

## Credentials

R2 credentials are read from:

1. Environment variables (highest priority)
2. `tools/wiki-media/.env` file (fallback)

### .env File Format

```dotenv
AWS_S3_URL=https://<account-id>.r2.cloudflarestorage.com
AWS_ACCESS_KEY_ID=<r2-access-key-id>
AWS_SECRET_ACCESS_KEY=<r2-secret-access-key>
```

**Important:**
- `AWS_S3_URL` is the **HTTPS S3 API endpoint** for Cloudflare R2
- NOT `https://cdn-wiki.tokenbel.info` (that's the CDN URL)
- `.env` file is git-ignored

### Environment Variable Priority

Exported shell variables take precedence over `.env` file values.

## Relationships

* [R2 Publishing](r2-publishing.md) — Cloudflare R2 immutable object handling
* [Upload Markers](upload-markers.md) — upload: marker syntax and processing

## Citations

[1] `tools/wiki-media/README.md` — Canonical CLI documentation
[2] `tools/wiki-media/pyproject.toml` — Project configuration
[3] `tools/wiki-media/Makefile` — Local make targets
[4] `tools/wiki-media/src/wiki_media/cli.py` — CLI entry point
[5] `tools/wiki-media/src/wiki_media/publisher.py` — Publish command implementation
[6] `tools/wiki-media/src/wiki_media/transaction.py` — Atomic transaction handling
[7] `tools/wiki-media/AGENTS.md` — Agent operating rules
[8] `Makefile:89-110` — Media publishing make targets
