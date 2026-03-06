# ttyblog

blog engine. reads .txt. no react, no rss library, no 37-step config.

## install

```
pip install git+https://github.com/f4rkh4d/ttyblog
```

python 3.10+.

## quick start

```
ttyblog init
ttyblog new "first post"
ttyblog build
ttyblog serve --port 8000
```

that's the loop. edit .txt, rerun `build`, refresh.

## the format

a post is just a text file. first line is the title. a few `key: value` lines can follow, then a blank line, then the body.

```
unix was a mistake (just kidding)
date: 2026-04-14
tags: unix, rambling

i spent an hour looking for a file today. it was in the place i put it.

inline you get *italic*, **bold**, and `code`. links are [https://frkhd.com]
or [named](https://frkhd.com). lists work if every line starts with `- `:

- this is a list item
- so is this
- three is a crowd

paragraphs are separated by a blank line. that's the whole grammar.
```

what the parser actually recognizes:

- line 1 → `<h1>` title
- `key: value` until first blank line → frontmatter (`date`, `tags`)
- blank-line separated blocks → `<p>` or `<ul>` (if every line starts with `- `)
- `*x*` `**x**` `` `x` `` for italic / bold / code
- `[url]` and `[text](url)` for links
- html is escaped, code spans are safe from other markers

filenames like `2026-04-14-slug.txt` set the slug and a fallback date.

## caveat

markdown it is not. the grammar is tiny. if you want footnotes, tables, headings inside posts, or asset pipelines, go use zola or hugo. this isn't that. it exists because i wanted to write posts in a terminal buffer and stop thinking about it.

## license

MIT.
