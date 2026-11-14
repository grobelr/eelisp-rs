#!/usr/bin/env python3
"""Build the self-hosting book (docs/self-hosting/) as one page.

    python3 scripts/build-book.py [out.html]

Every chapter in order, with a chapter list beside them and links between chapters kept inside
the page. Links to other files of the repository point at them on GitHub. The Markdown converter
is the one scripts/build-docs.py uses for the manual (standard library only). The output is a page
fragment: a <title>, a <style> and the content, as an Artifact page expects; default
target/book/book.html.
"""

import html
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOK = ROOT / "docs" / "self-hosting"
REPO = "https://github.com/santacroce-tech/eelisp-rs/blob/exp/register-vm/"

spec = importlib.util.spec_from_file_location("build_docs", ROOT / "scripts" / "build-docs.py")
docs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(docs)

CHAPTERS = ["README.md"] + sorted(p.name for p in BOOK.glob("[0-9][0-9]-*.md"))
docs.CHAPTERS = CHAPTERS
docs.DOCS = BOOK


def link(target, chapter):
    """Chapters link to each other inside the page; anything else in the repository, on GitHub."""
    if re.match(r"https?://", target):
        return html.escape(target)
    path, _, frag = target.partition("#")
    if not path:
        return "#" + docs.chapter_id(chapter) + "-" + frag
    if path in CHAPTERS:
        cid = docs.chapter_id(path)
        return "#" + (cid + "-" + frag if frag else cid)
    resolved = (BOOK / path).resolve()
    try:
        rel = resolved.relative_to(ROOT)
    except ValueError:
        return html.escape(target)
    return html.escape(REPO + str(rel) + ("#" + frag if frag else ""))


docs.link = link


def title_of(md):
    m = re.search(r"^# (.+)$", md, re.M)
    return m.group(1).strip() if m else ""


STYLE = """
/* A book read on screen: one reading column of serif text, the chapter list beside it. */
:root {
  --paper: #fafaf8; --ink: #1d2024; --muted: #5d6570; --rule: #e1e4e8;
  --accent: #2a5d8f; --code-bg: #eff2f5; --side: #f2f3f1;
  --t-c: #6a737d; --t-s: #8a4b08; --t-k: #6f42c1; --t-n: #1b6e5a; --t-f: #b31d28; --t-p: #8b949e; --t-r: #2a5d8f;
  --body: "Source Serif 4", "Iowan Old Style", Georgia, serif;
  --head: "Inter Tight", "Inter", system-ui, sans-serif;
  --mono: "JetBrains Mono", ui-monospace, "SF Mono", Menlo, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --paper: #15171a; --ink: #e4e6e9; --muted: #9aa2ad; --rule: #2a2e34;
  --accent: #8cb8e6; --code-bg: #1d2025; --side: #1a1d21;
  --t-c: #8b949e; --t-s: #e3b778; --t-k: #c4a5f5; --t-n: #7fd1b9; --t-f: #f08a8a; --t-p: #6e7681; --t-r: #8cb8e6;
  color-scheme: dark } }
:root[data-theme="dark"] {
  --paper: #15171a; --ink: #e4e6e9; --muted: #9aa2ad; --rule: #2a2e34;
  --accent: #8cb8e6; --code-bg: #1d2025; --side: #1a1d21;
  --t-c: #8b949e; --t-s: #e3b778; --t-k: #c4a5f5; --t-n: #7fd1b9; --t-f: #f08a8a; --t-p: #6e7681; --t-r: #8cb8e6;
  color-scheme: dark }

html { scroll-behavior: smooth; scroll-padding-top: 16px; }
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }
body { background: var(--paper); color: var(--ink); font-family: var(--body); font-size: 18px; line-height: 1.6; }
.shell { display: grid; grid-template-columns: 1fr; max-width: 1200px; margin: 0 auto; }
@media (min-width: 980px) { .shell { grid-template-columns: 290px minmax(0, 1fr); } }

nav.toc { font-family: var(--head); font-size: 14px; line-height: 1.35;
  padding-block: 24px; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: 16px; }
@media (min-width: 980px) {
  nav.toc { position: sticky; top: env(safe-area-inset-top, 0px); height: 100vh; overflow-y: auto;
    border-right: 1px solid var(--rule); background: var(--side); }
}
nav.toc details > summary { cursor: pointer; font-weight: 600; letter-spacing: .02em; padding: 8px 0; color: var(--ink); }
@media (min-width: 980px) { nav.toc details > summary { display: none; } }
nav.toc .book { display: block; font-weight: 700; font-size: 15px; color: var(--ink); text-decoration: none; margin-bottom: 14px; }
nav.toc ol { list-style: none; margin: 0; padding: 0; display: grid; gap: 2px; }
nav.toc a.ch { display: grid; grid-template-columns: 2.1em 1fr; gap: 4px; padding: 5px 8px; border-radius: 5px;
  color: var(--muted); text-decoration: none; }
nav.toc a.ch:hover, nav.toc a.ch:focus-visible { color: var(--ink); background: var(--code-bg); outline: none; }
nav.toc a.ch .n { font-variant-numeric: tabular-nums; color: var(--accent); }

main { min-width: 0; padding-block: 32px 96px; padding-left: max(16px, env(safe-area-inset-left, 0px));
  padding-right: max(16px, env(safe-area-inset-right, 0px)); }
article { max-width: 68ch; margin: 0 auto; }
article + article { margin-top: 88px; padding-top: 40px; border-top: 1px solid var(--rule); }
.eyebrow { font-family: var(--head); font-size: 13px; text-transform: uppercase; letter-spacing: .09em; color: var(--accent); margin: 0 0 6px; }
h1, h2, h3, h4 { font-family: var(--head); line-height: 1.2; text-wrap: balance; color: var(--ink); }
h1 { font-size: 2.1rem; font-weight: 700; margin: 0 0 18px; letter-spacing: -.01em; }
h2 { font-size: 1.4rem; font-weight: 650; margin: 2.2em 0 .6em; }
h3 { font-size: 1.12rem; font-weight: 650; margin: 1.8em 0 .5em; }
h1 .anchor, h2 .anchor, h3 .anchor, h4 .anchor { margin-left: .35em; color: var(--rule); text-decoration: none; font-weight: 400; }
h1:hover .anchor, h2:hover .anchor, h3:hover .anchor { color: var(--muted); }
p, li { hyphens: auto; }
a { color: var(--accent); text-underline-offset: 2px; }
a:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 2px; }
em { font-style: italic; }
code { font-family: var(--mono); font-size: .84em; background: var(--code-bg); padding: .08em .32em; border-radius: 4px; }
pre { background: var(--code-bg); border-radius: 8px; padding: 14px 16px; overflow-x: auto; font-size: 14.5px; line-height: 1.5; }
pre code { background: none; padding: 0; font-size: inherit; }
pre .c { color: var(--t-c); font-style: italic; } pre .s { color: var(--t-s); } pre .k { color: var(--t-k); }
pre .n { color: var(--t-n); } pre .f { color: var(--t-f); font-weight: 600; } pre .p { color: var(--t-p); } pre .r { color: var(--t-r); }
.table { overflow-x: auto; margin: 1.4em 0; }
table { border-collapse: collapse; font-family: var(--head); font-size: 14.5px; line-height: 1.4; min-width: 60%; }
th, td { text-align: left; padding: 7px 12px; border-bottom: 1px solid var(--rule); vertical-align: top; }
th { font-weight: 600; color: var(--muted); border-bottom-width: 2px; }
td { font-variant-numeric: tabular-nums; }
blockquote { margin: 1.2em 0; padding-left: 16px; border-left: 3px solid var(--rule); color: var(--muted); }
ul, ol { padding-left: 1.3em; } li + li { margin-top: .3em; }
.next { margin-top: 48px; font-family: var(--head); font-size: 15px; }
.next a { text-decoration: none; }
.cover { margin-bottom: 8px; }
.cover .meta { font-family: var(--head); font-size: 14px; color: var(--muted); margin-top: -6px; }
"""


