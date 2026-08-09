from __future__ import annotations

import os
import json
from pathlib import Path
from urllib.error import URLError, HTTPError
from urllib.parse import urlparse
from urllib.request import Request, HTTPRedirectHandler, build_opener

from .r2 import make_client, publish_assets
from .keys import cdn_url
from .config import MEDIA_INBOX_ROOT, ALLOWED_CDN_PREFIXES
from .images import validate_image, resolve_inbox_path
from .models import Occurrence, ArticlePlan, PublishPlan, CleanupError, WikiMediaError
from .markdown import scan_images
from .discovery import resolve_scope, discover_content_files
from .transaction import promote, sha256_text, make_run_dir, stage_rewrites


def _read_article(path: Path) -> str:
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            return handle.read()
    except UnicodeDecodeError as error:
        raise WikiMediaError("article is not UTF-8") from error


def _error(path: Path, message: str, destination: str = "") -> str:
    suffix = f"; upload destination: {destination}" if destination else ""
    return f"{path}: {message}{suffix}; required action: correct the source and retry"


def build_plan(root: Path, supplied_scope: str | None) -> PublishPlan:
    scope = resolve_scope(root, supplied_scope)
    articles: list[ArticlePlan] = []
    assets = {}
    occurrence_assets = {}
    errors = []
    inbox = root / MEDIA_INBOX_ROOT
    for path in discover_content_files(root, scope):
        try:
            source = _read_article(path)
        except WikiMediaError as error:
            errors.append(_error(path, str(error)))
            continue
        scanned, parse_errors = scan_images(source)
        errors.extend(_error(path, error) for error in parse_errors)
        article = ArticlePlan(path, source, sha256_text(source))
        for item in scanned:
            occurrence = Occurrence(path, item.destination, item.span, item.kind, item.construct)
            try:
                local = resolve_inbox_path(root, item.destination)
                asset = assets.get(local)
                if asset is None:
                    asset = validate_image(local, inbox)
                    assets[local] = asset
                article.occurrences.append(occurrence)
                occurrence_assets[occurrence] = asset
            except WikiMediaError as error:
                errors.append(_error(path, f"{item.span.line}:{item.span.column}: {error}", item.destination))
        if article.occurrences:
            articles.append(article)
    return PublishPlan(root, scope, articles, assets, occurrence_assets, errors)


def plan_summary(plan: PublishPlan) -> dict:
    objects = {asset.sha256: asset for asset in plan.occurrence_assets.values()}
    return {
        "scope": str(plan.scope.relative_to(plan.root)),
        "content_files_scanned": len(discover_content_files(plan.root, plan.scope)),
        "files_with_upload_markers": len(plan.articles),
        "image_references": plan.references,
        "unique_images": len(plan.assets),
        "unique_r2_objects": len(objects),
        "validation_errors": plan.errors,
    }


def write_artifacts(run_dir: Path, plan: PublishPlan, report: dict) -> None:
    def safe(value):
        if isinstance(value, Path):
            return str(value)
        if isinstance(value, set):
            return sorted(value)
        raise TypeError

    (run_dir / "plan.json").write_text(
        json.dumps(plan_summary(plan), ensure_ascii=False, indent=2, default=safe) + "\n", encoding="utf-8"
    )
    (run_dir / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, default=safe) + "\n", encoding="utf-8"
    )


def publish(root: Path, supplied_scope: str | None, dry_run: bool, remote: bool) -> dict:
    plan = build_plan(root, supplied_scope)
    report = plan_summary(plan)
    if plan.errors:
        return report
    assets = sorted({asset.sha256: asset for asset in plan.occurrence_assets.values()}.values(), key=lambda a: a.sha256)
    remote_results: dict[str, str] = {}
    if remote or not dry_run:
        remote_results = publish_assets(make_client(), assets, dry_remote=dry_run)
    report.update(
        {
            "uploaded": sum(v == "uploaded" for v in remote_results.values()),
            "already_present": sum(v == "present" for v in remote_results.values()),
            "to_upload": sum(v == "missing" for v in remote_results.values()),
            "remote_verified": sum(v in {"uploaded", "present"} for v in remote_results.values()),
            "files_to_rewrite": len(plan.articles),
        }
    )
    if dry_run:
        return report
    run_dir = make_run_dir(root)
    try:
        write_artifacts(run_dir, plan, report)
        staged = stage_rewrites(run_dir, plan, cdn_url)
        promote(root, run_dir, staged)
    except Exception:
        # Artifacts intentionally remain for diagnosis; immutable R2 objects are never deleted.
        raise
    report["articles_updated"] = len(staged)
    report["run_dir"] = str(run_dir.relative_to(root))
    write_artifacts(run_dir, plan, report)
    return report


