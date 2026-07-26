"""alerter.py 单元测试"""
import unittest
from datetime import datetime
from scripts.alerter import TelegramAlerter, AlerterFactory
from scripts.scanner import ScanResult


class TestTelegramAlerter(unittest.TestCase):
    """TelegramAlerter 测试类"""

    def test_not_configured(self):
        """测试未配置状态"""
        alerter = TelegramAlerter()
        self.assertFalse(alerter.is_configured())

    def test_configured_empty_token(self):
        """测试空 token"""
        alerter = TelegramAlerter(bot_token="", chat_id="123")
        self.assertFalse(alerter.is_configured())

    def test_configured_empty_chat_id(self):
        """测试空 chat_id"""
        alerter = TelegramAlerter(bot_token="abc", chat_id="")
        self.assertFalse(alerter.is_configured())

    def test_configured(self):
        """测试已配置"""
        alerter = TelegramAlerter(bot_token="abc", chat_id="123")
        self.assertTrue(alerter.is_configured())

    def test_send_message_not_configured(self):
        """测试未配置时不发送"""
        alerter = TelegramAlerter()
        result = alerter.send_message("test")
        self.assertFalse(result)

    def test_send_signal_invalid_result(self):
        """测试发送无效信号"""
        alerter = TelegramAlerter(bot_token="abc", chat_id="123")
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
        # 即使配置了，无效信号也不发送
        sent = alerter.send_signal(result)
        self.assertFalse(sent)


class TestAlerterFactory(unittest.TestCase):
    """AlerterFactory 测试"""

    def test_create_telegram(self):
        """测试创建 Telegram 报警器"""
        alerter = AlerterFactory.create_telegram(
            bot_token="test_token",
            chat_id="test_chat"
        )
        self.assertIsInstance(alerter, TelegramAlerter)
        self.assertTrue(alerter.is_configured())

    def test_create_telegram_defaults(self):
        """测试创建默认 Telegram 报警器"""
        alerter = AlerterFactory.create_telegram()
        self.assertIsInstance(alerter, TelegramAlerter)
        self.assertFalse(alerter.is_configured())


if __name__ == '__main__':
    unittest.main()
