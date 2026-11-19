---
name: manim-skill
description: Manim 数学动画的最佳实践、模式与可运行示例合集，覆盖 Manim Community Edition（manim）与 ManimGL（3b1b 版本）两套。包含 3 个子 Skill：manim-composer（编排创作）、manimce-best-practices（CE 版最佳实践）、manimgl-best-practices（GL 版最佳实践）。当用户要做"数学动画""公式动画""3Blue1Brown 风格动画""Manim 教学视频"时使用。
license: MIT
---

# Manim Skills

> **AI Skills 创作小店** 整理版 · 上游项目经许可保留原署名与许可证
>
> 本 Skill 由 AI Skills 创作小店 收录整理，能力方向来自上游开源项目。
> 运行时命令、工具名、路径与协议标识均保持原样以确保可用性。

**Manim 数学动画**的最佳实践、模式与可运行示例合集，覆盖两套主流版本。

## 两个版本

| 版本 | Skill | 说明 |
|---|---|---|
| Manim Community Edition（`manim`） | `manimce-best-practices` | 社区维护，API 稳定，文档全 |
| ManimGL（3b1b 版本） | `manimgl-best-practices` | 3Blue1Brown 使用的版本，3D 与着色器更强 |

## 子 Skill

| Skill | 作用 |
|---|---|
| `manim-composer` | 编排创作 —— 从想法到成片的组织方法 |
| `manimce-best-practices` | CE 版最佳实践 |
| `manimgl-best-practices` | GL 版最佳实践 |

子 Skill 位于 `skills/<name>/SKILL.md`。

## 环境要求

Manim 需要系统级 `cairo` / `pango` 依赖，安装方式随系统而异：

```bash
# Ubuntu / Debian
sudo apt install libcairo2-dev libpango1.0-dev pkg-config python3-dev ffmpeg

# macOS
brew install cairo pango pkg-config ffmpeg
```

装好后：

```bash
pip install manim        # Community Edition
pip install manimgl      # 3b1b 版本
```

## 自测

本仓库附带的测试脚本会抽取 Markdown 里的代码块并逐个渲染验证：

```bash
cd tests/manimce && python3 test_all_skills.py -j 4
cd tests/manimgl && python3 test_all_skills.py -j 4
```

## 上游与许可

- 上游：https://github.com/adithya-s-k/manim_skill
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
