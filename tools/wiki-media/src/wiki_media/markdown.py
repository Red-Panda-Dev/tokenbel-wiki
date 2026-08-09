"""A small Markdown-aware scanner.  It intentionally preserves source bytes and spans."""

from __future__ import annotations

from dataclasses import dataclass

from .models import SourceSpan


@dataclass(frozen=True)
class ImageDestination:
    destination: str
    span: SourceSpan
    kind: str
    construct: SourceSpan | None = None  # whole ![alt](...) span; markdown images only


def _line_col(text: str, pos: int) -> tuple[int, int]:
    line = text.count("\n", 0, pos) + 1
    previous = text.rfind("\n", 0, pos)
    return line, pos - previous


def _protected(text: str) -> list[bool]:
    """Mark fenced/indented code, comments, and inline-code source characters."""
    mark = [False] * len(text)
    in_fence: tuple[str, int] | None = None
    offset = 0
    for line in text.splitlines(keepends=True):
        body = line.rstrip("\r\n")
        stripped = body.lstrip(" ")
        fence = stripped[:3] if len(stripped) >= 3 and stripped[:3] in {"```", "~~~"} else None
        if in_fence:
            mark[offset : offset + len(line)] = [True] * len(line)
            if fence and fence[0] == in_fence[0] and len(stripped) - len(stripped.lstrip(fence[0])) >= in_fence[1]:
                in_fence = None
        elif fence:
            mark[offset : offset + len(line)] = [True] * len(line)
            char = fence[0]
            in_fence = (char, len(stripped) - len(stripped.lstrip(char)))
        elif body.startswith("    ") or body.startswith("\t"):
            mark[offset : offset + len(line)] = [True] * len(line)
        offset += len(line)
    i = 0
    while i < len(text):
        if mark[i]:
            i += 1
            continue
        if text.startswith("<!--", i):
            end = text.find("-->", i + 4)
            end = len(text) if end < 0 else end + 3
            mark[i:end] = [True] * (end - i)
            i = end
            continue
        # Script/style/pre/textarea contents are raw HTML, not Markdown source.
        if text[i] == "<":
            lower = text[i:].lower()
            for tag in ("script", "style", "pre", "textarea"):
                opening = f"<{tag}"
                if lower.startswith(opening) and (
                    len(lower) == len(opening) or lower[len(opening)].isspace() or lower[len(opening)] == ">"
                ):
                    opening_end = _html_tag_end(text, i + len(opening))
                    close = lower.find(f"</{tag}", max(0, opening_end - i + 1)) if opening_end >= 0 else -1
                    closing_end = _html_tag_end(text, i + close) if close >= 0 else -1
                    end = len(text) if closing_end < 0 else closing_end + 1
                    if end <= 0:
                        end = len(text)
                    mark[i:end] = [True] * (end - i)
                    i = end
                    break
            else:
                i += 1
            if i > 0 and (i >= len(text) or mark[i - 1]):
                continue
        if text[i] == "`":
            run = 1
            while i + run < len(text) and text[i + run] == "`":
                run += 1
            close = text.find("`" * run, i + run)
            if close >= 0:
                mark[i : close + run] = [True] * (close + run - i)
                i = close + run
                continue
        i += 1
    return mark


def _balanced(text: str, start: int, opening: str, closing: str, protected: list[bool]) -> int:
    depth = 1
    i = start
    while i < len(text):
        if protected[i]:
            i += 1
            continue
        if text[i] == "\\":
            i += 2
            continue
        if text[i] == opening:
            depth += 1
        elif text[i] == closing:
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def _html_tag_end(text: str, start: int) -> int:
    """Find a closing tag delimiter without mistaking quoted `>` for one."""
    quote: str | None = None
    i = start
    while i < len(text):
        char = text[i]
        if quote:
            if char == "\\":
                i += 2
                continue
            if char == quote:
                quote = None
        elif char in "\"'":
            quote = char
        elif char == ">":
            return i
        i += 1
    return -1


def _destination(text: str, left: int, right: int, protected: list[bool]) -> tuple[str, int, int] | None:
    i = left
    while i < right and text[i].isspace():
        i += 1
    if i >= right:
        return None
    if text[i] == "<":
        end = text.find(">", i + 1, right + 1)
        if end < 0:
            return None
        return text[i + 1 : end], i + 1, end
    end = i
    while end < right and not text[end].isspace():
        if text[end] == "\\":
            end += 2
        else:
            end += 1
    return text[i:end], i, end


