# 导演视觉语言速查 (Director Styles)

**用法**：Phase 0 选定一位导演 → 取其「镜头锚定片段」**逐字写进设定卡的"风格锚定"段** → 全片所有分镜图/图生视频 prompt 复用同一段，禁止中途更换。

> ⚠️ **不要在 prompt 里写导演本人的名字**。模型对具名人物的理解不稳定，且可能触发安全策略。名字是给我们选风格用的，不是给 API 的——要把风格翻译成**可复现的技术参数**（画幅/镜头/景深/布光/调色/运镜质感）。

---

## 一、诺兰 · IMAX handheld（本系列实战采用，深解）

**母题**：时间。滴答倒计时、并行时间线、时间膨胀与倒流——诺兰所有作品都在讲"时间不可逆"。

**为什么适合"把日常品拍成奢侈品"**：奢侈品的本质是**不可得性**。而在物质极大丰富的今天，唯一真正不可再生的奢侈品是**时间**。任何"对抗时间流逝"的产品（保温杯、护肤品、相机、手表、保险、储蓄）都能撞上这个母题，命题即刻成立。

**镜头锚定片段（直接复制进设定卡）**：

```
Large-format 65mm spherical prime look, deep focus rendering both close foreground
and distant horizon equally sharp. Naturalistic motivated lighting only — overcast
daylight, real magic-hour sun. Restrained grade of taupe, dust-blue and slate-grey
mids, neutral skin, no orange-and-teal extremes. Aspect 2.39:1 for intimate moments
expanding toward a near-square IMAX vista on the reveal beat. Heavyweight handheld
camera, operator mass dampening the motion into a slow grounded sway, never shaky.
Real location with real weather and real horizon. Subject grounded by gravity, breath
visible in cold air. Atmosphere weighty, geographic, urgent.
```

| 维度 | 参数 |
|---|---|
| 画幅 | 2.39:1 亲密 / 1.43:1 近方形 IMAX（结尾"撑开"） |
| 镜头 | 65mm 大画幅球面定焦（28/35/50mm 等效） |
| 景深 | **深景深**——前景与地平线同样锐利（关键识别特征） |
| 布光 | **仅自然动机光**：阴天、真实魔幻时刻、真实钨丝内景；不打灯、不加色纸 |
| 调色 | taupe（灰褐）· dust-blue · slate grey · 中性肤色 · 微赭石；**严禁橙青** |
| 运镜 | 重型手持，**操作者质量把抖动阻尼成缓慢的接地摇摆**，绝不抖 |
| 剪辑 | 中速偏紧，卡"滴答"节拍；长留白全景做地理揭示 |
| 配乐 | cinematic-orchestral，铜管为主，滴答动机，全片铺满 |
| 适配 | 品牌 anthem、叙事预告片、风景旅拍、紧迫过程纪实 |
| 避用 | 亲密自白、喜剧、单房间对话、需要轻盈俏皮的场景 |

**动作词汇（分镜可从中取）**：宽景航拍揭示地貌并 hold 6s → 主体入画；重型手持跟随奔跑主体穿废墟；锁定对称建筑内景、单人横穿；慢推入眼睛、虹膜里映出事件；井土到远方的慢摇上；主体走向背景中巨大的实拍奇观；**画幅从 2.39:1 在揭示拍点上"撑开"到 1.43:1**。

---

## 二、12 种导演风格速查表

