---
name: link-ops-master
description: >-
  短链与归因运营大师 — 创建可追踪的短链、设计 UTM 归因参数、跑 A/B 测试、回传转化事件、
  分析点击来源并落地到投放决策。适用于投放素材追踪、渠道归因、联盟营销、落地页测试、
  裂变分享链接、活动链接。触发词：短链、链接归因、UTM、A/B 测试、转化追踪、
  link tracking、UTM builder、短链接、渠道追踪。
brand: AI Skills 创作小店
price: 2990
tags:
  - 短链接
  - 归因分析
  - UTM参数
  - A-B测试
  - 转化追踪
  - 投放运营
  - 联盟营销
  - 渠道分析
specs:
  - SPEC-DEFAULT
  - PLAN-DEFAULT
  - SKU-DEFAULT
author: ERIC
author_email: gyc567@gmail.com
author_twitter: https://twitter.com/EricBlock2100
author_blog: https://topdigg.com
---

# 短链与归因运营大师

> 每一个链接都应该能回答三个问题：**谁点的？点了之后做了什么？值不值得继续投？**

品牌：**AI Skills 创作小店**

---

## 什么时候用这个 Skill

| 场景 | 要解决的问题 |
|------|-------------|
| 投放素材追踪 | 同一张图发到 10 个渠道，不知道哪个渠道有效 |
| 落地页 A/B | 两个版本各一半流量，谁转化更好 |
| 联盟/分销 | 推广者的链接要能统计点击与成交 |
| 裂变分享 | 用户分享出去的链接要能追溯来源与收益 |
| 活动链接 | 限时活动要有独立的数据口径 |
| 内容平台 | 公众号、小红书、即刻的链接要区分来源 |

**不适用**：纯站内跳转、需要登录态的深链、纯内部路由。

---

## 核心原则

### 1. 短链不是"变短"，是"加数据层"

一个可归因的短链要同时携带三样东西：

```
https://your.domain/promo
      ↑              ↑
   短链域名        业务 slug（人可读、语义化）
   品牌资产         用于区分活动/渠道/素材
```

### 2. UTM 是"命名规范"，不是"随便填"

一套能用的 UTM 规范（**动手前先和用户确认这套命名**）：

| 参数 | 填什么 | 规则 |
|------|-------|------|
| `utm_source` | 渠道 | 微信 / xiaohongshu / douyin / newsletter / partner-name |
| `utm_medium` | 类型 | social / email / cpc / referral / qr |
| `utm_campaign` | 活动 | 活动名，用日期前缀：`202610-launch` |
| `utm_term` | 人群/内容 | 细分受众或素材角度：`beginner`、`demo` |
| `utm_content` | 素材 | 具体版本：`a` / `b` / `carousel-1` |

**铁律**
- 全部小写，连字符分隔，不加空格（`utm_source=wechat` 不是 `utm_source=WeChat`）
- 一个维度一个值，不要塞 `wechat-2`（那是 content 的活）
- 上线前把命名表写下来，否则三个月后没人知道 `tt1` 是什么

### 3. 转化要回传，不能只看点击

```
点击 → 落地页 → 转化（留资/下单/注册）
      └── 只有把转化回传，才能算 ROI
```

平台原生统计只看得到"来了多少人"，回传事件才看得到"赚了多少"。

### 4. 一次只改一个变量

A/B 测试的 split URL 只能在**一个维度**上分叉。同时改文案和落地页，赢了也不知道是谁的功劳。

---

## 工作流

### Step 1 — 先问清楚这 4 件事

在动手创建任何链接之前：

1. **归因目标**：这次投放要优化什么？（点击 / 留资 / 成交 / 加粉）
2. **渠道清单**：链接会出现在哪些地方？
3. **命名规范**：utm_source / campaign 用什么前缀？
4. **回传方案**：转化发生在哪？能不能拿到事件回调？

### Step 2 — 建短链

```bash
export LINK_OPS_API_KEY=dub_xxx      # 或 bitly_xxx
export LINK_OPS_PROVIDER=dub

python3 scripts/link_ops.py create "https://your.site/landing" \
  --key promo-202610 \
  --utm-source wechat \
  --utm-medium social \
  --utm-campaign 202610-launch \
  --utm-content a
```

