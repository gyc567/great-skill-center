"""exchanges 单元测试"""
import unittest
import pandas as pd
from scripts.exchanges.base import ExchangeAdapter, Kline
from scripts.exchanges.binance import BinanceAdapter
from scripts.exchanges.okx import OKXAdapter
from scripts.exchanges.bybit import BybitAdapter


class TestExchangeAdapter(unittest.TestCase):
    """ExchangeAdapter 测试类"""

    def test_kline_dataclass(self):
        """测试 Kline 数据类"""
        kline = Kline(
            timestamp=1234567890,
            open=100.0,
            high=105.0,
            low=98.0,
            close=103.0,
            volume=1000.0
        )
        self.assertEqual(kline.open, 100.0)
        self.assertEqual(kline.high, 105.0)

    def test_normalize_symbol(self):
        """测试交易对格式化"""
        class TestAdapter(ExchangeAdapter):
            def get_klines(self, symbol, timeframe="4h", limit=200):
                pass

        adapter = TestAdapter("test")
        result = adapter.normalize_symbol("BTC/USDT")
        self.assertEqual(result, "BTCUSDT")

    def test_parse_timeframe(self):
        """测试时间周期解析"""
        class TestAdapter(ExchangeAdapter):
            def get_klines(self, symbol, timeframe="4h", limit=200):
                pass

        adapter = TestAdapter("test")
        self.assertEqual(adapter.parse_timeframe("1m"), "1m")
        self.assertEqual(adapter.parse_timeframe("4h"), "4h")
        self.assertEqual(adapter.parse_timeframe("1d"), "1d")

    def test_to_dataframe(self):
        """测试 DataFrame 转换"""
        # 模拟 Binance API 返回格式: [open_time, open, high, low, close, volume]
        klines = [
            [1234567890000, 100, 105, 98, 103, 1000],
            [1234567891000, 103, 108, 101, 106, 1200],
        ]
        df = ExchangeAdapter.to_dataframe(klines)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        self.assertIn("open", df.columns)
        self.assertIn("close", df.columns)

    def test_to_dataframe_empty(self):
        """测试空数据转换"""
        df = ExchangeAdapter.to_dataframe([])
        self.assertEqual(len(df), 0)


class TestBinanceAdapter(unittest.TestCase):
    """BinanceAdapter 测试类"""

    def setUp(self):
        """创建适配器"""
        self.adapter = BinanceAdapter()

    def test_adapter_name(self):
        """测试适配器名称"""
        self.assertEqual(self.adapter.name, "binance")

    def test_normalize_symbol(self):
        """测试 Binance 交易对格式化"""
        result = self.adapter.normalize_symbol("BTC/USDT")
        self.assertEqual(result, "BTCUSDT")

    def test_get_klines_returns_dataframe(self):
        """测试获取 K 线返回 DataFrame"""
        # 这是一个实际 API 调用测试
        df = self.adapter.get_klines("BTC/USDT", timeframe="4h", limit=10)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertIn("open", df.columns)
        self.assertIn("close", df.columns)

    def test_get_klines_invalid_symbol(self):
        """测试无效交易对"""
        df = self.adapter.get_klines("INVALID_SYMBOL_XYZ", timeframe="4h", limit=10)
        # 应该返回空 DataFrame 而不是抛出异常
        self.assertIsInstance(df, pd.DataFrame)

    def test_get_ticker(self):
        """测试获取价格"""
        ticker = self.adapter.get_ticker("BTC/USDT")
        if ticker:
            self.assertIn("price", ticker)
            self.assertIsInstance(ticker["price"], float)


class TestOKXAdapter(unittest.TestCase):
    """OKXAdapter 测试类"""

    def setUp(self):
        """创建适配器"""
        self.adapter = OKXAdapter()

    def test_adapter_name(self):
        """测试适配器名称"""
        self.assertEqual(self.adapter.name, "okx")

    def test_normalize_symbol(self):
        """测试 OKX 交易对格式化"""
        result = self.adapter.normalize_symbol("BTC/USDT")
        self.assertEqual(result, "BTCUSDT")


class TestBybitAdapter(unittest.TestCase):
    """BybitAdapter 测试类"""

    def setUp(self):
        """创建适配器"""
        self.adapter = BybitAdapter()

    def test_adapter_name(self):
        """测试适配器名称"""
        self.assertEqual(self.adapter.name, "bybit")

    def test_normalize_symbol(self):
        """测试 Bybit 交易对格式化"""
        result = self.adapter.normalize_symbol("BTC/USDT")
        self.assertEqual(result, "BTCUSDT")


if __name__ == '__main__':
    unittest.main()
