"""scan, parse, render, write."""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from .parse import Post, parse_file
from .render import make_env, render_index, render_post

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib


DEFAULT_CONFIG = {
    "title": "my blog",
    "author": "farkhad",
    "url": "https://blog.frkhd.com",
    "posts_dir": "posts",
    "output_dir": "public",
}


@dataclass
class BuildResult:
    posts: list[Post]
    output_dir: Path
    written: list[Path]


def load_config(root: Path) -> dict:
    cfg_path = root / "config.toml"
    if not cfg_path.exists():
        return dict(DEFAULT_CONFIG)
    with cfg_path.open("rb") as f:
        data = tomllib.load(f)
    merged = dict(DEFAULT_CONFIG)
    merged.update(data)
    return merged


def scan_posts(posts_dir: Path) -> list[Post]:
    if not posts_dir.is_dir():
        return []
    posts: list[Post] = []
    for p in sorted(posts_dir.glob("*.txt")):
        posts.append(parse_file(p))
    posts.sort(key=lambda x: (x.date, x.slug), reverse=True)
    return posts


def build(root: Path) -> BuildResult:
    config = load_config(root)
    posts_dir = root / config["posts_dir"]
    output_dir = root / config["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)

    posts = scan_posts(posts_dir)
    local_templates = root / "templates"
    env = make_env(local_templates)

    site = {
        "title": config["title"],
        "author": config["author"],
        "url": config["url"],
    }

    written: list[Path] = []

    index_html = render_index(env, posts, site)
    idx_path = output_dir / "index.html"
    idx_path.write_text(index_html, encoding="utf-8")
    written.append(idx_path)

    posts_out = output_dir / "posts"
    posts_out.mkdir(exist_ok=True)
    for post in posts:
        html_doc = render_post(env, post, site)
        out_path = posts_out / f"{post.slug}.html"
        out_path.write_text(html_doc, encoding="utf-8")
        written.append(out_path)

    return BuildResult(posts=posts, output_dir=output_dir, written=written)
