---
name: animated-explainer-skills
description: 一套完整的 Kurzesagt 风格动画讲解视频生产系统 —— 分层视差世界、飞行吉祥物、GSAP 物理感编排、YouTube 留存方法论、0.5s 分辨率重叠审计和逐场景配音流水线，产物是单个自包含 HTML 文件。包含 4 个子 Skill：explainer-studio（7 阶段引导式主流程）、explainer-assets（组件与角色生成）、gsap-explainer（编排与制作）、retention-pass（留存优化）。当用户要"做一条动画讲解视频""科普动画""Kurzgesagt 风格""用 HTML 做动画视频"时使用。
license: MIT
---

# Animated Explainer Skills

> **AI Skills 创作小店** 整理版 · 上游项目经许可保留原署名与许可证
>
> 本 Skill 由 AI Skills 创作小店 收录整理，能力方向来自上游开源项目。
> 运行时命令、工具名、路径与协议标识均保持原样以确保可用性。

一套完整的 **Kurzgesagt 风格动画讲解视频**生产系统。产物是**单个自包含 HTML 文件**，可直接播放和分享。

## 子 Skill

| Skill | 作用 |
|---|---|
| `explainer-studio` | **从这里开始** —— 7 阶段引导流程：脚本 → 素材 → 编排 → 留存 → 闸门 → 配音 → 发布，每阶段都有退出检查表 |
| `explainer-assets` | 生成精心制作的组件、道具、角色与世界 |
| `gsap-explainer` | 编排方法论与制作落地（GSAP 3.13） |
| `retention-pass` | YouTube 留存率方法论 |

子 Skill 位于 `skills/<name>/SKILL.md`。

## 核心能力

- **分层视差世界** —— 3 个深度层，剪辑间推轨运镜
- **物理感编排** —— `CustomBounce` 带挤压拉伸（挤压本身就是重量）、`Physics2D` 爆散带可复现的索引种子碎片
- **Kurzgesagt「保险丝」动作** —— `MorphSVG` 把 N 个对象变成它们代表的概念
- **飞行吉祥物** —— 指、点、跳、反应，默认是友好的蜜蜂，换一个 SVG 字符串即可换品牌
- **人口即角色** —— 数量是little角色，不是圆点
- **可跳转播放器** —— 点击跳转条、章节刻度、←/→ 键、滚动自动播放、reduced-motion 降级

## 参考构建

`skills/gsap-explainer/scaffold.html` 是可直接运行的 5 场景参考构建，涵盖全部模式。主题是「复利如何滚雪球」，可整体替换。

## 上游与许可

- 上游：https://github.com/BusyBee3333/animated-explainer-skills
- 许可：MIT
- 依赖：GSAP 3.13（免费）

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
