"""Cut Linglong art out of its light background and export web images.

Usage: py -3 scripts/make-art.py [--src DIR]

Source PNGs live outside the repo (concept art folder). Outputs go to
site/assets/img/ as WebP (and AVIF through ffmpeg when available).
"""
import argparse
import os
import shutil
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "site", "assets", "img")
DEFAULT_SRC = r"C:\Users\Administrator\outputs\玲珑-概念图"


def load(path):
    return np.array(Image.open(path).convert("RGB"))


def cutout(rgb, tol=16, band=6, bg_tol=7, min_gap=120):
    """Return RGBA for art drawn on a plain light background.

    Builds a trimap (sure background / sure foreground / unknown), takes the
    foreground colour of each unknown pixel from its nearest sure-foreground
    pixel, and solves C = a*F + (1-a)*B for alpha. Cheap, but it keeps thin
    hair strands and removes the white gaps between them.
    """
    h, w, _ = rgb.shape
    col = rgb.astype(np.float32)
    edge = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]])
    bg = np.median(edge, axis=0).astype(np.float32)
    diff = np.abs(col - bg).max(axis=2)

    near = (diff < tol).astype(np.uint8)
    _, labels = cv2.connectedComponents(near, connectivity=4)
    border = set(np.unique(np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]])))
    border.discard(0)
    outside = np.isin(labels, list(border))

    # Sure background: border-connected, plus enclosed pure-bg pockets big
    # enough not to be eye whites or highlights.
    pure = (diff < bg_tol).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(pure, connectivity=4)
    big = np.zeros(n, bool)
    big[1:] = stats[1:, cv2.CC_STAT_AREA] >= min_gap
    bg_sure = (big[lab] & (pure > 0)) | (outside & (diff < bg_tol + 3))

    lum = col.mean(axis=2)
    sat = col.max(axis=2) - col.min(axis=2)
    k3 = np.ones((3, 3), np.uint8)
    # Small pockets between hair strands: pure-ish bg surrounded by dark,
    # unsaturated pixels. Eye whites sit next to skin, so they fail the test.
    loose = (diff < bg_tol + 4).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(loose, connectivity=4)
    for i in range(1, n):
        area = stats[i, cv2.CC_STAT_AREA]
        if area < 6 or area >= 200000:
            continue
        x, y, ww, hh = stats[i, :4]
        sl = (slice(max(y - 3, 0), y + hh + 3), slice(max(x - 3, 0), x + ww + 3))
        m = lab[sl] == i
        ring = (cv2.dilate(m.astype(np.uint8), k3, iterations=2) > 0) & ~m
        if not ring.any():
            continue
        rc = col[sl][ring]
        skin = ((rc[:, 0] - rc[:, 2]) > 25) & (rc.mean(axis=1) > 150)
        if skin.mean() < 0.15 and rc.mean() < 200:
            bg_sure[sl] |= m

    fgmask = (~outside).astype(np.uint8)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (band * 2 + 1, band * 2 + 1))
    core = cv2.erode(fgmask, k) > 0
    # Grey floor shadows and light halos that touch the background are not
    # sure foreground even when they are wide.
    neutral = ((sat < 18) & (lum > 185) & ~bg_sure).astype(np.uint8)
    n, lab = cv2.connectedComponents(neutral, connectivity=8)
    touch = np.unique(lab[(cv2.dilate(bg_sure.astype(np.uint8), k3) > 0) & (neutral > 0)])
    halo = np.isin(lab, touch[touch > 0])
    fg_sure = ((core | (diff > 70)) & ~bg_sure & ~halo)

    # Nearest sure-foreground colour for every pixel.
    src = (~fg_sure).astype(np.uint8)
    _, idx = cv2.distanceTransformWithLabels(src, cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    ys, xs = np.where(src == 0)
    lut_y = np.zeros(idx.max() + 1, np.int32)
    lut_x = np.zeros(idx.max() + 1, np.int32)
    # Labels for DIST_LABEL_PIXEL are assigned in row-major scan order.
    lut_y[1:len(ys) + 1] = ys
    lut_x[1:len(xs) + 1] = xs
    F = col[lut_y[idx], lut_x[idx]]
    F = cv2.blur(F, (5, 5))

    d = F - bg
    c = col - bg
    den = (d * d).sum(axis=2)
    a = (c * d).sum(axis=2) / np.maximum(den, 1.0)
    a = np.clip(a, 0, 1)
    a = np.where(den < 400, np.clip(diff / 40.0, 0, 1), a)

    alpha = a
    alpha[bg_sure] = 0.0
    alpha[fg_sure] = 1.0
    unknown = ~(bg_sure | fg_sure)
    alpha[unknown & (diff < 3)] = 0.0

    am = alpha[..., None]
    unmixed = (col - (1 - am) * bg) / np.maximum(am, 1e-3)
    out_col = np.where(am > 0.35, unmixed, F)
    out_col = np.where(fg_sure[..., None], col, out_col)
    out_col = np.clip(out_col, 0, 255)
    return np.dstack([out_col, alpha * 255]).astype(np.uint8)


def trim(rgba, pad=8):
    a = rgba[..., 3]
    ys, xs = np.where(a > 8)
    y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad, rgba.shape[0])
    x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad, rgba.shape[1])
    return rgba[y0:y1, x0:x1]


