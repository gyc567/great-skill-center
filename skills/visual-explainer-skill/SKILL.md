---
name: visual-explainer-skill
description: 把任意内容转成高质量视觉讲解图 —— 白板手绘风、信息图、演示幻灯片、技术图表、思维导图和 UI 线框稿，由 OpenAI gpt-image-1.5 或 Google Gemini Nano Banana 2 生成。核心是 400-800 字的深度结构化提示词模板（空间布局、图标描述、配色、字体、连接关系）。当用户要做"配图""信息图""白板图""思维导图""图解""把文档变成图"时使用。
license: MIT
---

# Visual Explainer Skill

> **AI Skills 创作小店** 整理版 · 上游项目经许可保留原署名与许可证
>
> 本 Skill 由 AI Skills 创作小店 收录整理，能力方向来自上游开源项目。
> 运行时命令、工具名、路径与协议标识均保持原样以确保可用性。

把**任意内容**变成高质量视觉讲解图：白板草图、专业信息图、演示幻灯片、技术图表、思维导图、UI 线框稿。

## 为什么需要它

NotebookLM、Gemini 这类工具也能做信息图，但它们是**封闭生态** —— 你无法定制输出风格、无法接进自己的开发流程、无法控制驱动生成的提示词。

Visual Explainer 把这个能力直接搬进你的 Agent 工作流：给它一个主题、一份文档、一次会议记录或一个代码库，它产出结构化的视觉讲解。

## 设计原则

- **风格光谱** —— 从粗糙白板草图到专业信息图，用 `--draw-level` 控制落点
- **深度内容分析** —— 生成前先结构化提取概念、关系、视觉隐喻和布局策略
- **提示词工程即产品** —— 核心价值在风格专属的提示词模板，不在 API 封装。每个风格（whiteboard / infographic / presentation / diagram / mindmap / mindmap-structured / mockup）都有专属模板
- **与文档协作** —— 天然配合 Agent 的读文件能力

## 风格

`whiteboard` · `infographic` · `presentation` · `diagram` · `mindmap` · `mindmap-structured` · `mockup`

## 依赖

需要至少一个图像生成 API key：

```bash
export OPENAI_API_KEY="sk-..."   # 默认后端
export GEMINI_API_KEY="AIza..."  # 备选
```

运行时还依赖 `jq`。

## 文件说明

| 文件 | 用途 |
|---|---|
| `skill/visual-explainer.md` | **Skill 正文** —— 提示词模板与工作流 |
| `skill/metadata.json` | 版本、依赖、风格列表等元数据 |

`Makefile` 提供 `make install` / `make check` / `make version` 等便捷命令。

## 上游与许可

- 上游：https://github.com/ericblue/visual-explainer-skill
- 作者：Eric Blue
- 许可：MIT

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
