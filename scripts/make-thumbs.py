"""Small copies of the chibi art for spots where the page shows it tiny (logo, crew row, film poster).

Usage: py -3 scripts/make-thumbs.py

Works from the 280 px WebP already in site/assets/img, so it does not need the concept sheets.
Output is WebP only: these are RGBA cut-outs, and the local ffmpeg's libaom drops alpha in AVIF.
"""
import os
from PIL import Image

IMG = os.path.join(os.path.dirname(__file__), "..", "site", "assets", "img")

# Widths are 2x of the largest CSS size each image gets on the page.
JOBS = {
    "q-happy-280.webp": [220, 140, 80],
    "q-idle-280.webp": [140],
    "q-think-280.webp": [140],
    "q-walk-280.webp": [140],
    "q-sleep-280.webp": [140],
}


def main():
    for src, widths in JOBS.items():
        im = Image.open(os.path.join(IMG, src)).convert("RGBA")
        base = src.rsplit("-", 1)[0]
        for w in widths:
            h = round(im.height * w / im.width)
            out = os.path.join(IMG, f"{base}-{w}.webp")
            im.resize((w, h), Image.LANCZOS).save(out, "WEBP", quality=82, method=6)
            print(os.path.basename(out), (w, h), os.path.getsize(out))


if __name__ == "__main__":
    main()
