#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""海报风片头标题页生成器（1080×1920 竖屏）

深色渐变底 + 金色径向光晕 + 粗宋大标题 + 数字金色高亮块 + 徽章 pill + CTA 胶囊。
适用于无参考封面图时制作片头/封面，交付 PNG 同时用作视频片头与视频号封面。

用法：
  python3 design_title_card.py --out 片头.png \
      --badge "2026 · 老板必看" --line1 "一个月用 AI" --hero "直接省了 " --chip "30 万" \
      --line3 "就靠换了这 6 个岗位" --cta "★ 先截图保存 · 红心关注 ★" --foot "第 7 个工具 · 下条视频补"
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920

# ---------- 字体解析（macOS 优先，Linux 回退） ----------
SONG_BLACK_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Songti.ttc",                 # macOS index 0 = Black
    "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc",
    "/usr/share/fonts/truetype/noto/NotoSerifCJK-Bold.ttf",
]
HG_CANDIDATES = [
    "/System/Library/Fonts/Hiragino Sans GB.ttc",                    # macOS 0=W3, 2=W6
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttf",
]
SONG_BLACK = next((p for p in SONG_BLACK_CANDIDATES if os.path.exists(p)), None)
HG = next((p for p in HG_CANDIDATES if os.path.exists(p)), None)
if SONG_BLACK is None or HG is None:
    sys.exit("错误：未找到可用中文字体，请安装 Noto Sans/Serif CJK 或在脚本字体候选列表中添加路径")
SONG_IDX = 0 if "Songti" in SONG_BLACK else 0
HG_W6_IDX = 2 if "Hiragino" in HG else 0
HG_W3_IDX = 0

# ---------- 配色 ----------
NAVY_TOP = (9, 17, 35)
NAVY_BOT = (19, 34, 64)
GOLD = (255, 196, 82)
GOLD_LIGHT = (255, 235, 175)
GOLD_DEEP = (255, 172, 40)
WHITE = (246, 248, 252)
WHITE_80 = (203, 210, 224)


def vgrad(size, top, bottom):
    """垂直渐变图"""
    w, h = size
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(1, h - 1)
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        d.line([(0, y), (w, y)], fill=c)
    return img


def radial_glow(size, center, radius, color, peak=95, blur=70):
    """径向光晕层（RGBA）"""
    m = Image.new("L", size, 0)
    md = ImageDraw.Draw(m)
    cx, cy = center
    steps = 90
    for i in range(steps, 0, -1):
        r = int(radius * i / steps)
        v = int(peak * (1 - i / steps) ** 2)
        md.ellipse([cx - r, cy - r, cx + r, cy + r], fill=v)
    m = m.filter(ImageFilter.GaussianBlur(blur))
    layer = Image.new("RGB", size, color)
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    out.paste(layer, (0, 0), m)
    return out


