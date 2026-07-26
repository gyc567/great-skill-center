"""交易所适配器基类"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import pandas as pd


@dataclass
class Kline:
    """K线数据"""
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float


class ExchangeAdapter(ABC):
    """交易所适配器基类"""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def get_klines(self, symbol: str, timeframe: str = "4h", limit: int = 200) -> pd.DataFrame:
        """
        获取K线数据

        Args:
            symbol: 交易对，如 BTC/USDT
            timeframe: K线周期，如 1m, 5m, 15m, 1h, 4h, 1d
            limit: 获取数量

        Returns:
            DataFrame with columns: open, high, low, close, volume
        """
        pass

    def normalize_symbol(self, symbol: str) -> str:
        """统一交易对格式: BTC/USDT -> BTCUSDT"""
        return symbol.replace("/", "")

    def parse_timeframe(self, timeframe: str) -> str:
        """解析时间周期为API需要的格式"""
        mapping = {
            "1m": "1m", "5m": "5m", "15m": "15m",
            "1h": "1h", "4h": "4h", "1d": "1d"
        }
        return mapping.get(timeframe, timeframe)

    @staticmethod
    def to_dataframe(klines: list) -> pd.DataFrame:
        """将K线列表转换为DataFrame"""
        if not klines:
            return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])

        df = pd.DataFrame(klines)
        df.columns = ["timestamp", "open", "high", "low", "close", "volume"]
        return df[["open", "high", "low", "close", "volume"]]
