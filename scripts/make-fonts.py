"""Subset fonts to exactly the characters the site uses.

Display font: Source Han Serif SC Medium (OFL)  -> site/assets/fonts/serif-sc.woff2
Latin accent: EB Garamond (OFL)                 -> site/assets/fonts/latin-display.woff2

Run again after any copy change:  py -3 scripts/make-fonts.py
"""
import os
import string
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
OUT = os.path.join(SITE, "assets", "fonts")
FONTS_DIR = os.path.join(os.environ["LOCALAPPDATA"], "Microsoft", "Windows", "Fonts")
SERIF = os.path.join(FONTS_DIR, "SourceHanSerifSC-Medium.otf")
LATIN = os.path.join(FONTS_DIR, "EBGaramond[wght].ttf")

PUNCT = "　、。，；：？！…—·「」『』（）《》【】〈〉“”‘’％℃×～"
# 页面上可能出现的全角/符号兜底
EXTRA = "①②③④⑤⑥→←↑↓★☆●○◆◇■□▲△✓✔"


def site_text():
    chars = set(PUNCT + EXTRA + string.printable)
    for dirpath, _dirs, files in os.walk(SITE):
        for f in files:
            if os.path.splitext(f)[1] in (".html", ".css", ".js"):
                with open(os.path.join(dirpath, f), encoding="utf-8") as fh:
                    chars.update(fh.read())
    chars.discard("\r")
    return "".join(sorted(chars))


def subset(src, out, text, extra_args=()):
    tmp = os.path.join(OUT, "_chars.txt")
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(text)
    cmd = [
        sys.executable, "-m", "fontTools.subset", src,
        "--text-file=" + tmp,
        "--flavor=woff2",
        "--output-file=" + out,
        "--layout-features=*,",
        "--no-hinting",
        "--desubroutinize",
    ] + list(extra_args)
    subprocess.run(cmd, check=True)
    os.remove(tmp)
    print(os.path.basename(out), os.path.getsize(out) // 1024, "KB")


def main():
    os.makedirs(OUT, exist_ok=True)
    text = site_text()
    subset(SERIF, os.path.join(OUT, "serif-sc.woff2"), text)
    # 英文装饰字体只放标题用得到的大写字母、数字和少量符号
    latin = string.ascii_uppercase + string.digits + " ·.,-'&"
    subset(LATIN, os.path.join(OUT, "latin-display.woff2"), latin)


if __name__ == "__main__":
    main()