| ID | 风格 | 一句话识别 | 镜头锚定片段（压缩版） | 适配产品 |
|---|---|---|---|---|
| `nolan-imax-handheld` | 诺兰 · IMAX 手持 | 大画幅深景深 + 冷调自然光 + 重型手持 | 见上方深解 | 时间/对抗时间、宏大叙事 |
| `villeneuve-monumental` | 维伦纽瓦 · 宏大 | 单色调 + 巨大留白 + 渺小的人 + 体积光 | Anamorphic 2.39:1 with horizontal lens flare, deep focus. Monochromatic per-scene grade — entire frame committed to one tonal family (ochre-amber dust / sterile cyan / blood-orange sky), no contrasting hue. Atmospheric haze omnipresent, every light rendering a visible volumetric beam. Tiny human figure dwarfed against monumental brutalist architecture or vast desert horizon, enormous negative space. Camera locked on tripod or a single slow push toward a vanishing point. Atmosphere solemn, ceremonial. | 高端科技、汽车、香水、腕表 |
| `wong-kar-wai-neon-dream` | 王家卫 · 霓虹梦 | 霓虹饱和色 + 前景遮挡 + 抽帧慢动作 | 24mm wide pushed within arm's length of the face, shallow DoF reducing background to smeared bokeh of coloured light. Saturated coloured practicals — red neon, jade fluorescent, magenta backlight — unbalanced white point, tungsten amber against ink-blue shadow. Off-center composition shot through a foreground obstruction (window frame, slat blind, hanging fabric, smoke). Loose handheld breathing with the subject. Step-printed stuttering slow-motion against normal-speed background. Humid, rain-slicked late-night interior. | 酒、香水、都市情感、美妆 |
| `wes-anderson-symmetric` | 韦斯·安德森 · 对称 | 死中轴对称 + 粉彩 + 平光 + 定点 | Centered planimetric composition, equal headroom and equal negative space left/right. 35mm spherical, deep focus, 1.85:1. Soft even toplight, key/fill 1:1, no dramatic shadows. Pastel palette of dusty pink, mustard, mint, navy, cream baked into wardrobe, walls, props. Background reads as a flat hand-painted proscenium. Camera locked or three primitive moves only (90° whip pan, slow horizontal truck, snap zoom on axis). Deadpan delivery. | 文具、家居、糖果、生活方式 |
| `fincher-cold-lowkey` | 芬奇 · 冷调低调 | 单硬光源 + 半脸入黑 + 微推 + 无颗粒 | Anamorphic 2.39:1, 40mm prime, shallow DoF with focal plane on the near eye. Low-key from a single hard motivated source — overhead fluorescent, desk lamp, monitor glow — no fill, half the face plugged into near-black. Cool desaturated teal/amber-tungsten/grey, digital cleanliness, no film grain. Architectural symmetry down a hallway. Camera locked, executing only a microscopic 6–12 inch dolly-in, no shake. Atmosphere clinical, methodical, surveillance-grade. | 金融、科技、腕表、咨询、安全 |
| `tarkovsky-slow-meditative` | 塔可夫斯基 · 凝视 | 极慢 + 自然元素即主角 + 深调 | Spherical prime, deep focus, 1.85:1. Natural-only lighting — overcast, candle, fire, single window — deep modeling shadows, mist shaping beams. Desaturated sepia or faded green-grey, ochre and candle-amber, decayed-memory feel. Figure placed at distance or frame edge, dwarfed, low horizon. Camera executing an imperceptibly slow dolly drift or locked frame held until organic elements enter/exit, unmotivated by subject. Water, fire, mist, rain treated as the subject. Atmosphere durational, patient. | 茶、香、酒、户外、人文 |
| `refn-neon-static` | 雷弗恩 · 霓虹静 | 单波长饱和色 + 完全对称 + 模特般静止 | 50mm spherical, medium DoF, 2.39:1, rigorously symmetrical centered composition. Single-wavelength saturated lighting — pure magenta, cyan or cobalt from large LED panels — bathing the whole frame, no contrasting fill. Flat frontal key rendering skin as fashion-editorial perfection, hard rim in same hue. Locked tripod or single glacial dolly-in. Subject motionless as a mannequin, vacant expression, gesture ritualized like a runway pose. Atmosphere hypnotic, ceremonial, lethally still. | 潮牌、香水、电子、美妆 |
| `chazelle-musical-glow` | 沙泽勒 · 歌舞光晕 | 原色布光 + 魔幻时刻 + 连贯运镜 | 40mm spherical, 2.39:1. Saturated primary-colour lighting — cyan, magenta, amber gels — as uplight/backlight against magic-hour twilight. Hard single-source key modeling the face, practical lens flare from a bulb or sun edge. Centered or paired-mirror composition, low angle favoring sky and stage. Continuous choreographed motion (Steadicam tracking, 360° orbit, jib rise) in one unbroken take. Subject moves with musical intention, every gesture on a beat. Romantic, heightened beyond naturalism. | 运动、饮料、时尚、音乐 |
| `inarritu-long-take-handheld` | 伊纳里图 · 一镜手持 | 单镜头不间断 + 贴脸跟随 + 现场光 | 18mm wide exaggerating depth, deep focus, 2.39:1. Natural light plus only practicals existing inside the location — fire, lamps, screen glow — no studio sources, no fill. Cold blue exteriors / warm tungsten interiors, neutral skin, mud-brown earth, occasional blood-red accent. Steadicam or shoulder rig following at near-walking distance in one unbroken take, flowing over-the-shoulder → alongside-the-face → reverse orbit without cutting. Face fills frame while geography peels by. Atmosphere immersive, raw, kinetic. | 运动、户外、纪实、工业 |
| `soderbergh-natural-light` | 索德伯格 · 自然光 | 纯可用光 + 手持漂移 + 前景遮挡 | 32mm spherical, shallow DoF, 1.85:1. Available-light only — window, real fluorescent, real lamp — natural cast left untouched (fluorescents green, tungsten amber, daylight cool). Real location, no design intervention, lived-in wardrobe, unstyled hair. Mild colour separation cued by setting (cyan-grey corporate, amber domestic, sterile green clinical), skin held real. Loose handheld by a single operator, restless reframes, frequent foreground obstruction. Atmosphere observational, fly-on-wall. | 医疗、办公、SaaS、生活服务 |
| `david-lynch-dream-static` | 林奇 · 梦境静止 | 单硬光 + 烟尘 + 一处"不对劲" | 50mm spherical, 1.85:1. Single hard practical source — ceiling fixture, table lamp, sodium streetlight or fridge interior — no fill, smoke/haze catching the beam. Mid-century-decay interior, red velvet, checkerboard floor, 1950s surfaces. Warm sodium-amber grade with deep plugged-black edges, skin pushed waxy. Symmetrical centered composition with one deliberate asymmetry (tilted picture, open drawer, one object out of place) creating quiet wrongness. Camera locked or a single glacial zoom. Atmosphere uncanny, dreamlike, suspended outside time. | 悬疑、酒、香水、艺术、潮玩 |
| `edgar-wright-snap-cuts` | 埃德加·赖特 · 快切 | 甩镜 + 弹变焦 + 卡点 + 短镜 | 24mm wide exaggerating depth and motion, deep focus, 1.85:1. Bright evenly-lit, key/fill near 2:1, slightly saturated, no shy shadows, practicals visible. Saturated palette of red, electric blue, warm yellow, clean white. Centered for punch lines or low-and-wide for hero entrances. Camera always doing one legible thing — whip-pan, snap-zoom, crash-zoom, or locked tableau. Shot duration deliberately brief (under 2s), every move and action landing on a sound cue. Kinetic, comedic, percussive. | 快消、零食、App、游戏 |

