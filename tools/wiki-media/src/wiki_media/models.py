from __future__ import annotations

from pathlib import Path
from dataclasses import field, dataclass


class WikiMediaError(Exception):
    exit_code = 3


class CliError(WikiMediaError):
    exit_code = 2


class RemoteError(WikiMediaError):
    exit_code = 4


class IntegrityError(WikiMediaError):
    exit_code = 5


class RewriteError(WikiMediaError):
    exit_code = 6


class CleanupError(WikiMediaError):
    exit_code = 7


@dataclass(frozen=True)
class SourceSpan:
    start: int
    end: int
    line: int
    column: int


@dataclass(frozen=True)
class Occurrence:
    article: Path
    destination: str
    span: SourceSpan
    kind: str  # markdown or html
    construct: SourceSpan | None = None  # whole ![alt](...) span; markdown images only


@dataclass(frozen=True)
class ImageAsset:
    path: Path
    sha256: str
    size: int
    mime: str
    extension: str
    fingerprint: tuple[int, int, int]


@dataclass
class ArticlePlan:
    path: Path
    source: str
    sha256: str
    occurrences: list[Occurrence] = field(default_factory=list)


@dataclass
class PublishPlan:
    root: Path
    scope: Path
    articles: list[ArticlePlan]
    assets: dict[Path, ImageAsset]
    occurrence_assets: dict[Occurrence, ImageAsset]
    errors: list[str] = field(default_factory=list)

    @property
    def references(self) -> int:
        return len(self.occurrence_assets)
