#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""探店爆款封面风封面生成器（1080×1920 竖屏）

风格范式（来自真实探店爆款封面拆解）：
  真人照片全铺背景 + 人物靠右 + 左侧压暗 + 黄字黑边三层大标题 + 底部深色圆角色条幅。
右侧裁剪让人物靠右的同时可去掉照片右下角的 AI 生成水印。

用法：
  python3 design_cover.py --photo 人物照片.jpg --out 封面.png \
      --line-white "一个月用 AI" --line-gold "直接省了" --line-hero "30 万" \
      --bar1 "6 个岗位，AI 全包了" --bar2 "第 7 个下条补 · 先截图保存"

可选参数：
  --crop-x 120   裁剪起点（控制人物水平位置，越小越靠右）
  --text-x 64    文字左边界
  --bg-dim 0.94  照片整体亮度系数
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFont, ImageEnhance

W, H = 1080, 1920

# ---------- 字体解析（macOS 优先，Linux 回退） ----------
FONT_CANDIDATES = [
    "/System/Library/Fonts/Hiragino Sans GB.ttc",            # macOS index 2 = W6
    "/System/Library/Fonts/Supplemental/Songti.ttc",         # macOS index 0 = Black
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttf",
    "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc",
]
HG_W6 = next((p for p in FONT_CANDIDATES if os.path.exists(p)), None)
if HG_W6 is None:
    sys.exit("错误：未找到可用中文字体，请安装 Noto Sans/Serif CJK 或在 FONT_CANDIDATES 中添加字体路径")
HG_W6_INDEX = 2 if "Hiragino" in HG_W6 else 0

# ---------- 配色（金钱主题：黄=钱，高饱和） ----------
YELLOW = (255, 214, 74)
YELLOW_TOP = (255, 233, 140)
YELLOW_BOT = (255, 178, 30)
DARK = (10, 12, 18)
WHITE = (250, 250, 250)


def vgrad(y_top, y_bot, top, bot):
    """垂直渐变层（RGBA）"""
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    for yy in range(max(0, int(y_top)), min(H, int(y_bot))):
        t = (yy - y_top) / max(1, y_bot - y_top)
        c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)) + (255,)
        gd.line([(0, yy), (W, yy)], fill=c)
    return g


