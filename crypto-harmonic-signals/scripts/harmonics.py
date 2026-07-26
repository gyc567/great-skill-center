"""
和谐形态检测模块
基于 harmonic_detector(1).py 重构，保持核心逻辑不变
"""
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Optional, Tuple


# 形态比例容差
DEFAULT_TOL = 0.12

# 启用的形态库 (Shark 已回测禁用)
PATTERNS = {
    "Gartley": {
        "B/XA": (0.618, 0.618),
        "C/AB": (0.382, 0.886),
        "D/XA": (0.786, 0.786),
        "CD/BC": (1.272, 1.618)
    },
    "Bat": {
        "B/XA": (0.382, 0.50),
        "C/AB": (0.382, 0.886),
        "D/XA": (0.886, 0.886),
        "CD/BC": (1.618, 2.618)
    },
    "Butterfly": {
        "B/XA": (0.786, 0.786),
        "C/AB": (0.382, 0.886),
        "D/XA": (1.272, 1.618),
        "CD/BC": (1.618, 2.24)
    },
    "Crab": {
        "B/XA": (0.382, 0.618),
        "C/AB": (0.382, 0.886),
        "D/XA": (1.618, 1.618),
        "CD/BC": (2.24, 3.618)
    },
    "DeepCrab": {
        "B/XA": (0.886, 0.886),
        "C/AB": (0.382, 0.886),
        "D/XA": (1.618, 1.618),
        "CD/BC": (2.0, 3.618)
    }
}


@dataclass
class HarmonicSignal:
    """和谐形态信号"""
    pattern: str
    direction: str  # bullish, bearish
    prz: Tuple[float, float]
    entry_price: float
    stop_loss: float
    tp1: float
    tp2: float
    rr_tp1: float
    rr_tp2: float
    grade: str  # A, B, C
    ratios: dict
    grade_score: float  # PRZ汇聚度百分比


def _in_range(ratio: float, lo: float, hi: float, tol: float) -> bool:
    """检查比率是否在范围内"""
    return lo * (1 - tol) <= ratio <= hi * (1 + tol)


def zigzag(df: pd.DataFrame, pct: float = 0.03) -> pd.DataFrame:
    """
    基于百分比反转阈值的 ZigZag

    Args:
        df: K线数据
        pct: 反转确认阈值

    Returns:
        DataFrame with ['idx', 'price', 'type']
    """
    highs, lows = df["high"].values, df["low"].values
    n = len(df)

    if n < 6:
        return pd.DataFrame(columns=["idx", "price", "type"])

    pivots = []
    trend = None
    ext_idx, ext_price = 0, df["close"].iloc[0]

    for i in range(1, n):
        h, l = highs[i], lows[i]

        if trend is None:
            if h >= ext_price * (1 + pct):
                pivots.append((ext_idx, ext_price, "L"))
                trend, ext_idx, ext_price = "up", i, h
            elif l <= ext_price * (1 - pct):
                pivots.append((ext_idx, ext_price, "H"))
                trend, ext_idx, ext_price = "down", i, l
            else:
                if l < ext_price:
                    ext_idx, ext_price = i, l
        elif trend == "up":
            if h >= ext_price:
                ext_idx, ext_price = i, h
            elif l <= ext_price * (1 - pct):
                pivots.append((ext_idx, ext_price, "H"))
                trend, ext_idx, ext_price = "down", i, l
        else:
            if l <= ext_price:
                ext_idx, ext_price = i, l
            elif h >= ext_price * (1 + pct):
                pivots.append((ext_idx, ext_price, "L"))
                trend, ext_idx, ext_price = "up", i, h

    if trend == "up":
        pivots.append((ext_idx, ext_price, "H"))
    elif trend == "down":
        pivots.append((ext_idx, ext_price, "L"))

    zz = pd.DataFrame(pivots, columns=["idx", "price", "type"])
    zz = zz[zz["type"] != zz["type"].shift()].reset_index(drop=True)
    return zz


