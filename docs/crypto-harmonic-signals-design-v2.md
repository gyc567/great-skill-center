# 加密货币和谐形态交易信号 Skill - 设计方案 v2.2

> 审计版本 | 日期: 2026-07-26 | 更新: 所有币种统一使用 Binance 4H K线

---

## 一、方案概述

| 项目 | 内容 |
|------|------|
| **Skill 名称** | `crypto-harmonic-signals` |
| **核心功能** | 每日三次扫描 9 种主流加密货币合约，多周期共振过滤，输出和谐形态交易信号 |
| **目标用户** | 加密货币合约交易者 |
| **扫描频率** | 00:00 / 08:00 / 16:00 (UTC+8) |
| **数据源** | Binance (主力) / OKX / Bybit (备选) |
| **扫描品种** | BTC, ETH, BNB, SOL, ZEC, UNI, AVAX, AAVE, HYPE |
| **K线周期** | 日线(EMA200趋势) / 4H(RSI+和谐形态) |

---

## 二、架构设计

```
┌─────────────────────────────────────────────────────────────────────┐
│                        三次每日扫描调度                               │
│              00:00 UTC+8 | 08:00 UTC+8 | 16:00 UTC+8                  │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      1. 数据获取层                                    │
├──────────────┬──────────────┬──────────────┬─────────────────────────┤
│  Binance     │    OKX       │   Bybit     │    统一适配器接口         │
│  (主力/全币种)│   (备选)     │   (备选)    │    ExchangeAdapter      │
└──────────────┴──────────────┴──────────────┴─────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      2. 趋势判断层 (日线 EMA200)                      │
├─────────────────────────────────────────────────────────────────────┤
│  EMA200 趋势过滤 (日线)                                              │
│  • price > EMA200 → 仅做多                                           │
│  • price < EMA200 → 仅做空                                           │
│  • price ≈ EMA200 → 趋势不明，跳过该币种                              │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      3. 入场确认层 (4H)                               │
├─────────────────────────────────────────────────────────────────────┤
│  RSI(14) 确认                                                        │
│  • 做多需 RSI < 30 (超卖)                                            │
│  • 做空需 RSI > 70 (超买)                                            │
│  • 中间区域 → 信号降级/标记"RSI未确认"                                 │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      4. 和谐形态扫描层 (4H)                            │
├─────────────────────────────────────────────────────────────────────┤
│  4H ZigZag 取点 → XABC 校验 → PRZ 计算                                │
│  形态: Gartley / Bat / Butterfly / Crab / DeepCrab                  │
│  分级: A级(<2%) / B级(2-4%) / C级(>4%放弃)                           │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      5. 信号输出层                                    │
├─────────────────────────────────────────────────────────────────────┤
│  • Markdown 报告                                                     │
│  • Telegram 推送                                                    │
│  • 信号存档 (CSV/JSON)                                              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 三、文件结构

```
crypto-harmonic-signals/
├── SKILL.md                           # Skill 定义
├── scripts/
│   ├── __init__.py
│   ├── config.py                      # 配置管理
│   ├── exchanges/
│   │   ├── __init__.py
│   │   ├── base.py                    # 基础适配器抽象类
│   │   ├── binance.py                 # Binance 实现 (全币种数据源)
│   │   ├── okx.py                     # OKX 实现 (备选)
│   │   └── bybit.py                   # Bybit 实现 (备选)
│   ├── indicators.py                  # EMA200 + RSI 计算
│   ├── harmonics.py                   # 和谐形态 (复用参考代码)
│   ├── scanner.py                     # 批量扫描逻辑
│   ├── filters.py                     # 多周期共振过滤器
│   ├── position_manager.py            # 仓位/持仓管理 (新增)
│   ├── reporter.py                    # Markdown 报告生成
│   ├── alerter.py                     # Telegram 推送
│   └── scheduler.py                   # 三次/日定时任务
├── references/
│   └── config.yaml                    # 默认配置
└── evals/
    └── evals.json                     # 测试用例
