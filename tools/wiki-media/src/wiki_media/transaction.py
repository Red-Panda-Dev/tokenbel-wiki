from __future__ import annotations

import os
import uuid
import shutil
import hashlib
from pathlib import Path

from .models import ArticlePlan, RewriteError
from .markdown import rewrite, scan_images


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def make_run_dir(root: Path) -> Path:
    path = root / ".wiki-media/run" / uuid.uuid4().hex
    path.mkdir(parents=True, exist_ok=False)
    return path


def stage_rewrites(run_dir: Path, plan, url_for_asset) -> list[tuple[ArticlePlan, Path]]:
    staged: list[tuple[ArticlePlan, Path]] = []
    stage_root = run_dir / "staged-content"
    for article in plan.articles:
        with article.path.open("r", encoding="utf-8", newline="") as handle:
            current = handle.read()
        if sha256_text(current) != article.sha256:
            raise RewriteError(f"article changed after planning: {article.path}")
        replacements = [(occ.span, url_for_asset(plan.occurrence_assets[occ])) for occ in article.occurrences]
        changed = rewrite(current, replacements)
        remaining, errors = scan_images(changed)
        if errors or remaining:
            raise RewriteError(f"staged Markdown did not validate: {article.path}")
        target = stage_root / article.path.relative_to(plan.root)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8", newline="") as handle:
            handle.write(changed)
        staged.append((article, target))
    return staged


def promote(root: Path, run_dir: Path, staged: list[tuple[ArticlePlan, Path]]) -> None:
    backup_root = run_dir / "backup"
    promoted: list[tuple[ArticlePlan, Path]] = []
    try:
        for article, source in staged:
            with source.open("r", encoding="utf-8", newline="") as handle:
                expected = sha256_text(handle.read())
            with article.path.open("r", encoding="utf-8", newline="") as handle:
                if sha256_text(handle.read()) != article.sha256:
                    raise RewriteError(f"article changed before promotion: {article.path}")
            backup = backup_root / article.path.relative_to(root)
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(article.path, backup)
            os.replace(source, article.path)
            promoted.append((article, backup))
            with article.path.open("r", encoding="utf-8", newline="") as handle:
                promoted_hash = sha256_text(handle.read())
            if promoted_hash != expected:
                raise RewriteError(f"promotion hash verification failed: {article.path}")
    except Exception as error:
        rollback_errors = []
        for article, backup in reversed(promoted):
            try:
                os.replace(backup, article.path)
            except OSError as rollback_error:
                rollback_errors.append(str(rollback_error))
        suffix = f"; rollback failed: {'; '.join(rollback_errors)}" if rollback_errors else ""
        raise RewriteError(f"atomic promotion failed: {error}{suffix}") from error
