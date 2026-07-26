"""reporter.py 单元测试"""
import unittest
from datetime import datetime
from scripts.reporter import Reporter, create_report, SignalReport
from scripts.scanner import ScanResult


class TestReporter(unittest.TestCase):
    """Reporter 测试类"""

    def setUp(self):
        """创建测试报告器"""
        self.reporter = Reporter()

    def test_format_direction_emoji_bullish(self):
        """测试看涨方向 emoji"""
        emoji = self.reporter.format_direction_emoji("bullish")
        self.assertEqual(emoji, "🟢")

    def test_format_direction_emoji_bearish(self):
        """测试看跌方向 emoji"""
        emoji = self.reporter.format_direction_emoji("bearish")
        self.assertEqual(emoji, "🔴")

    def test_format_status_emoji_oversold(self):
        """测试超卖状态 emoji"""
        emoji = self.reporter.format_status_emoji("oversold")
        self.assertEqual(emoji, "✅")

    def test_format_status_emoji_overbought(self):
        """测试超买状态 emoji"""
        emoji = self.reporter.format_status_emoji("overbought")
        self.assertEqual(emoji, "⚠️")

    def test_format_status_emoji_neutral(self):
        """测试中性状态 emoji"""
        emoji = self.reporter.format_status_emoji("neutral")
        self.assertEqual(emoji, "⚪")

    def test_format_trend_status_bullish(self):
        """测试看涨趋势"""
        status = self.reporter.format_trend_status("bullish")
        self.assertIn("多头", status)
        self.assertIn("EMA200", status)

    def test_format_trend_status_bearish(self):
        """测试看跌趋势"""
        status = self.reporter.format_trend_status("bearish")
        self.assertIn("空头", status)

    def test_format_trend_status_neutral(self):
        """测试中性趋势"""
        status = self.reporter.format_trend_status("neutral")
        self.assertIn("不明", status)

    def test_format_rsi_status_oversold(self):
        """测试 RSI 超卖"""
        status = self.reporter.format_rsi_status("oversold", 25.0)
        self.assertIn("超卖", status)
        self.assertIn("25.0", status)

    def test_format_rsi_status_overbought(self):
        """测试 RSI 超买"""
        status = self.reporter.format_rsi_status("overbought", 75.0)
        self.assertIn("超买", status)

    def test_generate_signal_table(self):
        """测试信号表格生成"""
        result = ScanResult(
            timestamp=datetime.now(),
            symbol="BTC/USDT",
            exchange="binance",
            signal={
                "pattern": "Gartley",
                "direction": "bullish",
                "prz": (67000, 67100),
                "entry_price": 67050,
                "stop_loss": 66800,
                "tp1": 67500,
                "tp2": 68000,
                "rr_tp1": 1.8,
                "rr_tp2": 2.5,
                "grade": "A"
            },
            trend={"direction": "bullish", "deviation": 2.5},
            rsi={"value": 25, "status": "oversold"},
            is_valid=True,
            notes=["信号有效"]
        )

        table = self.reporter.generate_signal_table(result)
        self.assertIn("Gartley", table)
        self.assertIn("67,050.00", table)
        self.assertIn("A", table)

    def test_generate_signal_table_empty(self):
        """测试空信号表格"""
        result = ScanResult(
            timestamp=datetime.now(),
            symbol="BTC/USDT",
            exchange="binance",
            signal=None,
            trend=None,
            rsi=None,
            is_valid=False,
            notes=[]
        )

        table = self.reporter.generate_signal_table(result)
        self.assertEqual(table, "")

    def test_generate_markdown_report(self):
        """测试 Markdown 报告生成"""
        result = ScanResult(
            timestamp=datetime.now(),
            symbol="BTC/USDT",
            exchange="binance",
            signal={
                "pattern": "Gartley",
                "direction": "bullish",
                "prz": (67000, 67100),
                "entry_price": 67050,
                "stop_loss": 66800,
                "tp1": 67500,
                "tp2": 68000,
                "rr_tp1": 1.8,
                "rr_tp2": 2.5,
                "grade": "A"
            },
            trend={"direction": "bullish", "deviation": 2.5},
            rsi={"value": 25, "status": "oversold"},
            is_valid=True,
            notes=["信号有效"]
        )

        report = SignalReport(
            timestamp=datetime.now(),
            round_num=1,
            total_symbols=1,
            valid_signals=1,
            results=[result]
        )

        md = self.reporter.generate_markdown_report(report)
        self.assertIn("# 🔔", md)
        self.assertIn("BTC/USDT", md)
        self.assertIn("Gartley", md)

    def test_generate_telegram_message(self):
        """测试 Telegram 消息生成"""
        result = ScanResult(
            timestamp=datetime.now(),
            symbol="BTC/USDT",
            exchange="binance",
            signal={
                "pattern": "Gartley",
                "direction": "bullish",
                "prz": (67000, 67100),
                "entry_price": 67050,
                "stop_loss": 66800,
                "tp1": 67500,
                "tp2": 68000,
                "rr_tp1": 1.8,
                "rr_tp2": 2.5,
                "grade": "A"
            },
            trend={"direction": "bullish", "deviation": 2.5},
            rsi={"value": 25, "status": "oversold"},
            is_valid=True,
            notes=["信号有效"]
        )

        msg = self.reporter.generate_telegram_message(result)
        self.assertIsNotNone(msg)
        self.assertIn("BTC/USDT", msg)
        self.assertIn("Gartley", msg)
        self.assertIn("67,050.00", msg)

    def test_generate_telegram_message_invalid(self):
        """测试无效信号不生成消息"""
        result = ScanResult(
            timestamp=datetime.now(),
            symbol="BTC/USDT",
            exchange="binance",
            signal=None,
            trend=None,
            rsi=None,
            is_valid=False,
            notes=["无信号"]
        )

        msg = self.reporter.generate_telegram_message(result)
        self.assertIsNone(msg)


class TestCreateReport(unittest.TestCase):
    """create_report 测试"""

    def test_create_report(self):
        """测试创建报告"""
        results = []
        report = create_report(results, round_num=1)

        self.assertIsInstance(report, SignalReport)
        self.assertEqual(report.round_num, 1)
        self.assertEqual(report.total_symbols, 0)
        self.assertEqual(report.valid_signals, 0)

    def test_create_report_with_valid_signal(self):
        """测试创建包含有效信号的报告"""
        result = ScanResult(
            timestamp=datetime.now(),
            symbol="BTC/USDT",
            exchange="binance",
            signal={"pattern": "Gartley"},
            trend={"direction": "bullish"},
            rsi={"value": 30},
            is_valid=True,
            notes=[]
        )

        report = create_report([result], round_num=2)
        self.assertEqual(report.total_symbols, 1)
        self.assertEqual(report.valid_signals, 1)


if __name__ == '__main__':
    unittest.main()
