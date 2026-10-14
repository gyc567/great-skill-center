---
name: nolanx-director-visual-language
description: "导演视觉语言库 — 把「高级感 / 电影感 / 有格调」这类形容词翻译成具体的机位、运镜、焦段、景别、光线与质感参数。含 20 个导演级子技能：视觉语言翻译、镜头语言、打光逻辑、分镜设计、连续性管控、短剧钩子、广告心理学、Seedance 2.0 提示词工程等。适用于任何需要「拍出来像导演拍的，而不是描述出来的」视频 / 分镜 / 提示词任务。触发词：机位、运镜、镜头语言、分镜、打光、景别、电影感、导演风格、visual language、camera language。"
license: MIT
source: https://github.com/nolanx-ai/nolanx.ai (.nolanx/skills/)
---

# 导演视觉语言库（NolanX）

把模糊的风格形容词，翻译成可执行的电影语言决策。核心信念：**风格服务于戏剧功能，不是装饰**。

## 主页（最常用）

**[references/director-visual-language.md](references/director-visual-language.md)** — 总纲。每个视觉需求都要拍板 7 件事：

- 景别尺度：micro / close-up / medium / wide / extreme wide
- 机位角度：eye-level / low / high / overhead / canted
- 焦段意图：intimate / compressed / expansive / voyeuristic / heroic
- 运镜：locked / drift / push-in / orbit / tracking / handheld / crane
- 打光逻辑：主光方向、轮廓光策略、阴影密度、实用光源、空气感
- 色彩逻辑：主色中性色、强调色能量、对比行为
- 质感逻辑：哑光 / 高光 / 潮湿 / 尘灰 / 烟雾 / 临床 / 有机

**反模式**：写 "very cinematic"、"beautiful composition"、"cool movie lighting" 这类空话。改为 "low-angle medium close shot with compressed perspective"、"harsh backlight with near-silhouette separation and red edge flare"。

## 子技能索引（按需加载 references/ 下对应文件）

| 需求 | 加载文件 |
|---|---|
| 风格→机位/光线总纲 | `director-visual-language.md` |
| 景别与角度语言、机位体系 | `shot-size-and-angle-language.md` |
| 分镜设计、逐镜拆解 | `storyboard-shot-design.md` |
| 打光连续性、光位设计 | `lighting-continuity-design.md` |
| 机位调度与走位、场面调度 | `scene-blocking-and-staging.md` |
| 动作场面编排 + 镜头逻辑 | `action-choreography-camera-logic.md` |
| 打斗节奏 / 命中判定 / 动作导演 | `cinematic-hit-marking-action-director.md` |
| 轴线规则、越轴、剪辑连续性 | `continuity-editing-axis-match.md` |
| 长片连续性圣经（多场次一致性） | `long-form-continuity-bible.md` |
| 世界资产 / 角色身份锁定 | `world-asset-identity-lock.md` |
| 镜头/影调风格（Cinema Studio 系） | `cinema-studio-lens-look.md` |
| 电影叙事结构 | `cinematic-story-architecture.md` |
| 对白与表演调度 | `dialogue-performance-blocking.md` |
| 场景/环境提取为拍摄圣经 | `environment-scene-extraction-bible.md` |
| 短片钩子工程（前 3 秒留人） | `short-drama-hook-engineering.md` |
| 广告心理学（商业片说服逻辑） | `commercial-ad-psychology.md` |
| 剧本 Fountain 格式 | `screenplay-fountain-format.md` |
| 参考驱动的视频提示词 | `reference-driven-video-prompting.md` |
| Seedance 2.0 提示词工程（@video/@image 有序绑定、V2V 续写） | `sd2-pe.md` |
| 模块化影视提示词圣经（可复用模板） | `modular-film-prompt-bible.md` |

## 使用方式

1. 接到视觉任务 → 先读 `director-visual-language.md`，把风格词落成上面 7 个维度。
2. 按任务类型从索引表加载 1–2 个专项子技能（不要全读，按需取）。
3. 输出时给出**具体参数**（机位/焦段/光位/运镜），而非形容词。
4. 多镜同段落 → 用 `continuity-editing-axis-match.md` + `long-form-continuity-bible.md` 保持轴线与影调连续。

## 铁律

- 风格必须服务戏剧功能，不为装饰而装饰。
- 相邻镜头复用同一套镜头/光线语法，不要每镜重置。
- 角色获得权力 → 构图与打光要体现；世界压抑 → 构图要压缩或困住主体。
- 刻意使用对比：尺度、色温、运动或静默。
- 写 "cinematic" 之前，先把它拆成镜头、光线、构图、质感、运动的具体决策。

## 与 product-short-video 技能的关系

本库负责**"怎么拍"**（机位/运镜/光线决策）；`product-short-video` 负责**"怎么走流程"**（创意方向→分镜→出图→出视频→成片）。做产品视频时两者配合：先用本库敲定视觉语言，再进 product-short-video 流水线。
