"""Inline site.css into the HTML pages: one less request before first paint.

Usage: py -3 scripts/inline-css.py

Lighthouse (mobile, simulated slow 4G) counts the html -> css -> font chain as
over a second of render blocking. The CSS is ~25 KB (7 KB gzipped), small enough
to ship inside the HTML, so each page carries it in a marked <style> block:

    <!-- inline:site.css --> ... <!-- /inline:site.css -->

site.css stays the source of truth; after editing it, rerun this script.
url() paths inside the CSS are relative to assets/css/, so they are rewritten
to be correct from each page's own location.
"""
import os
import re

ROOT = os.path.join(os.path.dirname(__file__), "..", "site")
CSS = os.path.join(ROOT, "assets", "css", "site.css")
PAGES = ["index.html", os.path.join("stories", "cheng.html")]

BEGIN = "<!-- inline:site.css -->"
END = "<!-- /inline:site.css -->"
LINK_RE = re.compile(r'<link rel="stylesheet" href="[^"]*assets/css/site\.css">')
BLOCK_RE = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END), re.S)


def inline_block(css, prefix):
    # ../fonts/x -> <prefix>assets/fonts/x, same for ../img/
    css = css.replace("url('../", "url('%sassets/" % prefix)
    return "%s\n<style>\n%s</style>\n%s" % (BEGIN, css, END)


def main():
    css = open(CSS, encoding="utf-8").read()
    for page in PAGES:
        p = os.path.join(ROOT, page)
        s = open(p, encoding="utf-8").read()
        prefix = "../" if os.path.dirname(page) else ""
        block = inline_block(css, prefix)
        if BEGIN in s:
            s2, n = BLOCK_RE.subn(block, s)
            assert n == 1, page
        else:
            m = LINK_RE.search(s)
            assert m, page
            s2 = s[: m.start()] + block + s[m.end():]
        open(p, "w", encoding="utf-8", newline="").write(s2)
        print(page, "inlined", len(css), "bytes")


if __name__ == "__main__":
    main()
