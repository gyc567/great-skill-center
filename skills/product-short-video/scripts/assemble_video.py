#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""assemble_video.py — 产品短视频后期合成一键脚本

流程：拼接多段分镜视频 → 叠化转场(xfade) → 统一调色 → 精确时长对齐(tpad) →
      中文金色字幕叠加(Pillow 渲染 PNG + overlay) → 静音轨 → ffprobe QC。

设计目标：在「ffmpeg 未编译 libass/freetype」的环境下也能稳定烧录中文字幕。

用法示例：
  python3 assemble_video.py \\
    --inputs c1.mp4 c2.mp4 c3.mp4 \\
    --output outputs/final_15s.mp4 \\
    --transition 0.5 --target-duration 15 --grade dark \\
    --subtitle "温度，是最稀有的奢侈|6.0|9.4|0.62" \\
    --subtitle "¥9,999|11.0|15.0|center" \\
    --font "/System/Library/Fonts/Supplemental/Songti.ttc" --font-index 3 --color D4AF37

依赖：ffmpeg/ffprobe；字幕功能需要 Pillow（pip install Pillow）。
"""

import argparse
import os
import subprocess
import sys

FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Songti.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
]

GRADES = {
    "dark": "eq=contrast=1.08:saturation=0.85:brightness=-0.02,"
            "colorbalance=rs=0.03:bs=-0.03,vignette=PI/5",
    "warm": "eq=contrast=1.05:saturation=1.05:brightness=0.01,colorbalance=rs=0.04:bs=-0.02",
    # film: 纪实电影感 —— 低饱和灰绿 + 轻微冷调 + 暗角 + 胶片颗粒
    "film": "eq=saturation=0.78:contrast=1.06:brightness=-0.01,"
            "colorbalance=bs=0.02:gs=0.02,vignette=PI/6,noise=alls=5:allf=t",
    # nolan: 诺兰 IMAX 手持 —— 冷调低饱和胶片感（taupe/dust-blue，严禁暖色/橙青）
    # 低饱和 + 微提对比 + 冷偏移（蓝）+ 暗角 + 胶片颗粒
    "nolan": "eq=saturation=0.82:contrast=1.07:brightness=-0.012,"
             "colorbalance=bs=0.045:bm=0.02:rs=-0.03,"
             "vignette=PI/5.5,noise=alls=4:allf=t",
    "none": None,
}


def run(cmd, dry=False):
    printable = " ".join('"%s"' % c if " " in c else c for c in cmd)
    print("[cmd]", printable)
    if dry:
        return
    subprocess.run(cmd, check=True)


def ffprobe_value(path, entry, fmt="default=noprint_wrappers=1:nokey=1"):
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", entry, "-of", fmt, path],
        stderr=subprocess.STDOUT,
    ).decode().strip().splitlines()
    return [line for line in out if line]


def probe(path):
    dur = float(ffprobe_value(path, "format=duration")[0])
    wh = ffprobe_value(path, "stream=width,height")
    w, h = int(wh[0]), int(wh[1])
    fps_raw = ffprobe_value(path, "stream=r_frame_rate")[0]
    num, den = fps_raw.split("/")
    fps = float(num) / float(den) if float(den) else 24.0
    return dur, w, h, fps


def hex_to_rgb(hex_str):
    s = hex_str.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def render_text_png(text, out_path, canvas_w, font_path, font_index, rgb, font_ratio=0.058,
                    tracking_ratio=0.10, stroke_width=None, stroke_alpha=0.55,
                    shadow=True, shadow_alpha=0.50, shadow_blur=None):
    """用 Pillow 把一行文字渲染为透明 PNG（文字水平居中，逐字加字距）。

    为提升在浅色（冰面）与深色（岩石）背景上的可读性，默认给文字叠加：
      - 一层柔和的深色高斯投影（near-black、半透明、带偏移）；
      - 一圈 2~3px 的近黑半透明描边（stroke）。
    可通过 stroke_width / stroke_alpha / shadow_* 调整。
    """
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageFilter
    except ImportError:
        sys.exit("[error] 需要 Pillow 渲染字幕： pip install Pillow（或改用无字幕模式）")

    size = max(24, int(canvas_w * font_ratio))
    font = ImageFont.truetype(font_path, size, index=font_index)
    tracking = int(size * tracking_ratio)

    # 描边 / 投影半径（默认约 2~3px 描边 @ size≈71）
    if stroke_width is None:
        stroke_width = max(2, int(round(size * 0.035)))
    if shadow_blur is None:
        shadow_blur = max(2, int(round(size * 0.085)))
    pad = int(stroke_width + shadow_blur * 2 + 8)

    # 计算文字宽度（逐字 + 字距）
    text_w = sum(font.getlength(ch) for ch in text) + tracking * (len(text) - 1)
    line_h = int(size * 1.6)
    W = int(text_w) + pad * 2
    H = line_h + pad * 2

    def _draw_line(draw, ox, oy, fill, sw=0, sfill=None):
        x = ox
        for ch in text:
            draw.text((x, oy + line_h * 0.12), ch, font=font, fill=fill,
                      stroke_width=sw, stroke_fill=sfill)
            x += font.getlength(ch) + tracking

    near_black = (0, 0, 0)

    # 1) 柔和深色投影（模糊 + 下移偏移）
    if shadow:
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ds = ImageDraw.Draw(sh)
        off = max(1, int(round(size * 0.04)))
        sh_color = near_black + (int(255 * shadow_alpha),)
        _draw_line(ds, pad, pad + off, sh_color, sw=stroke_width, sfill=sh_color)
        img = sh.filter(ImageFilter.GaussianBlur(shadow_blur))
    else:
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    # 2) 描边 + 主色文字
    draw = ImageDraw.Draw(img)
    _draw_line(draw, pad, pad, rgb + (255,), sw=stroke_width,
               sfill=near_black + (int(255 * stroke_alpha),))

    img.save(out_path)
    return img.width, img.height


def parse_subtitle(spec):
    """spec: text|start|end|pos[|font_ratio]
    pos ∈ {top,center,bottom} 或 0~1 的纵向比例（表示文字块中心位置）；
    font_ratio 可选，覆盖全局字号比例（用于局部放大/缩小某一行）。"""
    parts = spec.split("|")
    if len(parts) < 3:
        sys.exit("[error] --subtitle 格式应为: 文本|开始秒|结束秒|位置[|字号比例]")
    text, start, end = parts[0], float(parts[1]), float(parts[2])
    pos = parts[3] if len(parts) > 3 and parts[3] != "" else "center"
    if pos not in ("top", "center", "bottom"):
        pos = float(pos)  # 相对纵向中心比例
    font_ratio = float(parts[4]) if len(parts) > 4 and parts[4] != "" else None
    return text, start, end, pos, font_ratio


def resolve_y(pos, frame_h, block_h):
    if isinstance(pos, float):
        y = frame_h * pos - block_h / 2
    elif pos == "top":
        y = frame_h * 0.10
    elif pos == "bottom":
        y = frame_h * 0.82 - block_h / 2
    else:  # center
        y = (frame_h - block_h) / 2
    return max(0, int(y))


def main():
    ap = argparse.ArgumentParser(description="产品短视频后期合成一键脚本")
    ap.add_argument("--inputs", nargs="+", required=True, help="分镜视频片段，按顺序传入")
    ap.add_argument("--output", required=True)
    ap.add_argument("--transition", type=float, default=0.5, help="叠化时长(秒)")
    ap.add_argument("--target-duration", type=float, default=None, help="目标总时长(秒)，用于 tpad 凑整")
    ap.add_argument("--grade", default="dark", choices=list(GRADES.keys()))
    ap.add_argument("--subtitle", action="append", default=[], help="文本|开始|结束|位置[|字号比例]（可多次）")
    ap.add_argument("--color", default="D4AF37", help="字幕颜色(hex)")
    ap.add_argument("--font", default=None)
    ap.add_argument("--font-index", type=int, default=3)
    ap.add_argument("--font-ratio", type=float, default=0.058)
    ap.add_argument("--tracking-ratio", type=float, default=0.10, help="字距 = 字号 × 该比例，越大字距越舒展")
    ap.add_argument("--fade", type=float, default=None, help="字幕淡入/淡出时长(秒)，默认自动")
    ap.add_argument("--crf", type=int, default=17, help="x264 CRF（胶片颗粒内容建议 21~23 控制体积）")
    ap.add_argument("--stroke-width", type=int, default=None, help="字幕描边宽度(px)，默认按字号自适应")
    ap.add_argument("--stroke-alpha", type=float, default=0.55, help="描边不透明度 0~1")
    ap.add_argument("--no-shadow", action="store_true", help="关闭字幕柔和投影")
    ap.add_argument("--shadow-alpha", type=float, default=0.50, help="投影不透明度 0~1")
    ap.add_argument("--audio", default=None, help="背景音乐/配音文件；给定时作为唯一音轨混入")
    ap.add_argument("--audio-bitrate", default="192k", help="输出音轨码率（默认 192k）")
    ap.add_argument("--fps", type=float, default=None, help="输出帧率，默认继承源")
    ap.add_argument("--size", default=None, help="输出尺寸 WxH，默认继承源")
    ap.add_argument("--no-audio", action="store_true", help="成片不含音轨")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    for p in args.inputs:
        if not os.path.isfile(p):
            sys.exit("[error] 找不到输入文件: %s" % p)

    # 读取素材参数
    metas = [probe(p) for p in args.inputs]
    durs = [m[0] for m in metas]
    W = int(args.size.split("x")[0]) if args.size else metas[0][1]
    H = int(args.size.split("x")[1]) if args.size else metas[0][2]
    fps_out = args.fps or metas[0][3]
    n = len(args.inputs)
    trans = args.transition if n > 1 else 0.0

    # 计算每段补帧后长度，使命中目标总时长
    if args.target_duration and n > 1:
        seg = (args.target_duration + (n - 1) * trans) / n
    elif args.target_duration and n == 1:
        seg = args.target_duration
    else:
        seg = None

    pads = [max(0.0, (seg - d)) if seg else 0.0 for d in durs]
    seg_len = [d + pd for d, pd in zip(durs, pads)]

    print("[info] %d 段素材 | 原始: %s | 补帧: %s | 叠化=%.2fs"
          % (n, ["%.3f" % d for d in durs], ["%.3f" % p for p in pads], trans))

    out_dir = os.path.dirname(os.path.abspath(args.output)) or "."
    os.makedirs(out_dir, exist_ok=True)
    render_dir = os.path.join(out_dir, "_render")
    os.makedirs(render_dir, exist_ok=True)

    # ---------- Step 1: 拼接 + 调色 ----------
    parts, labels = [], []
    for i, p in enumerate(args.inputs):
        vf = []
        if args.size:
            vf.append("scale=%d:%d" % (W, H))
        vf.append("setsar=1")
        if pads[i] > 0.001:
            vf.append("tpad=stop_mode=clone:stop_duration=%.4f" % pads[i])
        vf.append("setpts=PTS-STARTPTS")
        parts.append("[%d:v]%s[v%d]" % (i, ",".join(vf), i))
        labels.append("[v%d]" % i)

    if n > 1:
        prev = labels[0]
        for k in range(1, n):
            # 第 k 个转场的起点 = 前 k 段累计时长 - k*转场时长（支持各段不等长）
            offset = sum(seg_len[:k]) - k * trans
            lab = "[x%d]" % k
            parts.append("%s%sxfade=transition=fade:duration=%.3f:offset=%.4f%s"
                         % (prev, labels[k], trans, offset, lab))
            prev = lab
        graded = prev
    else:
        graded = labels[0]

    grade = GRADES.get(args.grade)
    if grade:
        parts.append("%s%s[vout]" % (graded, grade))
        final_label = "[vout]"
    else:
        final_label = graded

    # ---------- Step 1: 拼接 + 转场 + 调色（纯视频流，暂不带音轨） ----------
    step1 = os.path.join(render_dir, "base.mp4")
    cmd1 = ["ffmpeg", "-y"]
    for p in args.inputs:
        cmd1 += ["-i", p]
    cmd1 += ["-filter_complex", ";".join(parts), "-map", final_label,
             "-c:v", "libx264", "-crf", str(args.crf), "-pix_fmt", "yuv420p",
             "-r", "%.6f" % fps_out, "-an", step1]
    run(cmd1, args.dry_run)

    # ---------- Step 2: 字幕叠加（纯视频流） ----------
    video_stage = step1
    if args.subtitle:
        font = args.font
        if not font:
            font = next((f for f in FONT_CANDIDATES if os.path.isfile(f)), None)
        if not font:
            sys.exit("[error] 未找到中文字体，请用 --font 指定 .ttc/.ttf")

        rgb = hex_to_rgb(args.color)
        pngs = []
        for idx, spec in enumerate(args.subtitle):
            text, start, end, pos, font_ratio = parse_subtitle(spec)
            ratio = font_ratio if font_ratio else args.font_ratio
            png = os.path.join(render_dir, "sub%d.png" % idx)
            w, h = render_text_png(text, png, W, font, args.font_index, rgb,
                                   ratio, args.tracking_ratio,
                                   stroke_width=args.stroke_width,
                                   stroke_alpha=args.stroke_alpha,
                                   shadow=not args.no_shadow,
                                   shadow_alpha=args.shadow_alpha)
            y = resolve_y(pos, H, h)
            if args.fade is not None:
                fade = args.fade
            else:
                fade = min(0.6, max(0.2, (end - start) / 4.0))
            pngs.append(dict(png=png, start=start, end=end, y=y, fade=fade))

        cmd2 = ["ffmpeg", "-y", "-i", step1]
        for s in pngs:
            cmd2 += ["-loop", "1", "-i", s["png"]]

        chain, prev = [], "[0:v]"
        for i, s in enumerate(pngs):
            in_idx = i + 1
            fade_out_start = max(s["start"], s["end"] - s["fade"])
            chain.append(
                "[%d:v]format=rgba,fade=in:st=%.3f:d=%.3f:alpha=1,"
                "fade=out:st=%.3f:d=%.3f:alpha=1[s%d]"
                % (in_idx, s["start"], s["fade"], fade_out_start, s["fade"], i)
            )
            out_lab = "[b%d]" % i
            # shortest=1：把输出限制在主输入（正片）时长内。
            # 注意：-loop 1 的 PNG 输入是无限流，若不设 shortest，overlay 输出会无限延长。
            # 这里用滤镜级 shortest=1 而不是输出级 -shortest，避免后者引起的掉帧问题。
            chain.append("%s[s%d]overlay=x=(W-w)/2:y=%d:shortest=1:"
                         "enable='between(t,%.3f,%.3f)'%s"
                         % (prev, i, s["y"], s["start"], s["end"], out_lab))
            prev = out_lab

        subbed = os.path.join(render_dir, "subbed.mp4")
        cmd2 += ["-filter_complex", ";".join(chain), "-map", prev,
                 "-c:v", "libx264", "-crf", str(args.crf), "-pix_fmt", "yuv420p",
                 "-r", "%.6f" % fps_out, "-an", subbed]
        if args.target_duration:
            cmd2 += ["-t", "%.3f" % args.target_duration]
        run(cmd2, args.dry_run)
        video_stage = subbed

    # ---------- Step 3: 音轨混入（视频流 -c:v copy 不重编码） ----------
    dur_video = args.target_duration or probe(video_stage)[0]
    if args.no_audio:
        cmd3 = ["ffmpeg", "-y", "-i", video_stage, "-c", "copy", args.output]
    elif args.audio:
        if not os.path.isfile(args.audio):
            sys.exit("[error] 找不到音频文件: %s" % args.audio)
        cmd3 = ["ffmpeg", "-y", "-i", video_stage, "-i", args.audio,
                "-map", "0:v:0", "-map", "1:a:0",
                "-c:v", "copy", "-c:a", "aac", "-b:a", args.audio_bitrate,
                "-t", "%.3f" % dur_video, args.output]
    else:
        cmd3 = ["ffmpeg", "-y", "-i", video_stage,
                "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                "-map", "0:v:0", "-map", "1:a:0",
                "-c:v", "copy", "-c:a", "aac", "-b:a", args.audio_bitrate,
                "-t", "%.3f" % dur_video, args.output]
    run(cmd3, args.dry_run)

    # ---------- Step 3: QC ----------
    if not args.dry_run:
        dur, w, h, fps = probe(args.output)
        print("=" * 52)
        print("[QC] %s" % args.output)
        print("     时长=%.3fs  尺寸=%dx%d  帧率=%.2f  fps" % (dur, w, h, fps))
        print("=" * 52)
    print("[done] 成片：%s" % args.output)


if __name__ == "__main__":
    main()
