# X Algorithm Expert — AI Skill

> A 400+ line intelligence skill that makes any AI assistant an expert on X's recommendation algorithm. Covers 22 engagement signals, Phoenix ML model, 77+ topic categories, thread strategies, and niche-specific optimization.

## Installation

### For Antigravity / Gemini CLI

```bash
# Clone the skill to your global skills directory
mkdir -p ~/.gemini/antigravity/skills/x-algorithm-expert
cp skill/SKILL.md ~/.gemini/antigravity/skills/x-algorithm-expert/SKILL.md
```

Or from GitHub:

```bash
# Download directly
curl -o ~/.gemini/antigravity/skills/x-algorithm-expert/SKILL.md \
  https://raw.githubusercontent.com/MrChartist/x-algorithm-toolkit/master/skill/SKILL.md
```

### For Workspace-Level Installation

```bash
# Add to your project
mkdir -p .agents/skills/x-algorithm-expert
cp skill/SKILL.md .agents/skills/x-algorithm-expert/SKILL.md
```

## What the Skill Covers

| Section | Content |
|---------|---------|
| System Architecture | 7-stage pipeline: Query → Sourcing → Hydration → Filtering → Scoring → Selection → Response |
| 22 Engagement Signals | Every weight from `weighted_scorer.rs` + `ranking_scorer.rs` |
| Phoenix ML Model | Grok-based transformer architecture (256-dim, 4 heads, 2 layers) |
| 10-Point Scoring | Score tweets 0-100 with S/A/B/C/D/F grades |
| Hook Writing | 7 strong patterns, 3 weak patterns, scoring 0-10 |
| Author Diversity | Exact decay formula: `(1-floor) × decay^position + floor` |
| OON Viral Mechanics | How tweets escape your follower bubble |
| Topic Classification | 77+ verified categories from `topic_ids_filter.rs` |
| 18 Safety Filters | Pre-scoring and post-selection filter pipeline |
| Thread Strategy | 6 proven templates with structural rules |
| Content Templates | 7 high-performance tweet formats |
| Niche Optimization | 7 niches with signal-specific strategies |

## Activation Triggers

The skill activates automatically when you ask about:
- X algorithm, tweet scoring, viral content
- Hook writing, thread building
- Engagement optimization, content strategy
- How the For You feed works
- Writing, scoring, rewriting, or improving tweets

## Source

All data extracted from X's open-source algorithm repository (`twitter/the-algorithm`).

## License

MIT — Built by [Mr_Chartist](https://github.com/MrChartist)

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
