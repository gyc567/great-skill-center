---
name: x-account-analyzer
description: >
  Twitter/X 账号逆向运营分析技能：输入任意 @handle，自动采集推文数据、
  分析内容性质与涨粉规律、归因增长驱动力、输出可复制的增长经验报告。
  内含 Twitter CLI + 多数据源自动安装与认证引导，用户无需额外安装任何工具。
  数据来源：twitter-cli + Exa搜索 + SuperX + SocialBlade(Jina) + fch(历史粉丝)。
triggers:
  - twitter/推特/x.com 分析
  - 账号分析/涨粉分析/运营分析
  - 竞品分析/对标分析
  - 内容策略/内容分类
  - 增长复盘/增长归因
  - 复制涨粉/学习涨粉
---
brand: AI Skills 创作小店
---

# Twitter 账号逆向分析 Skill

> **一句话定位**：给我一个 @handle，还你一份「为什么他能涨粉 + 你怎么复制」的全链路分析报告。

## 适用范围

- 🔍 任意 Twitter/X 公开账号的运营轨迹分析
- 📊 内容性质分类（技术/观点/互动/教程/营销/日常/…）
- 📈 涨粉规律与时间线复盘
- 🎯 涨粉归因（哪些内容带来了增长高峰）
- 📋 可复制的增长经验提取
- 🆚 竞品/对标账号对比分析
- 🧠 AI 驱动的内容策略建议

---

## 0) 环境自检与自动安装（所有任务的第一步）

> **核心理念**：用户安装本 Skill 后，不需要再手动安装任何 Twitter 相关工具。本步骤自动完成所有依赖安装与认证配置。
> 本 Skill 集成多数据源，安装时会一并部署：twitter-cli、fch（历史粉丝数）、Exa搜索、Jina Reader 等。

### 0.1) 一键安装所有依赖

按以下顺序自动检查并安装：

```bash
# ===== 工具 1: twitter-cli（核心推文采集） =====
if ! command -v twitter &>/dev/null; then
    echo "[安装] twitter-cli..."
    # 先确保 pipx 可用
    command -v pipx &>/dev/null || {
        python3 -m pip install --user pipx && python3 -m pipx ensurepath
        source ~/.zshrc 2>/dev/null || source ~/.bashrc 2>/dev/null
    }
    pipx install twitter-cli
fi
echo "twitter-cli: $(twitter --version 2>&1 || echo '安装失败')"

# ===== 工具 2: fch（历史粉丝数追踪，从 Wayback Machine 获取） =====
if ! command -v fch &>/dev/null; then
    echo "[安装] fch (Follower Count History)..."
    pipx install fch
fi
echo "fch: $(fch --version 2>&1 || echo '安装失败')"

# ===== 工具 3: mcporter（Exa 搜索，用于补充推文和社交数据） =====
if ! command -v mcporter &>/dev/null; then
    echo "[提示] mcporter 未安装，Exa 搜索将不可用"
    echo "可选安装: npm i -g mcporter"
fi

# ===== 工具 4: curl/Jina Reader（用于抓取 Social Blade 等第三方分析数据） =====
echo "curl: $(curl --version | head -1)"
echo "r.jina.ai: 通用网页阅读器（无需安装，直接 curl 调用）"
```

### 0.2) Twitter 认证配置

```bash
twitter status
```

- ✅ **已认证** → 跳到 0.3
- ❌ **未认证** → 向用户输出认证引导：

```
📋 Twitter 认证配置引导（约 2 分钟完成）

步骤 1：在浏览器中登录 https://x.com
步骤 2：安装 Cookie-Editor 浏览器扩展（Chrome/Firefox/Edge 均可）
步骤 3：在 x.com 页面上打开 Cookie-Editor
步骤 4：找到并复制以下两个 Cookie 值：
  • auth_token（名称为 "auth_token" 的 Cookie）
  • ct0（名称为 "ct0" 的 Cookie）
步骤 5：将这两个值告诉我，格式如：
  auth_token=xxxxxx
  ct0=yyyyyy
```

获取到用户的 `auth_token` 和 `ct0` 后，自动配置：

