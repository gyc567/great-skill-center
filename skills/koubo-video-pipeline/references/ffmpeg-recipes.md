# ffmpeg 命令集与常见坑

口播视频流水线全部用到的 ffmpeg 操作。路径含空格必须加引号。

## 1. 横屏转竖屏（居中裁剪 + 缩放）

模型直出横屏（如 1600×1440）时转 1080×1920：

```bash
ffmpeg -y -v error -i "输入.mp4" \
  -vf "crop='min(iw,ih*9/16)':'min(ih,iw*16/9)',scale=1080:1920,setsar=1,format=yuv420p" \
  -c:v libx264 -preset medium -crf 18 -c:a copy "输出.mp4"
```

保留偏右构图（人物偏左、右侧带水印时从左侧裁）：

```bash
-vf "crop=ih*9/16:ih:<x偏移>:0,scale=1080:1920,setsar=1,format=yuv420p"
```

裁剪后必须抽帧确认人物头/肩/手势完整。

## 2. 片尾卡片（图片 → 静态卡片视频）

```bash
ffmpeg -y -loop 1 -i "福利图.jpg" -t 3.5 \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=0x212522,format=yuv420p" \
  -r 24 -c:v libx264 -preset medium -crf 18 -an /tmp/endcard.mp4
```

- `force_original_aspect_ratio=decrease` + `pad`：等比缩放居中，不裁切不变形
- `color=` 背景色应从图片四角采样（见 scripts/add_endcard.sh 内嵌 python）
- **不加任何 zoompan/scale 动画**，保证截图清晰

## 3. 交叉溶解转场（xfade）

```bash
ffmpeg -y -i "A.mp4" -i "B.mp4" \
  -filter_complex "[0:v]fps=24,format=yuv420p[v0];[1:v]fps=24,format=yuv420p[v1];[v0][v1]xfade=transition=fade:duration=0.5:offset=9.625,format=yuv420p[v]" \
  -map "[v]" -c:v libx264 -preset medium -crf 18 -movflags +faststart "输出.mp4"
```

**关键公式**：
- `offset = A 的时长 − 转场时长`
- `总时长 = A 时长 + B 时长 − 转场时长`
- xfade 要求两段 fps 一致、像素格式一致，先用 `fps=` 和 `format=yuv420p` 归一化
- 转场中点帧 = 两段各 50% 线性混合（交叉溶解），不是擦除

## 4. 片头接入（淡入 + xfade + 音频延迟）

```bash
ffmpeg -y -v error \
  -loop 1 -t 2.5 -i "封面.png" \
  -i "正片.mp4" \
  -filter_complex "[0:v]fps=24,scale=1080:1920,setsar=1,format=yuv420p,fade=t=in:st=0:d=0.35[v0];[1:v]fps=24,setsar=1,format=yuv420p[v1];[v0][v1]xfade=transition=fade:duration=0.5:offset=2.0,format=yuv420p[v];[1:a]adelay=2000|2000,apad,atrim=0:15.125,asetpts=N/SR/TB[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -preset medium -crf 18 -c:a aac -b:a 128k -movflags +faststart "完整版.mp4"
```

- `fade=t=in:st=0:d=0.35`：片头黑场淡入
- `adelay=2000|2000`：立体声双声道都延迟（口播从片头停留时刻开始）
- `apad` + `atrim`：补静音并裁到目标总长
- 总时长 = 片头停留 + 正片 − 转场

## 5. 音频淡出 + 补静音（接片尾卡片时）

```bash
[0:a]afade=t=out:st=9.7:d=0.4,apad,atrim=0:13.125,asetpts=N/SR/TB[a]
```

- `afade st` = 正片时长 − 0.425（让淡出在转场开始前完成）
- `atrim` 目标 = 总时长（含卡片段）

## 6. 抽帧核验

```bash
# 指定帧号拼图（tile）
ffmpeg -y -v error -i "视频.mp4" -vf "select='eq(n\,0)+eq(n\,120)+eq(n\,240)',scale=270:480,tile=3x1" -frames:v 1 /tmp/check.png

# 按时间点抽单帧
ffmpeg -y -v error -ss 12 -i "视频.mp4" -frames:v 1 /tmp/frame.png

# 转场区间连续帧（每 3 帧取 1）
ffmpeg -y -v error -i "视频.mp4" -vf "select='eq(n\,234)+eq(n\,237)+eq(n\,240)+eq(n\,243)',scale=270:480,tile=4x1" -frames:v 1 /tmp/transition.png
```

注意：`select` 表达式中逗号需转义 `\,`。

## 7. 音量检测（验证静音段）

```bash
ffmpeg -v info -ss 11 -t 2.5 -i "视频.mp4" -af volumedetect -f null /dev/null 2>&1 | grep -E "mean_volume|max_volume"
```

- 数字静音 ≈ -91 dB；人声段 max_volume 通常 > -20 dB
- 分时段检测：片头段（应静音）、人声段（应正常）、尾段（应静音）

## 8. 音频提取（供转写核验）

```bash
ffmpeg -y -v error -i "视频.mp4" -vn -ac 1 -ar 16000 -f wav /tmp/audio.wav
```

单声道 16kHz WAV，适配 AudioTranscribe 等转写工具。

## 9. 参数核验

```bash
ffprobe -v error -show_entries format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate,pix_fmt \
  -of default=noprint_wrappers=1 "视频.mp4"
```

## 常见坑

| 坑 | 解法 |
|---|---|
| xfade 报帧率不匹配 | 两段都先过 `fps=24`（或源帧率） |
| xfade 报格式不匹配 | 两段都先过 `format=yuv420p` |
| `select` 过滤器语法错误 | 逗号转义：`eq(n\,0)` |
| adelay 只有一个值导致单声道延迟 | 立体声写两个值：`adelay=2000\|2000` |
| 模型直出横屏 | 用第 1 条居中裁剪转竖屏，抽帧验人物完整 |
| 转场看起来像「擦除」 | 实为交叉溶解，肉眼误判；用逐帧像素比对确认（中点帧两段各约 50% 混合） |
| 音量检测无输出 | 用 `2>&1` 捕获 stderr，volumedetect 输出在 stderr |
