#!/usr/bin/env python3
"""
抖音大字卡片生成器（1080×1920）
用法: python3 gen_cards.py cards.json [outdir]
cards.json 结构:
[
  {"img": "17127003.jpg", "main": ["老板 也会失业"], "sub": ["40岁 公司没了", "三个月 没敢告诉家里人"],
   "main_size": 96, "sub_size": 52, "fit": false},
  ...
]
- img: 相对于 IMG_DIR（脚本内配置）或绝对路径
- main: 主标题行列表（黄字）
- sub: 副标题行列表（白字）
- fit: 原图非 9:16 时置 true（ImageOps.fit 居中裁剪到 1080×1920）
默认样式：黄 RGB(255,200,40) Bold 黑描边4px / 白 RGB(255,255,255) Bold 黑描边3px / 上下黑条遮罩110 alpha
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps

FONT_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
# 免费风景图库目录；可按环境修改
IMG_DIR = os.environ.get("IMG_DIR", "assets/free-stock")

def render(cfg, outname):
    img = cfg["img"]
    base = Image.open(img if os.path.isabs(img) else os.path.join(IMG_DIR, img)).convert("RGB")
    if cfg.get("fit"):
        base = ImageOps.fit(base, (1080, 1920), method=Image.LANCZOS, centering=(0.5, 0.5))
    W, H = base.size
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rectangle([0, 0, W, 220], fill=(0, 0, 0, 110))
    d.rectangle([0, H - 230, W, H], fill=(0, 0, 0, 110))
    main_size = cfg.get("main_size", 96)
    sub_size = cfg.get("sub_size", 52)
    fm = ImageFont.truetype(FONT_B, main_size)
    y = cfg.get("main_start", 240)
    for line in cfg["main"]:
        w = d.textlength(line, font=fm)
        d.text(((W - w) / 2, y), line, font=fm, fill=(255, 200, 40), stroke_width=4, stroke_fill=(0, 0, 0, 220))
        y += main_size + 16
    fs = ImageFont.truetype(FONT_B, sub_size)
    y = cfg.get("sub_start", 580)
    gap = cfg.get("sub_gap", 64)
    for line in cfg["sub"]:
        w = d.textlength(line, font=fs)
        d.text(((W - w) / 2, y), line, font=fs, fill=(255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0, 220))
        y += sub_size + gap - 18
    Image.alpha_composite(base.convert("RGBA"), ov).convert("RGB").save(outname)
    print("生成", outname)

def main():
    if len(sys.argv) < 2:
        print("用法: python3 gen_cards.py cards.json [outdir]")
        sys.exit(1)
    with open(sys.argv[1], encoding="utf-8") as f:
        cards = json.load(f)
    outdir = sys.argv[2] if len(sys.argv) > 2 else "cards"
    os.makedirs(outdir, exist_ok=True)
    for i, cfg in enumerate(cards, 1):
        render(cfg, os.path.join(outdir, f"c{i}.png"))

if __name__ == "__main__":
    main()