```bash
SHELL_RC="${HOME}/.zshrc"
grep -q "TWITTER_AUTH_TOKEN" "$SHELL_RC" 2>/dev/null || echo 'export TWITTER_AUTH_TOKEN="用户的auth_token"' >> "$SHELL_RC"
grep -q "TWITTER_CT0" "$SHELL_RC" 2>/dev/null || echo 'export TWITTER_CT0="用户的ct0"' >> "$SHELL_RC"
export TWITTER_AUTH_TOKEN="用户的auth_token"
export TWITTER_CT0="用户的ct0"
twitter status  # 验证
```

**网络代理**（如果用户在墙内）：

```
⚠️ 如果你在中国大陆，Twitter API 需要代理访问。
请确认你的代理端口（常见端口：7890/7897/1080），然后告诉我。
```

```bash
PROXY_PORT="用户提供的端口号"
grep -q "HTTP_PROXY" "${HOME}/.zshrc" 2>/dev/null || echo "export HTTP_PROXY=http://127.0.0.1:${PROXY_PORT}" >> "${HOME}/.zshrc"
grep -q "HTTPS_PROXY" "${HOME}/.zshrc" 2>/dev/null || echo "export HTTPS_PROXY=http://127.0.0.1:${PROXY_PORT}" >> "${HOME}/.zshrc"
export HTTP_PROXY="http://127.0.0.1:${PROXY_PORT}"
export HTTPS_PROXY="http://127.0.0.1:${PROXY_PORT}"
```

### 0.3) 完整自检清单

| 检查项 | 命令 | 预期结果 | 必须？ |
|--------|------|----------|--------|
| twitter-cli | `command -v twitter` | 有输出 | ✅ 必须 |
| 版本 ≥ 0.8.5 | `twitter --version` | v0.8.5+ | ✅ 必须 |
| 认证成功 | `twitter status` | authenticated | ✅ 必须 |
| fch | `command -v fch` | 有输出 | 💡 可选（增强历史粉丝数据） |
| mcporter | `command -v mcporter` | 有输出 | 💡 可选（增强推文搜索） |
| curl + Jina | `curl -s https://r.jina.ai/https://x.com` | 有内容 | 💡 可选（第三方分析页面） |

全部 ✅ 后进入分析流程。

---

## 1) 核心分析流程

### 整体流程图

```
用户输入 @handle
      │
      ▼
[Step 1] 基础画像采集 ─── twitter user + Exa搜索补充 + SuperX/SocialBlade
      │
      ▼
[Step 2] 推文全量抓取 ─── twitter user-posts + twitter search + Exa搜索补充
      │
      ▼
[Step 2.5] 历史粉丝增长曲线 ─── fch (Wayback Machine) + 多次采样推算
      │
      ▼
[Step 3] 内容性质分类（AI 驱动）
      │
      ▼
[Step 4] 互动数据关联分析
      │
      ▼
[Step 5] 涨粉规律与归因 ─── 结合粉丝曲线 + 高互动帖时间线
      │
      ▼
[Step 6] 可复制经验提取
      │
      ▼
[输出] 完整分析报告
```

### 多数据源矩阵

| 数据源 | 工具 | 获取什么 | 必须？ |
|--------|------|----------|--------|
| 推文内容 + 互动数 | `twitter user-posts` | 该用户所有推文及 likes/retweets/replies | ✅ 必须 |
| 用户基础画像 | `twitter user` | 粉丝数、简介、注册时间等 | ✅ 必须 |
| 历史粉丝增长 | `fch` (Wayback Machine) | 历史各时间点的粉丝数快照 | 💡 强烈推荐 |
| 补充推文搜索 | `twitter search --from` | 按时间/类型过滤的推文 | ✅ 必须 |
| 全网高互动帖 | `mcporter` → Exa 搜索 | 找到该用户被广泛转发的帖文 | 💡 推荐 |
| 第三方分析页面 | `web_fetch` / Jina Reader | 抓取 SocialBlade/SuperX 的公开分析数据 | 💡 推荐 |
| 竞品对比数据 | `twitter user` × N 个账号 | 多账号基础画像对比 | 按需 |

