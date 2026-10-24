# Remotion 视频编程大师（remotion-video-master）

> 用 React 组件以编程方式创建 MP4 视频 —— 动画、字幕、音乐可视化、AI 配音、场景自动配时，
> 全部代码控制。

品牌：**AI Skills 创作小店**

[中文文档](README_CN.md) · 上游项目：[wshuyi/remotion-video-skill](https://github.com/wshuyi/remotion-video-skill)

---

## Features

- 用 React 组件编程式创建视频
- AI 配音（TTS）生成，MiniMax（支持音色克隆）或 Edge TTS（免费）
- 场景化架构，自动按音频时长配时
- 支持动画、字幕、音乐可视化、3D 场景、Logo 动画

---

## Installation

```bash
git clone https://github.com/gyc567/great-skill-center.git
cp -r great-skill-center/skills/remotion-video-master ~/.claude/skills/
```

然后重启 Claude Code 或开启新会话。

### TTS Setup（选一个）

#### Option A: Edge TTS（免费，推荐快速上手）

无需任何配置，装个 Python 依赖即可：

```bash
pip install edge-tts
```

#### Option B: MiniMax TTS（付费，支持音色克隆）

```bash
export MINIMAX_API_KEY="your-api-key-here"
export MINIMAX_VOICE_ID="your-voice-id-here"
```

Voice ID 可以在 MiniMax 平台获取：使用内置音色，或克隆自己的声音。

---

## Usage

安装后这样触发：

- "用代码做视频"
- "编程视频"
- "Remotion"
- "/remotion-video"

### 示例提示词

**教程视频**
> 帮我做一个讲解 Python 装饰器的教程视频，5分钟左右

**数据可视化**
> 用 Remotion 做一个展示 2024 年销售数据的动画视频

**音乐可视化**
> 帮我做一个音乐可视化视频，配合这首歌的节奏

**产品 3D 展示**
> 做一个产品展示动画，讲清楚我们的产品结构

---

## Project Structure

Skill 创建新项目时的结构：

```
my-video-project/
├── src/
│   ├── Root.tsx           # 主 Composition 注册
│   ├── audioConfig.ts     # 场景配时（TTS 后自动生成）
│   └── scenes/            # 场景组件
├── public/
│   └── audio/             # TTS 音频文件
├── scripts/
│   └── generate_audio.py  # TTS 生成脚本
└── package.json
```

---

## Requirements

- Node.js 18+
- Python 3.8+（TTS 用）
- ffprobe（检测音频时长）

```bash
# macOS
brew install ffmpeg
# Ubuntu / Debian
sudo apt install ffmpeg
```

---

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

需要把你的品牌模板、数据源、字幕样式或配音流程接进 Remotion 流水线，
或者想要一套批量出片的生产线 —— **直接联系我**。

常见方向：
- 品牌化模板（片头片尾、配色、字体、转场规范）
- 数据接入（数据库 / API → 年度总结 / 数据播报视频）
- 配音体系（接你自己的 TTS 或音色克隆流程）
- 批量生产（一套模板批量生成 N 条视频）
- 私有化部署与内部培训材料

> 本 Skill 免费使用。定制化开发、付费咨询与商业授权，请通过上表任一渠道直接联系 ERIC。

---

## 许可

MIT（原始作品 © wshuyi，品牌与包装 © ERIC / AI Skills 创作小店）。
