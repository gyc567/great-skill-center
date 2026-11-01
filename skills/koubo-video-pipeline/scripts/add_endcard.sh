#!/usr/bin/env bash
# 片尾福利卡片追加：原视频结尾交叉淡入到全屏静态福利卡片（方便观众截图保存）
#
# 用法：
#   ./add_endcard.sh <原视频.mp4> <福利图.jpg> <输出.mp4> [卡片时长秒=3.5] [转场秒=0.5]
#
# 说明：
#   - 福利图等比缩放居中放入 1080×1920 画布，背景色自动从图片四角采样均值
#   - 卡片静态展示（无任何动画），保证截图清晰
#   - xfade offset = 原视频时长 - 转场时长；总时长 = 原视频 + 卡片 - 转场
#   - 原人声淡出后补静音至全片结束
set -euo pipefail

VIDEO="$1"
IMAGE="$2"
OUT="$3"
CARD_DUR="${4:-3.5}"
FADE_DUR="${5:-0.5}"

[ -f "$VIDEO" ] || { echo "错误：视频不存在 $VIDEO"; exit 1; }
[ -f "$IMAGE" ] || { echo "错误：图片不存在 $IMAGE"; exit 1; }

# ---------- 1. 探测原视频参数 ----------
read -r V_W V_H V_FPS V_DUR < <(ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height,r_frame_rate:format=duration \
  -of csv=p=0 "$VIDEO" | awk -F'[,/]' '{printf "%d %d %.4f %.4f", $1, $2, $3, $4}')
echo "原视频: ${V_W}x${V_H} @ ${V_FPS}fps, 时长 ${V_DUR}s"

# ---------- 2. 从图片四角采样背景色 ----------
BG_HEX=$(python3 - "$IMAGE" <<'PYEOF'
import sys
from PIL import Image
im = Image.open(sys.argv[1]).convert("RGB")
w, h = im.size
pts = [(2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3)]
r = sum(im.getpixel(p)[0] for p in pts) // 4
g = sum(im.getpixel(p)[1] for p in pts) // 4
b = sum(im.getpixel(p)[2] for p in pts) // 4
print("0x%02X%02X%02X" % (r, g, b))
PYEOF
)
echo "卡片背景色(采样四角均值): $BG_HEX"

# ---------- 3. 生成片尾卡片（静态，24fps 兼容多数源） ----------
FPS=$(python3 -c "print(int(round(${V_FPS:-24})))")
ffmpeg -y -v error -loop 1 -i "$IMAGE" -t "$CARD_DUR" \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=${BG_HEX},format=yuv420p" \
  -r "$FPS" -c:v libx264 -preset medium -crf 18 -an /tmp/koubo_endcard.mp4

# ---------- 4. xfade 交叉溶解 + 音频淡出补静音 ----------
OFFSET=$(python3 -c "print(round($V_DUR - $FADE_DUR, 3))")
TOTAL=$(python3 -c "print(round($V_DUR + $CARD_DUR - $FADE_DUR, 3))")
FADE_OUT_ST=$(python3 -c "print(round($V_DUR - 0.425, 3))")
echo "xfade offset=${OFFSET}s, 总时长=${TOTAL}s"

ffmpeg -y -v error -i "$VIDEO" -i /tmp/koubo_endcard.mp4 \
  -filter_complex "[0:v]fps=${FPS},format=yuv420p[v0];[1:v]fps=${FPS},format=yuv420p[v1];[v0][v1]xfade=transition=fade:duration=${FADE_DUR}:offset=${OFFSET},format=yuv420p[v];[0:a]afade=t=out:st=${FADE_OUT_ST}:d=0.4,apad,atrim=0:${TOTAL},asetpts=N/SR/TB[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -preset medium -crf 18 -c:a aac -b:a 128k -movflags +faststart \
  "$OUT"

rm -f /tmp/koubo_endcard.mp4
echo "saved: $OUT"
