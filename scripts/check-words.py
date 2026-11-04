"""Scan site copy for forbidden words (project rules) and ad-law risk words.

py -3 scripts/check-words.py   -> exit 1 on any hit.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")

# 项目禁用词（REL-060 规矩）
BANNED = ["看不见", "中国台湾", "世界第一", "世界首个", "首个", "意识", "AGI"]
# 广告法风险词（出现即报告，人工确认语境）
AD_LAW = [
    "第一", "首选", "顶级", "顶尖", "极致", "最佳", "最强", "最好", "最先进",
    "最大", "最低", "最贵", "唯一", "独一无二", "100%", "百分百", "永久",
    "全网最低", "全国领先", "世界领先", "领先全球", "领导者", "填补空白",
    "史上", "国家级", "世界级", "王牌", "销量冠军", "绝无仅有", "史无前例",
]
# 白名单：产品名里的固定用法不算违规
WHITELIST = ["万能创作终端"]
# 序数/日常用法不算广告法违规：第一次、第一篇、两步走……
ORDINAL = re.compile(r"第[一二三四五六七八九十\d]+[次篇位个步期款行条]")

EXT = (".html", ".js")  # CSS 不扫（会误伤 100%、Hiragino 之类）


def scan():
    hits = []
    for dirpath, _dirs, files in os.walk(SITE):
        for f in files:
            if os.path.splitext(f)[1] not in EXT:
                continue
            path = os.path.join(dirpath, f)
            with open(path, encoding="utf-8") as fh:
                in_style = False
                for ln, line in enumerate(fh, 1):
                    # CSS 不扫（会误伤 100%、Hiragino 之类）；site.css 内联进 HTML 后同样跳过
                    if "<style" in line:
                        in_style = True
                    if in_style:
                        if "</style>" in line:
                            in_style = False
                        continue
                    for w in WHITELIST:
                        line = line.replace(w, "")
                    line = ORDINAL.sub("", line)
                    for word in BANNED:
                        # AGI 只按大写整体算，避免误伤 Hiragino 之类
                        found = (word in line) if word == "AGI" else (word.lower() in line.lower())
                        if found:
                            hits.append((path, ln, "禁用词", word, line.strip()[:80]))
                    for word in AD_LAW:
                        if word in line:
                            hits.append((path, ln, "广告法", word, line.strip()[:80]))
    return hits


def main():
    hits = scan()
    if not hits:
        print("OK：没有发现禁用词或广告法风险词。")
        return 0
    for path, ln, kind, word, line in hits:
        rel = os.path.relpath(path, ROOT)
        print(f"[{kind}] {rel}:{ln} 「{word}」 {line}")
    print(f"\n共 {len(hits)} 处，请逐条确认或修改。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
