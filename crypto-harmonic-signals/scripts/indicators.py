"""技术指标计算"""
import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class TrendResult:
    """趋势判断结果"""
    direction: str  # bullish, bearish, neutral
    price: float
    ema_value: float
    deviation_pct: float


@dataclass
class RSIResult:
    """RSI计算结果"""
    value: float
    status: str  # oversold, overbought, neutral


class Indicators:
    """技术指标计算器"""

    @staticmethod
    def calculate_ema(prices: pd.Series, period: int) -> float:
        """计算EMA"""
        if len(prices) < period:
            return prices.mean() if len(prices) > 0 else 0.0
        return prices.ewm(span=period, adjust=False).mean().iloc[-1]

    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> float:
        """计算RSI"""
        if len(prices) < period + 1:
            return 50.0

        delta = prices.diff()
        gain = delta.where(delta > 0, 0.0).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0.0)).rolling(period).mean()

        rs = gain / loss
        rs = rs.replace([np.inf, -np.inf], np.nan)
        rsi = 100 - (100 / (1 + rs))

        return rsi.iloc[-1] if not np.isnan(rsi.iloc[-1]) else 50.0

    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> float:
        """计算ATR"""
        if len(df) < period + 1:
            return 0.0

        high = df['high']
        low = df['low']
        close = df['close']

        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())

        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()

        return atr.iloc[-1] if len(atr) > 0 else 0.0

    @classmethod
    def get_trend(cls, df: pd.DataFrame, ema_period: int = 200,
                   neutral_zone: float = 0.01) -> TrendResult:
        """
        获取趋势方向

        Args:
            df: K线数据
            ema_period: EMA周期
            neutral_zone: 中性区域百分比

        Returns:
            TrendResult
        """
        prices = df['close']
        ema_value = cls.calculate_ema(prices, ema_period)
        current_price = prices.iloc[-1]

        deviation = (current_price - ema_value) / ema_value

        if deviation > neutral_zone:
            direction = "bullish"
        elif deviation < -neutral_zone:
            direction = "bearish"
        else:
            direction = "neutral"

        return TrendResult(
            direction=direction,
            price=current_price,
            ema_value=ema_value,
            deviation_pct=deviation * 100
        )

    @classmethod
    def get_rsi(cls, df: pd.DataFrame, period: int = 14,
                oversold: float = 30, overbought: float = 70) -> RSIResult:
        """
        获取RSI状态

        Args:
            df: K线数据
            period: RSI周期
            oversold: 超卖阈值
            overbought: 超买阈值

        Returns:
            RSIResult
        """
        prices = df['close']
        rsi_value = cls.calculate_rsi(prices, period)

        if rsi_value < oversold:
            status = "oversold"
        elif rsi_value > overbought:
            status = "overbought"
        else:
            status = "neutral"

        return RSIResult(value=rsi_value, status=status)

    @classmethod
    def get_all_indicators(cls, df: pd.DataFrame,
                          ema_period: int = 200,
                          rsi_period: int = 14,
                          atr_period: int = 14,
                          neutral_zone: float = 0.01,
                          oversold: float = 30,
                          overbought: float = 70) -> dict:
        """
        获取所有指标

        Returns:
            dict with trend, rsi, atr
        """
        trend = cls.get_trend(df, ema_period, neutral_zone)
        rsi = cls.get_rsi(df, rsi_period, oversold, overbought)
        atr = cls.calculate_atr(df, atr_period)

        return {
            "trend": trend,
            "rsi": rsi,
            "atr": atr
        }
