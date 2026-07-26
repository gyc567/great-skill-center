"""Binance 交易所适配器"""
import requests
from typing import Optional
import pandas as pd
from .base import ExchangeAdapter


class BinanceAdapter(ExchangeAdapter):
    """Binance 交易所适配器"""

    BASE_URL = "https://api.binance.com"
    API_VERSION = "v3"

    def __init__(self):
        super().__init__("binance")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        })

    def get_klines(self, symbol: str, timeframe: str = "4h", limit: int = 200) -> pd.DataFrame:
        """
        获取Binance K线数据

        Args:
            symbol: 交易对，如 BTC/USDT
            timeframe: K线周期，1m, 5m, 15m, 1h, 4h, 1d
            limit: 获取数量，默认200根
        """
        endpoint = f"{self.BASE_URL}/api/{self.API_VERSION}/klines"
        params = {
            "symbol": self.normalize_symbol(symbol),
            "interval": timeframe,
            "limit": limit
        }

        try:
            resp = self.session.get(endpoint, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            if not data:
                return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])

            # Binance返回格式: [open_time, open, high, low, close, volume, ...]
            klines = []
            for k in data:
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
        endpoint = f"{self.BASE_URL}/api/{self.API_VERSION}/ticker/price"
        params = {"symbol": self.normalize_symbol(symbol)}

        try:
            resp = self.session.get(endpoint, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            return {"price": float(data["price"])}
        except requests.exceptions.RequestException:
            return None
