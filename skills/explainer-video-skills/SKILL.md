---
name: explainer-video-skills
description: 讲解视频 Skill 合集 —— 把脚本、分镜和渲染串成一条流水线，产出带旁白的讲解视频、年度回顾和动画图表。包含 5 个子 Skill：explainer-video（主流程）、diagram-animation（动画图表）、whiteboard-animation（白板动画）、isometric-animation（等距动画）、wrapped-video（包装视频）。当用户要做"讲解视频""解说视频""图文转视频""年度回顾""动画图表视频"时使用。
license: MIT
---

# Explainer Video Skills

> **AI Skills 创作小店** 整理版 · 上游项目经许可保留原署名与许可证
>
> 本 Skill 由 AI Skills 创作小店 收录整理，能力方向来自上游开源项目。
> 运行时命令、工具名、路径与协议标识均保持原样以确保可用性。

面向 AI 编码 Agent 的**讲解视频 Skill 合集**：脚本、分镜、渲染一条龙，产出带旁白的讲解视频、年度回顾和动画图表。

## 子 Skill

| Skill | 作用 |
|---|---|
| `explainer-video` | **主流程** —— 脚本 → 分镜 → 旁白 → 渲染 |
| `diagram-animation` | 动画图表 |
| `whiteboard-animation` | 白板手绘风动画 |
| `isometric-animation` | 等距视角动画 |
| `wrapped-video` | 包装已有视频（加旁白、字幕、封面） |

子 Skill 位于 `skills/<name>/SKILL.md`。

## 辅助工具

`scripts/` 下提供 shell 工具：

| 脚本 | 用途 |
|---|---|
| `probe-mp4.sh` | 探测 MP4 的编码、时长、分辨率、帧率 |
| `seek-shot.sh` | 抽帧定位关键画面 |
| `contact-sheet.sh` | 生成缩略图网格，快速浏览全片 |

## 上游与许可

- 上游：https://github.com/iart-ai/explainer-video-skills
- 许可：MIT
- 运行环境：Claude Code、Cursor、Codex 及其他 40+ Agent

---

## 定制化开发

如需定制化开发，可直接联系 ERIC：

- **ERIC AI 技术专家**，专注于人工智能和自动化工具的研究与应用
- 邮箱：`gyc567@gmail.com`
- Twitter：`@EricBlock2100`
- 微信：`360369487`
- Telegram：`https://t.me/fatoshi_block`
- Telegram 频道：`https://t.me/cryptochanneleric`
- 加密情报 TG 群：`https://t.me/btcgogopen`
- YouTube：`@0XBitFinance`
- 博客：`topdigg.com`
