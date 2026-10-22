---
name: code-film-studio
description: >-
  代码电影工作室 — 用纯代码（无实拍、无素材库）生成一支完整短片，20 种电影级视觉风格（完整库 60 种）。
  含油画厚涂、中国水墨、浮世绘、纸雕灯影、剪纸窗花、版画木刻、丝网印刷、Risograph 孔版印刷、
  赛璐璐动画、HD-2D、16-bit 像素 RPG、装饰艺术、瑞士动态排版、卫星简报、产品拆解、
  显微叙事、点云测绘、档案灯台、新闻包装、1920 默片、视觉调查、活体录屏等风格。
  适用于用户要做视频/短片/动画/宣传片/数据解说/产品拆解/科普短片/纪实剪辑，
  要指定某种视觉风格，要把自己的风格存下来复用，或不确定该选哪种风格时。
  不适用于对用户已有视频文件做普通剪辑、裁剪、转码。
brand: AI Skills 创作小店
price: 3990
tags:
  - 代码电影
  - 视觉风格
  - 短片制作
  - 品牌片
  - 数据解说
  - 剪映替代
specs:
  - SPEC-DEFAULT
  - PLAN-DEFAULT
  - SKU-DEFAULT
author: ERIC
author_email: gyc567@gmail.com
author_twitter: https://twitter.com/EricBlock2100
author_blog: https://topdigg.com
---

# 代码电影工作室

用纯代码生成一支完整短片：**画面、图形、排版、动效、声音、混音、字幕**全部由代码绘制与合成，
不依赖实拍素材、不依赖素材库、不需要 AE / PR / 达芬奇。

本 Skill 内置 20 种电影级视觉风格，完整库共 60 种，每一种都自带提示词、渲染代码与制作指南。

---

## 快速开始

```bash
# 1. 准备库（首次会下载）
sh "<skill base directory>/scripts/setup.sh"

# 2. 装依赖（后台跑，第一次几分钟）
sh "<skill base directory>/scripts/setup.sh" deps

# 3. 按 AGENTS.md 的流程做片子
```

装完后 `setup.sh` 最后一行会打印 `LIB=<路径>`，后续所有命令都在 `$LIB` 下执行：

```bash
cd "$LIB" && node core/render/still.mjs "<项目目录>" 1.5 3
```

---

## 三步工作流

| 步骤 | 做什么 | 读哪个文件 |
|------|--------|-----------|
| **1. 定风格** | 找到风格、或从空白页做自己的、或复用已存风格 | `$LIB/AGENTS.md` → Start；`$LIB/MY-STYLES.md` |
| **2. 做方案** | 一轮提问 → 写 `TREATMENT.md`（创意方案） | `$LIB/DIRECTOR.md` |
| **3. 做片子** | 渲染、声音、混音、字幕、交付 | `$LIB/TECHNIQUE.md`、`$LIB/core/README.md` |

**一轮提问原则**：该问的一次问完，不要挤牙膏。系统工具缺失（Node / ffmpeg / Python）只在那一轮里报告一次，
不要自己装系统级软件；单个风格需要的 npm 包由你自己装进项目目录。

---

## 打包的 20 种风格

本商品内置以下 20 种风格（每种含 `STYLE.md` 提示词 + `style.json` 元数据 + 字幕轨）：

| 分类 | 风格 |
|------|------|
| **数据解说 / 科技发布** | 暗色科技发布 · 数据叙事 · 科幻全息界面 · 等距信息图 · 活体实机录屏 · 产品拆解 |
| **品牌片 / 商业视觉** | 玻璃质感产品 · 移轴微缩 · 装饰艺术 · 瑞士动态排版 · 丝印旅行海报 · Risograph 孔版印刷 |
| **东方美学** | 中国水墨 · 浮世绘 · 纸雕灯影 · 红色窗花剪纸 · 油画厚涂 · 水彩笔刷 |
| **手绘 / 讲解** | 白板讲解 · 蜡笔儿童绘本 |

