# 剪辑配方 (Edit Recipes)

ffmpeg 后期合成配方与踩坑记录。**环境差异务必先探测**：本机 ffmpeg 可能**不含 libass/libfreetype**（无法用 `drawtext`/`subtitles`/`ass`），因此中文字幕走"Pillow 渲染透明 PNG → overlay"路径。

---

## 0. 环境探测（先做）

```bash
ffmpeg -version
ffmpeg -hide_banner -filters | grep -E "drawtext|subtitles|xfade|tpad|vignette|colorbalance"
# 若没有 drawtext/subtitles → 禁用 libass 路线，改用 overlay 方案
```

---

## 1. 拼接 + 叠化转场（xfade）

段间叠化 0.5s。注意 **xfade 会消耗时长**：N 段 L 秒素材，叠化后总长 = N*L - (N-1)*D。

```bash
ffmpeg -i c1.mp4 -i c2.mp4 -i c3.mp4 -filter_complex \
"[0][1]xfade=transition=fade:duration=0.5:offset=4.54[v01]; \
 [v01][2]xfade=transition=fade:duration=0.5:offset=9.08[v]" \
-map "[v]" -c:v libx264 -crf 17 -pix_fmt yuv420p out.mp4
```
> offset 计算：第 1 个转场 offset = 第 1 段时长 − 0.5；后续依次累加 (段时长 − 0.5)。

---

## 2. 精确时长对齐（凑整到目标秒数）

素材长度往往不是整数（如 5.0417s）。两种做法：

**A. tpad 克隆尾帧补足（推荐）**：给每段末尾补几帧，使命中目标秒数且**定格落在叠化窗口内**、视觉不可察。
```bash
ffmpeg -i c1.mp4 -vf "tpad=stop_mode=clone:stop_duration=0.3" c1p.mp4
```
**B. 变速重定时（慎用）**：`setpts` 会带来帧节奏抖动，非必要不用。

本次实战：3 段 5.0417s，每段补至 5.3333s，则 `3*5.3333 - 2*0.5 = 15.000s` 整。

---

## 3. 统一调色（暗调高级感）

```bash
-vf "eq=contrast=1.08:saturation=0.85:brightness=-0.02,\
colorbalance=rs=0.03:bs=-0.03,\
vignette=PI/5"
```
- `eq`：降饱和 + 提对比 + 压亮度 → 冷艳电影感
- `colorbalance`：少量暖金偏移（rs 红移、bs 蓝减）
- `vignette`：暗角聚焦视线

---

## 4. 中文金色字幕（无 libass 环境的解法）

**步骤**：Pillow 渲染透明 PNG → ffmpeg overlay + alpha fade。

```python
# render_text.py 要点
from PIL import Image, ImageDraw, ImageFont
font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Songti.ttc", 72, index=3)  # 细体衬线
# 逐字手动加字距：draw.text((x, y), ch, font=font, fill=(212,175,55,255)); x += font.getlength(ch)+tracking
# 保存 RGBA 透明 PNG
```

```bash
# 叠加 + 淡入淡出
ffmpeg -i base.mp4 -loop 1 -i slogan.png -filter_complex \
"[1]format=rgba,fade=in:st=6.0:d=0.6:alpha=1,fade=out:st=8.8:d=0.6:alpha=1[s]; \
 [0][s]overlay=(W-w)/2:H*0.62:enable='between(t,6.0,9.4)'" \
-c:v libx264 -crf 17 -pix_fmt yuv420p out.mp4
```

- macOS 中文字体：`/System/Library/Fonts/PingFang.ttc`、`/System/Library/Fonts/Supplemental/Songti.ttc`（Songti SC Light = index 3）
- 香槟金：`#D4AF37` = RGB(212,175,55)
- 字距（tracking）：奢侈品文案建议字距舒展（tracking ≈ 字号 × 0.08~0.15）

---

## 5. 音频

- "无声的高级感"：输出静音 AAC 轨以兼容各平台：`-f lavfi -i anullsrc=r=48000:cl=stereo -shortest`
- 加 BGM：`-i bgm.mp3 -filter_complex "[1:a]volume=0.4,afade=t=out:st=13:d=2[a]" -map 0:v -map "[a]"`

---

## 6. QC 自检（交付前必做）

```bash
# 参数校验
ffprobe -v error -show_entries format=duration,size \
  -show_entries stream=codec_type,width,height,r_frame_rate -of default=noprint_wrappers=1 out.mp4

# 抽帧目检（字幕/转场/边界）
for t in 2 7 13; do ffmpeg -v error -ss $t -i out.mp4 -frames:v 1 -y f$t.jpg; done
```
逐帧核对：转场中间帧是否正常混合、字幕是否无方框乱码、淡入淡出边界无残留。

---

## 7. 常见坑

| 现象 | 原因 | 解法 |
|---|---|---|
| 中文显示方框 | 字体不支持中文或未指定字体文件 | 指定 PingFang/Songti.ttc 并核对 index |
| `No such filter: drawtext/subtitles` | ffmpeg 未编译 libass/freetype | 改用 Pillow PNG + overlay |
| 拼接后时长不是目标值 | xfade 消耗时长未计入 | 用 tpad 补帧或重算 offset |
| 视频画面出现乱码文字 | 生成模型渲染了 prompt 里的文字 | 生成层 prompt 禁止文字，文字走确定性层 |
| 音画不同步 | 变速后未同步音频 | 统一重采样/对齐，或用静音轨 |
