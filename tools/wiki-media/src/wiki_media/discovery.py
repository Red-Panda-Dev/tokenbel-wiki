from __future__ import annotations

import os
from pathlib import Path

from .config import CONTENT_ROOT
from .models import CliError


def _inside(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def resolve_scope(root: Path, supplied: str | None) -> Path:
    content = (root / CONTENT_ROOT).resolve()
    if supplied is None:
        return content
    raw = Path(supplied)
    if raw.is_absolute() or ".." in raw.parts:
        raise CliError("scope must be a non-traversing path inside content/")
    candidate = (root / raw).resolve(strict=False)
    if not _inside(candidate, content):
        raise CliError("scope must be inside content/")
    if not candidate.exists() or not (candidate.is_dir() or candidate.suffix.lower() == ".md"):
        raise CliError(f"scope does not exist or is not Markdown: {supplied}")
    if candidate.is_file() and candidate.name not in {"index.md", "_index.md"}:
        raise CliError("only index.md and _index.md content pages can be selected")
    # resolve() catches a final symlink; explicitly reject a link in the supplied route too.
    probe = root
    for part in raw.parts:
        probe /= part
        if probe.is_symlink():
            raise CliError("scope must not traverse symlinks")
    return candidate


def discover_content_files(root: Path, scope: Path) -> list[Path]:
    content = (root / CONTENT_ROOT).resolve()
    if scope.is_file():
        return [scope]
    found: list[Path] = []
    for directory, dirs, names in os.walk(scope, followlinks=False):
        dirs[:] = sorted(d for d in dirs if not d.startswith(".") and not (Path(directory) / d).is_symlink())
        directory_path = Path(directory)
        if directory_path.is_symlink() or not _inside(directory_path.resolve(), content):
            continue
        for name in sorted(names):
            candidate = directory_path / name
            if name in {"index.md", "_index.md"} and candidate.is_file() and not candidate.is_symlink():
                found.append(candidate)
    return sorted(found, key=lambda p: p.relative_to(root).as_posix())
