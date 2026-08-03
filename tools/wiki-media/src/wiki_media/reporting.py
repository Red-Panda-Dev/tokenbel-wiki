from __future__ import annotations

import json
from pathlib import Path


def render(report: dict) -> str:
    labels = [
        ("scope", "Scope"),
        ("content_files_scanned", "Content files scanned"),
        ("files_with_upload_markers", "Files with upload markers"),
        ("image_references", "Image references"),
        ("unique_images", "Unique images"),
        ("unique_r2_objects", "Unique R2 objects"),
        ("uploaded", "Uploaded"),
        ("already_present", "Already present"),
        ("to_upload", "To upload"),
        ("remote_verified", "Remote verified"),
        ("files_to_rewrite", "Files to rewrite"),
        ("articles_updated", "Articles updated"),
        ("removed", "Removed"),
    ]
    output = [f"{label}: {report[key]}" for key, label in labels if key in report]
    for error in report.get("validation_errors", []):
        output.append(f"Error: {error}")
    output.append("Result: success" if not report.get("validation_errors") else "Result: failed")
    return "\n".join(output)


def write_json(path: str | None, report: dict) -> None:
    if path:
        Path(path).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