---

## 2) Step 1：基础画像采集

### 2.1) 用户资料

```bash
twitter user HANDLE --json
```

提取字段：
- `screen_name`：用户名
- `name`：昵称
- `description`：简介
- `followers_count`：粉丝数
- `friends_count`：关注数
- `statuses_count`：推文总数
- `created_at`：注册时间
- `profile_image_url`：头像
- `verified`：是否认证
- `location`：位置

### 2.2) 初步画像判断

基于以上数据，AI 自动分析：
- **账号年龄**：从 `created_at` 计算运营时长
- **发帖频率**：`statuses_count` ÷ 运营天数 = 日均发帖量
- **粉关注比**：`followers_count` ÷ `friends_count` → 影响力指标
- **简介关键词**：提取定位标签

---

## 3) Step 2：推文全量抓取（多源融合）

### 3.1) 主数据源：twitter-cli

```bash
# 抓取用户最近推文（默认 100 条，可扩展）
twitter user-posts HANDLE -n 100 --json -o /tmp/twitter_analysis_HANDLE_tweets.json

# 如果 100 条不够，扩展到 200 条
twitter user-posts HANDLE -n 200 --json -o /tmp/twitter_analysis_HANDLE_tweets.json
```

### 3.2) 搜索补充（按时间/类型过滤）

```bash
# 通过搜索获取该用户的推文（排除转发的原创内容）
twitter search --from HANDLE --exclude retweets -n 50 --json -o /tmp/twitter_analysis_HANDLE_search.json

# 按时间范围补充（分阶段抓取）
twitter search --from HANDLE --since 2026-01-01 --until 2026-02-28 -n 50 --json
```

### 3.3) Exa 搜索补充（获取全网传播数据）

如果 mcporter 可用：

```bash
# 搜索该用户被广泛讨论的推文（能找到高互动帖的二次传播）
mcporter call 'exa.web_search_exa(query: "site:x.com from:HANDLE", numResults: 10)'

# 搜索该用户最出名的推文（第三方引用）
mcporter call 'exa.web_search_exa(query: "HANDLE most popular tweet viral", numResults: 5)'
```

### 3.4) 第三方分析页面数据（SuperX / SocialBlade）

用 Jina Reader 抓取公开的 Twitter 分析页面数据：

```bash
# SuperX（有互动率、增长趋势等数据）
curl -s "https://r.jina.ai/https://superx.so/creators/HANDLE" -H "Accept: text/markdown" --max-time 20

# 如果 web_fetch 工具可用，也可以直接用
# web_fetch https://superx.so/creators/HANDLE
```

### 3.5) 互动数据补充

```bash
# 获取用户的 likes（注意：2024.6 后只能看自己的）
twitter likes HANDLE --json -n 20

# 查看用户的粉丝列表（了解粉丝画像）
twitter followers HANDLE --json -n 20

# 查看用户关注了谁（了解他的信息源）
twitter following HANDLE --json -n 20
```

### 3.6) 历史粉丝增长曲线

```bash
# 使用 fch 从 Wayback Machine 获取历史粉丝数
# 按月采样，获取最近 1 年的数据
fch --st=$(date -v-1y +%Y%m%d)000000 --et=$(date +%Y%m%d)000000 --freq=2592000 -f /tmp/twitter_analysis_HANDLE_follower_history.csv HANDLE

# 如果 fch 太慢或无数据，用「多次采样推算」方法：
# 从推文数据中按周统计互动量变化，结合当前粉丝数反推增长曲线
```

> **注意**：fch 依赖 Wayback Machine 快照，不是每个账号都有完整数据。
> 如果 fch 无数据，AI 应基于推文互动量变化 + 当前粉丝数做增长趋势推算。

---

## 4) Step 3：内容性质分类（AI 驱动）

### 4.1) 分类维度

对每条推文，AI 自动打以下标签：

