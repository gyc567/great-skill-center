#!/usr/bin/env bash
# 视频核验：参数 + 抽帧 + 分时段音量（口播视频流水线终检工具）
#
# 用法：
#   ./verify_video.sh <视频.mp4> [静音时段列表，如 "0:2 11:2.5"]
#
# 输出：
#   1) ffprobe 参数（分辨率/帧率/时长/编码/大小）
#   2) 关键帧抽取到 /tmp/verify_frames/（首/中/尾 + 可选自定义）
#   3) 分时段 volumedetect（静音段应 ≈ -91dB，人声段应正常）
set -euo pipefail

VIDEO="$1"
SEGMENTS="${2:-}"

[ -f "$VIDEO" ] || { echo "错误：视频不存在 $VIDEO"; exit 1; }

echo "========== 1. 参数 =========="
ffprobe -v error -show_entries format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate,pix_fmt \
  -of default=noprint_wrappers=1 "$VIDEO"

echo "========== 2. 关键帧（输出到 /tmp/verify_frames/） =========="
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$VIDEO")
FPS=$(ffprobe -v error -select_streams v:0 -show_entries r_frame_rate -of csv=p=0 "$VIDEO" | awk -F/ '{printf "%.4f", $1/$2}')
rm -rf /tmp/verify_frames && mkdir -p /tmp/verify_frames
MID=$(python3 -c "print(int(float('$DUR') * float('$FPS') / 2))")
END=$(python3 -c "print(int(float('$DUR') * float('$FPS')) - 2)")
ffmpeg -y -v error -i "$VIDEO" -vf "select='eq(n\,0)+eq(n\,$MID)+eq(n\,$END)',scale=270:480,tile=3x1" \
  -frames:v 1 /tmp/verify_frames/head_mid_tail.png
echo "首/中/尾三帧拼图: /tmp/verify_frames/head_mid_tail.png（fps=$FPS, mid_n=$MID, end_n=$END）"

echo "========== 3. 分时段音量 =========="
if [ -n "$SEGMENTS" ]; then
  for seg in $SEGMENTS; do
    st="${seg%%:*}"; len="${seg##*:}"
    echo "--- 时段 ${st}s 起 ${len}s ---"
    ffmpeg -v info -ss "$st" -t "$len" -i "$VIDEO" -af volumedetect -f null /dev/null 2>&1 \
      | grep -E "mean_volume|max_volume" || echo "(无输出)"
  done
else
  echo "(未提供时段，跳过。用法: verify_video.sh 视频.mp4 \"0:2 2.5:8\")"
fi
echo "参考: 静音段 mean_volume ≈ -91 dB；人声段 max_volume 通常 > -20 dB"