---

## 三、选型决策（Phase 0 用）

先问三个问题，再定导演：

1. **产品的本质是什么？**（对抗时间 / 极致稀缺 / 暧昧诱惑 / 秩序美感 / 冷峻精密 / 自然疗愈）
2. **要唤起哪种情绪？**（敬畏 / 渴望 / 心动 / 会心一笑 / 不安 / 亢奋）
3. **受众在什么平台看？**（竖屏刷流→运镜要克制、主体要居中；横屏展示→可放开阔景）

**速配**：

| 产品本质 | 推荐导演 |
|---|---|
| 对抗时间、守护、宏大命题 | `nolan-imax-handheld` |
| 极致稀缺、科技敬畏 | `villeneuve-monumental` |
| 暧昧、诱惑、都市夜 | `wong-kar-wai-neon-dream` |
| 秩序、手工、克制设计 | `wes-anderson-symmetric` |
| 精密、冷峻、可信 | `fincher-cold-lowkey` |
| 静谧、自然、疗愈 | `tarkovsky-slow-meditative` |
| 潮、酷、静默的力量 | `refn-neon-static` |
| 运动、活力、青春 | `chazelle-musical-glow` / `edgar-wright-snap-cuts` |
| 真实、介入、纪实 | `inarritu-long-take-handheld` / `soderbergh-natural-light` |

> 给出 3 个候选时，每条附**一句话理由**（为什么它适配这个产品），让用户挑，不要替用户决定。
