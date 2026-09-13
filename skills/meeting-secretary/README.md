# meeting-secretary

> 一人公司的社交智囊 Skill。帮你在每次重要会面前把局势想透。
> 不是"信息整理工具"，而是"帮你推导出该怎么准备"的智囊。

---

## 这是什么

每次见重要的人——投资人、媒体主编、品牌客户、导师、合作伙伴——你都只有一次机会留下印象。

`meeting-secretary` 不是让你填表然后出报告。它是一个**对话式智囊**：

```
你（固定底座，越用越准）
  × 对方（深搜 + 推断需求 + 累积档案）
  × 场景（会面类型自适应）
  → 策略（对话中想透 + markdown 沉淀）
```

**核心能力**：从对方的公开行为中推断他的隐性需求，然后找到他的需求和你的能力的交集——这就是这次会面的最佳策略。

---

## 用了哪些思维框架

这个 skill 把 18 个领域的专业方法论落地成可执行步骤：

### 情报收集层（L1 · OSINT）
- **CIA Intelligence Cycle**（情报五步循环）— Planning → Collection → Processing → Analysis → Dissemination
- **Trace Labs 三步法** — Identify / Verify / Amplify，No-touch 被动观察原则
- **Bazzell 七维度人物画像**（前 FBI 网络犯罪探员）— 人口统计 / 兴趣关注 / 组织关系 / 沟通模式 / 行为倾向 / 动机意图 / 专业技能

### 人格推断层（L2 · 心理学）
- **OCEAN / Big Five**（Kosinski & Stillwell, PNAS 2015）— 从数字足迹推断五大人格
- **DISC 快速画像法** — D 支配 / I 影响 / S 稳定 / C 严谨，对应不同沟通策略
- **Thin Slicing**（Ambady & Rosenthal 1992）— 30 秒视频判断性格准确率媲美长期接触
- **Pennebaker LIWC 语言分析** — 功能词（代词/介词）比内容词更暴露人格

### 需求推断层（L3）
- **JTBD 三层需求**（Clayton Christensen）— 功能性 / 情感性 / 社会性
- **Empathy Map 共情地图**（Nielsen Norman Group）— Says / Thinks / Does / Feels 四象限，矛盾处 = 突破口
- **社会交换分析** — 付出时间期望什么回报
- **BATNA 对方版**（Harvard PON）— 他不见你还能找谁，你在候选名单第几
- **信息差分析** — 他对你的认知准不准、该释放什么修正

### 假设检验层（L4 · CIA）
- **ACH 竞争假设分析**（Richards Heuer, CIA 45 年）— 列 2-3 个假设，矩阵交叉，**尝试否证**而非确认
- **关键假设检查**（CIA Tradecraft Primer）— 列出所有隐含假设逐一质问

### 策略制定层（L5 · 谈判 / 政治 / 军事）
- **Chris Voss Negotiation One Sheet**（前 FBI 首席人质谈判专家）— Goal / Summary / Accusation Audit / Calibrated Questions / Non-Cash Items
- **Voss Accusation Audit** — 提前列出对方可能对你说的最难听的话，用 Label 化解
- **Cialdini Pre-Suasion** — Unity Principle（找共性）/ Privileged Moment（注意力峰值）/ Franklin Effect（请教建议）
- **教员矛盾论** — 抓主要矛盾，集中优势兵力
- **Munger Inversion** — "这次会面怎么才能搞砸？" 反向思考
- **确认 → 升级 → 反转**（展示节奏）— 先强化第一印象，再给意外

### 简报输出层（L6）
- **白宫简报术**（Grant Harris, HBR）— 3 页以内，预判 Q&A 必选
- **McKinsey SCR 框架** — Situation / Complication / Resolution
- **Minto 金字塔原理** — 结论先行，每页过 So What 测试

---

## 用了哪些网页抓取工具

skill 设计为"**有专用工具时加速 / 没有时用通用 fallback**"，覆盖 10+ 平台：

| 平台 | PAI 首选工具 | 通用 Fallback |
|---|---|---|
| **X / Twitter** | `x-fetcher` skill | WebFetch + nitter/xcancel 镜像 / WebSearch `site:x.com` |
| **微信公众号** | `wechat-fetcher` skill | UA 伪装 curl（MicroMessenger User-Agent）/ 搜狗微信 `weixin.sogou.com` |
| **微博** | — | WebSearch + WebFetch `m.weibo.cn` / Playwright |
| **小红书** | `union-search-skill` | WebSearch + 浏览器自动化 |
| **LinkedIn** | — | WebSearch `site:linkedin.com` / web.archive.org |
| **36氪 / 虎嗅 / 品玩** | `baoyu-url-to-markdown` | WebSearch + WebFetch |
| **B 站** | — | B 站开放 API (`api.bilibili.com/x/...`) |
| **YouTube** | `yt-search-download` / `baoyu-youtube-transcript` | `yt-dlp` CLI |
| **小宇宙 / Apple Podcast** | — | iTunes Search API + RSS + WebFetch |
| **GitHub** | `gh` CLI + `mcp__grep__searchGitHub` | GitHub REST API (`api.github.com`) |
| **登录态内容**（微信视频号/私域）| `bb-browser` / `agent-browser` | Playwright MCP / Puppeteer |
| **通用搜索 / 抓取** | — | **WebSearch + WebFetch（所有 Claude Code 环境都有）** |

