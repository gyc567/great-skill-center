"""批量扫描器"""
from dataclasses import dataclass
from typing import List, Optional, Dict
from datetime import datetime
import pandas as pd

from .exchanges.binance import BinanceAdapter
from .exchanges.okx import OKXAdapter
from .exchanges.bybit import BybitAdapter
from .indicators import Indicators
from .harmonics import scan as harmonic_scan, grade_signal
from .filters import SignalFilter, create_filtered_signal
from .config import Config


@dataclass
class ScanResult:
    """扫描结果"""
    timestamp: datetime
    symbol: str
    exchange: str
    signal: Optional[dict]
    trend: Optional[dict]
    rsi: Optional[dict]
    is_valid: bool
    notes: List[str]


class Scanner:
    """批量扫描器"""

    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.exchanges = self._init_exchanges()
        self.indicator = Indicators()
        self.filter = SignalFilter(
            ema_period=self.config.ema.period,
            rsi_period=self.config.rsi.period,
            oversold=self.config.rsi.oversold,
            overbought=self.config.rsi.overbought,
            neutral_zone=self.config.ema.neutral_zone_pct,
            min_grade=self.config.harmonic.min_grade
        )

    def _init_exchanges(self) -> Dict[str, object]:
        """初始化交易所适配器"""
        adapters = {
            "binance": BinanceAdapter(),
            "okx": OKXAdapter(),
            "bybit": BybitAdapter()
        }
        return adapters

    def get_exchange(self, name: str):
        """获取交易所适配器"""
        return self.exchanges.get(name.lower())

    def scan_symbol(self, symbol: str, exchange_name: str = "binance") -> ScanResult:
        """
        扫描单个交易对

        Args:
            symbol: 交易对，如 BTC/USDT
            exchange_name: 交易所名

        Returns:
            ScanResult
        """
        exchange = self.get_exchange(exchange_name)
        if not exchange:
            return ScanResult(
                timestamp=datetime.now(),
                symbol=symbol,
                exchange=exchange_name,
                signal=None,
                trend=None,
                rsi=None,
                is_valid=False,
                notes=[f"交易所 {exchange_name} 不可用"]
            )

        notes = []
        now = datetime.now()

        # 获取4H K线 (用于和谐形态和RSI)
        df_4h = exchange.get_klines(symbol, timeframe="4h", limit=200)
        if df_4h.empty or len(df_4h) < 50:
            return ScanResult(
                timestamp=now,
                symbol=symbol,
                exchange=exchange_name,
                signal=None,
                trend=None,
                rsi=None,
                is_valid=False,
                notes=["4H K线数据不足"]
            )

        # 获取日K线 (用于EMA200趋势)
        df_1d = exchange.get_klines(symbol, timeframe="1d", limit=250)
        if df_1d.empty or len(df_1d) < 200:
            notes.append("日K线不足，使用4H趋势")
            df_trend = df_4h
        else:
            df_trend = df_1d

        # 计算趋势
        trend = Indicators.get_trend(
            df_trend,
            ema_period=self.config.ema.period,
            neutral_zone=self.config.ema.neutral_zone_pct
        )

        # 计算RSI
        rsi = Indicators.get_rsi(
            df_4h,
            period=self.config.rsi.period,
            oversold=self.config.rsi.oversold,
            overbought=self.config.rsi.overbought
        )

        # 扫描和谐形态
        harmonic_signals = harmonic_scan(
            df_4h,
            zz_pct=self.config.harmonic.zz_pct,
            tol=self.config.harmonic.tol,
            patterns=self.config.harmonic.patterns,
            only_latest=True
        )

        if not harmonic_signals:
            return ScanResult(
                timestamp=now,
                symbol=symbol,
                exchange=exchange_name,
                signal=None,
                trend={"direction": trend.direction, "deviation": trend.deviation_pct},
                rsi={"value": rsi.value, "status": rsi.status},
                is_valid=False,
                notes=["未检测到和谐形态"]
            )

        # 取最新信号
        signal = harmonic_signals[0]
        signal["symbol"] = symbol
        signal["exchange"] = exchange_name

        # 创建过滤信号
        filtered = create_filtered_signal(
            symbol=symbol,
            exchange=exchange_name,
            harmonic_result=signal,
            trend=trend,
            rsi=rsi,
            min_grade=self.config.harmonic.min_grade
        )

        return ScanResult(
            timestamp=now,
            symbol=symbol,
            exchange=exchange_name,
            signal={
                "pattern": filtered.pattern,
                "direction": filtered.direction,
                "prz": filtered.prz,
                "entry_price": filtered.entry_price,
                "stop_loss": filtered.stop_loss,
                "tp1": filtered.tp1,
                "tp2": filtered.tp2,
                "rr_tp1": filtered.rr_tp1,
                "rr_tp2": filtered.rr_tp2,
                "grade": filtered.grade
            },
            trend={"direction": trend.direction, "deviation": trend.deviation_pct},
            rsi={"value": rsi.value, "status": rsi.status},
            is_valid=filtered.is_valid,
            notes=filtered.validation_notes
        )

    def scan_all(self) -> List[ScanResult]:
        """
        扫描所有配置的交易对

        Returns:
            ScanResult列表
        """
        results = []

        for symbol in self.config.symbols:
            result = self.scan_symbol(symbol, exchange_name="binance")
            results.append(result)

        return results

    def get_valid_signals(self, results: List[ScanResult]) -> List[ScanResult]:
        """获取有效信号"""
        return [r for r in results if r.is_valid and r.signal is not None]

    def get_summary(self, results: List[ScanResult]) -> dict:
        """获取扫描摘要"""
        valid = self.get_valid_signals(results)

        return {
            "total": len(results),
            "valid": len(valid),
            "invalid": len(results) - len(valid),
            "timestamp": datetime.now().isoformat(),
            "symbols": [r.symbol for r in results],
            "valid_symbols": [r.symbol for r in valid]
        }
