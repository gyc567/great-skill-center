---
name: higgsfield-skills
description: Higgsfield AI 的完整 Skill 集合 —— 图像/视频/3D 资产/音频生成、品牌系统、产品图、YouTube 缩略图、无脸人视频、网页与可玩游戏、身份一致性（soul id）以及视频解说。包含 9 个子 Skill。当用户要做"生成图片""做视频""换脸一致性""产品图""缩略图""广告素材""3D 资产"时使用。
license: MIT
---

# Higgsfield Skills

> **AI Skills 创作小店** 整理版 · 上游项目经许可保留原署名与许可证
>
> 本 Skill 由 AI Skills 创作小店 收录整理，能力方向来自上游开源项目。
> 运行时命令、工具名、路径与协议标识均保持原样以确保可用性。

**Higgsfield AI** 的完整 Skill 集合：生成、编辑、风格化、包装，全流程覆盖。

## 子 Skill

| Skill | 作用 |
|---|---|
| `higgsfield-generate` | **主入口** —— 图片/视频/3D/音频生成，含 Marketing Studio 与 Virality Predictor |
| `higgsfield-soul-id` | 身份一致性 —— 保持人脸/角色在多镜头间统一 |
| `higgsfield-brandkit` | 品牌系统与品牌手册 |
| `higgsfield-product-photoshoot` | 产品摄影棚效果 |
| `higgsfield-youtube-thumbnail` | YouTube 缩略图 |
| `higgsfield-marketplace-cards` | 电商详情卡片 |
| `higgsfield-faceless-video` | 无脸人视频（不出镜口播） |
| `higgsfield-video-explainer` | 视频解说 |
| `higgsfield-websites` | 可交互网页与小游戏 |

子 Skill 位于 `<name>/SKILL.md`。

## 常用模型（`higgsfield-generate` 默认）

| 用途 | 模型 |
|---|---|
| 图片 / 动图 / SVG | GPT Image 2.6 |
| 视频 | Seedance 2.5 |
| 卡通角色 | Nano Banana 2 |
| 广告 | Marketing Studio |
| 音频 | Seed Audio 1.0 |

## 前置条件

需要安装并登录 `higgsfield` CLI：

```bash
curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh
higgsfield auth login
```

## 目录说明

| 目录 | 用途 |
|---|---|
| `assets/` | 共享素材与资源 |
| `evals/` | 评测场景 |
| `scripts/` | 辅助脚本（`update-check.sh`） |
| `setup/` | 安装引导 |

## 上游与许可

- 上游：https://github.com/higgsfield-ai/skills
- 许可：MIT
- 官网：https://higgsfield.ai

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
