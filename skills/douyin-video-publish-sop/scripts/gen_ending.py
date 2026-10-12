#!/usr/bin/env python3
"""
抖音结尾灰词埋词帧生成器（1080×1920，0.1s 尾帧用）
用法: python3 gen_ending.py words.json [outpath]
words.json:
{"img": "4030371.jpg", "rows": ["词1 词2 ...", "..."]}
默认参数（douyin-search-word-ending 已验证）：
亮灰 RGB(205,205,205) / alpha 115 (45%) / Bold 24px / 行距42 / y起675 / 背景 fit 9:16
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps

FONT_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
IMG_DIR = os.environ.get("IMG_DIR", "assets/free-stock")

def main():
    if len(sys.argv) < 2:
        print("用法: python3 gen_ending.py words.json [outpath]")
        sys.exit(1)
    with open(sys.argv[1], encoding="utf-8") as f:
        cfg = json.load(f)
    out = sys.argv[2] if len(sys.argv) > 2 else "cards/ending.png"
    img = cfg["img"]
    base = Image.open(img if os.path.isabs(img) else os.path.join(IMG_DIR, img)).convert("RGB")
    base = ImageOps.fit(base, (1080, 1920), method=Image.LANCZOS, centering=(0.5, 0.5))
    W, H = base.size
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    f = ImageFont.truetype(FONT_B, 24)
    y = cfg.get("y", 675)
    for row in cfg["rows"]:
        w = d.textlength(row, font=f)
        d.text(((W - w) / 2, y), row, font=f, fill=(205, 205, 205, 115))
        y += 42
    os.makedirs(os.path.dirname(out), exist_ok=True) if os.path.dirname(out) else None
    Image.alpha_composite(base.convert("RGBA"), ov).convert("RGB").save(out)
    print("尾帧生成OK", out)

if __name__ == "__main__":
    main()