| 维度 | 标签选项 |
|------|----------|
| **内容类型** | 技术干货 / 行业观点 / 个人故事 / 教程教程 / 资源分享 / 互动提问 / 热点评论 / 产品营销 / 日常感悟 / 段子幽默 / 数据报告 / 长文深度 |
| **内容形式** | 纯文字 / 图片 / 视频 / Thread 长帖 / 引用转发 / 投票 / 链接分享 |
| **情绪基调** | 积极鼓励 / 中性客观 / 争议挑战 / 共情共鸣 / 好奇探索 / 批评反思 |
| **互动钩子** | 提问式 / 观点站队 / 资源诱惑 / 悬念设计 / 共情触发 / 数据冲击 |
| **目标受众** | 初学者 / 从业者 / 决策者 / 泛大众 / 特定社群 |

### 4.2) 分类流程

1. 将推文数据传给 AI
2. AI 按上述维度逐条打标签
3. 汇总统计各类占比
4. 识别 TOP3 主导内容类型

### 4.3) 输出格式

```
📊 内容性质分类报告 — @HANDLE

内容类型分布：
  技术干货    ████████░░  35%  (28条)
  行业观点    ██████░░░░  25%  (20条)
  个人故事    ████░░░░░░  15%  (12条)
  互动提问    ███░░░░░░░  12%  (10条)
  资源分享    ██░░░░░░░░   8%  (6条)
  其他        █░░░░░░░░░   5%  (4条)

情绪基调分布：
  积极鼓励  40%  |  中性客观  30%  |  争议挑战  20%  |  其他  10%

互动钩子 TOP3：
  1. 提问式（引发讨论）   32%
  2. 观点站队（激化立场） 28%
  3. 数据冲击（震撼感）   18%
```

---

## 5) Step 4：互动数据关联分析

### 5.1) 数据维度

对每条推文提取互动指标：
- `likes`：点赞数
- `retweets`：转发数
- `replies`：回复数
- `quotes`：引用数
- `views`（如有）：浏览量

### 5.2) 计算衍生指标

- **互动率** = (likes + retweets + replies) ÷ followers_count
- **传播率** = retweets ÷ likes（越高说明内容越有传播性）
- **讨论率** = replies ÷ likes（越高说明内容越有讨论价值）

### 5.3) 识别高表现内容

```python
# AI 自动筛选逻辑
top_tweets = sorted(tweets, key=lambda t: t['likes'] + t['retweets']*3 + t['replies']*2, reverse=True)[:10]
viral_tweets = [t for t in tweets if t['retweets'] > avg_retweets * 3]
```

### 5.4) 高表现内容 vs 低表现内容对比

| 维度 | 高表现（TOP 10%） | 低表现（BOTTOM 50%） |
|------|-------------------|---------------------|
| 内容类型 | ? | ? |
| 发帖时间 | ? | ? |
| 内容长度 | ? | ? |
| 是否带图 | ? | ? |
| 情绪基调 | ? | ? |
| 互动钩子 | ? | ? |

---

## 6) Step 5：涨粉规律与归因

### 6.1) 时间线分析

基于推文的发布时间，分析：
- **发帖时间分布**：哪几个小时发帖最多？哪个时间段互动最好？
- **发帖频率变化**：是否有阶段性爆发？
- **内容类型变化**：是否在某个时期切换了内容策略？

### 6.2) 粉丝增长曲线构建

#### 方法 A：fch 历史数据（最佳）

```bash
# 已在 Step 3.6 获取，读取 CSV
# 格式：datetime, follower_count
# 用 AI 解析并绘制增长曲线
```

#### 方法 B：互动量 + 当前粉丝数推算

如果 fch 无数据，用以下方法推算：

```
推算逻辑：
1. 从 twitter user 获取当前粉丝数（精确值）
2. 从推文数据按时间窗口统计互动量
3. 高互动期 → 推算为高增长期
4. 结合 SuperX/Exa 获取的公开分析数据校准
5. 输出「增长趋势图」（而非精确曲线）
```

#### 方法 C：SuperX / SocialBlade 公开数据

```bash
# SuperX 通常有近期的增长数据
curl -s "https://r.jina.ai/https://superx.so/creators/HANDLE" | grep -i "growth\|follower\|impression"
```

### 6.3) 涨粉归因模型

AI 基于以下信号做归因（融合多数据源）：

