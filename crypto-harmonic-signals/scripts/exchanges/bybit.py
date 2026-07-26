"""Bybit 交易所适配器"""
import requests
from typing import Optional
import pandas as pd
from .base import ExchangeAdapter


class BybitAdapter(ExchangeAdapter):
    """Bybit 交易所适配器"""

    BASE_URL = "https://api.bybit.com"
    API_VERSION = "v5"

    def __init__(self):
        super().__init__("bybit")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        })

    def get_klines(self, symbol: str, timeframe: str = "4h", limit: int = 200) -> pd.DataFrame:
        """
        获取Bybit K线数据

        Args:
            symbol: 交易对，如 BTC/USDT
            timeframe: K线周期
            limit: 获取数量
        """
        endpoint = f"{self.BASE_URL}/public/{self.API_VERSION}/market/kline"
        params = {
            "category": "linear",
            "symbol": self.normalize_symbol(symbol),
            "interval": self._map_timeframe(timeframe),
            "limit": limit
        }

        try:
            resp = self.session.get(endpoint, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            if data.get("retCode") != 0 or not data.get("result"):
                return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])

            items = data["result"]["list"]

            # Bybit返回格式: [open_time, open, high, low, close, volume]
            klines = []
            for k in reversed(items):
                klines.append({
                    "open": float(k[1]),
                    "high": float(k[2]),
                    "low": float(k[3]),
                    "close": float(k[4]),
                    "volume": float(k[5])
                })

            return pd.DataFrame(klines)

        except requests.exceptions.RequestException:
            return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])

    def get_ticker(self, symbol: str) -> Optional[dict]:
        """获取当前价格"""
        endpoint = f"{self.BASE_URL}/public/{self.API_VERSION}/market/ticker"
        params = {
            "category": "linear",
            "symbol": self.normalize_symbol(symbol)
        }

        try:
            resp = self.session.get(endpoint, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            if data.get("retCode") == 0 and data.get("result"):
                return {"price": float(data["result"]["list"][0]["lastPrice"])}
            return None
        except requests.exceptions.RequestException:
            return None

    @staticmethod
    def _map_timeframe(tf: str) -> str:
        """映射时间周期"""
        mapping = {
            "1m": "1", "5m": "5", "15m": "15",
            "1h": "60", "4h": "240", "1d": "D"
        }
        return mapping.get(tf, tf)