def _urls_outside_protected(text: str) -> list[str]:
    # Existing published URLs are checked without rewriting or parsing generic links.
    found = []
    i = 0
    while i < len(text):
        point = text.find("http", i)
        if point < 0:
            break
        end = point
        while end < len(text) and text[end] not in " \t\r\n()[]<>'\"":
            end += 1
        found.append(text[point:end])
        i = end
    return found


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def _validate_remote_cdn(url: str) -> str | None:
    opener = build_opener(_NoRedirect())
    for method, headers in (("HEAD", {}), ("GET", {"Range": "bytes=0-0"})):
        try:
            response = opener.open(Request(url, method=method, headers=headers), timeout=15)
            if urlparse(response.geturl()).hostname != "cdn-wiki.tokenbel.info":
                return "redirected to another hostname"
            response.close()
            return None
        except HTTPError as error:
            if error.code in {405, 501} and method == "HEAD":
                continue
            return f"CDN returned HTTP {error.code}"
        except URLError as error:
            return f"CDN request failed: {error.reason}"
    return "CDN does not support HEAD or range GET"


def validate(root: Path, supplied_scope: str | None, remote: bool = False) -> dict:
    plan = build_plan(root, supplied_scope)
    report = plan_summary(plan)
    for file in discover_content_files(root, plan.scope):
        try:
            images, _ = scan_images(_read_article(file), include_all=True)
        except WikiMediaError:
            continue
        for image in images:
            url = image.destination
            if url.startswith("upload:"):
                continue
            parsed = urlparse(url)
            if url.startswith("file:") or "r2.dev" in parsed.netloc or parsed.netloc == "static.tokenbel.info":
                plan.errors.append(_error(file, f"disallowed published image URL: {url}"))
            elif parsed.scheme in {"http", "https"}:
                if parsed.netloc != "cdn-wiki.tokenbel.info":
                    continue  # External images are not the wiki CDN contract.
                if not any(parsed.path.startswith(prefix) for prefix in ALLOWED_CDN_PREFIXES):
                    plan.errors.append(_error(file, f"disallowed CDN prefix: {url}"))
                elif remote:
                    error = _validate_remote_cdn(url)
                    if error:
                        plan.errors.append(_error(file, error))
            else:
                plan.errors.append(_error(file, f"local image path is not allowed: {url}"))
    report["validation_errors"] = plan.errors
    return report


def cleanup(root: Path, dry_run: bool) -> dict:
    plan = build_plan(root, None)
    if plan.errors:
        raise CleanupError("cleanup blocked because content parsing/validation failed: " + " | ".join(plan.errors))
    referenced = {asset.path.resolve() for asset in plan.assets.values()}
    inbox = root / MEDIA_INBOX_ROOT
    removable: list[Path] = []
    if inbox.exists():
        for directory, dirs, files in os.walk(inbox, followlinks=False):
            dirs[:] = [d for d in dirs if not (Path(directory) / d).is_symlink()]
            for name in files:
                candidate = Path(directory) / name
                if candidate.is_file() and not candidate.is_symlink() and candidate.resolve() not in referenced:
                    removable.append(candidate)
    if not dry_run:
        for candidate in removable:
            candidate.unlink()
        for directory, dirs, _ in os.walk(inbox, topdown=False, followlinks=False) if inbox.exists() else []:
            path = Path(directory)
            if path != inbox and not path.is_symlink() and not any(path.iterdir()):
                path.rmdir()
    return {
        "scope": "content",
        "unreferenced_files": [str(p.relative_to(root)) for p in removable],
        "removed": 0 if dry_run else len(removable),
        "dry_run": dry_run,
    }