```
涨粉驱动因素分析：
├── 内容因素（来自 twitter-cli 推文数据）
│   ├── 高互动内容类型占比（什么类型最涨粉）
│   ├── Thread 长帖 vs 短推的涨粉效率对比
│   └── 特定话题/标签的涨粉效果
├── 行为因素（来自 twitter-cli 推文时间分析）
│   ├── 发帖频率（日均几条）
│   ├── 互动频率（回复别人的推文数）
│   └── 发帖时间窗口（哪个时区/时段）
├── 关系因素（来自 Exa 搜索 + twitter followers/following）
│   ├── 被大 V 转发的次数（Exa 全网搜索）
│   ├── 参与 Twitter 圈子讨论的频率
│   └── 引用/互动链（社交网络效应）
├── 策略因素（AI 分析推文模式）
│   ├── 是否有固定的内容系列/栏目
│   ├── 是否有规律性的互动活动
│   └── 简介是否持续优化
└── 外部因素（来自 Exa/Jina 搜索）
    ├── 媒体报道/采访带来的溢出流量
    ├── 跨平台导流（YouTube/播客/LinkedIn）
    └── 事件驱动的突发增长
```

### 6.3) 输出格式

```
📈 涨粉归因分析 — @HANDLE

核心增长驱动（按权重排序）：
  1. 🎯 [40%] 技术干货 Thread → 长帖带来了大量转发和涨粉
     证据：TOP 10 涨粉帖中 7 条是技术 Thread
  2. 💬 [25%] 高频互动回复 → 在大 V 帖下高质量回复吸引关注
     证据：日均回复 15+ 条，被引用率高于行业平均 3 倍
  3. ⏰ [20%] 固定发帖时间 → 在目标受众活跃期准时发帖
     证据：80% 高互动帖集中在 9:00-11:00 EST
  4. 🏷️ [15%] 热点蹭流 → 快速跟进热门话题获得曝光
     证据：热点相关帖的平均曝光是日常帖的 5 倍
```

---

## 7) Step 6：可复制经验提取

### 7.1) 经验提炼框架

AI 从分析结果中提取以下可操作经验：

| 维度 | 提取内容 |
|------|----------|
| **内容公式** | 他最有效的内容结构是什么？（标题→正文→CTA） |
| **发帖节奏** | 每天几条？什么时间？Thread vs 短推比例？ |
| **互动策略** | 怎么回复别人？怎么引导讨论？怎么用 DM？ |
| **话题选择** | 聊什么话题涨粉？什么话题互动高但涨粉少？ |
| **视觉风格** | 是否统一风格？图片/视频怎么用？ |
| **个人品牌** | 他在 Twitter 上的「人设」是什么？怎么维持的？ |

### 7.2) 30 天复制计划模板

```
📋 30 天复制计划 — 学习 @HANDLE 的增长策略

第 1 周：打基础
  Day 1-2：完善个人简介（参考他的简介结构）
  Day 3-5：每天发 2 条内容（1 条观点 + 1 条资源）
  Day 6-7：在大 V 帖下做 5 条高质量回复

第 2 周：找到节奏
  Day 8-10：尝试发第一条 Thread（模仿他的结构）
  Day 11-12：分析第一周数据，调整内容类型
  Day 13-14：固定发帖时间窗口

第 3-4 周：放大增长
  持续他的高频内容类型
  每周 1 条深度 Thread
  每天互动回复 ≥ 10 条
```

---

## 8) 完整分析报告模板

每次分析输出一份结构化报告，格式如下：

```markdown
# 🔍 Twitter 账号逆向分析报告

## 基本信息
- **账号**：@HANDLE
- **昵称**：NAME
- **粉丝数**：XX,XXX
- **注册时间**：XXXX 年 XX 月
- **运营时长**：X 年 X 月
- **日均发帖**：X.X 条

## 一、基础画像
[AI 生成的一段话概括这个账号是谁、做什么、受众是谁]

## 二、内容性质分析
[内容类型分布 + 情绪基调 + 互动钩子分析]

## 三、涨粉规律
[时间线分析 + 增长阶段识别 + 关键转折点]

## 四、涨粉归因
[核心驱动因素 + 权重 + 证据]

## 五、可复制经验
[内容公式 + 发帖节奏 + 互动策略 + 话题选择]

## 六、30 天复制计划
[按周拆解的可执行计划]

## 七、风险提示
[哪些做法可能不适合所有人 / 哪些有封号风险]
```