def build(photo_path, out, line_white, line_gold, line_hero, bar1, bar2,
          crop_x=120, text_x=64, bg_dim=0.94):
    # ---------- 1. 照片铺满 + 右侧裁剪（人物靠右，裁掉右下水印） ----------
    photo = Image.open(photo_path).convert("RGB")
    scale = H / photo.height
    photo = photo.resize((int(photo.width * scale), H), Image.LANCZOS)
    photo = photo.crop((crop_x, 0, crop_x + W, H))
    photo = ImageEnhance.Brightness(photo).enhance(bg_dim)
    photo = ImageEnhance.Color(photo).enhance(1.06)

    # ---------- 2. 左侧压暗渐变（保证黄字可读）+ 底部轻压暗 ----------
    scrim = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(scrim)
    for x in range(W):
        t = max(0.0, 1 - x / 860)  # x=0 处 1，x>=860 处 0
        sd.line([(x, 0), (x, H)], fill=int(150 * t))
    black = Image.new("RGB", (W, H), (0, 0, 0))
    photo.paste(black, (0, 0), scrim)
    scrim2 = Image.new("L", (W, H), 0)
    sd2 = ImageDraw.Draw(scrim2)
    for y in range(H):
        t = max(0.0, (y - 1250) / 670)
        sd2.line([(0, y), (W, y)], fill=int(70 * t))
    photo.paste(black, (0, 0), scrim2)

    img = photo.convert("RGBA")

    def font(size):
        return ImageFont.truetype(HG_W6, size, index=HG_W6_INDEX)

    def stroke_text(xy, text, size, fill_color, stroke=12, anchor="lm"):
        """深色描边 + 纯色填充"""
        f = font(size)
        d = ImageDraw.Draw(img)
        d.text(xy, text, font=f, fill=DARK, stroke_width=stroke, stroke_fill=DARK, anchor=anchor)
        d.text(xy, text, font=f, fill=fill_color, anchor=anchor)

    def grad_stroke_text(xy, text, size, stroke=14, anchor="lm"):
        """深色描边 + 金色渐变填充"""
        f = font(size)
        d = ImageDraw.Draw(img)
        d.text(xy, text, font=f, fill=DARK, stroke_width=stroke, stroke_fill=DARK, anchor=anchor)
        mask = Image.new("L", (W, H), 0)
        md = ImageDraw.Draw(mask)
        md.text(xy, text, font=f, fill=255, anchor=anchor)
        x0, y0, x1, y1 = md.textbbox(xy, text, font=f, anchor=anchor)
        img.paste(vgrad(y0, y1, YELLOW_TOP, YELLOW_BOT), (0, 0), mask)
        return (x0, y0, x1, y1)

    # ---------- 3. 三层大标题 ----------
    stroke_text((text_x, 400), line_white, 82, WHITE, stroke=10)      # 白字
    grad_stroke_text((text_x, 585), line_gold, 138, stroke=14)        # 金黄渐变
    grad_stroke_text((text_x, 820), line_hero, 205, stroke=16)        # 超大金色数字

    # ---------- 4. 底部深色条幅 ----------
    def dark_bar(y, parts, h=92, pad_x=56):
        """parts: [(text, color, size)]，关键词用黄色"""
        d = ImageDraw.Draw(img)
        fonts = [font(s) for (_, _, s) in parts]
        total = sum(d.textlength(t, font=f) for (t, _, _), f in zip(parts, fonts))
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        od.rounded_rectangle([text_x - 24, y, text_x - 24 + total + pad_x * 2, y + h],
                             radius=14, fill=(8, 11, 20, 218))
        img.alpha_composite(ov)
        x = text_x - 24 + pad_x
        for (t, c, s), f in zip(parts, fonts):
            d.text((x, y + h / 2), t, font=f, fill=c, anchor="lm")
            x += d.textlength(t, font=f)

    def bar_parts(spec):
        """把 '白字[黄字]白字' 简易语法拆成 parts；无标记则整条白字"""
        parts, buf, color = [], "", WHITE
        i = 0
        while i < len(spec):
            ch = spec[i]
            if ch == "[":
                if buf:
                    parts.append((buf, color, 46))
                buf, color, i = "", YELLOW, i + 1
                continue
            if ch == "]":
                parts.append((buf, color, 46))
                buf, color, i = "", WHITE, i + 1
                continue
            buf += ch
            i += 1
        if buf:
            parts.append((buf, color, 46))
        return parts

    dark_bar(1470, bar_parts(bar1))
    dark_bar(1600, bar_parts(bar2))

    img.convert("RGB").save(out, quality=95)
    print("saved:", out)


def main():
    ap = argparse.ArgumentParser(description="探店爆款封面风封面生成器")
    ap.add_argument("--photo", required=True, help="人物照片路径")
    ap.add_argument("--out", required=True, help="输出 PNG 路径")
    ap.add_argument("--line-white", default="一个月用 AI", help="第一行白字")
    ap.add_argument("--line-gold", default="直接省了", help="第二行金色渐变字")
    ap.add_argument("--line-hero", default="30 万", help="第三行超大金色数字（视觉焦点）")
    ap.add_argument("--bar1", default="6 个岗位，[AI] 全包了", help="底部条幅1，[ ] 内为黄色关键词")
    ap.add_argument("--bar2", default="第 7 个下条补 · [先截图保存]", help="底部条幅2")
    ap.add_argument("--crop-x", type=int, default=120, help="裁剪起点，控制人物水平位置")
    ap.add_argument("--text-x", type=int, default=64, help="文字左边界")
    ap.add_argument("--bg-dim", type=float, default=0.94, help="照片亮度系数")
    args = ap.parse_args()
    if not os.path.exists(args.photo):
        sys.exit(f"错误：照片不存在 {args.photo}")
    build(args.photo, args.out, args.line_white, args.line_gold, args.line_hero,
          args.bar1, args.bar2, args.crop_x, args.text_x, args.bg_dim)


if __name__ == "__main__":
    main()
