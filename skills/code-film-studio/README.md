# 代码电影工作室（code-film-studio）

> 用纯代码生成一支完整短片 —— 画面、图形、排版、动效、声音、混音、字幕全部代码绘制与合成。
> 不需要 AE / PR / 达芬奇，不需要素材库，不需要实拍。

品牌：**AI Skills 创作小店**

---

## 这是什么

一个给 AI Agent 用的**代码电影工作室**。你的 Agent 负责导演：选风格、写方案、
写代码画每一帧、配乐、混音、加字幕，最后导出成片。

**20 种电影级视觉风格**内置，每一种都带一份详尽的风格提示词（`STYLE.md`）——
里面写清楚了材质、渲染方式、配色逻辑、光线规则、运动节奏与声音设计。

---

## 快速开始

```bash
# 1. 准备风格库（会打印 LIB=<路径>）
sh scripts/setup.sh

# 2. 装依赖（首次几分钟，建议后台跑）
sh scripts/setup.sh deps

# 3. 开工
export LIB=$(sh scripts/setup.sh | grep '^LIB=' | cut -d= -f2)
cd "$LIB"
```

依赖：Node.js ≥ 20、ffmpeg、Python ≥ 3.11（或装 uv）。Chromium 由 `setup.sh deps` 自动装。

---

## 内置风格

| 分类 | 风格 |
|------|------|
| **数据解说 / 科技发布** | 暗色科技发布 · 数据叙事 · 科幻全息界面 · 等距信息图 · 活体实机录屏 · 产品拆解 |
| **品牌片 / 商业视觉** | 玻璃质感产品 · 移轴微缩 · 装饰艺术 · 瑞士动态排版 · 丝印旅行海报 · Risograph 孔版印刷 |
| **东方美学** | 中国水墨 · 浮世绘 · 纸雕灯影 · 红色窗花剪纸 · 油画厚涂 · 水彩笔刷 |
| **手绘 / 讲解** | 白板讲解 · 蜡笔儿童绘本 |

完整 60 种风格库见 `github.com/gyc567/great-skill-center`。

---

## 目录结构

```
code-film-studio/
├── SKILL.md              # Skill 主文件
├── scripts/
│   └── setup.sh          # 库定位 + 依赖安装
└── library/              # 风格库
    ├── AGENTS.md         # 主工作流
    ├── DIRECTOR.md       # 导演手册：写方案
    ├── TECHNIQUE.md      # 技术手册：渲染 / 声音 / 混音
    ├── MY-STYLES.md      # 你的自有风格
    ├── core/             # 渲染引擎 + 音效 + 混音 + 字幕 + TTS
    ├── styles/           # 20 种风格
    └── tools/            # 素材下载、目录生成、发布
```

---

## 三步工作流

| 步骤 | 做什么 | 读哪里 |
|------|--------|--------|
| 1. 定风格 | 找风格 / 从空白做自己的 / 复用存过的 | `library/AGENTS.md` → Start |
| 2. 做方案 | 一轮提问 → 写 `TREATMENT.md` | `library/DIRECTOR.md` |
| 3. 做片子 | 渲染 → 声音 → 混音 → 字幕 → 交付 | `library/TECHNIQUE.md` |

渲染命令：

```bash
cd "$LIB" && node core/render/still.mjs "<项目目录>" 1.5 3    # 静帧
cd "$LIB" && node core/render/video.mjs "<项目目录>" --fps 24 --out out/video.mp4
```

---

## 能力

| 能力 | 说明 |
|------|------|
| 纯代码渲染 | Playwright + Three.js，矢量图形清晰可缩放 |
| 真实素材解说 | 卫星影像、激光扫描、CAD 模型、档案扫描件可直接做成解说片 |
| 档案影像剪辑 | 从真实档案影像与文档剪出新片 |
| 自己的风格 | 改现有风格，或从空白页做一套并存下来复用 |
| 声音分层 | 音效层、混音、字幕、联络表；语音（Kokoro / edge-tts）与音乐为可选层 |
| 确定性输出 | 同一份代码渲染出同一份成片 |

---

## 边界

- 不做普通视频剪辑、裁剪、转码。
- 不承诺与参考影片像素级一致 —— 风格是视觉语言框架，不是抄袭样片。
- 使用真实档案影像前请确认素材授权与出处。
- 复杂 3D 场景在无 GPU 的机器上会走软件渲染，较慢。

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

需要把渲染管线适配到你自己的项目结构、部署流程，或为你的行业新增专属风格，
或者想要团队内部的一键生产封装 —— **直接联系我**。

> 本 Skill 免费使用。定制化开发、付费咨询与商业授权，请通过上表任一渠道联系 ERIC。

---

## 许可

- 代码与文档：MIT（原始库 © LemoLab，品牌与包装 © ERIC / AI Skills 创作小店）
- 样片视频及其静帧：CC BY 4.0
- 你用本库做出的片子：归你自己，无须署名
