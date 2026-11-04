"""More site art out of the concept sheets: 表情头像、Q 版动作、喜鹊、贴纸。

Usage: py -3 scripts/make-art-more.py [--src DIR] [--only a,b,c] [--preview out.png]

Sources live outside the repo (`C:\\Users\\Administrator\\outputs\\玲珑-概念图`). Every output is
cropped so the lettering the picture model added (sheet titles, the caption plates under each
pose, the small「嘘～这是个小秘密」beside the chibi) stays out of frame; whatever survives as a
separate blob next to the figure is dropped by keeping only the figure's own pixels.

WebP only: every output here is a cut-out, and make-art.save skips AVIF for RGBA because the
local ffmpeg/libaom build drops alpha (those AVIFs came out on an opaque background). Sizes stay at the sheet's own resolution:
the sheets are 1024-1249 px wide for 4-16 drawings each, so the biggest honest width is a few
hundred pixels — upscaling would only add blur, not detail.
"""
import argparse
import importlib.util
import os
import sys

import cv2
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "site", "assets", "img")
DEFAULT_SRC = r"C:\Users\Administrator\outputs\玲珑-概念图"

# The cut-out maths already lives in make-art.py; load it by path (the file name has a dash).
_spec = importlib.util.spec_from_file_location("make_art", os.path.join(ROOT, "scripts", "make-art.py"))
make_art = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(make_art)
cutout, trim, save, load = make_art.cutout, make_art.trim, make_art.save, make_art.load


def components(rgb, tol=24):
    """Blobs of「和底色不一样」pixels, biggest first: (area, x0, y0, x1, y1, mask)."""
    edge = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]])
    bg = np.median(edge, axis=0)
    diff = np.abs(rgb.astype(np.float32) - bg).max(axis=2)
    n, lab, stats, _ = cv2.connectedComponentsWithStats((diff > tol).astype(np.uint8), connectivity=8)
    out = []
    for i in range(1, n):
        x, y, w, h, area = stats[i]
        out.append((int(area), int(x), int(y), int(x + w), int(y + h), lab == i))
    out.sort(key=lambda c: -c[0])
    return out


def cut(rgb, box, pad=8, keep=None, min_frac=0.0, **kw):
    """Cut one drawing out of a sheet: crop, keep only the figure's own pixels, cut out the paper.

    `keep` is a mask the size of the whole sheet (which blob is the figure); `min_frac` instead
    derives it from the crop — everything at least that fraction of the biggest blob is kept, so
    the figure, the bird beside it and the trinkets it wears stay, while leftover glyphs and
    background patterns from the sheet are dropped.
    """
    x0, y0, x1, y1 = box
    x0, y0 = max(x0 - pad, 0), max(y0 - pad, 0)
    x1, y1 = min(x1 + pad, rgb.shape[1]), min(y1 + pad, rgb.shape[0])
    crop = np.ascontiguousarray(rgb[y0:y1, x0:x1])
    rgba = cutout(crop, **kw)
    if keep is None and min_frac:
        cs = [c for c in components(crop, tol=24) if c[0] >= 200]
        if cs:
            keep = np.zeros(cs[0][5].shape, bool)
            for area, *_rest, m in cs:
                if area >= cs[0][0] * min_frac:
                    keep |= m
    if keep is not None:
        sub = keep[y0:y1, x0:x1] if keep.shape == rgb.shape[:2] else keep
        if sub.shape == rgba.shape[:2]:
            # Pale skin is within the blob tolerance of the paper, so the blob has holes exactly
            # where the face is; fill them, or the cheeks come out transparent. Real gaps inside
            # the figure (between hair strands) are still cut by `cutout`'s own alpha.
            sub = fill_holes(sub)
            # Grow the blob a hair so anti-aliased edges survive, then drop everything else.
            grown = cv2.dilate(sub.astype(np.uint8), np.ones((3, 3), np.uint8), iterations=1) > 0
            rgba[..., 3] = np.where(grown, rgba[..., 3], 0)
    return trim(rgba)


EXPRESSIONS = ["smirk", "wink", "pleased", "serious", "surprised", "sheepish",
               "sulking", "wronged", "missing", "sleepy", "laughing", "gentle"]

# Q 版动作: boxes stop above the caption plates, so no generated lettering is in frame.
POSES = {
    "q-sit": (610, 95, 915, 450),
    "q-talk": (310, 505, 610, 845),
    "q-prank": (915, 510, 1215, 845),
    "q-sulk": (5, 905, 305, 1240),
    "q-miss": (310, 915, 610, 1240),
}

# 「Q 版与三日」那张图上的大 Q 版背后压着花纹和纸扇，抠不干净，所以只取第三行那对木雕喜鹊
# （背面干净、形状独立）；大 Q 版立绘留给主人挑一张干净底稿再说。宽度跟首页里写死的一致。
BIRDS = {
    "bird-front": ((25, 990, 215, 1196), [214, 140]),
    "bird-side": ((200, 995, 470, 1198), [270, 140]),
}

