"""filters.py 单元测试"""
import unittest
from scripts.filters import SignalFilter, create_filtered_signal
from scripts.indicators import TrendResult, RSIResult


class TestSignalFilter(unittest.TestCase):
    """SignalFilter 测试类"""

    def setUp(self):
        """创建测试过滤器"""
        self.filter = SignalFilter(
            ema_period=200,
            rsi_period=14,
            oversold=30,
            overbought=70,
            neutral_zone=0.01,
            min_grade="B"
        )

    def test_filter_trend_bullish_match(self):
        """测试趋势匹配 - 看涨"""
        trend = TrendResult(
            direction="bullish",
            price=105,
            ema_value=100,
            deviation_pct=5.0
        )
        is_valid, notes = self.filter.filter_by_trend(trend, "bullish")
        self.assertTrue(is_valid)
        self.assertIn("趋势确认", notes[0])

    def test_filter_trend_bullish_against(self):
        """测试趋势逆势 - 看涨但趋势下跌"""
        trend = TrendResult(
            direction="bearish",
            price=95,
            ema_value=100,
            deviation_pct=-5.0
        )
        is_valid, notes = self.filter.filter_by_trend(trend, "bullish")
        self.assertFalse(is_valid)
        self.assertIn("趋势逆势", notes[0])

    def test_filter_trend_neutral(self):
        """测试趋势中性"""
        trend = TrendResult(
            direction="neutral",
            price=100,
            ema_value=100,
            deviation_pct=0.0
        )
        is_valid, notes = self.filter.filter_by_trend(trend, "bullish")
        self.assertFalse(is_valid)

    def test_filter_trend_bearish_match(self):
        """测试趋势匹配 - 看跌"""
        trend = TrendResult(
            direction="bearish",
            price=95,
            ema_value=100,
            deviation_pct=-5.0
        )
        is_valid, notes = self.filter.filter_by_trend(trend, "bearish")
        self.assertTrue(is_valid)

    def test_filter_rsi_oversold_bullish(self):
        """测试 RSI 超卖确认 - 看涨"""
        rsi = RSIResult(value=25, status="oversold")
        is_valid, notes = self.filter.filter_by_rsi(rsi, "bullish", require_confirmation=True)
        self.assertTrue(is_valid)
        self.assertIn("RSI超卖确认", notes[0])

    def test_filter_rsi_overbought_bullish(self):
        """测试 RSI 超买 - 看涨"""
        rsi = RSIResult(value=75, status="overbought")
        is_valid, notes = self.filter.filter_by_rsi(rsi, "bullish", require_confirmation=True)
        self.assertFalse(is_valid)

    def test_filter_rsi_neutral_bullish(self):
        """测试 RSI 中性 - 看涨"""
        rsi = RSIResult(value=50, status="neutral")
        is_valid, notes = self.filter.filter_by_rsi(rsi, "bullish", require_confirmation=True)
        self.assertFalse(is_valid)

    def test_filter_rsi_overbought_bearish(self):
        """测试 RSI 超买确认 - 看跌"""
        rsi = RSIResult(value=75, status="overbought")
        is_valid, notes = self.filter.filter_by_rsi(rsi, "bearish", require_confirmation=True)
        self.assertTrue(is_valid)

    def test_filter_rsi_no_confirmation(self):
        """测试 RSI 确认禁用"""
        rsi = RSIResult(value=50, status="neutral")
        is_valid, notes = self.filter.filter_by_rsi(rsi, "bullish", require_confirmation=False)
        self.assertTrue(is_valid)
        self.assertIn("RSI确认已禁用", notes[0])

    def test_filter_grade_a(self):
        """测试 A 级"""
        is_valid, notes = self.filter.filter_by_grade("A")
        self.assertTrue(is_valid)
        self.assertIn("信号等级", notes[0])

    def test_filter_grade_b(self):
        """测试 B 级"""
        is_valid, notes = self.filter.filter_by_grade("B")
        self.assertTrue(is_valid)

    def test_filter_grade_c(self):
        """测试 C 级"""
        is_valid, notes = self.filter.filter_by_grade("C")
        self.assertFalse(is_valid)
        self.assertIn("太低", notes[0])

    def test_filter_grade_min_a(self):
        """测试最低要求 A 级"""
        filter_a = SignalFilter(min_grade="A")
        is_valid, notes = filter_a.filter_by_grade("B")
        self.assertFalse(is_valid)

    def test_filter_signal_full_bullish(self):
        """测试完整信号过滤 - 看涨"""
        signal = {
            "pattern": "Gartley",
            "direction": "bullish",
            "PRZ": (100, 101),
            "entry_ref": 100.5,
            "stop": 99,
            "tp1": 102,
            "tp2": 103,
            "rr_tp1": 1.5,
            "rr_tp2": 2.5
        }
        trend = TrendResult(direction="bullish", price=105, ema_value=100, deviation_pct=5)
        rsi = RSIResult(value=25, status="oversold")

        result = self.filter.filter_signal(signal, trend, rsi)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.pattern, "Gartley")
        self.assertEqual(result.direction, "bullish")

    def test_filter_signal_rejected_by_trend(self):
        """测试信号被趋势过滤"""
        signal = {
            "pattern": "Gartley",
            "direction": "bullish",
            "PRZ": (100, 101),
            "entry_ref": 100.5,
            "stop": 99,
            "tp1": 102,
            "tp2": 103,
            "rr_tp1": 1.5,
            "rr_tp2": 2.5
        }
        trend = TrendResult(direction="bearish", price=95, ema_value=100, deviation_pct=-5)
        rsi = RSIResult(value=25, status="oversold")

        result = self.filter.filter_signal(signal, trend, rsi)
        self.assertFalse(result.is_valid)


class TestCreateFilteredSignal(unittest.TestCase):
    """create_filtered_signal 测试"""

    def test_create_filtered_signal(self):
        """测试创建过滤信号"""
        harmonic = {
            "pattern": "Bat",
            "direction": "bearish",
            "PRZ": (100, 102),
            "entry_ref": 101,
            "stop": 103,
            "tp1": 98,
            "tp2": 95,
            "rr_tp1": 1.5,
            "rr_tp2": 3.0
        }
        trend = TrendResult(direction="bearish", price=95, ema_value=100, deviation_pct=-5)
        rsi = RSIResult(value=80, status="overbought")

        result = create_filtered_signal(
            symbol="BTC/USDT",
            exchange="binance",
            harmonic_result=harmonic,
            trend=trend,
            rsi=rsi
        )

        self.assertEqual(result.symbol, "BTC/USDT")
        self.assertEqual(result.exchange, "binance")
        self.assertEqual(result.pattern, "Bat")


if __name__ == '__main__':
    unittest.main()
