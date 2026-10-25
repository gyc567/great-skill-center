# AI Skills 创作小店

> **112 个可直接投产的 AI Agent Skills** —— 营销增长、视频电影、内容创作、开发工程、个人 IP、电商出海六大领域，全部免费使用。

[![Skills](https://img.shields.io/badge/Skills-112-blue)](skills/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Author](https://img.shields.io/badge/author-ERIC-orange)](https://topdigg.com)

---

## 这是什么

一个**精选、验证过、可直接使用**的 AI Agent Skills 仓库。

每个 Skill 都是一个独立目录，包含 `SKILL.md` 主文件加上配套的 `references/`、`templates/`、`scripts/`、`assets/`，可以单独取用、单独安装、单独卖。

- **不是**一堆提示词合集 —— 每个 Skill 都有可执行脚本、有质检工具、有失败边界
- **不是**简单的目录堆砌 —— 全部统一了品牌、作者信息、规格标识
- **不是**只给别人看的 —— 装上就能跑，不依赖本仓库其它 Skill

---

## 快速开始

### 方式一：直接复制（推荐）

```bash
git clone https://github.com/gyc567/great-skill-center.git
cp -r great-skill-center/skills/你的目标skill ~/.agents/skills/
```

### 方式二：整个装上

```bash
git clone https://github.com/gyc567/great-skill-center.git
cp -r great-skill-center/skills/* ~/.agents/skills/
```

### 方式三：单个下载

```bash
npx degit gyc567/great-skill-center/skills/geo-audit ~/.agents/skills/geo-audit
```

> 所有 Skill 的 `SKILL.md` 位于各自目录根部，可直接被 Claude Code / Cursor / Codex / Hermes Agent / OpenHands 等支持 agentskills.io 规范的工具加载。

---

## 六大分类

### 🎬 视频与电影（28）

电影级视觉语言、AI 视频提示词、成片合成、动效引擎。

| Skill | 说明 | 定价 |
|-------|------|------|
| `cinematic-director-language` | 电影导演视觉语言大师 — 20 方法论模块 + 12 位导演镜头语法 | ¥39.9 |
| `cinematic-ad-film-master` | 电影广告大片大师 — 把普通产品拍成奢侈品级大片 | ¥29.9 |
| `ai-shortfilm-prompt` | AI 短片提示词大师 — 25 个中英双语场景模板 | ¥19.9 |
| `product-short-video-master` | 产品短视频自动化大师 — 从一张图到成片全流程 | ¥19.9 |
| `pinned-video-master` | 个人 IP 置顶视频生成大师 — 30 秒「我是谁」视频 | ¥39.9 |
| `framefields` / `framefields-compose` / `framefields-effects` / `framefields-render` | WebGPU 代码视频 — 渲染 / 动画 / VFX / 导出四件套 | ¥9.9~19.9 |
| `video-shot-craft` | 电影级产品视频 — Remotion + 2.5D 运镜 | ¥19.9 |
| `ffmpeg` / `gsap-plugins` / `beautiful-mermaid` / `d3-viz` | 视频处理 / GSAP 特效 / 图表渲染 / 交互可视化 | ¥9.9~19.9 |
| `action-scene-director` / `cinematic-asset-designer` / `travel-film-director` | 动作打戏 / 概念美术 / 文旅宣传片 | ¥14.9 |
| `miora-video-studio-cn` / `short-video-scripter` / `douyin-video-publish-sop` | 视频工作台 / 短视频脚本 / 抖音发布 SOP | — |
| `agentcut-video-studio` | AI 视频剪辑工作室 — 60+ 动效组件 + 8 套风格 + Remotion 渲染 | ¥39.9 |
| `code-film-studio` | 代码电影工作室 — Node 驱动的电影级视觉引擎 | ¥39.9 |
| `remotion-video-master` | Remotion 视频编程大师 — 代码化视频 + 教程场景驱动 | ¥29.9 |
| `animation-vocabulary` / `find-animation-opportunities` / `improve-animations` / `review-animations` | 动效词汇表 / 动效机会挖掘 / 动效改进 / 动效评审 | ¥9.9 |
| `awesome-seedance` | Seedance 视频提示词库 | — |### 📈 营销与增长（34）

GEO（生成式引擎优化）全链路、竞品情报、关键词研究、爆款公式。

| Skill | 说明 | 定价 |
|-------|------|------|
| `geo-audit` | AI 全站 GEO 审计大师 — 让 ChatGPT / Perplexity 引用你 | ¥39.9 |
| `geo-proposal` / `geo-report` / `geo-report-pdf` | 客户方案书 / 交付报告 / PDF 导出 | ¥29.9 / 19.9 / 14.9 |
| `geo-citability` / `geo-content` / `geo-schema` / `geo-technical` | 可引用性 / 内容质量 / 结构化数据 / 技术审计 | ¥19.9 |
| `geo-brand-mentions` / `geo-prospect` / `geo-platform-optimizer` | 品牌扫描 / 线索挖掘 / 平台优化 | ¥19.9 |
| `geo-compare` / `geo-crawlers` / `geo-llmstxt` | 竞品对比 / 爬虫分析 / llms.txt 生成 | ¥9.9 |
| `audit` / `competitors` / `keywords` / `strategy` | 社媒搜索审计 / 竞品情报 / 关键词研究 / 增长策略 | ¥9.9 |
| `xhs-title-formula` / `viral-headlines` / `hook-writer-pro` / `x-emotion-hook` | 小红书标题公式 / 爆款标题 / 钩子写作 | — |
| `wechat-article` / `wechat-draft-push` / `wechat-topic-hunter` | 公众号爆文 / 草稿推送 / 选题猎手 | ¥9.9 |
| `douyin-script-master` / `douyin-search-word-ending` | 抖音脚本 / 结尾热搜词截图法 | — |
| `launch-skill` | 产品上线全流程启动 | ¥39.9 |
| `link-ops-master` | 短链与归因运营大师 — 命名规范 / UTM / A-B / 转化回传 | ¥29.9 |
| `x-account-analyzer` / `x-algorithm-expert` / `x-research-master` / `tweet-composer` | X 账号诊断 / 算法机制 / 深度研究 / 推文创作 | ¥9.9 |
| `timezone-information-arbitrage` | 时区信息套利 — 跨时区信息差机会挖掘 | — |### ✍️ 内容创作（15）

去 AI 味、选题、跨平台改写、信息图、复盘。

| Skill | 说明 | 定价 |
|-------|------|------|
| `ai-humanizer` | AI 痕迹去除师 — 识别并清除 74 种 AI 写作特征 | — |
| `content-topic-generator` / `content-writing-style` / `content-publish-precheck` | 选题 / 风格底盘 / 发布前检查 | — |
| `infographic-master` / `social-review-master` / `social-monthly` | 信息图设计 / 社媒复盘 | ¥9.9 |
| `article-replatformer` / `argument-structure-master` / `x-original-content-creator` | 跨平台改写 / 论证结构 / 原创内容 | — |
| `youtube-monthly` / `post-writer-pro` / `thread-writer-pro` | 月度总结 / 长文 / 长帖写作 | — |
| `content-strategy-pro` | 内容策略大师 — 选题到分发的完整策略 | ¥9.9 |
| `meeting-secretary` | 会议纪要大师 — 录音转结构化纪要 + 待办 | ¥9.9 |### 🛠️ 开发与工程（12）

代码审查、证明式校验、前端月报、PPT、技术文档。

| Skill | 说明 | 定价 |
|-------|------|------|
| `ai-proofreading-pro` / `litprog-skill` | 证明式校验 / Literate Programming | — / ¥9.9 |
| `frontend-monthly` / `frontend-slides` / `guizang-ppt-skill` / `slides-master` | 前端月报 / 幻灯片 | — |
| `prototype` / `reading-comprehension-master` / `distribb-skill` | 原型 / 阅读理解 / 分发 | — |
| `github-skill-audit-install` / `security-audit-master` | Skill 审计安装 / 安全审计 | — |
| `vocabulary-tiering-master` | 词汇分层大师 — 分级词表构建与记忆优化 | ¥9.9 |### 🎨 设计与可视化（11）

等距插图、SVG、图表、UI 选型、幻灯片。

| Skill | 说明 | 定价 |
|-------|------|------|
| `anatomy-business-charts` | 等距技术插图 — 商业场景图表 | — |
| `gzh-design` / `slides-master` / `guizang-ppt-skill` | 公众号排版 / 幻灯片 | ¥9.9 / — |
| `apple-design` / `emil-design-eng` / `pick-ui-library` | 苹果风格设计 / 设计工程 / UI 库选型 | — |
| `tailwind-design-system` / `midjourney-quick-ref` | Tailwind 设计系统 / MJ 速查 | ¥14.9 / — |
| `elevenlabs` | ElevenLabs 语音合成指南 | — |
| `flux-best-practices` | FLUX 图像生成最佳实践 | — |### 💼 个人 IP 与商业（14）

| Skill | 说明 | 定价 |
|-------|------|------|
| `personal-ip-master` | AI 个人 IP 打造大师 — 人设 / 内容 / 变现全链路 | ¥39.9 |
| `interview-100` | 面试题库 | — |
| `weekly-report-template` | 周报模板 | — |
| `sales-brain` / `sales-ops` / `remote-dispatch` | 销售脑 / 销售运营 / 远程任务调度 | ¥9.9 |

| `service-ops-master` | 极致服务运营大师 — 服务信条 / 26 项权益 / 裂变 SOP / 完整话术库 | ¥39.9 |
| `company-valuation-master` | 企业估值大师 — 投融资估值建模 | ¥29.9 |
| `earnings-preview-master` | 财报预期大师 — 业绩前瞻与预期差分析 | ¥19.9 |
| `life-decision-master` | 人生决策大师 — 结构化决策框架 | ¥9.9 |
| `options-payoff-visualizer` | 期权收益可视化 — 盈亏结构直观呈现 | — |
| `stock-monthly` / `stock-correlation-analyst` / `stock-strategy-collection` | 月度复盘 / 相关性分析 / 策略合集 | ¥9.9 |### 🧰 集合包（9 个目录）

按场景打包的组合目录，内含多个完整 Skill：

`anbeime/`（61 个 · 视频与电商全家桶）· `best/`（15 个 · 办公文档全套）· `ecommerce/`（38 个 · 跨境电商）· `youtube-skills/`（12 个 · YouTube 全流程）· `chinese-social-pack/`（4 个）· `garden/`（5 个 · 设计与内容）· `productivity-pack/`（4 个）· `resume-report-maker/` · `great/`

---

## 目录结构

```
great-skill-center/
├── skills/
│   ├── geo-audit/
│   │   ├── SKILL.md          # 主文件（agentskills.io 规范）
│   │   ├── references/       # 深度参考文档
│   │   ├── templates/        # 可直接填写的模板
│   │   ├── scripts/          # 可执行脚本
│   │   └── assets/           # 静态资源
│   ├── cinematic-director-language/
│   └── ...
├── scripts/
│   └── brand-inject.py       # 批量注入作者信息（幂等）
├── docs/
├── SKILLS.md                 # 技能总览
├── SKILLS_INDEX.md           # 索引
├── AUDIT_REPORT.md           # 质量审计报告
└── README.md
```

---

## 设计原则

| 原则 | 说明 |
|------|------|
| **自包含** | 每个 Skill 独立可用，不强依赖其它 Skill |
| **可验证** | 脚本能跑出真实结果，不返回伪造输出 |
| **有边界** | 明确写出能力边界与红线，不越界承诺 |
| **统一规格** | `SPEC-DEFAULT` / `PLAN-DEFAULT` / `SKU-DEFAULT` |
| **带质检** | 关键 Skill 内置体检工具，生成前先自检 |
| **中英双语** | 面向出海场景的 Skill 提供双语版本 |

---

## 贡献

发现问题和改进建议，欢迎直接联系 ERIC（见下方联系方式），或提 Issue / Pull Request。

新增 Skill 请遵循 `skills/` 下现有规范：`SKILL.md` 置于目录根部、frontmatter 完整、附 `references/` 或 `templates/`。

---

## 📬 联系作者

### ERIC

**AI技术专家，专注于人工智能和自动化工具的研究与应用**

### 联系方式与平台

| 渠道 | 链接 |
|------|------|
| 📧 邮箱 | [gyc567@gmail.com](mailto:gyc567@gmail.com) |
| 🐦 Twitter | [@EricBlock2100](https://twitter.com/EricBlock2100) ↗ |
| 💬 微信 | `360369487` |
| ✈️ Telegram | [https://t.me/fatoshi_block](https://t.me/fatoshi_block) ↗ |
| 📢 Telegram 频道 | [https://t.me/cryptochanneleric](https://t.me/cryptochanneleric) ↗ |
| 🔐 加密情报 TG 群 | [https://t.me/btcgogopen](https://t.me/btcgogopen) ↗ |
| ▶️ YouTube 频道 | [@0XBitFinance](https://www.youtube.com/@0XBitFinance) ↗ |
| 🌐 个人技术博客 | [topdigg.com](https://topdigg.com) ↗ |

---

### 💼 定制化开发

**如果你需要把某个 Skill 改造成适合自己业务的样子，或者需要一套全新的定制 Skill —— 直接联系我。**

常见的定制方向：

- 把现有 Skill 适配到你自己的业务流程、数据源与输出格式
- 围绕你的行业场景封装垂直 Skill（例如你所在行业的 GEO 审计、选品分析、内容生产）
- 把多个 Skill 串成一条端到端流水线（建档 → 生产 → 分发 → 复盘）
- 私有化部署：把依赖的第三方 API 换成你自己的模型与接口
- 团队内部版本：统一规范、批量安装、内部培训材料

> **所有 Skill 均免费使用。** 定制化开发、付费咨询与商业授权，请通过上表任一渠道直接联系 ERIC，收到消息会尽快回复。

---

## 📄 许可

本仓库 Skills 遵循 MIT 许可发布（个别 Skill 保留原作者版权声明，见各 Skill 的 `LICENSE` 或 `metadata` 字段）。

**作者：ERIC — AI Skills 创作小店**
