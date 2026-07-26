---
name: crypto-harmonic-signals
description: |
  加密货币和谐形态交易信号扫描 Skill。每日三次 (00:00/08:00/16:00 UTC+8) 扫描 BTC, ETH, BNB, SOL, ZEC, UNI, AVAX, AAVE, HYPE 九种加密货币合约，输出和谐形态交易信号。

  触发场景:
  - "扫描加密货币交易信号"
  - "帮我看看 BTC/ETH 的机会"
  - "每天三次自动扫描信号"
  - "和谐形态检测"
  - "获取交易信号"
  - 任何涉及加密货币技术分析、合约信号的内容

  功能:
  - 多交易所适配 (Binance/OKX/Bybit)
  - 多周期共振过滤 (日线 EMA200 趋势 + 4H RSI 入场确认)
  - 和谐形态检测 (Gartley/Bat/Butterfly/Crab/DeepCrab)
  - 信号分级 (A/B/C 级)
  - Telegram 推送通知
  - 定时自动扫描

compatibility: python 3.8+, pandas, numpy, requests
---

# 加密货币和谐形态交易信号 Skill

## 快速开始

```python
from scripts.scanner import Scanner
from scripts.config import Config

# 创建扫描器
scanner = Scanner()

# 扫描所有币种
results = scanner.scan_all()

# 获取有效信号
valid = scanner.get_valid_signals(results)
print(f"有效信号: {len(valid)}")

# 手动触发一次扫描
summary = scanner.get_summary(results)
```

## 架构

```
数据获取层 (Binance/OKX/Bybit)
         ↓
趋势判断层 (日线 EMA200)
         ↓
入场确认层 (4H RSI)
         ↓
和谐形态层 (4H ZigZag + XABCD)
         ↓
信号过滤层 (多周期共振)
         ↓
信号输出层 (Markdown/Telegram)
```

## 配置

```python
from scripts.config import Config

config = Config(
    symbols=["BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT"],
    ema={"period": 200, "neutral_zone_pct": 0.01},
    rsi={"period": 14, "oversold": 30, "overbought": 70},
    harmonic={"zz_pct": 0.03, "tol": 0.12}
)
```

## 核心模块

| 模块 | 职责 |
|------|------|
| `scanner.py` | 批量扫描调度 |
| `indicators.py` | EMA200 + RSI 计算 |
| `harmonics.py` | 和谐形态检测 |
| `filters.py` | 多周期共振过滤 |
| `reporter.py` | Markdown 报告 |
| `alerter.py` | Telegram 推送 |
| `scheduler.py` | 定时任务 |

## 和谐形态

支持形态: Gartley, Bat, Butterfly, Crab, DeepCrab

信号分级:
- **A级**: PRZ 汇聚度 < 2% (正常仓位)
- **B级**: PRZ 汇聚度 2-4% (半仓)
- **C级**: PRZ 汇聚度 > 4% (放弃)

## 定时调度

```python
from scripts.scheduler import Scheduler

scheduler = Scheduler()
scheduler.start()  # 阻塞模式

# 或手动运行
scheduler.run_once()
```

## Telegram 推送

```python
from scripts.alerter import AlerterFactory

alerter = AlerterFactory.create_telegram(
    bot_token="YOUR_BOT_TOKEN",
    chat_id="YOUR_CHAT_ID"
)

if alerter.is_configured():
    alerter.send_signal(result)
```

## 信号格式

```markdown
🟢 [BINANCE] BTC/USDT | 做多 | Gartley A级

📊 趋势: bullish ✅
📉 RSI: 28.5 (oversold) ✅

🎯 入场: 67,500
🛑 止损: 66,850
🏁 TP1: 68,245 (RR 1:1.8)
🏁 TP2: 69,120 (RR 1:2.6)
```
