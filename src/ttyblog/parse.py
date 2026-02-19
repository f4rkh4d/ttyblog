"""txt -> Post. tiny grammar, no markdown library."""
from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from datetime import date as _date
from pathlib import Path


@dataclass
class Post:
    slug: str
    title: str
    date: str = ""
    tags: list[str] = field(default_factory=list)
    body_html: str = ""
    source_path: str = ""
    word_count: int = 0


_CODE_RE = re.compile(r"`([^`]+)`")
_BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")
_ITALIC_RE = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")


def _slugify(title: str) -> str:
    s = title.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "post"


def _inline(text: str) -> str:
    out = html.escape(text)
    placeholders: list[str] = []

    def _stash(m: re.Match) -> str:
        placeholders.append(f"<code>{m.group(1)}</code>")
        return f"\x00{len(placeholders) - 1}\x00"

    out = _CODE_RE.sub(_stash, out)
    out = _BOLD_RE.sub(r"<strong>\1</strong>", out)
    out = _ITALIC_RE.sub(r"<em>\1</em>", out)

    def _restore(m: re.Match) -> str:
        return placeholders[int(m.group(1))]

    out = re.sub(r"\x00(\d+)\x00", _restore, out)
    return out


def _render_body(lines: list[str]) -> str:
    blocks: list[list[str]] = []
    current: list[str] = []
    for ln in lines:
        if ln.strip() == "":
            if current:
                blocks.append(current)
                current = []
        else:
            current.append(ln)
    if current:
        blocks.append(current)

    html_parts: list[str] = []
    for block in blocks:
        joined = " ".join(l.strip() for l in block)
        html_parts.append(f"<p>{_inline(joined)}</p>")
    return "\n".join(html_parts)


def parse_text(text: str, slug: str = "post", source_path: str = "") -> Post:
    raw_lines = text.replace("\r\n", "\n").split("\n")
    if not raw_lines or raw_lines[0].strip() == "":
        raise ValueError("empty post: need a title on line 1")

    title = raw_lines[0].strip()
    idx = 1
    date = ""
    tags: list[str] = []

    while idx < len(raw_lines):
        line = raw_lines[idx]
        if line.strip() == "":
            idx += 1
            break
        m = re.match(r"^([a-zA-Z_][a-zA-Z0-9_-]*)\s*:\s*(.*)$", line)
        if not m:
            break
        key, val = m.group(1).lower(), m.group(2).strip()
        if key == "date":
            date = val
        elif key == "tags":
            tags = [t.strip() for t in val.split(",") if t.strip()]
        idx += 1

    body_lines = raw_lines[idx:]
    body_html = _render_body(body_lines)
    wc = sum(len(l.split()) for l in body_lines)

    return Post(
        slug=slug,
        title=title,
        date=date,
        tags=tags,
        body_html=body_html,
        source_path=source_path,
        word_count=wc,
    )


def parse_file(path: Path) -> Post:
    text = path.read_text(encoding="utf-8")
    stem = path.stem
    m = re.match(r"^(\d{4}-\d{2}-\d{2})-(.+)$", stem)
    if m:
        slug = m.group(2)
        fallback_date = m.group(1)
    else:
        slug = _slugify(stem)
        fallback_date = ""
    post = parse_text(text, slug=slug, source_path=str(path))
    if not post.date and fallback_date:
        post.date = fallback_date
    return post


def slugify(title: str) -> str:
    return _slugify(title)


def today_iso() -> str:
    return _date.today().isoformat()