```

---

## 四、核心配置

```yaml
# ============ 扫描配置 ============
# 所有币种均使用 Binance 4H K线进行和谐形态判断
symbols:
  - BTC/USDT    # 比特币
  - ETH/USDT    # 以太坊
  - BNB/USDT    # 币安币
  - SOL/USDT    # Solana
  - ZEC/USDT    # Zcash
  - UNI/USDT    # Uniswap
  - AVAX/USDT   # Avalanche
  - AAVE/USDT   # Aave
  - HYPE/USDT   # Hyperliquid (使用币安合约数据)

exchanges:
  primary: binance        # 所有币种主力数据源
  fallbacks: [okx, bybit] # 备选交易所

# ============ K线周期配置 ============
# 所有币种统一使用 4H K线进行和谐形态检测
# 日线 EMA200 仅用于趋势方向判断
timeframes:
  harmonic: "4h"       # 和谐形态检测 (统一 4H)
  trend: "1d"          # EMA200 趋势判断 (日线)
  rsi: "4h"            # RSI 计算 (统一 4H)
  confirm: "1h"        # 辅助确认

# ============ 趋势参数 ============
ema200:
  enabled: true
  trend_filter: true
  neutral_zone_pct: 0.01   # 价格在 EMA±1% 内视为中性

rsi:
  period: 14
  oversold: 30
  overbought: 70
  confirmation_required: true
  divergence_check: false   # 未来扩展: RSI 背离检测

# ============ 和谐形态参数 ============
harmonics:
  zz_pct: 0.03
  tol: 0.12
  patterns: [Gartley, Bat, Butterfly, Crab, DeepCrab]
  min_grade: "B"
  # Shark 已回测禁用: "高胜率但总亏损，小赢大亏结构"

# ============ 止损止盈 (精准版) ============
stop_loss:
  type: "atr_buffer"
  atr_period: 14
  atr_multiplier: 0.7
  prz_buffer_ratio: 0.5   # PRZ 外侧 0.5% 缓冲
  # 计算: stop = PRZ_edge ± max(ATR*0.7, XA*0.5%)

take_profit:
  tp1_ratio: 0.382         # AD 腿的 38.2% 回撤位
  tp2_ratio: 0.618         # AD 腿的 61.8% 回撤位
  partial_exit_1: 0.50     # TP1 时平 50%
  partial_exit_2: 1.00     # TP2 时全平

# ============ 三次扫描时间 (UTC+8) ============
schedule:
  times: ["00:00", "08:00", "16:00"]
  timezone: "Asia/Shanghai"
  lookback_minutes: 30     # 扫描最近 30 分钟的 K 线变化

# ============ 风险控制 ============
risk:
  max_positions: 3         # 最大同时持仓数
  max_risk_per_trade: 0.02 # 单笔最大风险 2%
  max_total_risk: 0.06      # 总风险敞口 6%
  signal_expiry_hours: 8    # 信号有效期 8 小时

# ============ Telegram 推送 ============
telegram:
  enabled: true
  bot_token: ""
  chat_id: ""
  new_signal_only: true     # 仅推送新信号
  include_chart: false      # 未来: 附带 K 线图
```

---

## 五、信号格式

### 5.1 完整信号报告 (Markdown)

```markdown
## 🔔 加密货币和谐形态信号报告
**扫描时间**: 2026-07-26 00:00 UTC+8
**扫描轮次**: 第 1/3 轮
**交易所**: Binance (主) / OKX (备)

---

### ✅ BTC/USDT-Binance | 看涨 Gartley | A级 | 做多
| 项目 | 数值 |
|------|------|
| 趋势状态 | ✅ 日线 EMA200 多头 (价格偏离 +2.3%) |
| RSI 状态 | ✅ 4H RSI 28.5 (超卖确认) |
| 形态 | Gartley (Bullish) |
| PRZ 区间 | 67,234 - 67,892 |
| 入场价格 | 67,500 |
| 止损价格 | 66,850 |
| 止损距离 | -2.1% |
| 止盈1 | 68,245 |
| 止盈1 RR | 1:1.8 |
| 止盈2 | 69,120 |
| 止盈2 RR | 1:2.6 |
| 风险等级 | A级 (汇聚度 1.2%) |
| 信号有效期 | 8 小时 |
| 信号 ID | sig_btc_gartley_20260726_00 |

