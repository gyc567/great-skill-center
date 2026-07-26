"""OKX 交易所适配器"""
import requests
from typing import Optional
import pandas as pd
from .base import ExchangeAdapter


class OKXAdapter(ExchangeAdapter):
    """OKX 交易所适配器"""

    BASE_URL = "https://www.okx.com"
    API_VERSION = "v5"

    def __init__(self):
        super().__init__("okx")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        })

    def get_klines(self, symbol: str, timeframe: str = "4h", limit: int = 200) -> pd.DataFrame:
        """
        获取OKX K线数据

        Args:
            symbol: 交易对，如 BTC/USDT
            timeframe: K线周期
            limit: 获取数量
        """
        endpoint = f"{self.BASE_URL}/api/{self.API_VERSION}/market/candles"
        inst_id = self.normalize_symbol(symbol).replace("USDT", "-USDT")
        params = {
            "instId": inst_id,
            "bar": timeframe,
            "limit": limit
        }

        try:
            resp = self.session.get(endpoint, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            if data.get("code") != "0" or not data.get("data"):
                return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])

            # OKX返回格式: [ts, open, high, low, close, volume, ...]
            klines = []
            for k in reversed(data["data"]):
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
        endpoint = f"{self.BASE_URL}/api/{self.API_VERSION}/market/ticker"
        inst_id = self.normalize_symbol(symbol).replace("USDT", "-USDT")
        params = {"instId": inst_id}

        try:
            resp = self.session.get(endpoint, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            if data.get("code") == "0" and data.get("data"):
                return {"price": float(data["data"][0]["last"])}
            return None
        except requests.exceptions.RequestException:
            return None
