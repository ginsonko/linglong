"""Generate favicon / app icons / og-image from the processed art in
site/assets/img (produced by make-art.py / make-art-more.py).

py -3 scripts/make-icons.py
"""
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "site", "assets", "img")
FONTS_DIR = os.path.join(os.environ["LOCALAPPDATA"], "Microsoft", "Windows", "Fonts")
SERIF = os.path.join(FONTS_DIR, "SourceHanSerifSC-Medium.otf")

BG = (22, 18, 15, 255)
RED = (180, 58, 46, 255)


def load(name):
    return Image.open(os.path.join(IMG, name)).convert("RGBA")


def rounded(im, rad):
    mask = Image.new("L", im.size, 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle([0, 0, im.width, im.height], rad, fill=255)
    im.putalpha(mask)
    return im


def icon(size, apple=False):
    """face-laughing head on a dark tile with a red glow."""
    face = load("face-laughing-240.webp")
    im = Image.new("RGBA", (size, size), BG)
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(glow)
    d.ellipse([size * .18, size * .30, size * .82, size * .94], fill=(180, 58, 46, 110))
    glow = glow.filter(ImageFilter.GaussianBlur(size * .12))
    im.alpha_composite(glow)
    f = face.resize((round(size * .86), round(face.height * size * .86 / face.width)), Image.LANCZOS)
    im.alpha_composite(f, (round((size - f.width) / 2), round(size * .12)))
    if apple:
        out = Image.new("RGBA", (size, size), BG)
        out.alpha_composite(rounded(im, round(size * .22)))
        return out.convert("RGB")
    return rounded(im, round(size * .22))


def og():
    w, h = 1200, 630
    im = Image.new("RGBA", (w, h), BG)
    d = ImageDraw.Draw(im)
    # 红色氛围光
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([w * .52, -h * .25, w * 1.15, h * .85], fill=(180, 58, 46, 90))
    gd.ellipse([-w * .2, h * .5, w * .25, h * 1.4], fill=(46, 139, 127, 28))
    glow = glow.filter(ImageFilter.GaussianBlur(80))
    im.alpha_composite(glow)
    # 立绘
    girl = load("linglong-730.webp")
    gh = round(h * 1.08)
    g = girl.resize((round(girl.width * gh / girl.height), gh), Image.LANCZOS)
    im.alpha_composite(g, (w - g.width - 60, h - g.height + 40))
    # 文案
    title = ImageFont.truetype(SERIF, 92)
    sub = ImageFont.truetype(SERIF, 40)
    en = ImageFont.truetype(SERIF, 26)
    d.text((80, 150), "说一句话。", font=title, fill=(246, 244, 238))
    d.text((80, 262), "一个团队替你做完。", font=title, fill=(214, 90, 73))
    d.text((82, 400), "玲珑工坊 · 装在电脑上的 AI 创作团队", font=sub, fill=(246, 244, 238, 220))
    d.text((82, 470), "LINGLONG STUDIO · v0.6.0", font=en, fill=(201, 169, 106))
    d.rectangle([80, 128, 150, 133], fill=RED)
    im.convert("RGB").save(os.path.join(IMG, "og-image.jpg"), quality=86)


def main():
    icon(32).save(os.path.join(IMG, "favicon-32.png"))
    icon(192).save(os.path.join(IMG, "icon-192.png"))
    icon(512).save(os.path.join(IMG, "icon-512.png"))
    icon(180, apple=True).save(os.path.join(IMG, "apple-touch-icon.png"))
    og()
    for n in ("favicon-32.png", "icon-192.png", "icon-512.png", "apple-touch-icon.png", "og-image.jpg"):
        print(n, os.path.getsize(os.path.join(IMG, n)) // 1024, "KB")


if __name__ == "__main__":
    main()