---

### ⚠️ ETH/USDT-Binance | 看跌 Butterfly | B级 | 做空
| 项目 | 数值 |
|------|------|
| 趋势状态 | ⚠️ 日线 EMA200 空头 (价格偏离 -1.8%) |
| RSI 状态 | ⚠️ 4H RSI 65.2 (中性偏强) |
| 形态 | Butterfly (Bearish) |
| 优先级 | B级 (RSI 未确认超买) |
| 建议 | 观察等待 RSI > 70 确认 |

---
```

### 5.2 Telegram 推送格式

```
🟢 [Binance] BTC/USDT | 做多 | Gartley A级

📊 趋势: EMA200 多头 ✅
📉 RSI: 28.5 (超卖确认) ✅

🎯 入场: 67,500
🛑 止损: 66,850 (-2.1%)
🏁 TP1: 68,245 (RR 1:1.8) → 平50%
🏁 TP2: 69,120 (RR 1:2.6) → 全平

⏰ 信号有效期: 08:00
🔗 报告: [链接]
```

---

## 六、错误处理策略

| 场景 | 策略 | 优先级 |
|------|------|--------|
| 交易所 API 超时 | 切换备选交易所 | P0 |
| K 线数据不足 | 跳过该币种 + 记录 | P1 |
| EMA200 未确认 | 信号降级 + 标记"趋势待确认" | P2 |
| RSI 中间区域 | 信号降级 + 标记"RSI未确认" | P2 |
| 所有交易所失败 | 发送报警 + 使用缓存 | P0 |
| 扫描超时 (>15min) | 强制终止 + 报警 | P1 |

---

## 七、风险控制机制

### 7.1 持仓管理

```python
# 持仓状态追踪
class PositionManager:
    active_positions: List[Position]    # 当前持仓
    pending_signals: List[Signal]      # 待执行信号
    closed_positions: List[Position]   # 历史持仓

    def can_open_new_position(self, risk_amount: float) -> bool:
        if len(self.active_positions) >= MAX_POSITIONS:
            return False
        if self.total_risk + risk_amount > MAX_TOTAL_RISK:
            return False
        return True
```

### 7.2 信号生命周期

```
信号生成 → 有效期计时 (8h) → 入场/过期 → 持仓跟踪 → 止盈/止损平仓
                                    ↓
                              最大持仓 3 个
