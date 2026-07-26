"""config.py 单元测试"""
import unittest
from scripts.config import (
    Config, ExchangeConfig, SymbolConfig, HarmonicConfig,
    EMAConfig, RSIConfig, StopLossConfig, TakeProfitConfig,
    ScheduleConfig, RiskConfig, TelegramConfig,
    DEFAULT_CONFIG
)


class TestConfig(unittest.TestCase):
    """Config 测试类"""

    def test_default_config(self):
        """测试默认配置"""
        self.assertIsInstance(DEFAULT_CONFIG, Config)

    def test_config_defaults(self):
        """测试配置默认值"""
        config = Config()
        self.assertEqual(len(config.symbols), 9)
        self.assertEqual(config.harmonic.zz_pct, 0.03)
        self.assertEqual(config.ema.period, 200)

    def test_config_symbols(self):
        """测试交易对配置"""
        config = Config(symbols=["BTC/USDT", "ETH/USDT"])
        self.assertEqual(len(config.symbols), 2)
        self.assertIn("BTC/USDT", config.symbols)

    def test_config_harmonic(self):
        """测试和谐形态配置"""
        config = Config()
        self.assertIn("Gartley", config.harmonic.patterns)
        self.assertIn("Bat", config.harmonic.patterns)
        self.assertNotIn("Shark", config.harmonic.patterns)

    def test_config_ema(self):
        """测试 EMA 配置"""
        config = Config()
        self.assertEqual(config.ema.period, 200)
        self.assertEqual(config.ema.neutral_zone_pct, 0.01)

    def test_config_rsi(self):
        """测试 RSI 配置"""
        config = Config()
        self.assertEqual(config.rsi.period, 14)
        self.assertEqual(config.rsi.oversold, 30)
        self.assertEqual(config.rsi.overbought, 70)

    def test_config_stop_loss(self):
        """测试止损配置"""
        config = Config()
        self.assertEqual(config.stop_loss.type, "atr_buffer")
        self.assertEqual(config.stop_loss.atr_multiplier, 0.7)

    def test_config_take_profit(self):
        """测试止盈配置"""
        config = Config()
        self.assertEqual(config.take_profit.tp1_ratio, 0.382)
        self.assertEqual(config.take_profit.tp2_ratio, 0.618)

    def test_config_schedule(self):
        """测试调度配置"""
        config = Config()
        self.assertEqual(len(config.schedule.times), 3)
        self.assertIn("00:00", config.schedule.times)
        self.assertIn("08:00", config.schedule.times)
        self.assertIn("16:00", config.schedule.times)

    def test_config_risk(self):
        """测试风险配置"""
        config = Config()
        self.assertEqual(config.risk.max_positions, 3)
        self.assertEqual(config.risk.max_risk_per_trade, 0.02)

    def test_config_telegram(self):
        """测试 Telegram 配置"""
        config = Config()
        self.assertFalse(config.telegram.enabled)
        self.assertEqual(config.telegram.bot_token, "")


class TestSubConfigs(unittest.TestCase):
    """子配置测试"""

    def test_exchange_config(self):
        """测试交易所配置"""
        ec = ExchangeConfig(name="binance", enabled=True, priority=0)
        self.assertEqual(ec.name, "binance")
        self.assertTrue(ec.enabled)

    def test_symbol_config(self):
        """测试交易对配置"""
        sc = SymbolConfig(symbol="BTC/USDT", exchange="binance")
        self.assertEqual(sc.symbol, "BTC/USDT")
        self.assertTrue(sc.enabled)

    def test_harmonic_config(self):
        """测试和谐形态子配置"""
        hc = HarmonicConfig(zz_pct=0.04, tol=0.10)
        self.assertEqual(hc.zz_pct, 0.04)
        self.assertEqual(hc.tol, 0.10)

    def test_ema_config(self):
        """测试 EMA 子配置"""
        ec = EMAConfig(period=100, neutral_zone_pct=0.02)
        self.assertEqual(ec.period, 100)

    def test_rsi_config(self):
        """测试 RSI 子配置"""
        rc = RSIConfig(period=20, oversold=25, overbought=75)
        self.assertEqual(rc.period, 20)

    def test_schedule_config(self):
        """测试调度子配置"""
        sc = ScheduleConfig(times=["06:00", "14:00", "22:00"])
        self.assertEqual(len(sc.times), 3)


if __name__ == '__main__':
    unittest.main()
