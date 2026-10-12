# 电影级后期配方 (Edit Recipes)

ffmpeg 后期合成配方与**踩坑清单**。所有配方均经过 15s 竖屏成片实战验证（macOS + ffmpeg 无 libass 环境）。

---

## 0. 环境探测（先做）

```bash
ffmpeg -version
ffmpeg -hide_banner -filters | grep -E "drawtext|subtitles|xfade|tpad|vignette|colorbalance|noise|overlay"
# 若无 drawtext/subtitles → 本机 ffmpeg 未编译 libass/freetype
#   → 禁用 drawtext/subtitles/ass 路线，改用「Pillow 渲染 PNG → overlay」方案
```

`scripts/assemble_video.py` 已内置该降级路线，直接用即可。

---

## 1. 拼接 + 叠化转场（xfade）

段间叠化 0.5s。**xfade 会吃掉时长**：N 段 L 秒素材，叠化后总长 = N×L − (N−1)×D。

```bash
ffmpeg -i c1.mp4 -i c2.mp4 -i c3.mp4 -filter_complex \
"[0][1]xfade=transition=fade:duration=0.5:offset=4.54[v01]; \
 [v01][2]xfade=transition=fade:duration=0.5:offset=9.08[v]" \
-map "[v]" -c:v libx264 -crf 17 -pix_fmt yuv420p out.mp4
```

> **offset 通用算法**（各段等长/不等长皆可）：
> 第 k 个转场的 offset = `sum(前 k 段补帧后时长) − k × 叠化时长`。
> ⚠️ 不要用固定 `%d` 或手写死数值——段长一变就错位。

---

## 2. 精确时长对齐（凑整到目标秒数）

素材长度往往不是整数（如 5.0417s）。**用 tpad 克隆尾帧补足**，使总时长命中整秒，且定格帧落在叠化窗口内、视觉不可察：

```bash
ffmpeg -i c1.mp4 -vf "tpad=stop_mode=clone:stop_duration=0.2916" c1p.mp4
```

> 实战：3 段各 5.0417s → 每段补至 5.3333s → `3×5.3333 − 2×0.5 = 15.000s` 整。
> ⚠️ 慎用 `setpts` 变速重定时——会引入帧节奏抖动。

---

## 3. 电影级调色预设

`scripts/assemble_video.py` 内置以下 `--grade` 预设：

| 预设 | 适用 | 配方 |
|---|---|---|
| `nolan` | 诺兰冷调低饱和（本系列主用） | `eq=saturation=0.82:contrast=1.07:brightness=-0.012, colorbalance=bs=0.045:bm=0.02:rs=-0.03, vignette=PI/5.5, noise=alls=4:allf=t` |
| `film` | 纪实冷调颗粒 | `eq=saturation=0.78:contrast=1.06:brightness=-0.01, colorbalance=bs=0.02:gs=0.02, vignette=PI/6, noise=alls=5:allf=t` |
| `dark` | 暗调高级感（通用奢品） | `eq=contrast=1.08:saturation=0.85:brightness=-0.02, colorbalance=rs=0.03:bs=-0.03, vignette=PI/5` |
| `warm` | 暖调 | `eq=contrast=1.05:saturation=1.05:brightness=0.01, colorbalance=rs=0.04:bs=-0.02` |
| `none` | 不调色 | — |

**调色三件套的作用**：
- `eq` 降饱和 + 微提对比 + 压亮度 → 电影感基调
- `colorbalance` 做色彩偏移（`bs` 蓝移=冷，`rs` 红移=暖）——诺兰要**冷**，所以 `bs` 为正、`rs` 为负（**严禁橙青**）
- `vignette` 暗角聚焦视线；`noise=alls=N:allf=t` 加胶片颗粒（**颗粒会让体积暴涨，此时 `-crf` 用 21~23**）

---

## 4. 衬线大字幕（无 libass 环境的解法）

**步骤**：Pillow 渲染透明 PNG（含描边 + 投影）→ ffmpeg overlay + alpha fade。

```python
from PIL import Image, ImageDraw, ImageFont
# 诺兰版用 Songti SC Black；细体衬线用 Songti SC Light（Songti.ttc index=3）
font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Songti.ttc", size, index=0)
# 逐字手动加字距：draw.text((x, y), ch, font=font, fill=(242,239,230,255),
#   stroke_width=2, stroke_fill=(0,0,0,140)); x += font.getlength(ch) + tracking
```

```bash
ffmpeg -i base.mp4 -loop 1 -i slogan.png -filter_complex \
"[1]format=rgba,fade=in:st=6.0:d=0.6:alpha=1,fade=out:st=9.4:d=0.6:alpha=1[s]; \
 [0][s]overlay=x=(W-w)/2:y=580:shortest=1:enable='between(t,6.0,10.0)'" \
-c:v libx264 -crf 22 -pix_fmt yuv420p out.mp4
```