def build(out, badge, line1, hero, chip, line3, cta, foot):
    # ---------- 1. 背景：深海军蓝渐变 + 光晕 ----------
    bg = vgrad((W, H), NAVY_TOP, NAVY_BOT).convert("RGBA")
    bg.alpha_composite(radial_glow((W, H), (540, 700), 720, (255, 190, 90), peak=80, blur=90))
    bg.alpha_composite(radial_glow((W, H), (540, 120), 520, (90, 130, 200), peak=42, blur=90))
    draw = ImageDraw.Draw(bg)

    # ---------- 2. 装饰：四角细金框 + 中部双圆环 ----------
    def corner_brackets(d, inset=56, arm=96, width=5, color=(255, 196, 82, 150)):
        d.line([(inset, inset + arm), (inset, inset), (inset + arm, inset)], fill=color, width=width)
        d.line([(W - inset - arm, inset), (W - inset, inset), (W - inset, inset + arm)], fill=color, width=width)
        d.line([(inset, H - inset - arm), (inset, H - inset), (inset + arm, H - inset)], fill=color, width=width)
        d.line([(W - inset - arm, H - inset), (W - inset, H - inset), (W - inset, H - inset - arm)], fill=color, width=width)

    corner_brackets(draw)
    ring = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring)
    rd.ellipse([540 - 400, 700 - 400, 540 + 400, 700 + 400], outline=(255, 196, 82, 60), width=3)
    rd.ellipse([540 - 470, 700 - 470, 540 + 470, 700 + 470], outline=(255, 196, 82, 28), width=2)
    bg.alpha_composite(ring)
    draw = ImageDraw.Draw(bg)

    # ---------- 3. 顶部徽章 pill ----------
    badge_font = ImageFont.truetype(HG, 38, index=HG_W6_IDX)
    bt_w = draw.textlength(badge, font=badge_font)
    bx0, by0, bx1, by1 = 540 - bt_w / 2 - 56, 246, 540 + bt_w / 2 + 56, 344
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=49, outline=(*GOLD, 235), width=3)
    draw.text((540, (by0 + by1) / 2), badge, font=badge_font, fill=(*GOLD, 255), anchor="mm")

    # ---------- 4. 第一行 ----------
    line1_font = ImageFont.truetype(HG, 94, index=HG_W6_IDX)
    draw.text((540, 512), line1, font=line1_font, fill=(*WHITE, 255), anchor="mm")

    # ---------- 5. 主标题：金色渐变字 + 数字高亮块 ----------
    hero_size = 150
    while hero_size > 90:
        f = ImageFont.truetype(SONG_BLACK, hero_size, index=SONG_IDX)
        if draw.textlength(hero, font=f) + draw.textlength(chip, font=f) <= 940:
            break
        hero_size -= 4
    hero_font = ImageFont.truetype(SONG_BLACK, hero_size, index=SONG_IDX)
    hero_y = 730
    w1 = draw.textlength(hero, font=hero_font)
    w2 = draw.textlength(chip, font=hero_font)
    x_start = 540 - (w1 + w2) / 2

    def gold_vgrad(y_top, y_bot):
        g = Image.new("RGB", (W, H))
        gd = ImageDraw.Draw(g)
        for yy in range(max(0, int(y_top)), min(H, int(y_bot))):
            t = (yy - y_top) / max(1, y_bot - y_top)
            c = tuple(int(GOLD_LIGHT[i] + (GOLD_DEEP[i] - GOLD_LIGHT[i]) * t) for i in range(3))
            gd.line([(0, yy), (W, yy)], fill=c)
        return g

    # 5a. 金色渐变字 + 外发光
    hmask = Image.new("L", (W, H), 0)
    hd = ImageDraw.Draw(hmask)
    hd.text((x_start, hero_y), hero, font=hero_font, fill=255, anchor="lm")
    gx0, gy0, gx1, gy1 = hd.textbbox((x_start, hero_y), hero, font=hero_font, anchor="lm")
    glow_mask = hmask.filter(ImageFilter.GaussianBlur(26)).point(lambda v: int(v * 0.45))
    bg.paste(Image.new("RGB", (W, H), GOLD_DEEP), (0, 0), glow_mask)
    bg.paste(gold_vgrad(gy0, gy1), (0, 0), hmask)

    # 5b. 数字金色圆角高亮块 + 深色字
    bx0 = x_start + w1 - 16
    bx1 = x_start + w1 + w2 + 16
    by0 = hero_y - hero_size * 0.66
    by1 = hero_y + hero_size * 0.66
    chip_mask = Image.new("L", (W, H), 0)
    cd = ImageDraw.Draw(chip_mask)
    cd.rounded_rectangle([bx0, by0, bx1, by1], radius=22, fill=255)
    chip_glow = chip_mask.filter(ImageFilter.GaussianBlur(30)).point(lambda v: int(v * 0.40))
    bg.paste(Image.new("RGB", (W, H), GOLD_DEEP), (0, 0), chip_glow)
    bg.paste(gold_vgrad(by0, by1), (0, 0), chip_mask)
    draw = ImageDraw.Draw(bg)
    draw.text((x_start + w1 + w2 / 2, hero_y), chip, font=hero_font, fill=(14, 22, 44, 255), anchor="mm")
    draw = ImageDraw.Draw(bg)

    # ---------- 6. 金色装饰分隔条 ----------
    bar_y = 872
    draw.rounded_rectangle([540 - 300, bar_y, 540 + 300, bar_y + 12], radius=6, fill=(*GOLD, 255))
    draw.rounded_rectangle([540 - 26, bar_y + 30, 540 + 26, bar_y + 38], radius=4, fill=(255, 255, 255, 110))

    # ---------- 7. 第三行 ----------
    line3_font = ImageFont.truetype(HG, 60, index=HG_W6_IDX)
    draw.text((540, 985), line3, font=line3_font, fill=(*WHITE_80, 255), anchor="mm")

    # ---------- 8. 底部 CTA 金色 pill ----------
    cta_font = ImageFont.truetype(HG, 46, index=HG_W6_IDX)
    ct_w = draw.textlength(cta, font=cta_font)
    cx0, cy0, cx1, cy1 = 540 - ct_w / 2 - 64, 1516, 540 + ct_w / 2 + 64, 1624
    pill_mask = Image.new("L", (W, H), 0)
    pd = ImageDraw.Draw(pill_mask)
    pd.rounded_rectangle([cx0, cy0, cx1, cy1], radius=54, fill=255)
    pgrad = Image.new("RGB", (W, H))
    pgd = ImageDraw.Draw(pgrad)
    for yy in range(int(cy0), int(cy1)):
        t = (yy - cy0) / max(1, cy1 - cy0)
        c = tuple(int(GOLD_LIGHT[i] + (GOLD_DEEP[i] - GOLD_LIGHT[i]) * t) for i in range(3))
        pgd.line([(0, yy), (W, yy)], fill=c)
    bg.paste(pgrad, (0, 0), pill_mask)
    draw = ImageDraw.Draw(bg)
    draw.text((540, (cy0 + cy1) / 2), cta, font=cta_font, fill=(16, 24, 46, 255), anchor="mm")

    # ---------- 9. 底部小字 ----------
    foot_font = ImageFont.truetype(HG, 34, index=HG_W3_IDX)
    draw.text((540, 1700), foot, font=foot_font, fill=(255, 214, 140, 170), anchor="mm")

    bg.convert("RGB").save(out, quality=95)
    print("saved:", out)
    print("hero size:", hero_size)


def main():
    ap = argparse.ArgumentParser(description="海报风片头标题页生成器")
    ap.add_argument("--out", required=True, help="输出 PNG 路径")
    ap.add_argument("--badge", default="2026 · 老板必看")
    ap.add_argument("--line1", default="一个月用 AI")
    ap.add_argument("--hero", default="直接省了 ", help="主标题渐变部分（注意保留尾部空格以对齐高亮块）")
    ap.add_argument("--chip", default="30 万", help="主标题高亮块部分（数字焦点）")
    ap.add_argument("--line3", default="就靠换了这 6 个岗位")
    ap.add_argument("--cta", default="★ 先截图保存 · 红心关注 ★")
    ap.add_argument("--foot", default="第 7 个工具 · 下条视频补")
    args = ap.parse_args()
    build(args.out, args.badge, args.line1, args.hero, args.chip,
          args.line3, args.cta, args.foot)


if __name__ == "__main__":
    main()
