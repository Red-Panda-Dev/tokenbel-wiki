from .config import R2_KEY_PREFIX, R2_PUBLIC_BASE_URL
from .models import ImageAsset


def object_key(asset: ImageAsset) -> str:
    return f"{R2_KEY_PREFIX}/{asset.sha256[:2]}/{asset.sha256}{asset.extension}"


def cdn_url(asset: ImageAsset) -> str:
    return f"{R2_PUBLIC_BASE_URL}/{object_key(asset)}"
