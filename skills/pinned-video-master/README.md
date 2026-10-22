# 个人 IP 置顶视频生成大师（pinned-video-master）

> 把一份个人简介，变成一段 30 秒的「我是谁」置顶视频。

## 为什么需要它

陌生人刷到你的主页，看完置顶视频就该知道三件事：**你是谁、你干过什么、你能帮他什么**。
一段可信的 30 秒视频，胜过十次自我介绍——这是个人 IP 最划算的一笔投入。

这个技能把「经历」编译成「有活人感的表达」：先建可信档案，再写强钩子脚本，
再出分镜，最后可调用 HeyGen 生成数字人成片。

## 核心特性

| 特性 | 说明 |
|---|---|
| 六模块档案 | 身份 / 经历 / 现状 / 服务 / 证据 / 平台风格，缺项标「待补」绝不编造 |
| 30 秒五段结构 | 钩子 3s → 身份 5s → 背书 12s → 现状 7s → 价值 CTA 3s |
| 中英双语 | 英文版按英文语感重写，不是逐字翻译 |
| 自动体检 | 可信度表 + 活人感表 + 迭代动作表，最多迭代 2 轮 |
| HeyGen 出片 | 竖屏/横屏、可调语速、可带字幕，自动轮询并下载 |
| 多平台适配 | 抖音 / 小红书 / 视频号 / B站 / LinkedIn 各版差异对照 |

## 快速开始

### 1. 建档
```bash
# 技能会引导你回答六组问题，生成 pinned-dossier.md
```

### 2. 出脚本
五段结构输出，中文 ≤90 字，英文 ≤75 词。

### 3. 体检
```bash
python3 scripts/pv-check.py --dossier pinned-dossier.md --script script.txt --stage full
```

### 4. 出片
```bash
export HEYGEN_API_KEY=你的key
python3 scripts/pv-generate.py \
  --dossier pinned-dossier.md \
  --script script.txt \
  --avatar-id <AVATAR_ID> \
  --voice-id <VOICE_ID> \
  --output out/pinned-video.mp4
```

预览请求体（不调用 API、不消耗配额）：
```bash
python3 scripts/pv-generate.py --script script.txt --avatar-id A --voice-id V --dry-run
```

## 目录结构

```
pinned-video-master/
├── SKILL.md                    主入口（入口行为 / 路由 / 结构 / 红线）
├── README.md                   本文件
├── SPEC.md                     规格说明
├── references/
│   ├── task-intake.md          建档与断点续访
│   ├── task-script.md          脚本与口播成稿
│   ├── task-storyboard.md      分镜与画面设计
│   ├── task-generate.md        HeyGen 生成
│   ├── task-platform.md        多平台适配
│   ├── task-quality.md         质量检测与迭代
│   └── launch-zh-CN.md         新手入门（中文）
│   └── launch-en.md            新手入门（英文）
├── templates/
│   ├── dossier-template.md     档案模板
│   ├── script-template.md      脚本模板
│   └── storyboard-template.md  分镜表模板
└── scripts/
    ├── pv-check.py             档案与脚本体检
    └── pv-generate.py          HeyGen 调用与轮询
```

## 设计原则

- **不编造**：经历、数字、客户名、资质只来自用户本人；缺失标「待补」。
- **先确认后出片**：脚本全文必须经用户一次明确确认才生成。
- **Key 不落盘**：`HEYGEN_API_KEY` 只从环境变量读，绝不写进档案或仓库。
- **不承诺流量**：技能负责让内容可信，不负责流量保证。

## 品牌

AI Skills 创作小店

## License

MIT

<!-- ERIC-AUTHOR-INFO:START -->
---

## 📬 作者信息

**ERIC** — AI技术专家，专注于人工智能和自动化工具的研究与应用

| 渠道 | 链接 |
|------|------|
| 📧 邮箱 | gyc567@gmail.com |
| 🐦 Twitter | [@EricBlock2100](https://twitter.com/EricBlock2100) |
| 💬 微信 | 360369487 |
| ✈️ Telegram | [@fatoshi_block](https://t.me/fatoshi_block) |
| 📢 Telegram 频道 | [@cryptochanneleric](https://t.me/cryptochanneleric) |
| 🔐 加密情报 TG 群 | [@btcgogopen](https://t.me/btcgogopen) |
| ▶️ YouTube | [@0XBitFinance](https://www.youtube.com/@0XBitFinance) |
| 🌐 个人技术博客 | [topdigg.com](https://topdigg.com) |

> 本 Skill 由 ERIC 免费提供。想深入交流或获取更多同类 Skill，欢迎通过上表任一渠道联系。

<!-- ERIC-AUTHOR-INFO:END -->