- **颜色**：冷白 `#F2EFE6` = RGB(242,239,230)（诺兰版）；香槟金 `#D4AF37`。
- **字体路径**：`/System/Library/Fonts/PingFang.ttc`（黑体）、`/System/Library/Fonts/Supplemental/Songti.ttc`（宋体，Black 抢眼 / Light 纤细）。
- **字距（tracking）**：奢侈品/电影文案建议字距舒展，`tracking ≈ 字号 × 0.10`。
- **浅色背景必须加描边 + 投影**：冰面/雪地/天空上白字会糊，加 ~2.5px 近黑描边（α≈0.55）+ 柔和高斯投影（下移偏移）。

`scripts/assemble_video.py` 已把描边/投影做成默认行为，参数 `--stroke-width / --stroke-alpha / --shadow-alpha / --no-shadow` 可调。

---

## 5. 音频（配乐 / 静音轨）

**选 BGM**：电影感首选**管弦乐**（cinematic-orchestral）。用 `ffmpeg` 分段 `volumedetect` 找一条有"**静→起→顶点→骤停**"弧线的段落，与画面同步（例：音乐在第 11s 推向高点、第 14.5s 骤停，只留风声与一次心跳）。

```bash
# 混入 BGM（视频流 -c:v copy 不重编码，音轨精确到 -t）
ffmpeg -y -i subbed.mp4 -i bgm.mp3 \
  -map 0:v:0 -map 1:a:0 \
  -c:v copy -c:a aac -b:a 192k \
  -t 15.000 \
  -af "afade=t=in:st=0:d=1.2,afade=t=out:st=13.0:d=2.0" \
  out.mp4
```

- **必须用 `-t <目标时长>` 对齐**，不要用输出级 `-shortest`（会引起掉帧）。
- 需要统一响度时前置 `loudnorm=I=-16:TP=-1.5:LRA=11`。
- **"无声的高级感"**（不加 BGM）：输出静音 AAC 轨以兼容平台：`-f lavfi -i anullsrc=r=48000:cl=stereo`。

---

## 6. QC 自检（交付前必做）

```bash
ffprobe -v error -show_entries format=duration,size \
  -show_entries stream=codec_type,width,height,r_frame_rate,bit_rate \
  -of default=noprint_wrappers=1 out.mp4

for t in 2 7 13; do ffmpeg -v error -ss $t -i out.mp4 -frames:v 1 -y f$t.jpg; done
```

逐帧核对：转场中间帧是否正常混合、字幕是否无方框乱码、淡入淡出边界无残留、末帧是否干净。

---

## 7. 踩坑清单（血泪史，按严重度排序）

| 现象 | 根因 | 解法 |
|---|---|---|
| **成片无限增大（涨到 GB 级）** | `-loop 1` 的 PNG 是无限流，`overlay` 输出被无限延长 | 用**滤镜级 `overlay=shortest=1`**，不要用输出级 `-shortest` |
| **音画掉帧 / 音轨错位** | 输出用 `-shortest` 对齐音轨 | 改用 `-t <精确秒数>` 对齐 + 视频流 `-c:v copy` |
| **字幕水平不居中** | overlay 的 `x=0`（左对齐） | 改为 `x=(W-w)/2` |
| **价格符号渲染成空白** | Songti SC Black **无半角 ¥（U+00A5）字形** | 改用**全角 ￥（U+FFE5）**，或换字体 |
| **浅色背景白字看不清** | 冰面/雪地/天空上白字对比不足 | 字幕加 ~2.5px 近黑描边（α≈0.55）+ 柔投影 |
| **长句字幕超出画幅被截** | 字号比例过大（如 0.066×1080 超宽） | 该行单设更小字号（如 0.058），或拆成两行 |
| **转场错位 / 丢帧** | xfade offset 用了固定值或 `%d` 误格式化 | 用通用 offset 算法（见 §1） |
| **拼接后时长不是目标值** | 未计入 xfade 吃掉的时长 | 用 tpad 补帧或重算 offset |
| **画面上出现乱码文字** | 生成模型渲染了 prompt 里的文字 | 生成层 prompt 禁止文字，文字走确定性层 |
| **中文显示方框** | 字体不支持中文或 index 选错 | 指定 PingFang/Songti.ttc 并核对 index |
| **`No such filter: drawtext/subtitles`** | ffmpeg 未编译 libass/freetype | 改用 Pillow PNG + overlay |
| **体积过大** | 加胶片颗粒后仍用低 CRF | 颗粒内容 `-crf 21~23` |

---

## 8. 一条命令搞定

```bash
python3 scripts/assemble_video.py \
  --inputs clip1.mp4 clip2.mp4 clip3.mp4 \
  --output outputs/final_15s.mp4 \
  --transition 0.5 --target-duration 15 \
  --grade nolan --crf 22 \
  --subtitle "文案一|3.0|5.0|0.30" \
  --subtitle "文案二|6.2|10.0|0.50|0.058" \
  --font "/System/Library/Fonts/Supplemental/Songti.ttc" --font-index 0 \
  --color F2EFE6 --audio bgm.mp3
```

`--subtitle` 格式：`文本|开始秒|结束秒|位置[|字号比例]`，位置可为 `top/center/bottom` 或 0~1 的纵向比例；`--subtitle` 可重复多次。
