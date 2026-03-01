from ttyblog.parse import parse_text
from ttyblog.render import make_env, render_index, render_post


SITE = {"title": "t", "author": "f", "url": "https://x"}


def test_render_post_contains_title_and_body():
    env = make_env()
    p = parse_text("hello\ndate: 2026-04-10\ntags: a, b\n\nbody here.", slug="hello")
    html = render_post(env, p, SITE)
    assert "<h1>hello</h1>" in html
    assert "body here." in html
    assert "#a" in html and "#b" in html


def test_render_post_escapes_title_in_head():
    env = make_env()
    p = parse_text("a & b\n\nx.", slug="a-b")
    html = render_post(env, p, SITE)
    assert "<title>a &amp; b" in html


def test_render_index_lists_posts():
    env = make_env()
    p1 = parse_text("one\ndate: 2026-04-10\n\nbody.", slug="one")
    p2 = parse_text("two\ndate: 2026-04-11\n\nbody.", slug="two")
    html = render_index(env, [p2, p1], SITE)
    assert "one" in html and "two" in html
    assert "/posts/one.html" in html


def test_render_index_empty():
    env = make_env()
    html = render_index(env, [], SITE)
    assert "no posts yet" in html
