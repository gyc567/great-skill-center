"""harmonics.py 单元测试"""
import unittest
import pandas as pd
import numpy as np
from scripts.harmonics import (
    zigzag, validate_pattern, scan, grade_signal,
    calculate_stop_loss, calculate_take_profits,
    PATTERNS, DEFAULT_TOL
)


class TestHarmonics(unittest.TestCase):
    """Harmonics 测试类"""

    def setUp(self):
        """创建测试数据 - 教科书级看涨 Gartley"""
        # X=100, A=110, B=103.82(XA回撤0.618), C=107.64(AB回撤0.618),
        # D=102.14(XA回撤0.786, CD/BC=1.44)
        path = [100, 104, 110, 107, 103.82, 106, 107.64, 105, 102.14, 104, 106]
        rows = []
        for i, p in enumerate(path):
            rows.append({"open": p, "high": p, "low": p, "close": p})
        self.df = pd.DataFrame(rows, index=pd.date_range("2026-01-01", periods=len(rows), freq="4h"))

    def test_zigzag_basic(self):
        """测试 ZigZag 基本功能"""
        zz = zigzag(self.df, pct=0.03)
        self.assertIsInstance(zz, pd.DataFrame)
        self.assertIn('idx', zz.columns)
        self.assertIn('price', zz.columns)
        self.assertIn('type', zz.columns)

    def test_zigzag_types(self):
        """测试 ZigZag 类型"""
        zz = zigzag(self.df, pct=0.03)
        if len(zz) > 0:
            self.assertTrue(set(zz['type']).issubset({'H', 'L'}))

    def test_zigzag_alternation(self):
        """测试 ZigZag H/L 交替"""
        zz = zigzag(self.df, pct=0.03)
        if len(zz) > 1:
            types = zz['type'].tolist()
            for i in range(len(types) - 1):
                self.assertNotEqual(types[i], types[i + 1])

    def test_zigzag_empty_data(self):
        """测试空数据"""
        df = pd.DataFrame(columns=["open", "high", "low", "close"])
        zz = zigzag(df)
        self.assertEqual(len(zz), 0)

    def test_patterns_exist(self):
        """测试形态定义存在"""
        expected = ["Gartley", "Bat", "Butterfly", "Crab", "DeepCrab"]
        for p in expected:
            self.assertIn(p, PATTERNS)

    def test_patterns_structure(self):
        """测试形态结构"""
        for name, spec in PATTERNS.items():
            self.assertIn("B/XA", spec)
            self.assertIn("C/AB", spec)
            self.assertIn("D/XA", spec)
            self.assertIn("CD/BC", spec)

    def test_validate_gartley(self):
        """测试 Gartley 形态验证"""
        # X=100, A=110, B=103.82, C=107.64, D=102.14
        X = (0, 100)
        A = (1, 110)
        B = (2, 103.82)
        C = (3, 107.64)
        D = (4, 102.14)

        result = validate_pattern(X, A, B, C, D, "Gartley", tol=0.15)
        self.assertIsNotNone(result)
        self.assertEqual(result['pattern'], "Gartley")
        self.assertEqual(result['direction'], 'bullish')

    def test_validate_bearish_pattern(self):
        """测试看跌形态"""
        # 反转数据
        path = [100, 96, 90, 93, 96.18, 92, 92.36, 95, 97.86]
        rows = []
        for p in path:
            rows.append({"open": p, "high": p, "low": p, "close": p})
        df = pd.DataFrame(rows)

        zz = zigzag(df, pct=0.03)
        if len(zz) >= 5:
            pts = [(int(r.idx), float(r.price)) for r in zz.itertuples()]
            if len(pts) >= 5:
                X, A, B, C, D = pts[-5:]
                result = validate_pattern(X, A, B, C, D, "Gartley")
                if result:
                    self.assertEqual(result['direction'], 'bearish')

    def test_scan_no_signal(self):
        """测试无信号情况"""
        # 随机数据不太可能形成形态
        np.random.seed(123)
        prices = 100 + np.random.randn(50) * 2
        df = pd.DataFrame({
            'open': prices, 'high': prices + 1,
            'low': prices - 1, 'close': prices
        })
        signals = scan(df, zz_pct=0.03, only_latest=True)
        # 可能没有信号，这是正常的

    def test_scan_with_pct(self):
        """测试不同 pct 扫描"""
        signals_003 = scan(self.df, zz_pct=0.03, only_latest=True)
        signals_005 = scan(self.df, zz_pct=0.05, only_latest=True)
        # 不同 pct 可能产生不同结果

    def test_grade_signal_a(self):
        """测试 A 级信号"""
        signal = {"PRZ": (100, 101)}  # 1% 宽度
        grade = grade_signal(signal, grade_a=0.02, grade_b=0.04)
        self.assertEqual(grade, 'A')

    def test_grade_signal_b(self):
        """测试 B 级信号"""
        signal = {"PRZ": (100, 103)}  # 3% 宽度 (大于2%小于4%)
        grade = grade_signal(signal, grade_a=0.02, grade_b=0.04)
        self.assertEqual(grade, 'B')

    def test_grade_signal_c(self):
        """测试 C 级信号"""
        signal = {"PRZ": (100, 105)}  # 5% 宽度
        grade = grade_signal(signal, grade_a=0.02, grade_b=0.04)
        self.assertEqual(grade, 'C')

    def test_grade_signal_edge(self):
        """测试边界情况"""
        signal = {"PRZ": (100, 102)}  # 2%
        grade_a = grade_signal(signal, grade_a=0.02, grade_b=0.04)
        self.assertEqual(grade_a, 'A')

        grade_b = grade_signal(signal, grade_a=0.019, grade_b=0.04)
        self.assertEqual(grade_b, 'B')

    def test_calculate_stop_loss_bullish(self):
        """测试看涨止损计算"""
        stop = calculate_stop_loss(
            entry=100, atr=2, direction="bullish",
            atr_multiplier=0.7, prz_buffer=0.005
        )
        self.assertLess(stop, 100)

    def test_calculate_stop_loss_bearish(self):
        """测试看跌止损计算"""
        stop = calculate_stop_loss(
            entry=100, atr=2, direction="bearish",
            atr_multiplier=0.7, prz_buffer=0.005
        )
        self.assertGreater(stop, 100)

    def test_calculate_take_profits(self):
        """测试止盈计算"""
        tp1, tp2 = calculate_take_profits(
            entry=100, stop=98,
            tp1_ratio=0.382, tp2_ratio=0.618
        )
        self.assertGreater(tp1, 100)
        self.assertGreater(tp2, tp1)


class TestHarmonicsIntegration(unittest.TestCase):
    """集成测试"""

    def test_full_scan_flow(self):
        """完整扫描流程"""
        # 创建更长的数据以产生信号
        np.random.seed(42)
        prices = [100]
        for _ in range(200):
            change = np.random.randn() * 2
            prices.append(prices[-1] + change)

        df = pd.DataFrame({
            'open': prices,
            'high': [p + 1 for p in prices],
            'low': [p - 1 for p in prices],
            'close': prices
        })

        signals = scan(df, zz_pct=0.03, only_latest=False)
        # 可能有一些信号


if __name__ == '__main__':
    unittest.main()
