from pathlib import Path

from click.testing import CliRunner

from ttyblog.build import build
from ttyblog.cli import main


def test_init_creates_layout(tmp_path: Path):
    runner = CliRunner()
    result = runner.invoke(main, ["init", "--path", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "posts").is_dir()
    assert (tmp_path / "public").is_dir()
    assert (tmp_path / "templates").is_dir()
    assert (tmp_path / "config.toml").is_file()


def test_new_creates_dated_file(tmp_path: Path):
    runner = CliRunner()
    runner.invoke(main, ["init", "--path", str(tmp_path)])
    result = runner.invoke(main, ["new", "my first one", "--path", str(tmp_path)])
    assert result.exit_code == 0
    files = list((tmp_path / "posts").glob("*my-first-one*.txt"))
    assert len(files) == 1


def test_end_to_end_build(tmp_path: Path):
    runner = CliRunner()
    runner.invoke(main, ["init", "--path", str(tmp_path)])
    (tmp_path / "posts" / "2026-04-12-second.txt").write_text(
        "second post\ndate: 2026-04-12\ntags: test\n\nhello *world*.\n",
        encoding="utf-8",
    )
    result = build(tmp_path)
    assert len(result.posts) >= 2
    index = (tmp_path / "public" / "index.html").read_text(encoding="utf-8")
    assert "second post" in index
    assert "hello-ttyblog" in index or "hello ttyblog" in index
    post_html = (tmp_path / "public" / "posts" / "second.html").read_text(
        encoding="utf-8"
    )
    assert "<em>world</em>" in post_html
    assert "#test" in post_html


def test_list_command(tmp_path: Path):
    runner = CliRunner()
    runner.invoke(main, ["init", "--path", str(tmp_path)])
    result = runner.invoke(main, ["list", "--path", str(tmp_path)])
    assert result.exit_code == 0
    assert "hello ttyblog" in result.output


def test_build_cli_prints_summary(tmp_path: Path):
    runner = CliRunner()
    runner.invoke(main, ["init", "--path", str(tmp_path)])
    result = runner.invoke(main, ["build", "--path", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert "built" in result.output


def test_posts_sorted_newest_first(tmp_path: Path):
    runner = CliRunner()
    runner.invoke(main, ["init", "--path", str(tmp_path)])
    (tmp_path / "posts" / "2026-01-01-old.txt").write_text(
        "old\ndate: 2026-01-01\n\nx.\n", encoding="utf-8"
    )
    (tmp_path / "posts" / "2026-03-01-mid.txt").write_text(
        "mid\ndate: 2026-03-01\n\nx.\n", encoding="utf-8"
    )
    result = build(tmp_path)
    dates = [p.date for p in result.posts]
    assert dates == sorted(dates, reverse=True)
