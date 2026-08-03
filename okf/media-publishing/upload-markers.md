---
type: Upload Marker Syntax
title: Upload Markers
description: upload: marker syntax and authoring workflow for TokenBel Wiki images
---

# Upload Markers

The **upload:** marker syntax used in Markdown to reference images that will be published to Cloudflare R2 and rewritten to CDN URLs.

## Syntax

### Basic Syntax

```markdown
![Alt text](upload:<inbox-relative-path>)
```

**Components:**
- `![Alt text]` — Standard Markdown image syntax
- `upload:` — Marker prefix (required)
- `<inbox-relative-path>` — Path relative to `.wiki-media/inbox/`

### With Title Attribute

```markdown
![Alt text](upload:<inbox-relative-path> "Title")
```

The title attribute is preserved during rewriting.

### HTML Syntax

```markdown
<img src="upload:<inbox-relative-path>" alt="Alt text">
```

Standard HTML image tag with `upload:` in the `src` attribute.

## Path Rules

### Valid Paths

**Must be:**
- Relative to `.wiki-media/inbox/`
- Use forward slashes (`/`)
- Use kebab-case or lowercase
- Include file extension

**Examples:**
```markdown
![График](upload:statistics/trading-volume.png)
![Логотип](upload:about/logo.svg)
![Диаграмма](upload:guides/flowchart.png)
```

### Invalid Paths

**Must NOT be:**
- Absolute paths: `upload:/absolute/path.png` ❌
- Parent references: `upload:../images/photo.png` ❌
- Home directory: `upload:~/images/photo.png` ❌
- URIs: `upload:https://example.com/image.png` ❌
- Symlinks: `upload:../../symlink.png` ❌

**Validation**: `images.py:resolve_inbox_path()` rejects all invalid patterns.

## Authoring Workflow

### Step 1: Place Image in Inbox

```bash
# Create inbox directory structure
mkdir -p .wiki-media/inbox/statistics

# Copy image to inbox
cp trading-volume.png .wiki-media/inbox/statistics/
```

**Inbox location**: `.wiki-media/inbox/` (git-ignored)

### Step 2: Reference in Markdown

```markdown
---
title: "Market Statistics"
date: 2025-01-04
---

Here is the trading volume chart:

![Trading Volume](upload:statistics/trading-volume.png)

With a title:

![Volume Trend](upload:statistics/trading-volume.png "Source: TokenBel")
```

**File location**: `content/statistics/market-overview/index.md`

### Step 3: Validate

```bash
# Validate markers and images
make media-validate MEDIA_PATH=content/statistics

# Or directly
python -m wiki_media validate content/statistics
```

**Checks:**
- All `upload:` markers reference existing inbox files
- All images are valid (format, size)
- No invalid path patterns

### Step 4: Dry Run

```bash
# Dry run to see what would be published
make media-publish-dry-run MEDIA_PATH=content/statistics

# Or directly
python -m wiki_media publish content/statistics --dry-run
```

**Output:**
- List of images to be uploaded
- List of Markdown files to be rewritten
- CDN URLs that would be generated
- No actual uploads or file modifications

### Step 5: Publish

```bash
# Actual publish (requires R2 credentials)
make media-publish MEDIA_PATH=content/statistics

# Or directly
python -m wiki_media publish content/statistics --remote
```

**Process:**
1. Upload images to R2 (if not already uploaded with matching content)
2. Verify remote SHA-256
3. Atomically rewrite Markdown files
4. Create rollback backups

### Step 6: Commit Changes

```bash
# Review changes
git diff content/

# Commit the rewritten Markdown
git add content/
git commit -m "Publish images for statistics section"
```

**Important**: The `wiki-media` CLI does **not** commit changes to Git.

## CDN URL Format

After publishing, `upload:` markers are replaced with CDN URLs:

**Before:**
```markdown
![Trading Volume](upload:statistics/trading-volume.png)
```

**After:**
```markdown
![Trading Volume](https://cdn-wiki.tokenbel.info/wiki/media/images/ab/cdef1234567890...png)
```

**CDN base**: `https://cdn-wiki.tokenbel.info/`
**Object prefix**: `wiki/media/images/`
**Object key**: Content-addressed (SHA-256 based)

## Rollback

If something goes wrong:

1. **Automatic rollback**: Transaction backups are in `.wiki-media/run/<timestamp>/backups/`
2. **Manual rollback**: Restore from Git (since changes were committed)
3. **Never re-upload**: Existing R2 objects are never overwritten

## Cleanup

To find and remove unused upload: markers:

```bash
# Dry run first
make media-cleanup DRY_RUN=--dry-run

# Or directly
python -m wiki_media cleanup --dry-run

# Actual cleanup
python -m wiki_media cleanup
```

**Behavior:**
- Scans entire `content/` for `upload:` markers
- Identifies markers referencing non-existent inbox files
- Reports or removes these markers

## Relationships

* [wiki-media CLI](wiki-media-cli.md) — CLI that processes upload: markers
* [R2 Publishing](r2-publishing.md) — R2 upload and CDN URL generation

## Citations

[1] `tools/wiki-media/README.md:20-35` — Authoring workflow documentation
[2] `tools/wiki-media/README.md:15-20` — upload: syntax examples
[3] `tools/wiki-media/src/wiki_media/markdown.py` — Marker parsing and rewriting
[4] `tools/wiki-media/src/wiki_media/images.py:resolve_inbox_path` — Path validation
[5] `tools/wiki-media/src/wiki_media/keys.py` — CDN URL generation
[6] `tools/wiki-media/src/wiki_media/publisher.py` — Publish orchestration
[7] `content/AGENTS.md:30-35` — Rules for new images
[8] `Makefile:89-110` — Media publishing make targets
