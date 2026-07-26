"""多周期共振过滤器"""
from dataclasses import dataclass
from typing import Optional, List
from .indicators import Indicators, TrendResult, RSIResult
from .harmonics import scan, grade_signal, HarmonicSignal


@dataclass
class FilteredSignal:
    """过滤后的信号"""
    symbol: str
    exchange: str
    pattern: str
    direction: str
    trend: str  # bullish, bearish, neutral
    rsi_status: str  # oversold, overbought, neutral
    prz: tuple
    entry_price: float
    stop_loss: float
    tp1: float
    tp2: float
    rr_tp1: float
    rr_tp2: float
    grade: str
    is_valid: bool
    validation_notes: List[str]


class SignalFilter:
    """信号过滤器"""

    def __init__(self,
                 ema_period: int = 200,
                 rsi_period: int = 14,
                 oversold: float = 30,
                 overbought: float = 70,
                 neutral_zone: float = 0.01,
                 min_grade: str = "B"):
        self.ema_period = ema_period
        self.rsi_period = rsi_period
        self.oversold = oversold
        self.overbought = overbought
        self.neutral_zone = neutral_zone
        self.min_grade = min_grade

    def filter_by_trend(self, trend: TrendResult, direction: str) -> tuple:
        """
        趋势方向过滤

        Args:
            trend: 趋势结果
            direction: 信号方向 (bullish/bearish)

        Returns:
            (is_valid, notes)
        """
        notes = []

        if trend.direction == "neutral":
            return False, ["趋势不明"]

        if direction == "bullish" and trend.direction != "bullish":
            return False, [f"趋势逆势: {trend.direction}"]

        if direction == "bearish" and trend.direction != "bearish":
            return False, [f"趋势逆势: {trend.direction}"]

        notes.append(f"趋势确认: {trend.direction}")
        return True, notes

    def filter_by_rsi(self, rsi: RSIResult, direction: str,
                     require_confirmation: bool = True) -> tuple:
        """
        RSI 过滤

        Args:
            rsi: RSI结果
            direction: 信号方向
            require_confirmation: 是否要求RSI确认

        Returns:
            (is_valid, notes)
        """
        notes = []

        if not require_confirmation:
            return True, ["RSI确认已禁用"]

        if direction == "bullish":
            if rsi.status == "oversold":
                notes.append(f"RSI超卖确认: {rsi.value:.1f}")
                return True, notes
            elif rsi.status == "neutral":
                notes.append(f"RSI中性偏强: {rsi.value:.1f} (未确认超卖)")
                return False, notes
            else:
                notes.append(f"RSI超买: {rsi.value:.1f} (不适合做多)")
                return False, notes

        elif direction == "bearish":
            if rsi.status == "overbought":
                notes.append(f"RSI超买确认: {rsi.value:.1f}")
                return True, notes
            elif rsi.status == "neutral":
                notes.append(f"RSI中性偏弱: {rsi.value:.1f} (未确认超买)")
                return False, notes
            else:
                notes.append(f"RSI超卖: {rsi.value:.1f} (不适合做空)")
                return False, notes

        return True, notes

    def filter_by_grade(self, grade: str) -> tuple:
        """
        信号分级过滤

        Args:
            grade: A, B, or C

        Returns:
            (is_valid, notes)
        """
        if grade == "C":
            return False, [f"信号等级{grade}太低，放弃"]

        if self.min_grade == "A" and grade != "A":
            return False, [f"最低要求A级，当前{grade}级"]

        return True, [f"信号等级: {grade}"]

    def filter_signal(self, signal: dict, trend: TrendResult,
                     rsi: RSIResult) -> FilteredSignal:
        """
        综合过滤信号

        Args:
            signal: 原始信号
            trend: 趋势结果
            rsi: RSI结果

        Returns:
            FilteredSignal
        """
        symbol = signal.get("symbol", "UNKNOWN")
        exchange = signal.get("exchange", "binance")
        direction = signal.get("direction", "bullish")

        all_notes = []
        is_valid = True

        # 趋势过滤
        trend_ok, trend_notes = self.filter_by_trend(trend, direction)
        all_notes.extend(trend_notes)
        if not trend_ok:
            is_valid = False

        # RSI过滤
        rsi_ok, rsi_notes = self.filter_by_rsi(rsi, direction, require_confirmation=True)
        all_notes.extend(rsi_notes)
        if not rsi_ok:
            is_valid = False

        # 分级过滤
        grade = grade_signal(signal)
        grade_ok, grade_notes = self.filter_by_grade(grade)
        all_notes.extend(grade_notes)
        if not grade_ok:
            is_valid = False

        return FilteredSignal(
            symbol=symbol,
            exchange=exchange,
            pattern=signal.get("pattern", "UNKNOWN"),
            direction=direction,
            trend=trend.direction,
            rsi_status=rsi.status,
            prz=signal.get("PRZ", (0, 0)),
            entry_price=signal.get("entry_ref", 0),
            stop_loss=signal.get("stop", 0),
            tp1=signal.get("tp1", 0),
            tp2=signal.get("tp2", 0),
            rr_tp1=signal.get("rr_tp1", 0),
            rr_tp2=signal.get("rr_tp2", 0),
            grade=grade,
            is_valid=is_valid,
            validation_notes=all_notes
        )


def create_filtered_signal(symbol: str, exchange: str,
                          harmonic_result: dict,
                          trend: TrendResult,
                          rsi: RSIResult,
                          min_grade: str = "B") -> FilteredSignal:
    """
    创建过滤后的信号

    Args:
        symbol: 交易对
        exchange: 交易所
        harmonic_result: 和谐形态检测结果
        trend: 趋势结果
        rsi: RSI结果
        min_grade: 最低信号等级

    Returns:
        FilteredSignal
    """
    filter_obj = SignalFilter(min_grade=min_grade)

    signal = harmonic_result.copy()
    signal["symbol"] = symbol
    signal["exchange"] = exchange

    return filter_obj.filter_signal(signal, trend, rsi)
