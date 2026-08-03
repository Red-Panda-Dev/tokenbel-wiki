from __future__ import annotations

import os
import time
import random
import hashlib
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

from .keys import object_key
from .config import R2_REGION, R2_BUCKET_NAME, R2_UPLOAD_CONCURRENCY
from .images import open_unchanged
from .models import CliError, ImageAsset, RemoteError, IntegrityError

_TRANSIENT = {
    "429",
    "500",
    "502",
    "503",
    "504",
    "RequestTimeout",
    "RequestTimeoutException",
    "InternalError",
    "SlowDown",
}


def make_client():
    endpoint = os.environ.get("AWS_S3_URL", "")
    access = os.environ.get("AWS_ACCESS_KEY_ID", "")
    secret = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
    parsed = urlparse(endpoint)
    if (
        not access
        or not secret
        or parsed.scheme != "https"
        or not parsed.netloc
        or endpoint.rstrip("/") == "https://cdn-wiki.tokenbel.info"
    ):
        raise CliError("remote operations require non-empty credentials and an HTTPS non-CDN AWS_S3_URL")
    try:
        import boto3
    except ImportError as error:
        raise CliError("boto3 is required for remote operations; install tools/wiki-media") from error
    return boto3.client(
        "s3", endpoint_url=endpoint, region_name=R2_REGION, aws_access_key_id=access, aws_secret_access_key=secret
    )


def _code(error: Exception) -> str:
    response = getattr(error, "response", {}) or {}
    return str(response.get("Error", {}).get("Code", ""))


def _is_missing(error: Exception) -> bool:
    return _code(error) in {"404", "NoSuchKey", "NotFound"}


def _is_transient(error: Exception) -> bool:
    return _code(error) in _TRANSIENT or isinstance(error, (TimeoutError, ConnectionError, OSError))


def _retry(action):
    for attempt in range(4):
        try:
            return action()
        except Exception as error:
            if attempt == 3 or not _is_transient(error):
                raise
            time.sleep(min(2.0, 0.15 * (2**attempt)) * (0.5 + random.random()))


def _head(client, key: str):
    try:
        return _retry(lambda: client.head_object(Bucket=R2_BUCKET_NAME, Key=key))
    except Exception as error:
        if _is_missing(error):
            return None
        raise RemoteError(f"R2 HeadObject failed for {key}: {_code(error) or type(error).__name__}") from error


def _matches(head: dict, asset: ImageAsset) -> bool:
    metadata = {str(k).lower(): str(v) for k, v in (head.get("Metadata") or {}).items()}
    return (
        head.get("ContentLength") == asset.size
        and metadata.get("sha256") == asset.sha256
        and metadata.get("source") == "wiki-media-cli"
        and metadata.get("schema-version") == "1"
    )


def publish_one(client, asset: ImageAsset, dry_remote: bool = False) -> str:
    key = object_key(asset)
    head = _head(client, key)
    if head is not None:
        if not _matches(head, asset):
            raise IntegrityError(f"existing R2 object integrity mismatch: {key}")
        return "present"
    if dry_remote:
        return "missing"
    try:
        with open_unchanged(asset) as body:

            def upload():
                body.seek(0)
                return client.put_object(
                    Bucket=R2_BUCKET_NAME,
                    Key=key,
                    Body=body,
                    ContentType=asset.mime,
                    ContentDisposition="inline",
                    CacheControl="public, max-age=31536000, immutable",
                    Metadata={"sha256": asset.sha256, "source": "wiki-media-cli", "schema-version": "1"},
                    IfNoneMatch="*",
                )

            _retry(upload)
    except Exception as error:
        if _code(error) in {"412", "PreconditionFailed"}:
            existing = _head(client, key)
            if existing is not None and _matches(existing, asset):
                return "present"
            raise IntegrityError(f"R2 object appeared with mismatched integrity: {key}") from error
        raise RemoteError(f"R2 upload failed for {key}: {_code(error) or type(error).__name__}") from error
    head = _head(client, key)
    if head is None or not _matches(head, asset):
        raise IntegrityError(f"post-upload R2 verification failed: {key}")

    def remote_hash() -> str:
        response = client.get_object(Bucket=R2_BUCKET_NAME, Key=key)
        body = response["Body"]
        digest = hashlib.sha256()
        try:
            while block := body.read(1024 * 1024):
                digest.update(block)
        finally:
            body.close()
        return digest.hexdigest()

    try:
        remote_digest = _retry(remote_hash)
    except Exception as error:
        raise RemoteError(f"R2 GetObject failed for {key}: {_code(error) or type(error).__name__}") from error
    if remote_digest != asset.sha256:
        raise IntegrityError(f"remote SHA-256 mismatch: {key}")
    return "uploaded"


def publish_assets(client, assets: list[ImageAsset], dry_remote: bool = False) -> dict[str, str]:
    results: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=R2_UPLOAD_CONCURRENCY) as pool:
        future_map = {pool.submit(publish_one, client, asset, dry_remote): asset for asset in assets}
        for future in as_completed(future_map):
            asset = future_map[future]
            results[asset.sha256] = future.result()
    return results
