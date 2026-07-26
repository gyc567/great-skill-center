"""配置管理"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class ExchangeConfig:
    """交易所配置"""
    name: str
    enabled: bool = True
    priority: int = 0


@dataclass
class SymbolConfig:
    """交易对配置"""
    symbol: str
    exchange: str = "binance"
    enabled: bool = True


@dataclass
class HarmonicConfig:
    """和谐形态配置"""
    zz_pct: float = 0.03
    tol: float = 0.12
    patterns: List[str] = field(default_factory=lambda: [
        "Gartley", "Bat", "Butterfly", "Crab", "DeepCrab"
    ])
    min_grade: str = "B"


@dataclass
class EMAConfig:
    """EMA配置"""
    enabled: bool = True
    period: int = 200
    neutral_zone_pct: float = 0.01


@dataclass
class RSIConfig:
    """RSI配置"""
    enabled: bool = True
    period: int = 14
    oversold: float = 30
    overbought: float = 70
    confirmation_required: bool = True


@dataclass
class StopLossConfig:
    """止损配置"""
    type: str = "atr_buffer"
    atr_period: int = 14
    atr_multiplier: float = 0.7
    prz_buffer_ratio: float = 0.005


@dataclass
class TakeProfitConfig:
    """止盈配置"""
    tp1_ratio: float = 0.382
    tp2_ratio: float = 0.618
    partial_exit_1: float = 0.50
    partial_exit_2: float = 1.00


@dataclass
class ScheduleConfig:
    """调度配置"""
    times: List[str] = field(default_factory=lambda: ["00:00", "08:00", "16:00"])
    timezone: str = "Asia/Shanghai"


@dataclass
class RiskConfig:
    """风险配置"""
    max_positions: int = 3
    max_risk_per_trade: float = 0.02
    max_total_risk: float = 0.06
    signal_expiry_hours: int = 8


@dataclass
class TelegramConfig:
    """Telegram配置"""
    enabled: bool = False
    bot_token: str = ""
    chat_id: str = ""
    new_signal_only: bool = True


@dataclass
class Config:
    """主配置"""
    symbols: List[str] = field(default_factory=lambda: [
        "BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT",
        "ZEC/USDT", "UNI/USDT", "AVAX/USDT", "AAVE/USDT", "HYPE/USDT"
    ])
    exchanges: List[str] = field(default_factory=lambda: ["binance"])
    fallbacks: List[str] = field(default_factory=lambda: ["okx", "bybit"])

    harmonic: HarmonicConfig = field(default_factory=HarmonicConfig)
    ema: EMAConfig = field(default_factory=EMAConfig)
    rsi: RSIConfig = field(default_factory=RSIConfig)
    stop_loss: StopLossConfig = field(default_factory=StopLossConfig)
    take_profit: TakeProfitConfig = field(default_factory=TakeProfitConfig)
    schedule: ScheduleConfig = field(default_factory=ScheduleConfig)
    risk: RiskConfig = field(default_factory=RiskConfig)
    telegram: TelegramConfig = field(default_factory=TelegramConfig)


# 默认配置实例
DEFAULT_CONFIG = Config()
