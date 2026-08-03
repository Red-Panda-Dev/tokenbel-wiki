from __future__ import annotations

import io
import os
import hashlib
from pathlib import Path

import pytest
from PIL import Image

from wiki_media import r2
from wiki_media.keys import cdn_url, object_key
from wiki_media.config import find_repository_root, load_credentials_from_dotenv
from wiki_media.images import validate_image, resolve_inbox_path
from wiki_media.models import CliError, ImageAsset, IntegrityError, WikiMediaError
from wiki_media.markdown import rewrite, scan_images
from wiki_media.discovery import resolve_scope, discover_content_files
from wiki_media.publisher import cleanup, publish, validate, build_plan


def make_root(tmp_path: Path) -> Path:
    (tmp_path / ".git").mkdir()
    (tmp_path / "hugo.yaml").write_text("title: test\n")
    (tmp_path / "content/guides/example").mkdir(parents=True)
    (tmp_path / ".wiki-media/inbox/statistics").mkdir(parents=True)
    return tmp_path


def png(path: Path, color="red") -> None:
    Image.new("RGB", (2, 2), color).save(path, "PNG")


def article(root: Path, source: str, path="content/guides/example/index.md") -> Path:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(source, encoding="utf-8", newline="")
    return target


@pytest.mark.parametrize(
    ("source", "count"),
    [
        ("![x](upload:statistics/a.png)", 1),
        ('![x](upload:statistics/a.png "title")', 1),
        ("![x](<upload:statistics/a b.png>)", 1),
        ("![a [b]](upload:statistics/a.png) ![b](upload:statistics/b.png)", 2),
        ("<img src='upload:statistics/a.png' alt='x'>", 1),
        ("```\n![x](upload:statistics/a.png)\n```", 0),
        ("    ![x](upload:statistics/a.png)", 0),
        ("`![x](upload:statistics/a.png)`", 0),
        ("<!-- ![x](upload:statistics/a.png) -->", 0),
        ("<script>const x = '![x](upload:statistics/a.png)'</script>", 0),
        ('<img alt=">" src="upload:statistics/a.png">', 1),
    ],
)
def test_markdown_scanner_recognizes_only_active_images(source, count):
    items, errors = scan_images(source)
    assert len(items) == count and not errors


@pytest.mark.parametrize(
    "source",
    [
        "[document](upload:a.pdf)",
        '<a href="upload:a.pdf">document</a>',
        '<a title=">" href="upload:a.pdf">document</a>',
    ],
)
def test_ordinary_upload_link_is_error(source):
    assert "only allowed" in scan_images(source)[1][0]


def test_rewrite_preserves_unrelated_bytes_and_crlf():
    source = '---\r\ntitle: Тест\r\n---\r\n![A](upload:a.png "T")\r\n'
    item = scan_images(source)[0][0]
    changed = rewrite(source, [(item.span, "https://cdn-wiki.tokenbel.info/wiki/media/images/aa/hash.png")])
    assert changed.endswith("\r\n") and "title: Тест" in changed and ' "T")' in changed


def test_scope_discovery_and_nested_cwd(tmp_path, monkeypatch):
    root = make_root(tmp_path)
    article(root, "text")
    article(root, "text", "content/statistics/index.md")
    monkeypatch.chdir(root / "content/guides")
    assert find_repository_root() == root
    assert [p.name for p in discover_content_files(root, resolve_scope(root, "content/guides"))] == ["index.md"]


def test_dotenv_loads_missing_credentials_without_overriding_environment(tmp_path, monkeypatch):
    dotenv = tmp_path / ".env"
    dotenv.write_text(
        "# local R2 credentials\nAWS_S3_URL=https://account.r2.cloudflarestorage.com\n"
        "export AWS_ACCESS_KEY_ID='from-dotenv'\nAWS_SECRET_ACCESS_KEY=secret-value\n",
        encoding="utf-8",
    )
    for key in ("AWS_S3_URL", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "from-shell")

    load_credentials_from_dotenv(dotenv)

    assert os.environ["AWS_S3_URL"] == "https://account.r2.cloudflarestorage.com"
    assert os.environ["AWS_ACCESS_KEY_ID"] == "from-shell"
    assert os.environ["AWS_SECRET_ACCESS_KEY"] == "secret-value"


@pytest.mark.parametrize("value", ["../content", "content/../guides", "/tmp/x"])
def test_scope_rejects_traversal(tmp_path, value):
    root = make_root(tmp_path)
    with pytest.raises(CliError):
        resolve_scope(root, value)


def test_scope_rejects_symlink(tmp_path):
    root = make_root(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "index.md").write_text("x")
    (root / "content/link").symlink_to(outside, target_is_directory=True)
    with pytest.raises(CliError):
        resolve_scope(root, "content/link")


def test_inbox_path_rejects_escapes(tmp_path):
    root = make_root(tmp_path)
    for value in ("upload:../x.png", "upload:/x.png", "upload:~/.x", "upload:file://x", "upload:https://x"):
        with pytest.raises(WikiMediaError):
            resolve_inbox_path(root, value)


