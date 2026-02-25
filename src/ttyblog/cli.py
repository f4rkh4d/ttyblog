"""ttyblog cli."""
from __future__ import annotations

from pathlib import Path

import click

from . import __version__
from .build import build, load_config, scan_posts
from .parse import slugify, today_iso
from .serve import serve as serve_dir


DEFAULT_CONFIG_TOML = """title = "my blog"
author = "farkhad"
url = "https://blog.frkhd.com"
posts_dir = "posts"
output_dir = "public"
"""

SAMPLE_POST = """hello ttyblog
date: {date}
tags: meta

first post. nothing much here yet.

paragraphs are separated by blank lines. inline you get *italic*, **bold**,
and `code`. links look like [https://frkhd.com].

- lists too
- one item per line
- starting with a dash
"""


@click.group()
@click.version_option(__version__, prog_name="ttyblog")
def main() -> None:
    """blog engine that only reads .txt."""


@main.command()
@click.option("--path", default=".", help="target directory")
def init(path: str) -> None:
    """create posts/, public/, config.toml, templates/."""
    root = Path(path).resolve()
    root.mkdir(parents=True, exist_ok=True)
    (root / "posts").mkdir(exist_ok=True)
    (root / "public").mkdir(exist_ok=True)
    (root / "templates").mkdir(exist_ok=True)
    cfg = root / "config.toml"
    if not cfg.exists():
        cfg.write_text(DEFAULT_CONFIG_TOML, encoding="utf-8")
    sample = root / "posts" / f"{today_iso()}-hello-ttyblog.txt"
    if not sample.exists():
        sample.write_text(SAMPLE_POST.format(date=today_iso()), encoding="utf-8")
    click.echo(f"initialized {root}")


@main.command()
@click.argument("title")
@click.option("--path", default=".", help="project root")
def new(title: str, path: str) -> None:
    """create posts/<date>-<slug>.txt with frontmatter skeleton."""
    root = Path(path).resolve()
    config = load_config(root)
    posts_dir = root / config["posts_dir"]
    posts_dir.mkdir(parents=True, exist_ok=True)
    date = today_iso()
    slug = slugify(title)
    fname = f"{date}-{slug}.txt"
    dest = posts_dir / fname
    if dest.exists():
        raise click.ClickException(f"{dest} already exists")
    body = f"{title}\ndate: {date}\ntags:\n\nstart writing.\n"
    dest.write_text(body, encoding="utf-8")
    click.echo(str(dest))


@main.command(name="build")
@click.option("--path", default=".", help="project root")
def build_cmd(path: str) -> None:
    """read posts/, write public/."""
    root = Path(path).resolve()
    result = build(root)
    click.echo(f"built {len(result.posts)} posts -> {result.output_dir}")
    for p in result.posts:
        click.echo(f"  {p.date or '----------'}  {p.slug}")


@main.command()
@click.option("--port", default=8000, show_default=True)
@click.option("--path", default=".", help="project root")
def serve(port: int, path: str) -> None:
    """preview via python http.server."""
    root = Path(path).resolve()
    config = load_config(root)
    out = root / config["output_dir"]
    if not out.is_dir():
        raise click.ClickException(f"{out} does not exist. run ttyblog build first.")
    serve_dir(out, port=port)


@main.command(name="list")
@click.option("--path", default=".", help="project root")
def list_cmd(path: str) -> None:
    """list all posts with date + word count."""
    root = Path(path).resolve()
    config = load_config(root)
    posts = scan_posts(root / config["posts_dir"])
    if not posts:
        click.echo("no posts yet")
        return
    for p in posts:
        click.echo(f"{p.date or '----------'}  {p.word_count:>5}w  {p.title}")


if __name__ == "__main__":
    main()
