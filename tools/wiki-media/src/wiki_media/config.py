from pathlib import Path

from .models import CliError

CONTENT_ROOT = Path("content")
MEDIA_WORK_ROOT = Path(".wiki-media")
MEDIA_INBOX_ROOT = MEDIA_WORK_ROOT / "inbox"
R2_BUCKET_NAME = "tokenbel-wiki"
R2_REGION = "auto"
R2_KEY_PREFIX = "wiki/media/images"
R2_PUBLIC_BASE_URL = "https://cdn-wiki.tokenbel.info"
R2_UPLOAD_CONCURRENCY = 4
MAX_IMAGE_BYTES = 25 * 1024 * 1024
CANONICAL_MIME_EXTENSIONS = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
    "image/avif": ".avif",
}
ALLOWED_CDN_PREFIXES = ("/wiki/media/images/", "/wiki/assets/")


def find_repository_root(start: Path | None = None) -> Path:
    """Find the repository independently of the shell working directory."""
    current = (start or Path.cwd()).resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if (
            (candidate / ".git").exists()
            and (candidate / "hugo.yaml").is_file()
            and (candidate / CONTENT_ROOT).is_dir()
        ):
            return candidate
    raise CliError("repository root not found (requires .git/, hugo.yaml and content/)")
