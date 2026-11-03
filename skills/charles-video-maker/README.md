# Charles 视频制作大师 (charles-video-maker)

> **用代码和真实素材做视频，用机器讲概念。**
> 代码逐帧渲染 + 配音流水线 + 事实核查 + 抖音复刻 + 等距机器插图。
> 品牌化改造：AI Skills 创作小店

[![许可](https://img.shields.io/badge/许可-MIT-blue)](https://opensource.org/licenses/MIT)
[![技术栈](https://img.shields.io/badge/技术-Python%20%7C%20Node%20%7C%20FFmpeg%20%7C%20Playwright-blue)]()
[![品牌](https://img.shields.io/badge/品牌-AI%20Skills%20创作小店-pink)](https://github.com/gyc567/great-skill-center)

---

## 🎯 它能做什么

| 能力 | 说明 |
|------|------|
| **代码渲染视频** | 写一个暴露 `render(t)` 的网页 → 脚本逐帧截图 → FFmpeg 合成 MP4 |
| **口播稿 → 视频** | 文字稿 → 合成配音 → 逐字时间戳 → 场景切换/字幕自动对齐 |
| **事实核查闸门** | 稿子里的价格、额度、日期先核查，渲染前过 `factcheck.py gate` |
| **真实素材打底** | 录屏 / 素材库 B-roll / 生成静帧 → 代码层渲成透明 `.mov` → 合成 |
| **抖音复刻** | 给一条爆款 → 蒸馏风格 → 重写文案 → 先测配乐 → 一锅出交付 |
| **机器讲概念** | 用 Anatomy 造一台会动的等距机器来讲原理（内置子技能） |
| **53 种画风** | Lemo-Opuscar 风格库（油画厚涂 / 水彩 / 浮世绘 / 水墨 / 像素 RPG…） |

---

## 🚀 三步跑通

```bash
# 1. 安装（隔离环境，不污染系统）
bash scripts/setup.sh --install

# 2. 渲染一张封面帧
export PATH="$HOME/.venvs/charles-video-maker/bin:$PATH"
python3 scripts/render.py index.html cover.png --still 0.0 --size 1080x1920

# 3. 渲染整条视频
python3 scripts/render.py index.html out.mp4 --size 1080x1920 --fps 30 --duration 30
```

**实测**：1080×1920 / 30fps / 90 帧，渲染耗时 **20.2 秒**，产出 H.264 MP4。

---

## 🧭 四条分流路线

| 用户要的 | 走哪条 | 从哪读起 |
|---|---|---|
| 一条视频（宣传片 / 动效 / 知识讲解） | 视频流程（第 0–6 步） | `SKILL.md` |
| 一张插图 / 原理图（不是视频） | Anatomy 流程 | `anatomy/SKILL.md` |
| 抖音视频 / 复刻爆款 / 找选题 | 抖音模式 | `references/douyin-remake.md` |
| 讲原理且概念能对应机器 | 先造机器再配音渲染 | `references/anatomy-video.md` |

---

## 📦 目录结构

```
charles-video-maker/
├── SKILL.md                    # 主流程：分流 + 7 步视频流程 + 交付规范
├── scripts/
│   ├── setup.sh                # 一键安装（系统依赖 + venv + Chromium + Node 依赖）
│   ├── check_env.py            # 环境自检
│   ├── render.py               # 逐帧渲染器（静帧 / 视频 / 透明 .mov）
│   ├── render_parallel.py      # 并行渲染（快约 2.8 倍，帧数完全一致）
│   ├── analyze_video.py        # 参考视频抽帧分析
│   ├── audio_tools.py          # 音效合成 / 响度归一 / 节拍检测
│   ├── factcheck.py            # 事实核查表：extract + gate
│   ├── qa_stills.py            # 场景拼图自检
│   ├── still_check.py          # 静止检测（>2 秒不动就报）
│   ├── topic_name.py           # 标题 → 安全文件名
│   ├── gemini_copy.py          # 文案交给本地 Gemini 写 + 硬校验
│   ├── douyin_*.py             # 抖音：选题 / 复刻 / 发布 / 数据
│   ├── voice/                  # TTS / 混音 / 配乐 / 对齐 / 时间轴
│   ├── footage/                # 录屏 / 素材库 / 生成静帧 / 合成
│   └── lemo/setup.sh           # Lemo-Opuscar 风格库（按需下载）
├── references/                 # 15 篇方法论
├── templates/vertical-explainer/  # 竖版讲解模板（可直接起步）
├── bridge/                     # 虚拟时钟 + 视频叠加 + 页面包装
└── anatomy/                    # 内嵌子技能：等距机器插图（MIT，独立）
```

---

## 🔧 依赖

### 必需

| 依赖 | 用途 | 安装 |
|------|------|------|
| **Python ≥ 3.9** | 全部脚本 | 系统 |
| **FFmpeg / ffprobe** | 合成、抽帧、音效 | `apt install ffmpeg` |
| **Node ≥ 20.10** | Anatomy 的 React 示例 | `apt install nodejs` |
| **playwright** | 逐帧截图 | `scripts/setup.sh` 自动装 |
| **numpy** | 音效合成 | 同上 |
| **scipy** | 混音滤波（`voice/mix.py`） | 同上 |
| **soundfile** | 音频读写 | 同上 |

### 可选

| 组件 | 用途 | 怎么装 |
|------|------|--------|
| **Lemo-Opuscar** | 53 种画风 + Kokoro 配音 + 配乐 | `sh scripts/lemo/setup.sh deps` |
| **Gemini CLI (`agy`)** | 写旁白/标题/tags | `AGY_BIN=/path/to/agy` |
| **faster_whisper / mlx_whisper** | 配音逐字时间戳 | `pip install faster-whisper`（Mac 用 `mlx-whisper`）|
| **DingTalk API** | 抖音发布 | 需自行配置 |

> ✅ **基础渲染（画面 + 合成）只需要 playwright + numpy + ffmpeg**，
> 其余按需。`setup.sh` 只装必需项。

---

## ✅ 交付实测

| 项 | 结果 |
|----|------|
| `setup.sh --install` | ✅ **exit 0**，check_env 返回 `ready`（含 WebGL2 ✅） |
| 静帧渲染 | ✅ 1080×1920 PNG，4 帧哈希各不相同 |
| 视频渲染 | ✅ 90 帧 / H.264 / 1080×1920 / 30fps / **20.2 秒** |
| MP4 有效性 | ✅ ffprobe 确认 `duration=3.000000, nb_frames=90` |
| 抽帧验证 | ✅ ffmpeg 抽第 0/45 帧成功 |
| 脚本 CLI | ✅ 12 个脚本 `--help` 正常 |
| **Anatomy 测试** | ✅ **279/279 通过** |
| Anatomy 示例构建 | ✅ 5/6 成功（raptor-engine 需 >4 分钟） |
| WebGL2 | ✅ Chromium 156 报告 `WebGL2: yes` |

---

## 📄 许可与来源

**MIT**。本仓库是多来源合并，来源已在 `NOTICE.md` 逐目录标注：

| 路径 | 来源 | 许可 |
|------|------|------|
| `anatomy/` | [wheresryan22/anatomy](https://github.com/wheresryan22/anatomy) by Ryan | MIT（原样收录） |
| 其余主体 | [Kianzzz/xilo-opus-video](https://github.com/Kianzzz/xilo-opus-video) by 周行 | MIT |
| `bridge/`、`scripts/footage/` | 本仓库新增 | MIT |
| Lemo-Opuscar 集成 | [lemomo-ai/lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar) by LemoLab | MIT（按需下载，不收录） |

Copyright (c) 2026 周行（xilo-opus-video）· Ryan (@wheresryan22, anatomy) · LemoLab（lemo-opuscar）· anneheartrecord（原仓库作者）

> 完整的逐目录来源与改动说明见 `NOTICE.md`。本仓库是独立的新仓库，不是任何上游的 fork。

> Lemo-Opuscar 的示范片与静帧是 **CC BY 4.0**，不进本仓库，也不剪进用户成片。

---

## 📞 定制化开发

如需**定制化开发**，可直接联系 ERIC：

| 项 | 联系方式 |
|----|---------|
| **作者定位** | ERIC AI技术专家，专注于人工智能和自动化工具的研究与应用 |
| 邮箱 | `gyc567@gmail.com` |
| Twitter | `@EricBlock2100` |
| 微信 | `360369487` |
| Telegram | https://t.me/fatoshi_block |
| Telegram 频道 | https://t.me/cryptochanneleric |
| 加密情报 TG 群 | https://t.me/btcgogopen |
| YouTube 频道 | `@0XBitFinance` |
| 个人技术博客 | `topdigg.com` |

> **品牌**：AI Skills 创作小店
> 如需定制化开发，可直接联系 ERIC。

---

## 🔗 相关

- **AI Skills 创作小店** — https://github.com/gyc567/great-skill-center
- 姊妹 Skill：`anatomy`（等距机器插图，独立版）、`free-model-router`、`ub-quality-gates`