def test_image_validation_and_key(tmp_path):
    root = make_root(tmp_path)
    image = root / ".wiki-media/inbox/statistics/a.PNG"
    png(image)
    asset = validate_image(image, root / ".wiki-media/inbox")
    assert (
        asset.mime == "image/png"
        and object_key(asset).startswith("wiki/media/images/")
        and cdn_url(asset).startswith("https://cdn-wiki.tokenbel.info/")
    )


def test_image_extension_mismatch_and_symlink(tmp_path):
    root = make_root(tmp_path)
    image = root / ".wiki-media/inbox/statistics/a.jpg"
    png(image)
    with pytest.raises(WikiMediaError):
        validate_image(image, root / ".wiki-media/inbox")
    real = root / ".wiki-media/inbox/statistics/real.png"
    png(real)
    link = root / ".wiki-media/inbox/statistics/link.png"
    link.symlink_to(real)
    with pytest.raises(WikiMediaError):
        validate_image(link, root / ".wiki-media/inbox")


def test_preflight_deduplicates_and_does_not_rewrite(tmp_path):
    root = make_root(tmp_path)
    png(root / ".wiki-media/inbox/statistics/a.png")
    article(root, "![one](upload:statistics/a.png)\n![two](upload:statistics/a.png)\n")
    plan = build_plan(root, None)
    assert not plan.errors and plan.references == 2 and len(plan.assets) == 1


def test_preflight_error_blocks_changes(tmp_path):
    root = make_root(tmp_path)
    target = article(root, "![one](upload:statistics/missing.png)\n")
    report = publish(root, None, dry_run=True, remote=False)
    assert report["validation_errors"] and target.read_text() == "![one](upload:statistics/missing.png)\n"


def test_scoped_plan_does_not_include_outside_article(tmp_path):
    root = make_root(tmp_path)
    png(root / ".wiki-media/inbox/statistics/a.png")
    article(root, "![one](upload:statistics/a.png)")
    article(root, "![two](upload:statistics/a.png)", "content/statistics/index.md")
    plan = build_plan(root, "content/guides")
    assert len(plan.articles) == 1 and "guides" in str(plan.articles[0].path)


def test_validate_preserves_migrated_url(tmp_path):
    root = make_root(tmp_path)
    article(root, "![x](https://cdn-wiki.tokenbel.info/wiki/assets/old.png)")
    report = validate(root, None)
    assert not report["validation_errors"]


def test_validate_rejects_forbidden_url(tmp_path):
    root = make_root(tmp_path)
    article(root, "![x](https://bucket.r2.dev/a.png)")
    assert validate(root, None)["validation_errors"]


def test_cleanup_only_removes_unreferenced_and_no_r2(tmp_path):
    root = make_root(tmp_path)
    used = root / ".wiki-media/inbox/statistics/used.png"
    unused = root / ".wiki-media/inbox/statistics/unused.png"
    png(used)
    png(unused)
    article(root, "![x](upload:statistics/used.png)")
    report = cleanup(root, dry_run=True)
    assert report["unreferenced_files"] == [".wiki-media/inbox/statistics/unused.png"] and unused.exists()
    cleanup(root, dry_run=False)
    assert used.exists() and not unused.exists()


class Body(io.BytesIO):
    closed_by_tool = False

    def close(self):
        self.closed_by_tool = True
        super().close()


class Client:
    def __init__(self, data: bytes, head=None):
        self.data = data
        self.head = head
        self.calls = []
        self.body = None

    def head_object(self, **kwargs):
        self.calls.append(("head", kwargs))
        if self.head is None:

            class Missing(Exception):
                response = {"Error": {"Code": "404"}}

            raise Missing()
        return self.head

    def put_object(self, **kwargs):
        self.calls.append(("put", kwargs))
        self.head = {
            "ContentLength": len(self.data),
            "Metadata": {
                "sha256": hashlib.sha256(self.data).hexdigest(),
                "source": "wiki-media-cli",
                "schema-version": "1",
            },
        }

    def get_object(self, **kwargs):
        self.calls.append(("get", kwargs))
        self.body = Body(self.data)
        return {"Body": self.body}


def asset_for_r2(tmp_path):
    file = tmp_path / "a.png"
    data = b"abc"
    file.write_bytes(data)
    return ImageAsset(
        file,
        hashlib.sha256(data).hexdigest(),
        len(data),
        "image/png",
        ".png",
        (len(data), file.stat().st_mtime_ns, file.stat().st_ino),
    ), data


def test_r2_upload_verifies_hash_closes_body_and_fixed_bucket(tmp_path):
    asset, data = asset_for_r2(tmp_path)
    client = Client(data)
    assert r2.publish_one(client, asset) == "uploaded"
    assert (
        client.body.closed_by_tool
        and {call[1]["Bucket"] for call in client.calls} == {"tokenbel-wiki"}
        and not any(name == "delete" for name, _ in client.calls)
    )


def test_r2_existing_mismatch_never_overwrites(tmp_path):
    asset, data = asset_for_r2(tmp_path)
    client = Client(data, {"ContentLength": 9, "Metadata": {}})
    with pytest.raises(IntegrityError):
        r2.publish_one(client, asset)
    assert not any(name == "put" for name, _ in client.calls)


def test_r2_remote_hash_mismatch(tmp_path):
    asset, data = asset_for_r2(tmp_path)
    client = Client(b"wrong")
    with pytest.raises(IntegrityError):
        r2.publish_one(client, asset)
