# 好用的 Skills 推荐

本文件记录一些好用的 Claude Code / AI Agent Skills。

---

## Taste Skill

**Anti-Slop Frontend Framework for AI Agents** - 让 AI 生成的界面更有设计感，不再是千篇一律的 boilerplate。

### 基本信息

| 项目 | 内容 |
|------|------|
| GitHub | https://github.com/Leonxlnx/taste-skill |
| 作者 | [Leonxlnx](https://github.com/Leonxlnx) |
| 官网 | https://tasteskill.dev |
| License | MIT |
| 赞助商 | IMG.LY, Animations.dev, Sent.dm, Vercel OSS |

### 核心功能

Portable **Agent Skills** that upgrade AI-built interfaces: stronger layout, typography, motion, and spacing instead of boilerplate-looking UIs.

包含 **image-generation skills** 用于生成参考图板（web, mobile, brand kits），可以配合 **ChatGPT Images** 或类似生成器使用，然后把设计稿交给 Codex, Cursor, Claude Code 来实现。

### 安装方式

```bash
npx skills add https://github.com/Leonxlnx/taste-skill
```

安装单个 skill：
```bash
npx skills add https://github.com/Leonxlnx/taste-skill --skill "design-taste-frontend"
```

### Skill 列表

#### Implementation Skills (输出代码)

| Skill | Install Name | 描述 |
|-------|-------------|------|
| **taste-skill** | `design-taste-frontend` | 🆕 v2 (experimental) - 默认技能。读取需求，推断设计语言，调整三个参数 (VARIANCE / MOTION / DENSITY)。包含 brief inference, design-system map, 禁止 em-dash, GSAP 代码骨架, redesign-audit protocol |
| **taste-skill-v1** | `design-taste-frontend-v1` | 原始 v1 版本，保留给需要精确行为的项目 |
| **gpt-tasteskill** | `gpt-taste` | 更严格的 GPT/Codex 变体：更高的 layout variance，更强的 GSAP 方向，更激进的 anti-slop |
| **image-to-code-skill** | `image-to-code` | 图片优先流程：生成网站参考图，分析，然后实现 frontend |
| **redesign-skill** | `redesign-existing-projects` | 改进现有项目：先审计 UI，然后修复 layout, spacing, hierarchy, styling |
| **soft-skill** | `high-end-visual-design` | 精致、冷静、高端 UI，更柔和的对比度、留白、高级字体、spring 动效 |
| **output-skill** | `full-output-enforcement` | 当模型输出半成品时：完整输出，禁止 placeholder 注释 |
| **minimalist-skill** | `minimalist-ui | 编辑类产品 UI (Notion/Linear 风格)，克制的调色板，清晰的结构 |
| **brutalist-skill** | `industrial-brutalist-ui` | 硬核机械语言：Swiss 字体，锐利对比度，实验性布局 |
| **stitch-skill** | `stitch-design-taste` | Google Stitch 兼容规则，可选 `DESIGN.md` 导出格式 |

#### Image Generation Skills (输出参考图)

| Skill | Install Name | 描述 |
|-------|-------------|------|
| **imagegen-frontend-web** | `imagegen-frontend-web` | 网站设计稿：hero, landing, 多区块强 typography 和 spacing |
| **imagegen-frontend-mobile** | `imagegen-frontend-mobile` | 移动端屏幕和流程：iOS/Android，mockups，可读字体 |
| **brandkit** | `brandkit` | 品牌套件：logo 方向、调色板、字体、跨类别身份应用 |

### 核心参数 (taste-skill only)

| 参数 | 范围 | 描述 |
|------|------|------|
| **DESIGN_VARIANCE** | 1-10 | 布局实验程度（低：居中/干净 · 高：不对称/现代） |
| **MOTION_INTENSITY** | 1-10 | 动画深度（低：hover · 高：scroll/magnetic） |
| **VISUAL_DENSITY** | 1-10 | 每屏信息密度（低：留白 · 高：密集仪表盘） |

### 使用建议

- 从 **taste-skill** (现在默认 v2) 开始
- 需要严格版用 **gpt-taste**
- 想做图片→代码流程用 **image-to-code-skill**
- 改进现有项目用 **redesign-skill**
- 视觉方向已选定则用 **soft-skill**, **minimalist-skill**, 或 **brutalist-skill**
- 模型总输出半成品加 **output-skill**
- 需要设计稿图片用 **imagegen-frontend-web**, **imagegen-frontend-mobile**, **brandkit**

### 设计示例

Created with taste-skill:

![Floria example](https://raw.githubusercontent.com/Leonxlnx/taste-skill/main/examples/floria-top.webp)
![Floria example](https://raw.githubusercontent.com/Leonxlnx/taste-skill/main/examples/floria-bottom.webp)

### 相关资源

- [tasteskill.dev](https://tasteskill.dev) - 官网
- [Changelog](https://www.tasteskill.dev/changelog) - 更新日志
- [@lexnlin](https://x.com/lexnlin) - Twitter
- hello@tasteskill.dev - 联系方式

---

*最后更新: 2026-07-21*
