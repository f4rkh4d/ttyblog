from ttyblog.parse import parse_text, slugify


def test_title_is_first_line():
    p = parse_text("hello world\n\nbody.")
    assert p.title == "hello world"


def test_frontmatter_date_and_tags():
    src = "t\ndate: 2026-04-10\ntags: unix, minimalism\n\nbody."
    p = parse_text(src)
    assert p.date == "2026-04-10"
    assert p.tags == ["unix", "minimalism"]


def test_missing_frontmatter_ok():
    p = parse_text("title\n\nbody paragraph.")
    assert p.date == ""
    assert p.tags == []
    assert "<p>body paragraph.</p>" in p.body_html


def test_paragraphs_split_on_blank_lines():
    p = parse_text("t\n\nfirst para.\n\nsecond para.")
    assert p.body_html.count("<p>") == 2


def test_inline_italic_bold_code():
    p = parse_text("t\n\nthis is *it* and **bold** and `code`.")
    assert "<em>it</em>" in p.body_html
    assert "<strong>bold</strong>" in p.body_html
    assert "<code>code</code>" in p.body_html


def test_bare_link():
    p = parse_text("t\n\nsee [https://example.com] for more.")
    assert '<a href="https://example.com">https://example.com</a>' in p.body_html


def test_text_link():
    p = parse_text("t\n\nsee [example](https://example.com) site.")
    assert '<a href="https://example.com">example</a>' in p.body_html


def test_list_wrapping():
    src = "t\n\n- one\n- two\n- three"
    p = parse_text(src)
    assert p.body_html.count("<ul>") == 1
    assert p.body_html.count("<li>") == 3


def test_list_and_paragraph_separate_blocks():
    src = "t\n\nintro para.\n\n- one\n- two\n\nafter para."
    p = parse_text(src)
    assert p.body_html.count("<p>") == 2
    assert p.body_html.count("<ul>") == 1


def test_escaping_html_entities():
    p = parse_text("t\n\n1 < 2 and a & b")
    assert "&lt;" in p.body_html
    assert "&amp;" in p.body_html


def test_code_protects_inner_markers():
    p = parse_text("t\n\n`*not italic*`")
    assert "<em>" not in p.body_html
    assert "<code>*not italic*</code>" in p.body_html


def test_empty_raises():
    import pytest
    with pytest.raises(ValueError):
        parse_text("")


def test_word_count():
    p = parse_text("t\n\none two three four five.")
    assert p.word_count == 5


def test_slugify():
    assert slugify("Hello, World!") == "hello-world"
    assert slugify("  weird   spaces  ") == "weird-spaces"
    assert slugify("___") == "post"
