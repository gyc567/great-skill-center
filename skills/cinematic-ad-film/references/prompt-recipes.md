# 提示词配方 (Prompt Recipes)

分镜图 / 图生视频 / 脚本的写法与实战范例。**核心：用"锚定片段"保证跨镜头一致性；用"命题"保证创意高度。**

---

## 1. 创意原点怎么找（Phase 1 关键）

宁可花十分钟找这句话，也不要花一小时调画面。

**公式**：`导演的母题` × `产品的本质` = `核心命题`

| 导演母题 | 产品本质 | 核心命题（示例） |
|---|---|---|
| 诺兰：时间不可逆 | 保温杯：把温度留了 12 小时 | 时间是唯一不可逆的奢侈品——而它，替你留住了温度 |
| 维伦纽瓦：人在宏大前的渺小 | 户外电源：荒野里唯一的光 | 世界很大，够你走很远；电，够你写很久 |
| 王家卫：错过与暧昧 | 香水：被人记住的味道 | 有些人，你只记得他的味道 |
| 韦斯·安德森：秩序与荒诞 | 文具：让生活井井有条 | 世界很乱，但你有一格一格的小秩序 |
| 塔可夫斯基：时间与记忆 | 茶叶：一杯里的四季 | 喝的不是茶，是那一年翻过的山 |

**写命题的三条戒律**：
- ❌ 不写功能（"316 不锈钢、12 小时保温"）
- ❌ 不写形容词堆砌（"高端奢华尊贵"）
- ✅ 写一句**能被截图当海报文案**的话

**广告语候选**：主推 2 条 + 备选 3–4 条，按"由暖到冷 / 由抒情到数字"排序，让用户感受调性差异。例（保温杯诺兰版）：

1. 时间带得走一切，带不走温度。 ← 主推
2. 温度，是对抗时间的方式。 ← 主推
3. 不谈永恒。只谈 12 小时。 ← 最诺兰，冷峻克制
4. 世界上最贵的不是你拥有的，是你留住的。
5. 有些东西，值得被时间放过。
6. 一秒 60 万次心跳，只为守住 55℃。 ← 数字感

---

## 2. 锚定片段写法（一致性关键）

分镜图 prompt 结构固定为：

```
[风格锚定] + [产品/主角锚定] + [该镜画面与动作] + [负面约束]
```

- **风格锚定**：从 `director-styles.md` 取所选导演的"镜头锚定片段"，**逐字复用**。
- **产品/主角锚定**：整条视频逐字复用。
- **负面约束**：`no text, no logo, no watermark, no subtitles, no extra fingers, no distorted face, no plastic CG look`。

> 生成层**绝对禁止**出现文字（字幕/价格/Logo 一律后期叠加），否则模型会渲染成乱码。

---

## 3. 分镜图 prompt 模板

### 3.1 产品微距（诺兰 / 芬奇 / 维伦纽瓦适用）

```
<风格锚定>,
macros of <产品锚定> resting on a frost-covered black rock,
a thin column of white vapour rising from the mouth and condensing in the cold air,
background landscape still in sharp focus (deep focus, not blurred),
real morning rim-light raking the silhouette, 9:16 vertical,
no text, no logo, no watermark
```

### 3.2 人物旷野（确立"渺小与宏大"）

```
<风格锚定>,
a man in his early 30s wearing a heavy charcoal-wool overcoat with the collar turned
up, short dark hair, weathered stoic face, walking away from camera toward the centre
of a frozen lake, a matte gunmetal-grey titanium vacuum flask in his hand,
footprints in thin snow, low taupe sky, 9:16 vertical,
no text, no logo, no watermark, no extra fingers
```

### 3.3 场景空镜（收尾留白用）

```
<风格锚定>,
ultra-wide of a frozen lake at dawn, a lone tiny figure standing on the ice,
white vapour rising, morning sun punching through cloud toward the horizon,
massive negative space, 9:16 vertical, no text, no logo
```

---

## 4. 图生视频运镜与动态词库

图生视频 prompt = `<该镜运镜>` + `<画面内动态>`。**越克制越高级。**

| 目的 | 运镜词 | 动态词 |
|---|---|---|
| 开场建立（旷野/时间开始） | extremely slow **push-in** | 风掠过薄雪，云层极缓慢移动，衣角微动 |
| 微距核心（产品特写） | locked-off + very slow **lateral drift** | 杯口白雾持续上升，冷空气中凝成可见气流 |
| 收尾加冕（留白/揭示） | slow **dolly-out** + 视野展开 | 白雾上升，晨光击穿云层，画面"撑开" |
| 人物情绪 | static with subtle push | 发丝微动、眨眼、呼吸在冷空气中可见 |
| 展示过程 | handheld follow | 环境光变化、行人虚化流动 |

