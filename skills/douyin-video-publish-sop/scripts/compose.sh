#!/usr/bin/env bash
# 抖音卡片视频合成器（1080×1920 / 30fps / 每卡4.8s + 0.1s灰词尾帧 + BGM）
# 用法: bash compose.sh "cards/c1.png cards/c2.png cards/c3.png cards/c4.png cards/c5.png cards/c6.png" cards/ending.png bgm.mp3 out.mp4
# 环境变量: CARD_SEC=每卡秒数(默认4.8) TAIL_SEC=尾帧秒数(默认0.1)
set -euo pipefail

CARDS="$1"; ENDING="$2"; BGM="$3"; OUT="$4"
CARD_SEC="${CARD_SEC:-4.8}"
TAIL_SEC="${TAIL_SEC:-0.1}"
N_CARDS=$(echo "$CARDS" | wc -w)
TOTAL=$(python3 -c "print(f'{($N_CARDS*$CARD_SEC+$TAIL_SEC):.1f}')")
FADE_ST=$(python3 -c "print(f'{($N_CARDS*$CARD_SEC+$TAIL_SEC-0.6):.1f}')")

# 构建 filter_complex
INPUTS=(); FILTERS=(); CONCAT=""
i=0
for c in $CARDS; do
  INPUTS+=("-loop" "1" "-i" "$c")
  FILTERS+=("[$i:v]trim=duration=$CARD_SEC,setpts=PTS-STARTPTS[v$i];")
  CONCAT+="[v$i]"
  i=$((i+1))
done
INPUTS+=("-loop" "1" "-i" "$ENDING")
FILTERS+=("[$i:v]trim=duration=$TAIL_SEC,setpts=PTS-STARTPTS[v$i];")
CONCAT+="[v$i]"
i=$((i+1))
FILTERS+=("${CONCAT}concat=n=$i:v=1:a=0[outv];")
INPUTS+=("-i" "$BGM")
FILTERS+=("[${i}:a]atrim=0:$TOTAL,afade=t=out:st=$FADE_ST:d=0.6[aout]")

ffmpeg -y "${INPUTS[@]}" -filter_complex "${FILTERS[*]}" \
  -map "[outv]" -map "[aout]" -c:v libx264 -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 128k -movflags +faststart "$OUT"

echo "合成OK: $OUT"
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$OUT"
