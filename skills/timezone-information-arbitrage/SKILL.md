---
name: timezone-information-arbitrage
description: >-
  时区信息套利 Agent：在美国东部时间凌晨 2-6 AM（全球政府公告、央行决议高发期），
  扫描各国官方信息源，捕捉预测市场错误定价机会。输入要追踪的国家/事件类型，
  输出事件扫描报告与错价分析。适合有技术背景的交易者。
---

# 时区信息套利（Timezone Information Arbitrage）

> 趁你睡觉偷钱 — 在美国人睡着时，用 AI 捕捉全球市场错价

## 触发条件

当用户提到以下任意关键词时激活此技能：
- "时区套利"、"timezone arbitrage"
- "趁睡觉赚钱"、"信息差套利"
- "预测市场套利"、"Polymarket 策略"
- "凌晨自动交易"、"cron 交易"
- "政府公告套利"、"央行决议交易"

---

## 核心策略原理

### 1. 运作逻辑（怎么赚钱？）

**时间差 × 信息差 × 流动性差 = 套利机会**

| 维度 | 说明 |
|------|------|
| **时间差** | EST 凌晨 2-6 AM，美国人都在睡觉，市场流动性极低，反应极度迟钝 |
| **信息差** | 欧洲、亚洲正值白天，各国政府公告、议会直播、央行决议正在发生或刚出结果 |
| **执行** | AI Agent 扫描官方信息源，发现"结果已定但市场未定价"的错价机会，立刻入场 |

**案例：** $200 本金 → $300K（30万美元），通过捕捉央行决议的预测市场错价。

### 2. 信息源优先级

```
第一梯队（最高价值）
  ├─ 央行决议公告（Fed/ECB/BOE/BOJ）
  ├─ 政府法案表决结果
  └─ 主权评级公告（穆迪/标普/惠誉）

第二梯队（中等价值）
  ├─ 议会投票结果
  ├─ 选举计票进度
  └─ 地缘政治事件声明

第三梯队（辅助验证）
  ├─ 官方新闻发布会文字直播
  ├─ 财政部公告
  └─ 监管机构裁决
```

### 3. 预测市场平台

| 平台 | 类型 | API 可用性 |
|------|------|-----------|
| Polymarket | 主流预测市场 | ✅ API 丰富 |
| Kalshi | 美国本土预测市场 | ✅ API |
| Betfair | 政治/体育预测 | ⚠️ 受限 |
| Metaculus | 研究型预测社区 | ⚠️ 有限 |

### 4. 错价识别规则

**触发入场的条件（必须同时满足）：**

```
✅ 官方信息源确认事件"结果已定"
✅ 预测市场价格 < 合理估值的 50%（严重低估）
✅ 事件宣布/结果时间 < 6 小时前
✅ 市场规模 > $10,000（足够流动性）
❌ 不满足以上任一条件 → 禁止入场
```

---

## Agent 执行流程

### Step 1: 信息源扫描（EST 02:00-06:00 每 15 分钟一次）

```python
# 伪代码：扫描逻辑
def scan_sources():
    events = []
    for country in TARGET_COUNTRIES:
        for source in OFFICIAL_SOURCES[country]:
            announcements = fetch_announcements(source)
            for ann in announcements:
                if is_decisive_result(ann) and not yet_priced(ann):
                    events.append(ann)
    return events
```

**扫描国家/地区：**
- 欧洲：英国、法国、德国、意大利、西班牙（议会/央行）
- 亚洲：日本、中国、韩国、澳大利亚（央行/政府）
- 中东：沙特、阿联酋（石油政策公告）

### Step 2: 错价分析

```python
def analyze_mispricing(event, market_price):
    # 事件结果的合理价格估算
    fair_value = estimate_fair_value(event)
    
    # 错价幅度
    mispricing_ratio = market_price / fair_value
    
    if mispricing_ratio < 0.5:  # 50% 以下低估
        return {
            "action": "BUY",
            "size": calculate_position_size(mispricing_ratio),
            "confidence": estimate_confidence(event),
            "upside": fair_value - market_price,
            "risk": assess_risk(event)
        }
    else:
        return {"action": "SKIP", "reason": "not_enough_mispricing"}
```