```

### 7.3 熔断机制

```python
circuit_breaker = {
    " consecutive_failures": 3,    # 连续失败次数
    " cooldown_minutes": 30,       # 熔断冷却
    " auto_resume": True           # 自动恢复
}
```

---

## 八、审计意见

### 8.1 架构层面

| 问题 | 严重性 | 建议 |
|------|--------|------|
| 多交易所数据差异未处理 | 高 | 统一 K 线重采样逻辑，优先使用 1m 聚合 |
| 缺少持仓管理模块 | 高 | 新增 `position_manager.py` |
| 信号未跟踪生命周期 | 中 | 添加信号状态机: new → active → filled → closed |
| 三次扫描时间可能重叠 | 中 | 添加互斥锁，防止并发扫描 |

### 8.2 指标层面

| 问题 | 严重性 | 建议 |
|------|--------|------|
| RSI 单周期确认太单薄 | 高 | 增加 RSI 背离检测 |
| EMA200 中性区域未定义 | 中 | 添加 neutral_zone_pct (建议 ±1%) |
| 缺少成交量确认 | 中 | 增加 VOL 过滤: 放量突破更可靠 |
| 未考虑 funding fee 差异 | 低 | 记录各交易所 funding fee 差异 |

### 8.3 和谐形态层面

| 问题 | 严重性 | 建议 |
|------|--------|------|
| Shark 禁用但代码未移除 | 低 | 确认移除或注释清楚 |
| 形态未做跨交易所回测 | 高 | 各交易所需单独回测验证 |
| PRZ 汇聚度分级阈值固定 | 中 | 考虑动态阈值 (根据波动率调整) |

### 8.4 风险层面

| 问题 | 严重性 | 建议 |
|------|--------|------|
| 无单笔最大仓位限制 | 高 | 添加 position_size 计算 |
| 无总风险敞口控制 | 高 | 添加 max_total_risk |
| 无最大持仓数控制 | 高 | 添加 max_positions |
| 止盈未考虑移动止损 | 中 | 增加 trailing stop 选项 |

### 8.5 运维层面

| 问题 | 严重性 | 建议 |
|------|--------|------|
| 无信号历史存档 | 中 | 添加 SQLite/JSON 信号库 |
| 无性能监控 | 低 | 添加扫描耗时统计 |
| 无报警机制 | 中 | 添加失败报警 (TG/Email) |

---

## 九、优化建议

### 9.1 高优先级优化

#### A. 增加 RSI 背离检测

```python
def check_rsi_divergence(prices: pd.Series, rsi: pd.Series,
                         lookback: int = 14) -> str:
    """
    检测价格与 RSI 背离
    - 底背离: 价格创新低但 RSI 未创新低 → 做多信号增强
    - 顶背离: 价格创新高但 RSI 未创新高 → 做空信号增强
    """
    price_lows = find_swings(prices, direction='low', lookback=lookback)
    rsi_lows = find_swings(rsi, direction='low', lookback=lookback)

    if price_lows[-1] < price_lows[-2] and rsi_lows[-1] > rsi_lows[-2]:
        return "bullish_divergence"

    return "none"
```

#### B. 增加成交量确认

```python
def check_volume_confirmation(df: pd.DataFrame,
                              threshold: float = 1.5) -> bool:
    """
    成交量确认: 当前 K 线成交量 > 过去 20 根均量 * threshold
    """
    vol_ma = df['volume'].rolling(20).mean()
    return df['volume'].iloc[-1] > vol_ma.iloc[-1] * threshold
```

#### C. 动态 PRZ 分级阈值

```python
def calculate_dynamic_prz_threshold(atr: float,
                                     center_price: float) -> dict:
    """
    根据波动率动态调整 PRZ 分级阈值
    高波动市场 → 放宽阈值
    低波动市场 → 收紧阈值
    """
    volatility_ratio = atr / center_price

    if volatility_ratio > 0.05:    # 高波动 (>5% ATR/价格)
        return {"grade_a": 0.04, "grade_b": 0.08}
    elif volatility_ratio > 0.02: # 中波动
        return {"grade_a": 0.03, "grade_b": 0.06}
    else:                           # 低波动
        return {"grade_a": 0.02, "grade_b": 0.04}
```

### 9.2 中优先级优化

#### D. 增加持仓快照功能

```python
@dataclass
class PositionSnapshot:
    signal_id: str
    entry_time: datetime
    entry_price: float
    position_size: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    current_price: float
    stop_loss: float
    tp1: float
    tp2: float
    time_in_trade: timedelta
    atr: float
```

#### E. 增加移动止损

```python
def apply_trailing_stop(position: Position,
                        current_price: float,
                        activation_pct: float = 0.01,
                        trail_pct: float = 0.005) -> float:
    """
    移动止损:
    1. 盈利达到 activation_pct 后激活
    2. 此后止损线随价格向盈利方向移动
    """
    pnl_pct = (current_price - position.entry_price) / position.entry_price

    if pnl_pct < activation_pct:
        return position.stop_loss  # 未激活

    new_stop = current_price * (1 - trail_pct)
    return max(new_stop, position.stop_loss)  # 只往上走/往下走
