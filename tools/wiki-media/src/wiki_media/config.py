import os
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
_CREDENTIAL_ENV_VARS = frozenset({"AWS_S3_URL", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"})
_TOOL_DOTENV_PATH = Path(__file__).resolve().parents[2] / ".env"


def load_credentials_from_dotenv(path: Path | None = None) -> None:
    """Load missing R2 credential variables from the tool-local .env file.

    Existing exported variables take precedence. Only the three supported R2
    variables are read, so unrelated dotenv entries never affect the process.
    """
    dotenv = path or _TOOL_DOTENV_PATH
    if not dotenv.exists():
        return
    if dotenv.is_symlink() or not dotenv.is_file():
        raise CliError(f"dotenv file must be a regular file: {dotenv}")
    try:
        lines = dotenv.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise CliError(f"cannot read dotenv file: {dotenv}") from error
    for number, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line.removeprefix("export ").lstrip()
        key, separator, value = line.partition("=")
        if key not in _CREDENTIAL_ENV_VARS:
            continue
        if not separator:
            raise CliError(f"invalid dotenv assignment for {key} at {dotenv}:{number}")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        if value:
            os.environ.setdefault(key, value)


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
