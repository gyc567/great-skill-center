# AI 视频剪辑工作室（agentcut-video-studio）

> 在用户眼前实时构建 Remotion 视频 —— 你聊天，Agent 就在你电脑上把视频写出来。
> 实时预览、拖拽时间轴、手工微调任意图层、浏览器直接导出 MP4。

品牌：**AI Skills 创作小店**

上游项目：[deifos/Agentcut](https://github.com/deifos/Agentcut) · 官方体验站：https://agentcut.synteq.app

---

## 这是什么

一套给 AI Agent 用的**视频剪辑工作室规范**。它不是"提示词合集"，而是一套完整的
制作方法论 + 组件库 + 工艺标准：

| 组成 | 数量 | 说明 |
|------|------|------|
| `SKILL.md` | 1 | 主工作流：从建项到导出的 7 步循环 |
| `references/` | 10 | 格式规范、声音、素材、风格侦测、性能、导出、指针、组件、预设、工艺 |
| `components/` | **60+** | 成品动效组件：标题、字幕条、数字滚动、聊天框、故障字、字效… |
| `components/styles.json` | **8 套** | 完整视觉风格系统（Voltrox / Snipwork / Doodlepad / Phosphor / Hexwire / Visualshot / Rewind / Lumen） |
| `components/presets/` | 2 套 | 整片配方：炭笔素描、朋克剪纸（含预览视频与示例工程） |

---

## 核心能力

### 🎬 实时可见的构建循环
Agent 每加一个图层，用户就能在时间轴上看到、拖动、裁剪、删掉。手工编辑写回 Agent 编辑的同一批文件。

### 🗂 一切皆可编辑
- 时间轴上的每个元素都是 `layers.json` 里的一个 clip → 用户能改
- 音乐、配音、每个音效都是音频 clip → 不藏在场景代码里
- 截图、Logo 是图片 clip；字幕是字幕 clip；颗粒、暗角是独立轨道上的场景 clip

### 🎨 8 套完整风格
每套风格定义：图形语言、字体、配色、字效、镜头运动、字幕样式、纹理叠加。

| 风格 | 定位 |
|------|------|
| **Voltrox** | 黄紫撞色、墨线描边、贴纸 slapped、punch-in 硬切 |
| **Snipwork** | 剪报勒索信字体、撕纸质感、定格动画、复印颗粒 |
| **Doodlepad** | 白板方格纸、手写体、荧光笔高亮、缓慢漂移 |
| **Phosphor** | 终端绿字黑底、打字机效果、扫描线、故障切换 |
| **Hexwire** | 赛博朋克霓虹洋红青、故障字体、HUD 边框、霓虹网格 |
| **Visualshot** | 解说风格、大字居中、黑白线稿图解、punch-in |
| **Rewind** | 90 年代家用录像带、VHS 噪点、电视画面、蓝屏菜单 |
| **Lumen** | 干净、Inter 字体、柔和深色卡片、单蓝色点缀、缓推 |

### 🔊 声音工程
配音与音乐先行，音效踩画面点。Agent **听不见**，所以必须靠 `agentcut_listen_*`
返回的数值判断混音，而不是"我觉得合适"。

### 🕵️ Style Spy（风格侦测）
粘贴一条 Instagram / TikTok / YouTube / X 链接，复制它的剪辑风格：
版式与分屏、剪辑节奏、字幕、动效、转场、配色。

---

## 项目结构（Agent 产出的工程）

```
projects/<slug>/
  project.json   fps、时长、variants（wide 1920x1080 / mobile 1080x1920）、字体、背景、风格
  layers.json    时间轴：轨道 → clip（以帧为单位）、标记
  scenes/*.tsx   自定义画面：每个文件一个默认导出的 React 组件
  assets/        配音、音乐、音效、图片、视频、字体
  notes.md       你的分镜表与声音决策背后的数字
  renders/       导出产物；永不删除或覆盖
```

**帧是全局唯一单位。** 轨道 0 绘制在最上层。

---

## 环境要求

| 项 | 要求 |
|----|------|
| Node.js | 20.10+ |
| Agent | Claude Code 或 Codex（需自行登录） |
| 浏览器 | Chrome（需允许访问本地网络，页面才能连上本地 helper） |
| 可选 | `yt-dlp` + `ffmpeg`（Style Spy 自动下载到 `~/.agentcut/tools`，校验和验证，不动系统） |
| 可选 | 配音/音乐 API Key（ElevenLabs、Gemini、OpenAI、xAI、Gemini Lyria） |

---

<!-- ERIC-AUTHOR-INFO:START -->

## 📬 联系作者

**ERIC** — AI技术专家，专注于人工智能和自动化工具的研究与应用

| 渠道 | 链接 |
|------|------|
| 📧 邮箱 | [gyc567@gmail.com](mailto:gyc567@gmail.com) |
| 🐦 Twitter | [@EricBlock2100](https://twitter.com/EricBlock2100) |
| 💬 微信 | `360369487` |
| ✈️ Telegram | [@fatoshi_block](https://t.me/fatoshi_block) |
| 📢 Telegram 频道 | [@cryptochanneleric](https://t.me/cryptochanneleric) |
| 🔐 加密情报 TG 群 | [@btcgogopen](https://t.me/btcgogopen) |
| ▶️ YouTube | [@0XBitFinance](https://www.youtube.com/@0XBitFinance) |
| 🌐 个人技术博客 | [topdigg.com](https://topdigg.com) |

### 💼 定制化开发

需要把这一套剪辑工作室接进你的产品、换成你的品牌风格、或者做成批量出片的生产线 ——
**直接联系我**。

常见方向：
- **品牌风格包** —— 把你的配色、字体、字幕样式做成一套可复用的 style
- **行业模板** —— 电商带货、课程宣传、个人 IP、发布会预热，各自的片头片尾与转场规范
- **批量生产线** —— 一套模板 × N 条内容，自动换文案/素材/配音
- **私有化部署** —— 全部跑在你自己的服务器与模型上
- **工作流集成** —— 接进你现有的 CMS、素材库、发布流水线
- **团队培训** —— 内部规范文档与上手材料

> 本 Skill 免费使用。定制化开发、付费咨询与商业授权，请通过上表任一渠道直接联系 ERIC。

---

<!-- ERIC-AUTHOR-INFO:END -->

## 许可

MIT（原始作品 © deifos / Agentcut 贡献者，品牌与包装 © ERIC / AI Skills 创作小店）。
