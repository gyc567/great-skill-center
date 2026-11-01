#!/usr/bin/env bash
# 片头接入：封面/标题页作为片头，黑场淡入 → 停留 → xfade 交叉溶解进正片
#
# 用法：
#   ./add_opening.sh <封面.png> <正片视频.mp4> <输出.mp4> [片头停留秒=2.5] [转场秒=0.5]
#
# 说明：
#   - 片头 0–0.35s 黑场淡入，静音展示；转场起点 = 片头停留 - 转场
#   - 正片音频 adelay 对齐：口播从片头停留时刻开始
#   - 总时长 = 片头停留 + 正片时长 - 转场
set -euo pipefail

COVER="$1"
VIDEO="$2"
OUT="$3"
HEAD_DUR="${4:-2.5}"
FADE_DUR="${5:-0.5}"
FADE_IN_DUR="0.35"

[ -f "$COVER" ] || { echo "错误：封面不存在 $COVER"; exit 1; }
[ -f "$VIDEO" ] || { echo "错误：视频不存在 $VIDEO"; exit 1; }

# ---------- 1. 探测正片参数 ----------
read -r V_W V_H V_FPS V_DUR < <(ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height,r_frame_rate:format=duration \
  -of csv=p=0 "$VIDEO" | awk -F'[,/]' '{printf "%d %d %.4f %.4f", $1, $2, $3, $4}')
echo "正片: ${V_W}x${V_H} @ ${V_FPS}fps, 时长 ${V_DUR}s"

FPS=$(python3 -c "print(int(round(${V_FPS:-24})))")
OFFSET=$(python3 -c "print(round($HEAD_DUR - $FADE_DUR, 3))")
TOTAL=$(python3 -c "print(round($HEAD_DUR + $V_DUR - $FADE_DUR, 3))")
DELAY_MS=$(python3 -c "print(int(round(($HEAD_DUR - $FADE_DUR) * 1000)))")
echo "xfade offset=${OFFSET}s, 音频延迟=${DELAY_MS}ms, 总时长=${TOTAL}s"

# ---------- 2. 片头生成 + xfade + 音频延迟 ----------
ffmpeg -y -v error \
  -loop 1 -t "$HEAD_DUR" -i "$COVER" \
  -i "$VIDEO" \
  -filter_complex "[0:v]fps=${FPS},scale=1080:1920,setsar=1,format=yuv420p,fade=t=in:st=0:d=${FADE_IN_DUR}[v0];[1:v]fps=${FPS},setsar=1,format=yuv420p[v1];[v0][v1]xfade=transition=fade:duration=${FADE_DUR}:offset=${OFFSET},format=yuv420p[v];[1:a]adelay=${DELAY_MS}|${DELAY_MS},apad,atrim=0:${TOTAL},asetpts=N/SR/TB[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -preset medium -crf 18 -c:a aac -b:a 128k -movflags +faststart \
  "$OUT"

echo "saved: $OUT"