> 完整 60 种风格库（含实证影像、剪辑纪实、印刷版画、卡通动画、游戏、默片等）
> 见上游仓库 `github.com/gyc567/great-skill-center`，或用 `setup.sh demo <slug>` 拉取参考样片。

## 关键能力

| 能力 | 说明 |
|------|------|
| **纯代码渲染** | Playwright + Three.js，矢量图形与排版清晰可缩放 |
| **真实素材解说** | 卫星影像、激光扫描、CAD 模型、档案扫描件可直接做成解说片 |
| **档案影像剪辑** | 从真实档案影像与文档剪出新片（新闻片、纪实） |
| **自己的风格** | 从空白页做风格，或改现有风格并存进 `~/lemo-my-styles/` 复用 |
| **声音分层** | 音效层、混音、字幕、联络表；语音（Kokoro / edge-tts）与音乐（numba 采样器）为可选层 |
| **确定性输出** | 同一份代码渲染出同一份成片，方便迭代 |

---

## Skill 模式下的差异

| 项 | 常规（库内） | Skill 模式 |
|---|---|---|
| 项目目录 | `films/<name>/` | 用户起始目录下的 `<name>/`（小写字母、数字、连字符） |
| 运行工具 | 相对路径 | `cd "$LIB" && node core/render/still.mjs "<项目绝对路径>" 1.5 3` |
| 页面引用 | 相对 | 绝对：`/core/lib.js`、`/node_modules/three/…`（项目服务在 `/@film/`） |
| 脚本与 `build.sh` | 相对 | `$LIB/…`，`build.sh` 顶部写 `LIB=<path>`；不要用 `../..` |
| 演示片 | 已附带 | `sh "<skill base directory>/scripts/setup.sh" demo <slug>`，`TREATMENT.md` 写完后再拉，仅作参考 |
| 品牌署名 | 库内可带 | 用户自己的片子不带库方署名、不加水印 |

---

## 环境要求

| 依赖 | 版本 | 说明 |
|------|------|------|
| Node.js | ≥ 20 | 渲染器运行时 |
| ffmpeg | 任意 | 合成音视频、导出 |
| Python | ≥ 3.11（或装 uv） | 音效、混音、字幕、联络表 |
| Chromium | headless shell | `setup.sh deps` 自动安装 |
| npm 包 | `playwright-core` + `three` | `setup.sh deps` 自动安装 |

语音层需 `kokoro-onnx`（Python 3.11–3.13）、`edge-tts`、`faster-whisper`；音乐层需 `numba`。
这些用 `setup.sh deps voice` / `setup.sh deps music` 单独安装。

---

## 边界

- 不做普通视频剪辑、裁剪、转码——那是 ffmpeg 基础操作，不走这套风格系统。
- 不承诺与参考影片像素级一致：风格是视觉语言与技法框架，不是抄袭样片。
- 使用真实档案影像前，确认所用素材的授权与出处。
- 渲染耗时取决于风格复杂度与分辨率；大分辨率或复杂 3D 场景需要预留时间。

---

## 资源索引

| 文件 | 内容 |
|------|------|
| `AGENTS.md` | 主工作流（Start → 提问 → 方案 → 制作 → 交付） |
| `DIRECTOR.md` | 导演手册：写方案、选风格、定调 |
| `TECHNIQUE.md` | 技术手册：渲染、声音、混音、字幕 |
| `MY-STYLES.md` | 用户的自有风格：存放、复用、改造 |
| `MAINTAINING.md` | 维护风格库的指南 |
| `core/README.md` | 渲染管线与工具说明 |
| `styles/README.md` | 60 种风格完整索引 |
| `styles/<slug>/STYLE.md` | 单个风格的提示词、技法、依赖 |

品牌：AI Skills 创作小店

<!-- ERIC-AUTHOR-INFO:START -->
---

## 📬 作者信息

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

> 本 Skill 由 ERIC 免费提供。想深入交流或获取更多同类 Skill，欢迎通过上表任一渠道联系。

<!-- ERIC-AUTHOR-INFO:END -->
