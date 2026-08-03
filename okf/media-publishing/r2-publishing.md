---
type: R2 Publishing
title: R2 Publishing
description: Cloudflare R2 immutable object publishing for TokenBel Wiki media
---

# R2 Publishing

The **immutable object publishing** workflow that uploads images to Cloudflare R2 with content-addressed keys and verifies integrity via SHA-256 checksums.

## R2 Configuration

### Fixed Configuration

```python
# From tools/wiki-media/src/wiki_media/config.py
BUCKET_NAME = "tokenbel-wiki"
PREFIX = "wiki/media/images"
CDN_BASE = "https://cdn-wiki.tokenbel.info"
```

**Immutable settings:**
- **Bucket**: Always `tokenbel-wiki`
- **Prefix**: Always `wiki/media/images`
- **CDN**: Always `https://cdn-wiki.tokenbel.info`

### Object Key Format

```
wiki/media/images/<sha[:2]>/<sha><canonical-extension>
```

**Components:**
- `<sha>`: SHA-256 hash of the image file content
- `<sha[:2]>`: First 2 characters of the SHA-256 hash (for directory organization)
- `<canonical-extension>`: Lowercase file extension (e.g., `.png`, `.jpg`, `.svg`)

**Example:**
```
wiki/media/images/ab/cdef1234567890...png
```

## Publishing Process

### Step 1: Image Validation

File: `tools/wiki-media/src/wiki_media/images.py`

**Validation checks:**
1. **Path resolution**: Resolve inbox-relative path to absolute path
2. **Path safety**: Reject absolute paths, `..`, `~`, URIs, symlinks
3. **File existence**: Verify file exists
4. **Format validation**: Check image is valid using Pillow
5. **Size validation**: Check image dimensions are reasonable
6. **SHA-256 calculation**: Compute hash of file content

**Path resolution logic:**
```python
def resolve_inbox_path(marker_path: str) -> Path | None:
    # Reject absolute paths, parent references, home, URIs, symlinks
    if (
        marker_path.startswith("/")
        or ".." in marker_path
        or marker_path.startswith("~")
        or "://" in marker_path
        or os.path.isabs(marker_path)
    ):
        return None
    
    # Resolve relative to inbox root
    inbox_root = config.MEDIA_INBOX_ROOT  # .wiki-media/inbox/
    return inbox_root / marker_path
```

### Step 2: Key Generation

File: `tools/wiki-media/src/wiki_media/keys.py`

**Key derivation:**
```python
def derive_object_key(image_hash: str, extension: str) -> str:
    """Derive S3 object key from image hash and extension."""
    prefix_dir = image_hash[:2]
    filename = f"{image_hash}{extension}"
    return f"{config.PREFIX}/{prefix_dir}/{filename}"
```

**Result**: `wiki/media/images/ab/cdef1234567890...png`

### Step 3: Remote Object Check

File: `tools/wiki-media/src/wiki_media/r2.py`

**Check existing objects:**
```python
async def _head(self, key: str) -> dict[str, Any] | None:
    """HEAD an object and return its metadata, or None if not found."""
    try:
        response = await self._s3.head_object(Bucket=config.BUCKET_NAME, Key=key)
        return {"ETag": response.get("ETag", ""), ...}
    except self._s3.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return None
        raise
```

**Behavior:**
- If object exists: Return metadata including ETag (SHA-256)
- If object doesn't exist: Return None
- If error: Raise exception

### Step 4: SHA-256 Verification

```python
async def _matches(self, key: str, expected_hash: str) -> bool:
    """Check if remote object matches expected hash."""
    head = await self._head(key)
    if head is None:
        return False
    # Extract hash from ETag (may be quoted)
    remote_hash = head["ETag"].strip('"')
    return remote_hash == expected_hash
```

**Key insight**: Cloudflare R2 stores SHA-256 as ETag, enabling content verification.

### Step 5: Upload (If Needed)