**用 `scripts/link_ops.py` 而不是手写 curl**——它已经处理了：
- 保留 slug 校验（`stats`、`api`、`pricing` 等 80+ 个词不能用作 key）
- 多平台适配（Dub / Bitly / TinyURL / 自定义）
- UTM 参数结构化传递
- 统一的错误输出

### Step 3 — 批量铺渠道

一个活动要在 5 个渠道投放时，**用脚本循环，不要手工点 5 次**：

```bash
# 5 个渠道 × 1 个活动 = 5 条带归因的短链
for src in wechat xiaohongshu douyin bilibili weibo; do
  python3 scripts/link_ops.py create "https://your.site/landing" \
    --key "202610-launch-$src" \
    --utm-source "$src" --utm-medium social \
    --utm-campaign 202610-launch
done
```

**关键**：slug 里也带上渠道名，这样在平台后台和短链服务两边都能对上账。

### Step 4 — 跑 A/B

Dub 的 split URL 支持在一条链接上做流量分叉（**只改一个变量**）：

```bash
python3 scripts/link_ops.py create "https://your.site/landing" \
  --key ab-test-202610 \
  --utm-source wechat --utm-campaign 202610-ab
```

然后通过平台的分流参数指定 50/50。分叉比例下限 10%，最多 4 个变体。

**A/B 前的检查清单**
- [ ] 两个版本的**唯一**差异是那一个变量
- [ ] 两版落地页加载性能接近（否则测的是速度不是内容）
- [ ] 转化回传埋点两版一致
- [ ] 样本量够跑出显著性（不要 100 次点击就下结论）

### Step 5 — 回传转化

```bash
# 留资
python3 scripts/link_ops.py track lead <linkId> --customer "user@example.com"

# 成交（金额单位为分）
python3 scripts/link_ops.py track sale <linkId> --amount 9900 --customer "user@example.com"
```

**埋点位置**：在**转化成功的那一页**调用，不要在按钮点击时调用。用户点了没买就回传，等于自欺欺人。

### Step 6 — 读数据做决策

```bash
python3 scripts/link_ops.py stats <linkId>
```

看三件事：
1. **clicks vs uniqueClicks** — 差值大说明重复点击多（可能是误触或爬虫）
2. **来源分布** — 哪个渠道的 uniqueClicks 最多
3. **转化率** — 有回传的话，转化/点击才是真效率

**常见结论模式**

| 现象 | 可能原因 | 下一步 |
|------|---------|--------|
| 点击高、转化低 | 落地页与素材承诺不符 | 改落地页，不是改素材 |
| 某渠道点击少但转化高 | 该渠道受众更精准 | 加预算，而不是砍掉 |
| 转化集中在少数用户 | 可能是老客/员工自点 | 检查是否需要排除内部流量 |
| 各渠道点击差不多但来源记错 | UTM 命名不一致 | 先统一命名规范再复盘 |

---

## 工具命令速查

```bash
# 解析 URL（补协议、取主域名、拆参数）
python3 scripts/link_ops.py urls "example.com/path?q=1"

# 构造 UTM 并合并进 URL
python3 scripts/link_ops.py utm --source wechat --campaign spring --url example.com

# 检查 slug 是否为保留字
python3 scripts/link_ops.py reserved stats

# 从品牌名生成候选短链域名
python3 scripts/link_ops.py domain "AI Skills 创作小店"

# 列出 / 查详情 / 回传
python3 scripts/link_ops.py list --limit 20
python3 scripts/link_ops.py stats <linkId>
python3 scripts/link_ops.py track lead|sale|open|click <linkId>
```

---

## 平台选择

| 平台 | 适合 | 需要 Key |
|------|------|---------|
| **Dub** | 完整归因：A/B、UTM、标签、文件夹、分析、转化回传、自定义域名 | ✅ |
| **Bitly** | 基础短链 + 品牌域名 | ✅ |
| **TinyURL** | 临时/测试短链，零配置 | ❌ |
| **自建** | 数据不出自己的服务器 | 视实现 |