**最小依赖**：即使所有 PAI 专用工具都不可用，skill 依然能跑——只靠 WebSearch / WebFetch / Read / Write / Edit / Glob / Grep / Bash 就能完成 90% 工作。

---

## 数据架构

```
~/.aoe/meeting-secretary/
├── me/
│   └── profile.md              ← 你的固定底座（越用越准）
├── contacts/
│   └── <人名>/
│       ├── profile.md           ← 对方档案（每次会面后累积更新）
│       ├── meetings/
│       │   └── <日期>_<主题>.md  ← 策略简报 + 复盘
│       └── research_raw/        ← 原始搜索数据
└── config.json
```

**越用越强**：
- 同一人第 N 次见面 → 自动读前 N-1 次所有记录作为上下文
- AI 推断被你修正 → 修正结果写回档案（系统学习你的判断）

---

## 使用

在 Claude Code 中直接说：

> "帮我准备见 XXX"
> "我要见 XXX"
> "调研这个人"
> "约了见面"
> "prep meeting with X"

skill 进入智囊模式：对话追问 → 深搜对方 → 推断需求 → 挑弹药 → 出策略简报。

---

## 五类场景剧本

skill 内置五套完整剧本，根据会面类型自动路由：

| 类型 | 你的位置 | 策略核心 |
|---|---|---|
| **A. 被采访 / 上节目** | 被展示方 | 控制叙事 + 故事选择 + 预设问答 |
| **B. 求资源（融资/合作/引荐）** | 需求方 | 不可替代性 + 降低决策成本 |
| **C. 接商单（被求资源）** | 供给方 | 针对需求展示 + 交付框架 |
| **D. 平等交流（同行/校友）** | 对等 | 找共鸣 + 建长期关系 |
| **E. 请教 / 拜访** | 学习方 | 带具体问题 + 不浪费对方时间 |

---

## 五大铁律（违反 = 失败）

1. **从对方出发，不从你出发** — 先花 80% 精力分析对方，再 20% 挑自己的牌
2. **不震撼的不要拿出来** — 每条弹药过三关（能震住人？有区分度？匹配需求？）
3. **找两个极端** — 两个反差 > 十个中等
4. **助手不是领导** — 给具体文件路径 / 话术 / 时间点，不给空泛建议
5. **有推导不迎合** — 先有独立判断，用户修正再调整

---

## 可移植性

- ✅ 不依赖 PAI 特有 skill（有则加速，无则 fallback）
- ✅ 跨平台（Mac / Linux / WSL）
- ✅ 最小依赖：只需 Claude Code 自带的 WebSearch / WebFetch / Read / Write / Glob / Grep / Bash

---

## 目录

[SKILL.md](./SKILL.md) — 3400+ 行完整定义（20 章：宪法 / 五铁律 / 九阶段 / 平台技术底层 / 五类场景剧本 / 反模式陷阱库 / 输出模板）

---

## 许可证

MIT License — 见 [LICENSE](./LICENSE)

---

*v2.0 · 2026-04-17*
*基于产品设计 v3 + 18 领域方法论武器库 + 真实案例实战验证*

---

## 📱 关注作者 / Follow Me

如果这个仓库对你有帮助，欢迎关注我。后面我会持续更新更多 AI Skill、会面准备、信息整理和方法论工作流。

If this repo helped you, follow me for more AI skills, meeting prep workflows, research systems, and practical frameworks.

- X (Twitter): [@xiaoerzhan](https://x.com/xiaoerzhan)
- 微信公众号 / WeChat Official Account: 扫码关注 / Scan to follow

<p align="center">
  <img src="./follow-wechat-qrcode.jpg" alt="Jane WeChat Official Account QR code" width="300" />
</p>

<p align="center"><strong>中文：</strong>欢迎关注我的公众号，一起研究 AI Skill、会面准备、人物研究和方法论应用。</p>

<p align="center"><strong>English:</strong> Follow my WeChat Official Account for more AI skills, meeting prep workflows, people research, and practical frameworks.</p>
