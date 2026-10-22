# GymCoach — Personal Fitness Coach

A Hermes Agent skill that turns your agent into a personal gym coach for a sedentary beginner (50+, low flexibility). Coaching happens via **Discord** — share gym photos, get progressive plans, track sessions. No tmux or terminal needed.

## Structure

```
gymcoach/
├── SKILL.md          # Agentskills.io-compliant skill definition
└── README.md         # This file
```

## Install

1. Copy `gymcoach/` into your Hermes skills directory:
   ```bash
   cp -r gymcoach ~/.hermes/profiles/<your-profile>/skills/
   ```
2. Create the project workspace on your server:
   ```bash
   mkdir -p ~/gymcoach/{data,plans,photos}
   ```
3. Create your personal profile in `~/gymcoach/data/user-profile.md` (see SKILL.md for template)
4. Invite your agent to a private Discord channel and load the skill:
   ```bash
   hermes chat --skills gymcoach
   ```

## Usage

Share gym photos in the Discord channel — the coach analyses equipment, builds a Phase 1 plan, and tracks every session. Three phases: Mobility & Foundation (weeks 1-4) → Strength Entry (5-8) → Consolidation (9+).

## License

MIT — see [LICENSE](../LICENSE).

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
