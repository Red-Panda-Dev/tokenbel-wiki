from __future__ import annotations

import os
import stat
import hashlib
import warnings
from pathlib import Path, PurePosixPath
from contextlib import contextmanager

from PIL import Image, UnidentifiedImageError
from PIL.Image import DecompressionBombError, DecompressionBombWarning

from .config import MAX_IMAGE_BYTES, CANONICAL_MIME_EXTENSIONS
from .models import ImageAsset, WikiMediaError


def _inside(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def resolve_inbox_path(root: Path, destination: str) -> Path:
    if not destination.startswith("upload:"):
        raise WikiMediaError("invalid marker")
    value = destination[7:]
    if not value or value.startswith(("/", "~", "file:", "http:", "https:")) or "\\" in value:
        raise WikiMediaError("upload destination must be a safe inbox-relative path")
    parts = PurePosixPath(value).parts
    if any(part in {"", ".", ".."} for part in parts):
        raise WikiMediaError("upload destination contains path traversal")
    inbox = (root / ".wiki-media/inbox").resolve(strict=False)
    candidate = inbox.joinpath(*parts)
    current = inbox
    for part in parts:
        current /= part
        if current.is_symlink():
            raise WikiMediaError("symlink is forbidden in inbox paths")
    real = candidate.resolve(strict=False)
    if not _inside(real, inbox):
        raise WikiMediaError("upload destination escapes inbox")
    return candidate


def _sniff(prefix: bytes) -> str | None:
    if prefix.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if prefix.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if prefix.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"
    if prefix.startswith(b"RIFF") and prefix[8:12] == b"WEBP":
        return "image/webp"
    if len(prefix) >= 16 and prefix[4:8] == b"ftyp" and b"avif" in prefix[8:32]:
        return "image/avif"
    return None


def _fingerprint(info: os.stat_result) -> tuple[int, int, int]:
    return (info.st_size, info.st_mtime_ns, info.st_ino)


@contextmanager
def open_no_symlink(path: Path):
    """Open every lexical component using dir_fd/O_NOFOLLOW, rejecting a TOCTOU symlink swap."""
    lexical = path.absolute()
    flags_dir = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    flags_file = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    current = os.open(lexical.anchor, flags_dir)
    try:
        parts = lexical.parts[1:]
        for index, part in enumerate(parts):
            next_fd = os.open(part, flags_file if index == len(parts) - 1 else flags_dir, dir_fd=current)
            os.close(current)
            current = next_fd
        info = os.fstat(current)
        if not stat.S_ISREG(info.st_mode):
            raise WikiMediaError("image must be a regular file")
        with os.fdopen(current, "rb", closefd=True) as handle:
            current = -1
            yield handle, info
    except OSError as error:
        if error.errno in {getattr(os, "ELOOP", 40), 40}:
            raise WikiMediaError("symlink is forbidden in inbox paths") from error
        raise WikiMediaError(f"cannot safely open image: {error}") from error
    finally:
        if current >= 0:
            os.close(current)


def validate_image(path: Path, inbox: Path) -> ImageAsset:
    try:
        if path.is_symlink() or not _inside(path.resolve(), inbox.resolve()):
            raise WikiMediaError("image escapes inbox")
        with open_no_symlink(path) as (fh, before):
            if not 0 < before.st_size <= MAX_IMAGE_BYTES:
                raise WikiMediaError("image is empty or exceeds 25 MiB")
            prefix = fh.read(64)
            fh.seek(0)
            mime = _sniff(prefix)
            if mime is None:
                raise WikiMediaError("unsupported image MIME (SVG is intentionally rejected)")
            extension = CANONICAL_MIME_EXTENSIONS[mime]
            if path.suffix.lower() != extension:
                raise WikiMediaError(f"extension must match {mime} ({extension})")
            digest = hashlib.sha256()
            while block := fh.read(1024 * 1024):
                digest.update(block)
            with warnings.catch_warnings():
                warnings.simplefilter("error", DecompressionBombWarning)
                try:
                    fh.seek(0)
                    with Image.open(fh) as image:
                        image.verify()
                    fh.seek(0)
                    with Image.open(fh) as image:
                        image.load()
                        if image.width <= 0 or image.height <= 0:
                            raise WikiMediaError("invalid image dimensions")
                except (UnidentifiedImageError, OSError, DecompressionBombError, DecompressionBombWarning) as error:
                    raise WikiMediaError(f"corrupt or unsafe image: {error}") from error
            if _fingerprint(os.fstat(fh.fileno())) != _fingerprint(before):
                raise WikiMediaError("image changed during validation")
        return ImageAsset(path, digest.hexdigest(), before.st_size, mime, extension, _fingerprint(before))
    except OSError as error:
        raise WikiMediaError(f"cannot validate image: {error}") from error


@contextmanager
def open_unchanged(asset: ImageAsset):
    with open_no_symlink(asset.path) as (fh, info):
        if _fingerprint(info) != asset.fingerprint:
            raise WikiMediaError(f"image changed after planning: {asset.path}")
        yield fh


def assert_unchanged(asset: ImageAsset) -> None:
    with open_unchanged(asset):
        pass