def save(rgba, name, widths, quality=82):
    im = Image.fromarray(rgba, "RGBA" if rgba.shape[2] == 4 else "RGB")
    made = []
    for w in sorted({min(w, im.width) for w in widths}):
        h = round(im.height * w / im.width)
        r = im.resize((w, h), Image.LANCZOS) if w != im.width else im
        p = os.path.join(OUT, f"{name}-{w}.webp")
        r.save(p, "WEBP", quality=quality, method=6)
        made.append((p, r.size))
        avif(r, p[:-5] + ".avif")
    return made


def avif(im, path):
    ff = shutil.which("ffmpeg")
    if not ff:
        return
    tmp = path + ".png"
    im.save(tmp)
    pix = "yuva420p" if im.mode == "RGBA" else "yuv420p"
    cmd = [ff, "-y", "-loglevel", "error", "-i", tmp, "-c:v", "libaom-av1", "-still-picture", "1",
           "-crf", "30", "-cpu-used", "6", "-pix_fmt", pix, path]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        if os.path.exists(path):
            os.remove(path)
    finally:
        os.remove(tmp)


def crop(rgb, box):
    x0, y0, x1, y1 = box
    return np.ascontiguousarray(rgb[y0:y1, x0:x1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=DEFAULT_SRC)
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    src = lambda n: os.path.join(args.src, n)
    only = set(filter(None, args.only.split(",")))
    want = lambda k: not only or k in only

    if want("hero"):
        rgb = load(src("F-定稿立绘.png"))
        rgba = trim(cutout(rgb))
        for p, s in save(rgba, "linglong", [480, 760, 1000]):
            print(p, s)

    # Chibi poses from the 1223x1286 desk-pet sheet; boxes stop above the
    # caption plates so no generated lettering ends up on the site.
    poses = {
        "q-idle": (5, 85, 300, 455),
        "q-walk": (310, 100, 610, 455),
        "q-sleep": (915, 165, 1215, 450),
        "q-think": (10, 505, 305, 830),
        "q-happy": (610, 505, 930, 830),
    }
    sheet = None
    for key, box in poses.items():
        if not want(key):
            continue
        if sheet is None:
            sheet = load(src("G-桌宠动作12.png"))
        rgba = trim(cutout(crop(sheet, box), tol=14, band=2, min_gap=40))
        for p, s in save(rgba, key, [280]):
            print(p, s)


if __name__ == "__main__":
    sys.exit(main())