def main():
    out_path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "target" / "book" / "book.html"
    texts = [(f, (BOOK / f).read_text(encoding="utf-8")) for f in CHAPTERS]
    book_title = title_of(texts[0][1])
    toc_items, articles = [], []
    for k, (fname, md) in enumerate(texts):
        cid = docs.chapter_id(fname)
        body = docs.md_to_html(md, fname, [])
        number = fname[:2] if fname[0].isdigit() else ""
        title = re.sub(r"^\d+\.\s*", "", title_of(md))
        if number:
            toc_items.append('<li><a class="ch" href="#{}"><span class="n">{}</span><span>{}</span></a></li>'
                             .format(cid, int(number), html.escape(title)))
            eyebrow = '<p class="eyebrow">Chapter {}</p>'.format(int(number))
        else:
            eyebrow = '<p class="eyebrow">EELisp · the self-hosting book</p>'
        nxt = ""
        if k + 1 < len(texts):
            nf, nmd = texts[k + 1]
            nxt = '<p class="next"><a href="#{}">Next: {} →</a></p>'.format(
                docs.chapter_id(nf), html.escape(title_of(nmd)))
        cls = ' class="cover"' if not number else ""
        articles.append('<article{}>{}{}{}</article>'.format(cls, eyebrow, body, nxt))
    page = """<title>{title}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@500;600;650;700&family=JetBrains+Mono:wght@400;600&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=swap">
<style>{style}</style>
<div class="shell">
<nav class="toc" aria-label="Chapters">
<details open><summary>Chapters</summary>
<a class="book" href="#top">{title}</a>
<ol>{toc}</ol>
</details>
</nav>
<main>{articles}</main>
</div>
""".format(title=html.escape(book_title), style=STYLE, toc="".join(toc_items), articles="\n".join(articles))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(page, encoding="utf-8")
    print("{}: {} chapters, {:,} bytes".format(out_path, len(toc_items), len(page.encode("utf-8"))))


if __name__ == "__main__":
    sys.exit(main())