### Step 3: 交易执行（可选）

```python
def execute_trade(signal):
    if signal["action"] == "BUY":
        # 通过 API 买入预测市场
        place_order(
            market=signal["market_id"],
            side="BUY",
            size=signal["size"],
            price=signal["current_price"]
        )
        # 设置止损：价格回归 80% 时退出
        set_exit_trigger(
            market=signal["market_id"],
            condition="price >= 0.8 * fair_value",
            action="CLOSE"
        )
```

---

## 风险控制（必须遵守）

### 🚨 绝对禁止

1. **不要在消息未确认时入场** — AI 可能误读"否决"为"通过"
2. **不要全仓梭哈** — 单笔最大亏损不超过总资金的 2%
3. **不要做空** — 预测市场的空头收益有限但风险无限
4. **不要在流动性 < $10K 的市场操作** — 滑点会吃掉所有利润

### ⚠️ 已知风险清单

| 风险类型 | 描述 | 缓解措施 |
|---------|------|---------|
| **信息延迟** | 政府网站卡顿，AI 看到的是旧消息 | 多源交叉验证（≥2个独立源） |
| **语境误读** | AI 把"否决"读成"通过" | 人工复核关键判断 |
| **流动性枯竭** | 凌晨买不到/卖不掉 | 仅做流动性 >$50K 市场 |
| **平台风控** | Polymarket 等封号/冻结资金 | 控制单账号交易频率 |
| **幸存者偏差** | 暴富案例是极端个例 | 用 70% 胜率做资金管理 |

---

## 预期收益模型

```
假设：
  - 单笔交易：投入 $100
  - 错价幅度：市场 25¢ vs 合理价 100¢
  - 胜率：70%
  - 失败损失：$100（全损）
  - 成功收益：$300（4倍）

凯利公式估算仓位：f = (bp - q) / b = (3 * 0.7 - 0.3) / 3 = 40%

资金管理：
  - 单笔最大仓位：总资金 × 5%（保守）
  - 单日最大亏损：总资金 × 2%
  - 月度目标：总资金 × 10%
```

---

## 搭建指南

### 环境要求

| 项目 | 最低要求 | 推荐配置 |
|------|---------|---------|
| 服务器 | 任意 VPS（美国区域） | 低延迟专线 |
| Python | 3.10+ | 3.11+ |
| 内存 | 1GB | 2GB+ |
| 网络延迟 | < 200ms | < 50ms |

### 依赖安装

```bash
pip install requests beautifulsoup4 httpx schedule
```

### cron 配置（凌晨执行）

```bash
# 每天 EST 02:00-06:00 每 15 分钟执行
0,15,30,45 2-6 * * * /usr/bin/python3 /opt/timezone-arbitrage/scanner.py
```

---

## 输出格式

Agent 执行后输出：

```
📊 [时区套利扫描报告] HH:MM EST

🔍 扫描范围：欧洲 + 亚洲 12 个国家/地区
⏰ 扫描窗口：EST 02:15

📋 发现机会：N 个

[机会 1] 🟢 买入
  事件：英国央行利率决议
  官方结果：维持利率不变 ✓
  当前市场价格：28¢
  合理估值：95¢
  错价幅度：-70%
  置信度：85%
  建议仓位：$200
  风险等级：🟡 中

[机会 2] 🟡 观察
  事件：日本央行前瞻指引
  官方结果：未明确（持续评估中）
  当前市场价格：52¢
  建议：等待结果确认

⛔ 跳过：
  - 澳大利亚就业数据：流动性不足 $10K
  - 法国议会表决：结果未确认

⚠️ 风险提示：
  当前时段流动性偏低，建议小仓位试探。
```

---

## 局限性与免责

**本技能仅供学习研究，不构成投资建议。**

- 预测市场存在显著不确定性，历史胜率不代表未来表现
- 自动化交易存在平台封号、策略失效等风险
- 代码仅供参考，实际部署前请充分测试
- $200 → $300K 案例为极端个例，存在严重幸存者偏差
