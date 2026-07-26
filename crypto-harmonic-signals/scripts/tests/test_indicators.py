"""indicators.py 单元测试"""
import unittest
import pandas as pd
import numpy as np
from scripts.indicators import Indicators, TrendResult, RSIResult


class TestIndicators(unittest.TestCase):
    """Indicators 测试类"""

    def setUp(self):
        """创建测试数据"""
        np.random.seed(42)
        n = 300
        prices = 100 + np.cumsum(np.random.randn(n) * 2)
        self.df = pd.DataFrame({
            'open': prices,
            'high': prices + 1,
            'low': prices - 1,
            'close': prices
        })

    def test_calculate_ema(self):
        """测试 EMA 计算"""
        ema = Indicators.calculate_ema(self.df['close'], period=20)
        self.assertIsInstance(ema, float)
        self.assertGreater(ema, 0)

    def test_calculate_ema_short_data(self):
        """测试数据不足时的 EMA 计算"""
        short_df = self.df.head(10)
        ema = Indicators.calculate_ema(short_df['close'], period=200)
        self.assertIsInstance(ema, float)

    def test_calculate_rsi(self):
        """测试 RSI 计算"""
        rsi = Indicators.calculate_rsi(self.df['close'], period=14)
        self.assertIsInstance(rsi, float)
        self.assertGreaterEqual(rsi, 0)
        self.assertLessEqual(rsi, 100)

    def test_calculate_rsi_short_data(self):
        """测试数据不足时的 RSI 计算"""
        short_df = self.df.head(10)
        rsi = Indicators.calculate_rsi(short_df['close'], period=14)
        self.assertEqual(rsi, 50.0)

    def test_calculate_atr(self):
        """测试 ATR 计算"""
        atr = Indicators.calculate_atr(self.df, period=14)
        self.assertIsInstance(atr, float)
        self.assertGreaterEqual(atr, 0)

    def test_get_trend_bullish(self):
        """测试上涨趋势"""
        trend = Indicators.get_trend(self.df, ema_period=50, neutral_zone=0.01)
        self.assertIsInstance(trend, TrendResult)
        self.assertIn(trend.direction, ['bullish', 'bearish', 'neutral'])

    def test_get_trend_properties(self):
        """测试 TrendResult 属性"""
        trend = Indicators.get_trend(self.df, ema_period=200)
        self.assertTrue(hasattr(trend, 'direction'))
        self.assertTrue(hasattr(trend, 'price'))
        self.assertTrue(hasattr(trend, 'ema_value'))
        self.assertTrue(hasattr(trend, 'deviation_pct'))

    def test_get_rsi(self):
        """测试 RSI 状态"""
        rsi = Indicators.get_rsi(self.df, period=14, oversold=30, overbought=70)
        self.assertIsInstance(rsi, RSIResult)
        self.assertIn(rsi.status, ['oversold', 'overbought', 'neutral'])

    def test_get_all_indicators(self):
        """测试获取所有指标"""
        result = Indicators.get_all_indicators(
            self.df,
            ema_period=200,
            rsi_period=14,
            atr_period=14
        )
        self.assertIn('trend', result)
        self.assertIn('rsi', result)
        self.assertIn('atr', result)


class TestIndicatorsEdgeCases(unittest.TestCase):
    """边界情况测试"""

    def test_empty_dataframe(self):
        """测试空 DataFrame"""
        df = pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume'])
        rsi = Indicators.calculate_rsi(df['close'])
        self.assertEqual(rsi, 50.0)

    def test_constant_price(self):
        """测试价格不变"""
        df = pd.DataFrame({
            'open': [100] * 50,
            'high': [101] * 50,
            'low': [99] * 50,
            'close': [100] * 50
        })
        rsi = Indicators.calculate_rsi(df['close'])
        self.assertEqual(rsi, 50.0)

    def test_very_small_numbers(self):
        """测试极小数值"""
        df = pd.DataFrame({
            'open': np.random.rand(50) * 0.001,
            'high': np.random.rand(50) * 0.001 + 0.001,
            'low': np.random.rand(50) * 0.001 - 0.001,
            'close': np.random.rand(50) * 0.001
        })
        trend = Indicators.get_trend(df, ema_period=20)
        self.assertIsInstance(trend.direction, str)


if __name__ == '__main__':
    unittest.main()