def scan_images(text: str, include_all: bool = False) -> tuple[list[ImageDestination], list[str]]:
    protected = _protected(text)
    images: list[ImageDestination] = []
    errors: list[str] = []
    i = 0
    while i < len(text):
        if protected[i]:
            i += 1
            continue
        # Markdown link/image, supporting escaped/nested alternative text.
        bang = text[i] == "!" and i + 1 < len(text) and text[i + 1] == "["
        normal = text[i] == "["
        if bang or normal:
            bracket = i + 1 if bang else i
            close = _balanced(text, bracket + 1, "[", "]", protected)
            if close >= 0 and close + 1 < len(text) and text[close + 1] == "(":
                end = _balanced(text, close + 2, "(", ")", protected)
                if end < 0:
                    errors.append(f"malformed link at {_line_col(text, i)[0]}:{_line_col(text, i)[1]}")
                else:
                    dest = _destination(text, close + 2, end, protected)
                    if dest:
                        value, start, finish = dest
                        if value.startswith("upload:"):
                            line, col = _line_col(text, start)
                            if bang:
                                images.append(
                                    ImageDestination(
                                        value,
                                        SourceSpan(start, finish, line, col),
                                        "markdown",
                                        SourceSpan(i, end + 1, *_line_col(text, i)),
                                    )
                                )
                            else:
                                errors.append(f"upload: is only allowed in an image at {line}:{col}")
                        elif bang and include_all:
                            line, col = _line_col(text, start)
                            images.append(
                                ImageDestination(
                                    value,
                                    SourceSpan(start, finish, line, col),
                                    "markdown",
                                    SourceSpan(i, end + 1, *_line_col(text, i)),
                                )
                            )
                    i = end + 1
                    continue
        # HTML ordinary links may not contain upload: destinations.
        if text[i : i + 2].lower() == "<a" and (i + 2 == len(text) or text[i + 2].isspace() or text[i + 2] == ">"):
            end = _html_tag_end(text, i + 2)
            if end >= 0:
                tag = text[i : end + 1]
                lower = tag.lower()
                k = 0
                while k < len(tag):
                    if lower.startswith("href", k) and (k == 0 or tag[k - 1].isspace()):
                        q = k + 4
                        while q < len(tag) and tag[q].isspace():
                            q += 1
                        if q < len(tag) and tag[q] == "=":
                            q += 1
                            while q < len(tag) and tag[q].isspace():
                                q += 1
                            quote = tag[q] if q < len(tag) and tag[q] in "\"'" else None
                            start = q + 1 if quote else q
                            finish = tag.find(quote, start) if quote else start
                            if not quote:
                                while finish < len(tag) and not tag[finish].isspace() and tag[finish] != ">":
                                    finish += 1
                            if finish >= 0 and tag[start:finish].startswith("upload:"):
                                line, col = _line_col(text, i + start)
                                errors.append(f"upload: is only allowed in an image at {line}:{col}")
                            break
                    k += 1
                i = end + 1
                continue
        # HTML img src: scan tag and one exact attribute span without rewriting any other attribute.
        if text[i : i + 4].lower() == "<img" and (i + 4 == len(text) or text[i + 4].isspace() or text[i + 4] == ">"):
            end = _html_tag_end(text, i + 4)
            if end >= 0:
                tag = text[i : end + 1]
                lower = tag.lower()
                # Deliberately local parser, no global regexp: locate src token with quote delimiter.
                k = 0
                while k < len(tag):
                    if lower.startswith("src", k) and (k == 0 or tag[k - 1].isspace()):
                        q = k + 3
                        while q < len(tag) and tag[q].isspace():
                            q += 1
                        if q < len(tag) and tag[q] == "=":
                            q += 1
                            while q < len(tag) and tag[q].isspace():
                                q += 1
                            quote = tag[q] if q < len(tag) and tag[q] in "\"'" else None
                            val_start = q + 1 if quote else q
                            val_end = tag.find(quote, val_start) if quote else val_start
                            if not quote:
                                while val_end < len(tag) and not tag[val_end].isspace() and tag[val_end] != ">":
                                    val_end += 1
                            if val_end >= 0:
                                value = tag[val_start:val_end]
                                if value.startswith("upload:") or include_all:
                                    absolute = i + val_start
                                    line, col = _line_col(text, absolute)
                                    images.append(
                                        ImageDestination(value, SourceSpan(absolute, i + val_end, line, col), "html")
                                    )
                                break
                    k += 1
                i = end + 1
                continue
        i += 1
    return images, errors


def rewrite(text: str, replacements: list[tuple[SourceSpan, str]]) -> str:
    for span, value in sorted(replacements, key=lambda item: item[0].start, reverse=True):
        text = text[: span.start] + value + text[span.end :]
    return text