**避雷**：不要写"快速切换""闪回""剧烈抖动""爆炸式转场"——图生视频易崩；不要让画面出现文字。

**时长**：每镜目标 5s（生成的实际时长常为 5.0417s 等非整数值，交给后期 `tpad` 凑整）。

---

## 5. 实战范例：诺兰版保温杯 15s 电影广告（已验证可复现）

**产品锚定**：
```
a matte gunmetal-grey titanium vacuum flask, minimalist cylinder, no pattern,
no logo, a thin polished silver ring at the base of the lid
```
**主角锚定**：
```
a man in his early 30s wearing a heavy charcoal-wool overcoat with the collar turned
up, short dark hair, weathered stoic face
```
**风格锚定**：见 `director-styles.md` 诺兰段落（65mm 深景深冷调重型手持那段）。
**调色规范**：taupe · dust-blue · slate grey · neutral skin · faint ochre；字幕 **Songti SC Black，冷白 #F2EFE6**，字距舒展，慢速淡入。

### 分镜表（3 镜 × 5s = 15.000s）

| 镜号 | 时长 | 画面 | 运镜 | 字幕 | 音效 |
|---|---|---|---|---|---|
| 1 | 0.0–5.0s | **寒地黎明·时间开始**。冰封湖面，taupe 冷蓝天光压低，地平线极深。厚重炭灰羊毛大衣的背影独自走向冰湖中央，手握保温杯，脚下薄雪。前景冰裂与远景雪山同样锐利 | 重型手持，极缓慢 push-in，缓慢 grounded sway | 「时间是唯一不可逆的奢侈品」（3.0s 淡入） | 风声、踩雪、低频 ticking 起 |
| 2 | 5.0–10.0s | **装置的核心·微距**。保温杯立于覆霜黑岩上，哑光枪灰钛金属，杯口一缕白雾在冷空气中凝成可见气流。背景冰湖**仍在焦内**，真实晨光侧逆打轮廓 | 锁定机位 + 极缓慢横移，微距 | 「它替你，把时间按住了 12 小时」（6.2s 淡入） | ticking 加速、呼吸声、金属轻响 |
| 3 | 10.0–15.0s | **加冕·画幅展开**。镜头拉远回到冰湖全景：人影渺小立于天地间，白雾上升，晨光击穿云层压向地平线。画面"撑开"，大留白 | 缓慢 dolly-out + 视野展开 | 中央「温度，是对抗时间的方式」（11.0s）→ 下方「¥9,999 / 仅限受邀者」（11.4s） | 管弦乐推向高点后**骤停**，只余风声与一次心跳 |

**转场**：段间 0.5s 叠化，总时长精确 15.000s。

### 合成命令（真实可跑）

```bash
python3 scripts/assemble_video.py \
  --inputs clip1.mp4 clip2.mp4 clip3.mp4 \
  --output outputs/thermos_nolan_15s.mp4 \
  --transition 0.5 --target-duration 15 \
  --grade nolan --crf 22 \
  --subtitle "时间是唯一不可逆的奢侈品|3.0|5.0|0.30" \
  --subtitle "它替你，把时间按住了 12 小时|6.2|10.0|0.32|0.058" \
  --subtitle "温度，是对抗时间的方式|11.0|15.0|0.46" \
  --subtitle "￥9,999|11.6|15.0|0.56|0.042" \
  --subtitle "仅限受邀者|12.0|15.0|0.60|0.026" \
  --font "/System/Library/Fonts/Supplemental/Songti.ttc" --font-index 3 \
  --color F2EFE6 --audio bgm_orchestral.mp3
```

> 价格符号必须用**全角 ￥（U+FFE5）**——Songti SC Black 无半角 ¥ 字形，会渲染成空白（详见 `edit-recipes.md` 踩坑表）。

---

## 6. 字幕文案节奏（15s 三镜的黄金分布）

- 第 1 句（3.0s 淡入）：**命题**，放画面上的空处，字号中偏大。
- 第 2 句（6.2s 淡入）：**解释/悖论**，居中偏下。
- 第 3 句（11.0s 淡入）：**主张**，居中，全片最大。
- 价格卡（11.4–11.6s）：主价格 + 下方小字（`仅限受邀者`），字号递减。

原则：**一句一屏，句不重叠**；字幕出现总时长不超过全片的 2/3，留白本身就是高级感。