```

#### F. 增加信号去重机制

```python
def deduplicate_signals(signals: List[Signal],
                        same_symbol_cooldown: int = 24) -> List[Signal]:
    """
    同币种信号冷却期: 24 小时内同向信号只保留最新
    逆向信号立即生效
    """
```

### 9.3 低优先级优化

#### G. 增加邮件推送

```python
class EmailAlerter:
    def send_signal(self, signal: Signal):
        # 备选推送通道
        pass

    def send_daily_summary(self, summary: DailySummary):
        # 每日汇总报告
        pass
```

#### H. 增加 Webhook 支持

```python
class WebhookAlerter:
    def send(self, payload: dict, url: str):
        # 接入 TradingView Alert 等
        pass
```

---

## 十、数据获取接口

### 10.1 统一适配器接口

```python
from abc import ABC, abstractmethod

class ExchangeAdapter(ABC):
    @abstractmethod
    def get_klines(self, symbol: str, timeframe: str,
                   limit: int = 200) -> pd.DataFrame:
        """获取 K 线数据"""
        pass

    @abstractmethod
    def get_ticker(self, symbol: str) -> dict:
        """获取当前价格"""
        pass

    @abstractmethod
    def get_funding_rate(self, symbol: str) -> float:
        """获取 funding fee"""
        pass

    def normalize_symbol(self, symbol: str) -> str:
        """统一交易对格式: BTC/USDT → BTCUSDT"""
        return symbol.replace("/", "")
```

### 10.2 各交易所实现

| 交易所 | K 线 API | 注意 |
|--------|----------|------|
| Binance | `/api/v3/klines` | 主力数据源，全币种 4H K线 |
| OKX | `/api/v5/market/candles` | 备选，响应格式不同，需映射 |
| Bybit | `/v5/market/kline` | 备选，支持 category=linear |

---

## 十一、性能要求

| 指标 | 目标 | 熔断阈值 |
|------|------|----------|
| 单币种扫描耗时 | < 2s | > 10s |
| 全币种扫描耗时 | < 30s | > 120s |
| API 重试次数 | 3 次 | - |
| API 超时 | 10s | - |
| 内存占用 | < 500MB | - |

---

## 十二、待办事项

- [ ] 完成 `exchanges/` 适配器实现
- [ ] 完成 `indicators.py` (EMA200 + RSI)
- [ ] 完成 `harmonics.py` 集成
- [ ] 完成 `filters.py` (多周期共振过滤)
- [ ] 完成 `position_manager.py`
- [ ] 完成 `scanner.py`
- [ ] 完成 `reporter.py`
- [ ] 完成 `alerter.py`
- [ ] 完成 `scheduler.py`
- [ ] 编写单元测试
- [ ] 回测验证 (各交易所、各币种)
- [ ] Telegram 推送联调

---

## 附录 A: 与参考代码的集成

| 参考代码模块 | 集成方式 |
|-------------|----------|
| `zigzag(df, pct)` | 直接复用 |
| `PATTERNS` dict | 直接复用 |
| `validate_pattern()` | 直接复用 |
| `scan(df)` | 直接复用 |
| `calc_entry()` | 用于未完成形态的 D 点预测 |

## 附录 B: EMA200 计算

```python
def calculate_ema200(df: pd.DataFrame) -> float:
    """计算 EMA200"""
    return df['close'].ewm(span=200, adjust=False).mean().iloc[-1]

def get_trend_direction(price: float, ema200: float,
                        neutral_zone: float = 0.01) -> str:
    if price > ema200 * (1 + neutral_zone):
        return "bullish"
    elif price < ema200 * (1 - neutral_zone):
        return "bearish"
    return "neutral"
```

## 附录 C: RSI 计算

```python
def calculate_rsi(prices: pd.Series, period: int = 14) -> float:
    delta = prices.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs)).iloc[-1]
```

---

*文档版本: v2.2*
*最后更新: 2026-07-26*
*更新内容: 所有币种统一使用 Binance 4H K线进行和谐形态检测*