```python
async def publish_assets(self, items: list[models.PublishItem]) -> None:
    """Publish assets to R2, skipping existing matching objects."""
    for item in items:
        if await self._matches(item.key, item.hash):
            continue  # Object exists and matches, skip upload
        
        # Upload new object
        await self._s3.upload_fileobj(
            item.filepath,
            Bucket=config.BUCKET_NAME,
            Key=item.key,
            ExtraArgs={"ContentType": item.content_type},
        )
        
        # Verify upload
        await self._verify(item.key, item.hash)
```

**Upload rules:**
1. **Skip if exists and matches**: Never overwrite matching content
2. **Upload if missing**: Upload new objects
3. **Verify after upload**: Ensure remote SHA-256 matches local hash
4. **Never delete**: Objects are never deleted from R2

### Step 6: Verify Remote SHA-256

```python
async def _verify(self, key: str, expected_hash: str) -> None:
    """Verify remote object has expected hash."""
    if not await self._matches(key, expected_hash):
        raise RuntimeError(f"Remote hash mismatch for {key}")
```

**Safety**: Ensures uploaded content matches local file exactly.

## CDN URL Generation

```python
def cdn_url(key: str) -> str:
    """Generate CDN URL for an R2 object key."""
    return f"{config.CDN_BASE}/{key}"
```

**Example:**
```
Input:  wiki/media/images/ab/cdef1234567890...png
Output: https://cdn-wiki.tokenbel.info/wiki/media/images/ab/cdef1234567890...png
```

## Markdown Rewriting

File: `tools/wiki-media/src/wiki_media/markdown.py`

**Process:**
1. Parse Markdown for `upload:` image markers
2. For each marker, generate CDN URL from inbox path
3. Replace `upload:<path>` with CDN URL
4. Preserve alt text, title attributes, and HTML syntax

**Supported syntaxes:**
```markdown
![Alt text](upload:path/to/image.png)
![Alt text](upload:path/to/image.png "Title")
<img src="upload:path/to/image.png" alt="Alt text">
```

**Rewriting logic:**
```python
def rewrite_upload_markers(content: str, replacements: dict[str, str]) -> str:
    """Replace upload: markers with CDN URLs."""
    # replacements: { "upload:path/to/image.png": "https://cdn...png" }
    for marker, url in replacements.items():
        content = content.replace(marker, url)
    return content
```

## Transaction Handling

File: `tools/wiki-media/src/wiki_media/transaction.py`

**Atomic transaction process:**

1. **Stage**: Create backup of each Markdown file to be modified
2. **Promote**: Atomically write all modified files
3. **Rollback**: On failure, restore from backups

**Backup location**: `.wiki-media/run/<timestamp>/backups/`

**Transaction steps:**
```python
async def run_transaction(
    self, rewrites: list[models.MarkdownRewrite]
) -> list[Path]:
    # 1. Validate all rewrites
    # 2. Create backups
    backups = [self._backup(r.path) for r in rewrites]
    
    # 3. Stage changes
    staged = []
    for rewrite in rewrites:
        staged_path = self._stage(rewrite.path, rewrite.content)
        staged.append(staged_path)
    
    # 4. Verify staged files
    # 5. Atomically promote all staged files
    promoted = [self._promote(s) for s in staged]
    
    # 6. Return list of promoted files
    return promoted
```

**Safety features:**
- **Atomic promotion**: All files promoted or none
- **Rollback backups**: Original files preserved
- **No Git commit**: Transaction never commits to Git
- **Dry run support**: Can validate without actual writes

## Relationships

* [wiki-media CLI](wiki-media-cli.md) — CLI that orchestrates this publishing
* [Upload Markers](upload-markers.md) — upload: marker syntax

## Citations

[1] `tools/wiki-media/src/wiki_media/config.py` — R2 configuration constants
[2] `tools/wiki-media/src/wiki_media/keys.py` — Object key derivation
[3] `tools/wiki-media/src/wiki_media/r2.py` — R2 client implementation
[4] `tools/wiki-media/src/wiki_media/images.py` — Image validation
[5] `tools/wiki-media/src/wiki_media/markdown.py` — Markdown rewriting
[6] `tools/wiki-media/src/wiki_media/transaction.py` — Atomic transaction handling
[7] `tools/wiki-media/src/wiki_media/publisher.py` — Publish orchestration
[8] `tools/wiki-media/README.md:30-40` — Immutable destination documentation