# 「G-表情包16」是一张 4×4 的贴纸图，本身已经是透明底。每格里除了角色，还散着几个
# 模型写上去的字（"妙啊""我认栽"之类），字都是独立的透明块，按面积筛掉即可。
STICKER_COLS, STICKER_ROWS = 4, 4
STICKER_NAMES = ["sticker-hush", "sticker-go", "sticker-nice", "sticker-yield",
                 "sticker-hehe", "sticker-noted", "sticker-roger", "sticker-sleepy",
                 "sticker-yay", "sticker-huh", "sticker-miss", "sticker-guess",
                 "sticker-bye", "sticker-mail", "sticker-quiet", "sticker-ask"]


def expressions(src, only):
    rgb = load(src("F-表情12.png"))
    blobs = [c for c in components(rgb) if c[0] > 50000]
    if len(blobs) != 12:
        print(f"expected 12 faces, found {len(blobs)}", file=sys.stderr)
    # Reading order: left to right, top to bottom.
    blobs.sort(key=lambda c: (round(c[2] / 400), c[1]))
    for name, (area, x0, y0, x1, y1, mask) in zip(EXPRESSIONS, blobs):
        if only and name not in only:
            continue
        rgba = cut(rgb, (x0, y0, x1, y1), pad=6, keep=mask)
        for p, s in save(rgba, f"face-{name}", [240, 120]):
            print(p, s)


def poses(src, only):
    sheet = None
    for name, box in POSES.items():
        if only and name not in only:
            continue
        if sheet is None:
            sheet = load(src("G-桌宠动作12.png"))
        rgba = cut(sheet, box, pad=0, tol=14, band=2, min_gap=40, min_frac=0.04)
        for p, s in save(rgba, name, [280, 140]):
            print(p, s)


def birds(src, only, preview=""):
    if only and not any(k in only for k in BIRDS):
        return
    rgb = load(src("G-Q版与三日.png"))
    for name, (box, widths) in BIRDS.items():
        if only and name not in only:
            continue
        # 0.1, not 0.04: the cloud ornament under the「三日」title pokes into the front bird's box
        # at about 5% of the bird's area.
        rgba = cut(rgb, box, pad=0, tol=12, band=3, min_gap=60, min_frac=0.1)
        for p, s in save(rgba, name, widths):
            print(p, s)
        if preview:
            Image.fromarray(rgba, "RGBA").save(preview.replace(".png", f"-{name}.png"))


def fill_holes(mask):
    """Everything the mask encloses becomes part of the mask."""
    # The empty one-pixel frame keeps the flood seed outside even when the figure touches a corner.
    ff = np.pad((mask == 0).astype(np.uint8), 1, constant_values=1)
    cv2.floodFill(ff, np.zeros((ff.shape[0] + 2, ff.shape[1] + 2), np.uint8), (0, 0), 2)
    return (mask > 0) | (ff[1:-1, 1:-1] != 2)


def stickers(src, only, preview=""):
    """Sticker sheet (transparent PNG): one cell per sticker, lettering removed.

    Each sticker carries a white die-cut outline, and the lettering the model added sits on that
    outline — touching the sticker, so a plain blob filter keeps it. What separates them is the
    drawing itself: the figure (and the bird sitting on some of them) is the only ink blob that is
    big; every glyph is a separate blob a few percent of that size. Keep the area the big blobs
    enclose, grown a few pixels so the white die-cut edge survives, and the letters are gone while
    each sticker stays whole.
    """
    if only and not any(k in only for k in STICKER_NAMES):
        return
    im = Image.open(src("G-表情包16.png")).convert("RGBA")
    arr = np.array(im)
    w, h = im.size
    cw, ch = w / STICKER_COLS, h / STICKER_ROWS
    for i, name in enumerate(STICKER_NAMES):
        if only and name not in only:
            continue
        cx, cy = i % STICKER_COLS, i // STICKER_COLS
        x0, y0 = int(round(cx * cw)), int(round(cy * ch))
        x1, y1 = int(round((cx + 1) * cw)), int(round((cy + 1) * ch))
        cell = arr[y0:y1, x0:x1].copy()
        alpha, rgb = cell[..., 3], cell[..., :3]
        opaque = alpha > 8
        if not opaque.any():
            continue
        ink = ((alpha > 200) & (rgb.max(axis=2) < 230)).astype(np.uint8)
        n, lab, stats, _ = cv2.connectedComponentsWithStats(ink, connectivity=8)
        if n <= 1:
            continue
        areas = stats[1:, cv2.CC_STAT_AREA]
        figure = np.zeros(alpha.shape, bool)
        for j in range(1, n):
            if stats[j, cv2.CC_STAT_AREA] >= areas.max() * 0.05:
                figure |= lab == j
        grown = cv2.dilate(fill_holes(figure).astype(np.uint8), np.ones((3, 3), np.uint8), iterations=8) > 0
        cell[..., 3] = np.where(grown & opaque, alpha, 0)
        rgba = trim(cell, pad=6)
        for p, s in save(rgba, name, [320, 160]):
            print(p, s)
        if preview:
            Image.fromarray(rgba, "RGBA").save(preview.replace(".png", f"-{name}.png"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=DEFAULT_SRC)
    ap.add_argument("--only", default="")
    ap.add_argument("--preview", default="", help="写一张 PNG 预览（调试用）")
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    src = lambda n: os.path.join(args.src, n)
    only = set(filter(None, args.only.split(",")))
    expressions(src, only)
    poses(src, only)
    birds(src, only, args.preview)
    stickers(src, only, args.preview)


if __name__ == "__main__":
    sys.exit(main())