**选 Dub 的理由**：它是开源的（AGPL-3.0，github.com/dubinc/dub，24.9k⭐），API 规范公开，
可以自托管，也可以只用它的托管服务。转化回传与 A/B 分流是它相对基础短链服务最大的差异。

---

## ⚠️ 实测坑点（AI Skills 创作小店 验证）

### 1. 保留 slug 会静默失败或报错

Dub 保留了 80+ 个 slug（`stats`、`api`、`pricing`、`admin`、`links`、`workspaces`…）。
用作短链 key 会失败。脚本已内置 `RESERVED_SLUGS` 集合并在创建前拦截：

```bash
python3 scripts/link_ops.py reserved stats   # {"reserved": true}
```

### 2. 裸域名必须补协议

`example.com` 直接当 URL 传，部分平台会拒绝或生成错误链接。
脚本的 `normalize_url()` 统一补 `https://`。

### 3. 二级后缀主域名要特殊处理

`shop.example.co.uk` 的主域名是 `example.co.uk` 而不是 `example.uk`；
建站平台子域（`foo.vercel.app`）的主域名是 `foo.vercel.app` 本身。
脚本的 `get_apex_domain()` 已覆盖这两类。

### 4. 金额单位是「分」

转化回传的 `--amount 9900` 表示 ¥99.00，不是 ¥9900。
传错会导致 ROI 算错 100 倍，且不会报错——只能靠复核发现。

### 5. 回传要在转化成功页，不在点击按钮

在按钮上回传 = 把"点了"当成"买了"。这是最常见的归因错误。

### 6. 401 会带结构化错误体

Dub 的错误响应是 JSON：

```json
{"error":{"code":"unauthorized","message":"Unauthorized: Invalid API key.",
          "doc_url":"https://dub.co/docs/api-reference/errors#unauthorized"}}
```

脚本会原样打印 `doc_url`——遇到权限问题先点那个链接，比猜快。

### 7. 别在 CI 里硬编码 API Key

用环境变量 `LINK_OPS_API_KEY`。Dub 支持 OAuth 2.0（授权码模式），
生产环境建议走 OAuth 而不是长期 API Key。

---

## 数据与合规

- 短链服务会记录 IP、UA、Referer —— 涉及用户隐私时要做脱敏与告知
- 联盟营销要明确披露推广关系（各平台 FTC/广告法要求）
- 用户的 UTM 归因数据属于业务数据，导出与留存遵守用户所在地的合规要求
---

<!-- ERIC-AUTHOR-INFO:START -->

## 📬 联系作者

**ERIC** — AI技术专家，专注于人工智能和自动化工具的研究与应用

| 渠道 | 链接 |
|------|------|
| 📧 邮箱 | [gyc567@gmail.com](mailto:gyc567@gmail.com) |
| 🐦 Twitter | [@EricBlock2100](https://twitter.com/EricBlock2100) |
| 💬 微信 | `360369487` |
| ✈️ Telegram | [@fatoshi_block](https://t.me/fatoshi_block) |
| 📢 Telegram 频道 | [@cryptochanneleric](https://t.me/cryptochanneleric) |
| 🔐 加密情报 TG 群 | [@btcgogopen](https://t.me/btcgogopen) |
| ▶️ YouTube | [@0XBitFinance](https://www.youtube.com/@0XBitFinance) |
| 🌐 个人技术博客 | [topdigg.com](https://topdigg.com) |

> 本 Skill 由 ERIC 免费提供。想深入交流或获取更多同类 Skill，欢迎通过上表任一渠道联系。

<!-- ERIC-AUTHOR-INFO:END -->

---

## 许可与来源

- **方法论与脚本**：本 Skill 由 AI Skills 创作小店（ERIC）编写
- **纯函数移植**：URL 处理、主域名提取、保留 slug 集合来自开源项目
  [dubinc/dub](https://github.com/dubinc/dub)（AGPL-3.0，© Dub Technologies, Inc.）
  的 `packages/utils`，已注明出处
- **平台选择**：Dub 为开源项目（24.9k⭐），自托管可参考
  [官方自托管指南](https://dub.co/docs/self-hosting/guide)