---

## 9) 高级功能

### 9.1) 竞品对比分析

输入多个 @handle，自动对比：

```
竞品对比维度：
  内容策略差异 | 互动策略差异 | 涨粉速度对比 | 内容类型差异
```

### 9.2) 长期追踪

对同一账号定期（周/月）重复分析，输出变化趋势：

```
变化追踪：
  内容类型占比变化 | 涨粉速度变化 | 互动率变化 | 策略调整识别
```

### 9.3) 指定维度深度分析

用户可以只关注某个维度：

- "只分析他的 Thread 长帖策略"
- "只看他怎么蹭热点的"
- "只分析他的互动策略"

---

## 10) 故障处理

### 10.1) 核心数据源故障

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| `twitter: command not found` | twitter-cli 未安装 | 执行 0.1 自动安装 |
| `twitter status` 返回未认证 | 缺少 Cookie | 执行 0.2 认证引导 |
| `user-posts` 超时 | 网络问题/频率限制 | 减少抓取数量，增加重试 |
| `search` 返回 404 | Twitter API 变更 | `pipx upgrade twitter-cli`，或改用 `user-posts` |
| `user-posts` 数据量不够 | 平台限制 | 多次抓取 + search 补充 + Exa 搜索补充 |
| 所有命令超时 | 代理未配置 | 执行 0.2 代理配置 |
| followers/following 被限制 | Twitter 风控 | 减少请求频率，使用住宅代理 |

### 10.2) 辅助数据源故障

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| `fch` 无数据 | Wayback Machine 无该账号快照 | 跳过，改用「互动量推算法」|
| `fch` 太慢 | Wayback Machine 查询慢 | 设 60s 超时，超时后跳过 |
| Exa 搜索无结果 | mcporter 未安装/Exa 无数据 | 跳过，仅依赖 twitter-cli 数据 |
| SuperX 页面无法读取 | JS 渲染/反爬 | 跳过，非关键数据 |
| Jina Reader 超时 | 网络问题 | 跳过，非关键数据 |

### 10.3) 降级策略

```
数据获取优先级（高 → 低）：
  1. twitter-cli user-posts + user        ← 必须，最可靠
  2. twitter-cli search --from            ← 补充推文
  3. fch 历史粉丝数据                      ← 增强涨粉分析
  4. Exa 搜索全网传播数据                  ← 增强归因分析
  5. Jina Reader 抓第三方分析页            ← 补充参考数据

如果 1-2 可用，就能输出完整报告（涨粉曲线用推算法代替）。
如果只有 1 可用，报告标注「数据源受限」但仍然可输出。
```

### 重试策略

- 数据抓取失败：自动重试 1 次，减少数量后重试 1 次
- API 返回 429（限流）：等待 60 秒后重试
- 连续 3 次失败：暂停并报告给用户，提供手动操作建议

---

## 11) 数据存储规范

### 11.1) 分析数据存储

```
knowledge-base/
├── accounts/           # 账号分析记录
│   └── HANDLE/
│       ├── profile.json        # 基础画像
│       ├── tweets_raw.json     # 原始推文数据
│       └── analysis_report.md  # 分析报告
├── patterns/           # 可复用模式
│   ├── content_formulas.md     # 内容公式库
│   ├── growth_tactics.md       # 涨粉策略库
│   └── engagement_hooks.md     # 互动钩子库
└── reviews/            # 复盘记录
    └── YYYY-MM-DD_HANDLE.md    # 按日期存档
```

### 11.2) 知识库沉淀规则

- 每次分析完成后，将可复用模式沉淀到 `patterns/`
- 重复分析同一账号时，先检索历史记录，标注变化
- 所有分析报告按 `reviews/YYYY-MM-DD_HANDLE.md` 归档
