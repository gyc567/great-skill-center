# 提示词库 (Prompt Library)

本文件提供可直接复用的分镜图 / 图生视频 / 文生视频提示词写法与实战范例。**核心原则：用"锚定片段"保证跨镜头一致性。**

---

## 1. 锚定片段写法（一致性关键）

每张分镜图的 prompt 结构固定为：

```
[主体锚定] + [该镜画面与动作] + [影调/打光/镜头] + [负面约束]
```

- **主体锚定**：整条视频逐字复用，绝不变形。例：`matte black titanium vacuum flask, minimalist cylinder, no pattern`
- **影调/打光/镜头**：整条视频逐字复用。例：`dark moody lighting, single cold spotlight, champagne gold rim light, macro lens, cinematic, 8K`
- **负面约束**：`no text, no logo, no watermark, no extra objects`（生成层禁止文字！）

---

## 2. 分镜图 prompt 模板

### 2.1 奢品调性（把日常品做成"消费不起"）

> 用于：想营造昂贵、距离感、高级感的任何产品。

```
Luxury product photography, <主体锚定>, <摆放/场景：on polished black marble / on dark velvet>,
single cold white spotlight from above, champagne gold rim-light outlining the silhouette,
floating water droplets and dust particles, pure black background, macro lens, low angle,
cinematic lighting, ultra realistic, 8K, minimalist luxury, no text, no logo
```

### 2.2 硬广种草

```
Clean commercial product shot of <主体锚定>, on a soft gradient background,
bright even lighting, crisp detail, shallow depth of field, 3/4 front angle,
vibrant but tasteful colors, e-commerce photography, ultra sharp, no text, no logo
```

### 2.3 剧情类分镜（人物出镜）

```
Cinematic film still, <主角锚定>, <动作与场景>, <运镜暗示：over-the-shoulder / low angle>,
<影调：warm indoor light / cold office light>, shallow depth of field, 35mm film look,
moody color grading, realistic, no text, no watermark
```

> 人物一致性：主角锚定必须逐字复用（年龄感、发型、脸型、服装）；跨镜换服装需在设定卡里统一说明。

---

## 3. 图生视频运镜与动态词库

图生视频 prompt = `<该镜运镜>` + `<画面内动态>`。**越克制越高级。**

| 目的 | 运镜词 | 动态词 |
|---|---|---|
| 产品登场 | dolly-in（极缓慢推近） | 光尘/水滴缓缓飘动，灯柱轻微呼吸 |
| 尊贵质感 | slow pan（缓慢横移） | 雾气袅袅上升，光斑轻微闪烁 |
| 品牌收尾 | dolly-out（极缓慢拉远） | 光晕缓缓扩散，画面静止静谧 |
| 人物情绪 | static with subtle push | 发丝微动、眨眼、呼吸起伏 |
| 场景种草 | handheld follow | 环境光变化、行人虚化流动 |

**避雷**：不要写"快速切换""闪回""剧烈抖动"等，图生视频容易崩；不要让画面出现文字。

---

## 4. 实战范例：奢侈品保温杯 15s（已验证可复现）

**产品锚定**：`matte black titanium vacuum flask, minimalist cylinder, no pattern`
**风格锚定**：`dark tones, champagne gold rim light, macro cinematic lighting, ultra realistic, 8K, no text, no logo`

| 镜 | 时长 | 画面 prompt（含锚定） | 运镜 |
|---|---|---|---|
| 1 | 5s | 保温杯立于抛光黑大理石，顶部冷白聚光柱，金色边缘光，悬浮水滴微尘，纯黑背景 | dolly-in |
| 2 | 5s | 保温杯斜置深色丝绒，杯口升起白雾，背景金色散焦光斑 | slow pan |
| 3 | 5s | 保温杯近剪影立于空旷黑空间，身后低饱和金色光晕，大留白 | dolly-out |

**确定性层字幕**（后期叠加，不写进生成 prompt）：
- 镜2 中下方淡入：`温度，是最稀有的奢侈`
- 镜3 中央淡入：`¥9,999`，下方小字 `仅限受邀者`

**成片**：1080×1920 / 24fps / 15.000s，叠化 0.5s×2，调色 `eq=contrast=1.08:saturation=0.85:brightness=-0.02` + 暖金 + 暗角。

---

## 5. 6 方向速生成模板（Phase 1 用）

针对产品 X，快速产出 6 条方向卡片：

```
1.【奢品调性】把 X 拍成欲望的展品——极致暗调 + 微距 + 大留白 | 3 镜 | 15s 竖屏
2.【硬广种草】痛点→产品→三大卖点→促单 | 4 镜 | 15s 竖屏
3.【霸道总裁】总裁手里那支 X 救了场——身份反差 | 5 镜 | 30s 竖屏
4.【逆袭打脸】用前被嘲 / 用后惊艳的对比爽感 | 5 镜 | 30s 竖屏
5.【悬疑反转】一个关于 X 的失踪案（钩子强、完播高） | 5 镜 | 30s 竖屏
6.【情绪共鸣】深夜加班那杯热水的安全感 | 4 镜 | 15s 竖屏
```
