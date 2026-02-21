"""Post -> html via jinja2. bundled templates, override from local templates/."""
from __future__ import annotations

from pathlib import Path

from jinja2 import ChoiceLoader, Environment, FileSystemLoader, PackageLoader, select_autoescape

from .parse import Post


def make_env(local_templates: Path | None = None) -> Environment:
    loaders = []
    if local_templates and local_templates.is_dir():
        loaders.append(FileSystemLoader(str(local_templates)))
    loaders.append(PackageLoader("ttyblog", "templates"))
    return Environment(
        loader=ChoiceLoader(loaders),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_post(env: Environment, post: Post, site: dict) -> str:
    tpl = env.get_template("post.html")
    return tpl.render(post=post, site=site)


def render_index(env: Environment, posts: list[Post], site: dict) -> str:
    tpl = env.get_template("index.html")
    return tpl.render(posts=posts, site=site)