def validate_pattern(X, A, B, C, D, name: str, tol: float = DEFAULT_TOL) -> Optional[dict]:
    """
    验证五点位是否构成和谐形态

    Args:
        X, A, B, C, D: (idx, price) 元组
        name: 形态名
        tol: 容差

    Returns:
        dict or None
    """
    if name not in PATTERNS:
        return None

    spec = PATTERNS[name]
    xp, ap, bp, cp, dp = X[1], A[1], B[1], C[1], D[1]

    bullish = ap > xp
    xa = abs(ap - xp)
    ab = abs(bp - ap)
    bc = abs(cp - bp)
    cd = abs(dp - cp)

    if xa == 0 or ab == 0 or bc == 0:
        return None

    # 方向结构校验
    if bullish and not (bp < ap and cp > bp and dp < cp):
        return None
    if not bullish and not (bp > ap and cp < bp and dp > cp):
        return None

    r_BXA = ab / xa
    r_CAB = bc / ab
    r_DXA = abs(ap - dp) / xa
    r_CDBC = cd / bc

    if not _in_range(r_BXA, *spec["B/XA"], tol):
        return None
    if not _in_range(r_CAB, *spec["C/AB"], tol):
        return None
    if not _in_range(r_DXA, *spec["D/XA"], tol):
        return None
    if not _in_range(r_CDBC, *spec["CD/BC"], tol):
        return None

    # PRZ 计算
    if bullish:
        m1 = [ap - xa * spec["D/XA"][0], ap - xa * spec["D/XA"][1]]
        m2 = [cp - bc * spec["CD/BC"][1], cp - bc * spec["CD/BC"][0]]
    else:
        m1 = [ap + xa * spec["D/XA"][0], ap + xa * spec["D/XA"][1]]
        m2 = [cp + bc * spec["CD/BC"][0], cp + bc * spec["CD/BC"][1]]

    prz_lo = max(min(m1), min(m2))
    prz_hi = min(max(m1), max(m2))

    if prz_lo > prz_hi:
        prz_lo, prz_hi = min(min(m1), min(m2)), max(max(m1), max(m2))

    # 止损
    buf = 0.5 * xa * 0.1
    if bullish:
        stop = prz_lo - buf
        tp1 = dp + (ap - dp) * 0.382
        tp2 = dp + (ap - dp) * 0.618
    else:
        stop = prz_hi + buf
        tp1 = dp - (dp - ap) * 0.382
        tp2 = dp - (dp - ap) * 0.618

    risk = abs(dp - stop)

    return {
        "pattern": name,
        "direction": "bullish" if bullish else "bearish",
        "ratios": {
            "B/XA": round(r_BXA, 3),
            "C/AB": round(r_CAB, 3),
            "D/XA": round(r_DXA, 3),
            "CD/BC": round(r_CDBC, 3)
        },
        "PRZ": (round(prz_lo, 4), round(prz_hi, 4)),
        "entry_ref": dp,
        "stop": round(stop, 4),
        "tp1": round(tp1, 4),
        "tp2": round(tp2, 4),
        "rr_tp1": round(abs(tp1 - dp) / risk, 2) if risk else None,
        "rr_tp2": round(abs(tp2 - dp) / risk, 2) if risk else None
    }


def scan(df: pd.DataFrame, zz_pct: float = 0.03, tol: float = DEFAULT_TOL,
         patterns: List[str] = None, only_latest: bool = True) -> List[dict]:
    """
    扫描和谐形态

    Args:
        df: K线数据
        zz_pct: ZigZag 反转阈值
        tol: 形态容差
        patterns: 扫描的形态列表
        only_latest: 是否只返回最新D点信号

    Returns:
        信号列表
    """
    zz_pct = zz_pct if zz_pct else 0.03
    tol = tol if tol else DEFAULT_TOL

    zz = zigzag(df, pct=zz_pct)
    signals = []

    if len(zz) < 5:
        return signals

    names = patterns or list(PATTERNS.keys())
    pts = [(int(r.idx), float(r.price)) for r in zz.itertuples()]
    n = len(pts)
    start = n - 1 if only_latest else 4

    for i in range(start, n):
        X, A, B, C, D = pts[i - 4:i + 1]
        for name in names:
            if name not in PATTERNS:
                continue
            sig = validate_pattern(X, A, B, C, D, name, tol)
            if sig:
                signals.append(sig)

    return signals


def grade_signal(signal: dict, grade_a: float = 0.02,
                 grade_b: float = 0.04) -> str:
    """
    对信号进行分级

    Args:
        signal: 信号字典
        grade_a: A级阈值
        grade_b: B级阈值

    Returns:
        grade: A, B, or C
    """
    prz = signal.get("PRZ", (0, 0))
    if len(prz) != 2:
        return "C"

    center = (prz[0] + prz[1]) / 2
    width = prz[1] - prz[0]

    if center == 0:
        return "C"

    width_pct = width / center

    if width_pct < grade_a:
        return "A"
    elif width_pct < grade_b:
        return "B"
    else:
        return "C"


def calculate_stop_loss(entry: float, atr: float, direction: str,
                       atr_multiplier: float = 0.7,
                       prz_buffer: float = 0.005) -> float:
    """
    计算止损价格

    Args:
        entry: 入场价格
        atr: ATR值
        direction: bullish or bearish
        atr_multiplier: ATR倍数
        prz_buffer: PRZ缓冲比例

    Returns:
        止损价格
    """
    atr_stop = atr * atr_multiplier
    buffer_stop = entry * prz_buffer
    stop_distance = max(atr_stop, buffer_stop)

    if direction == "bullish":
        return round(entry - stop_distance, 4)
    else:
        return round(entry + stop_distance, 4)


def calculate_take_profits(entry: float, stop: float,
                          tp1_ratio: float = 0.382,
                          tp2_ratio: float = 0.618) -> Tuple[float, float]:
    """
    计算止盈价格

    Args:
        entry: 入场价格
        stop: 止损价格
        tp1_ratio: TP1比率
        tp2_ratio: TP2比率

    Returns:
        (tp1, tp2)
    """
    risk = abs(entry - stop)

    tp1 = round(entry + risk * tp1_ratio, 4)
    tp2 = round(entry + risk * tp2_ratio, 4)

    return tp1, tp2
