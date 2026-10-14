---
name: video-director-styles
description: "导演风格库 — 内置 12 种电影导演的镜头语法（诺兰 IMAX 手持、芬奇冷调低照、韦斯·安德森对称粉彩、王家卫霓虹梦境、维伦纽瓦恢弘科幻、塔可夫斯基凝视慢镜、伊纳里图长镜头手持、林奇梦境静态、埃德加·赖特快切、沙泽勒爵士光晕、雷弗恩霓虹冷峻、索德伯格自然光手持）。每种风格提供可直接拼进视频提示词的「镜头锚点」段落：焦段、光比、运镜、剪辑节奏、色板、动作词汇、声音设计。适用于 AI 视频生成（Veo / Sora / Kling / Runway / Seedance）与分镜设计。触发词：导演风格、电影感、大片感、风格化运镜、director style、film look。"
license: MIT
source: https://github.com/Mikefluff/skills (common/style-library/video/)
---

# 导演风格库（12 种）

把「像某位导演拍的」翻译成模型能听懂的具体参数。**这不是模仿导演，而是提取其镜头语法**——导演名字只留给我们人类看，绝不写进发给模型的提示词。

## 12 种风格速查

| ID | 风格 | 情绪 | 节奏 | 适合对白 |
|---|---|---|---|---|
| `fincher-cold-lowkey` | 芬奇 · 冷调低照 | 紧张 · 精准 · 无菌 | 慢 | ✅ |
| `nolan-imax-handheld` | 诺兰 · IMAX 手持 | 史诗 · 沉重 · 紧迫 | 中 | ✅ |
| `wes-anderson-symmetric` | 韦斯·安德森 · 对称粉彩 | 怪趣 · 冷面 · 精致 | 中 | ✅ |
| `wong-kar-wai-neon-dream` | 王家卫 · 霓虹梦境 | 忧郁 · 感官 · 律动 | 中 | ❌ |
| `villeneuve-monumental` | 维伦纽瓦 · 恢弘科幻 | 敬畏 · 冷峻 · 思辨 | 慢 | ❌ |
| `tarkovsky-slow-meditative` | 塔可夫斯基 · 凝视冥想 | 精神性 · 耐心 · 忧郁 | 慢 | ❌ |
| `inarritu-long-take-handheld` | 伊纳里图 · 长镜头手持 | 激烈 · 沉浸 · 生猛 | 快 | ✅ |
| `david-lynch-dream-static` | 林奇 · 梦境静态 | 超现实 · 诡异 · 慢燃 | 慢 | ✅ |
| `edgar-wright-snap-cuts` | 埃德加·赖特 · 快切 | 律动 · 喜剧 · 节奏感 | 极快 | ✅ |
| `chazelle-musical-glow` | 沙泽勒 · 爵士光晕 | 浪漫 · 动感 · 爵士 | 快 | ❌ |
| `refn-neon-static` | 雷弗恩 · 霓虹冷峻 | 疏离 · 催眠 · 静默暴力 | 慢 | ❌ |
| `soderbergh-natural-light` | 索德伯格 · 自然光手持 | 纪实 · 亲密 · 不安 | 中 | ✅ |

## 每个风格文件包含什么

`references/<id>.md` 均为 YAML frontmatter + 正文，正文含 14 个固定段落：

`Inspired by` · `Cinematography anchor`（摄影总纲）· `Color palette`（色板）· `Lens & framing`（焦段与构图）· `Lighting`（光位与光比）· `Motion language`（运镜语法）· `Editing rhythm`（剪辑节奏，每分钟切几次）· **`Shot anchor`（逐镜提示词片段——真正要拼进 prompt 的那段）** · `Action vocabulary`（动作词汇表）· `Sound design implications`（声音设计）· `Best for` · `Avoid for` · `Suggested duration` · `Suggested music style`

## 使用方式

1. **选风格** → 读 `references/_index.md` 或上表，按情绪 + 节奏 + 是否要台词挑一个。
2. **加载** → 读 `references/<id>.md`。
3. **拼提示词** → 把 `Shot anchor` 段落（必要时加 `Lens & framing` / `Lighting` / `Motion language`）拼到每一镜的 prompt 后面。
4. **一致性关键** → 同一支片子所有镜头复用**同一个风格锚点**，片子才会读起来像"一个人的作品"，而不是风格大杂烩。
5. **配乐** → 每个风格末尾的 `Suggested music style` 给出建议曲风（可用于配 BGM）。
6. **自定义** → 复制 `references/_template.md` 改写，保持 `Shot anchor` 具体（焦段/光比/光学行为），删掉导演名字。

## 铁律

- **导演名字绝不进 prompt**。只传"语法"（光比 8:1、40mm 定焦、锁机位微推 6–12 英寸）。
- **Shot anchor 必须具体**：焦段、光比、具名颜色、真实镜头行为。不写 "cinematic"。
- **一镜一个主导运镜意图**，别堆矛盾动词。
- 相邻镜头沿用同一套镜头/光线语法，风格要"渐变"不要"重置"。

## 与其它技能的配合

- 想从风格倒推机位/光线的**通用方法论** → 用 `nolanx-director-visual-language`。
- 想把风格落到**完整产品视频生产流水线**（创意→分镜→出图→出片） → 用 `product-short-video`。
- 想写 **Seedance / Sora 的具体提示词** → 用 `shortfilm-prompt` 或 `awesome-seedance`。
