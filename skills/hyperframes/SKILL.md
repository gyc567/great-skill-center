---
name: hyperframes
description: HTML 写视频 —— HyperFrames 视频渲染框架的完整 Skill 集合。写 HTML，用浏览器渲染成视频。包含 9 个子 Skill：hyperframes（主框架）、hyperframes-cli（命令行）、hyperframes-registry（组件与动画块注册表）、media-use（素材生成与管理）、figma（Figma 导入）、slideshow（幻灯片视频）、style-sampling（风格采样）、remotion-to-hyperframes（Remotion 迁移）、reverse-any-video（视频逆向）。当用户要做"HTML 转视频""程序化视频""浏览器渲染视频""动态图形"时使用。
license: Apache-2.0
---

# HyperFrames

> **AI Skills 创作小店** 整理版 · 上游项目经许可保留原署名与许可证
>
> 本 Skill 由 AI Skills 创作小店 收录整理，能力方向来自上游开源项目。
> 运行时命令、工具名、路径与协议标识均保持原样以确保可用性。

**写 HTML，渲染视频。** 面向 Agent 设计的视频渲染框架。

## 子 Skill

| Skill | 作用 |
|---|---|
| `hyperframes` | **主框架** —— 场景、时间轴、动画模型 |
| `hyperframes-cli` | 命令行：构建、预览、渲染 |
| `hyperframes-registry` | 组件与动画块注册表（`registry/registry.json` 是索引） |
| `media-use` | 素材生成与管理（图片、视频、音频） |
| `figma` | 从 Figma 导入设计稿 |
| `slideshow` | 幻灯片视频 |
| `style-sampling` | 从参考视频采样风格 |
| `remotion-to-hyperframes` | 从 Remotion 项目迁移 |
| `reverse-any-video` | 逆向还原任意视频的构造方式 |

子 Skill 位于 `skills/<name>/SKILL.md`。

## 快速上手

```bash
# 安装 CLI
npm install -g hyperframes

# 预览
hyperframes studio

# 渲染
hyperframes render scene.html -o out.mp4
```

## 环境要求

- Node.js >= 22
- Chrome / Chromium（渲染与检查）

## 关于遥测

上游默认带匿名用量遥测。本仓库版本已将 PostHog key 改为**从环境变量读取**，默认**不发送**任何遥测：

```bash
export HYPERFRAMES_NO_TELEMETRY=1   # 显式关闭
export DO_NOT_TRACK=1              # 通用退出标记
```

需要启用遥测时，自行设置 `HYPERFRAMES_POSTHOG_KEY` 或 `MEDIA_USE_POSTHOG_KEY`。

## 上游与许可

- 上游：https://github.com/heygen-com/hyperframes
- 许可：Apache-2.0
- 官网：https://hyperframes.studio

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
