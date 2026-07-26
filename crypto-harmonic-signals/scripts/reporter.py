"""报告生成器"""
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

from .scanner import ScanResult


@dataclass
class SignalReport:
    """信号报告"""
    timestamp: datetime
    round_num: int
    total_symbols: int
    valid_signals: int
    results: List[ScanResult]


class Reporter:
    """Markdown 报告生成器"""

    @staticmethod
    def format_direction_emoji(direction: str) -> str:
        """方向emoji"""
        return "🟢" if direction == "bullish" else "🔴"

    @staticmethod
    def format_status_emoji(status: str) -> str:
        """状态emoji"""
        if status == "oversold":
            return "✅"
        elif status == "overbought":
            return "⚠️"
        return "⚪"

    @staticmethod
    def format_trend_status(trend: str) -> str:
        """趋势状态"""
        if trend == "bullish":
            return "✅ EMA200 多头"
        elif trend == "bearish":
            return "🔴 EMA200 空头"
        return "⚪ 趋势不明"

    @staticmethod
    def format_rsi_status(rsi_status: str, rsi_value: float) -> str:
        """RSI状态"""
        if rsi_status == "oversold":
            return f"✅ RSI {rsi_value:.1f} (超卖)"
        elif rsi_status == "overbought":
            return f"⚠️ RSI {rsi_value:.1f} (超买)"
        return f"⚪ RSI {rsi_value:.1f} (中性)"

    def generate_signal_table(self, result: ScanResult) -> str:
        """生成单个信号表格"""
        if not result.signal:
            return ""

        sig = result.signal
        direction = sig["direction"]

        grade_emoji = "🟢" if sig["grade"] == "A" else ("🟡" if sig["grade"] == "B" else "🔴")

        lines = [
            f"| 项目 | 数值 |",
            f"|------|------|",
            f"| 形态 | {sig['pattern']} ({direction}) |",
            f"| 方向 | {self.format_direction_emoji(direction)} {'做多' if direction == 'bullish' else '做空'} |",
            f"| 风险等级 | {grade_emoji} {sig['grade']}级 |",
            f"| PRZ 区间 | {sig['prz'][0]:,.2f} - {sig['prz'][1]:,.2f} |",
            f"| 入场价格 | {sig['entry_price']:,.2f} |",
            f"| 止损价格 | {sig['stop_loss']:,.2f} |",
            f"| 止盈1 | {sig['tp1']:,.2f} (RR 1:{sig['rr_tp1']}) |",
            f"| 止盈2 | {sig['tp2']:,.2f} (RR 1:{sig['rr_tp2']}) |",
        ]

        return "\n".join(lines)

    def generate_summary_section(self, result: ScanResult) -> str:
        """生成摘要部分"""
        if not result.trend or not result.rsi:
            return ""

        trend_dir = result.trend.get("direction", "unknown")
        trend_dev = result.trend.get("deviation", 0)
        rsi_val = result.rsi.get("value", 0)
        rsi_status = result.rsi.get("status", "neutral")

        lines = [
            f"| 趋势状态 | {self.format_trend_status(trend_dir)} (偏离 {trend_dev:+.1f}%) |",
            f"| RSI 状态 | {self.format_rsi_status(rsi_status, rsi_val)} |",
        ]

        return "\n".join(lines)

    def generate_invalid_section(self, result: ScanResult) -> str:
        """生成无效信号原因"""
        if result.is_valid:
            return ""

        lines = [
            f"| 原因 | {', '.join(result.notes)} |",
        ]

        return "\n".join(lines)

    def generate_markdown_report(self, report: SignalReport,
                               include_invalid: bool = False) -> str:
        """
        生成 Markdown 报告

        Args:
            report: SignalReport
            include_invalid: 是否包含无效信号

        Returns:
            Markdown 格式报告
        """
        valid_results = [r for r in report.results if r.is_valid and r.signal]
        invalid_results = [r for r in report.results if not r.is_valid]

        lines = [
            "# 🔔 加密货币和谐形态信号报告",
            "",
            f"**扫描时间**: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')} UTC+8",
            f"**扫描轮次**: 第 {report.round_num}/3 轮",
            f"**扫描品种**: {report.total_symbols} 个",
            f"**有效信号**: {report.valid_signals} 个",
            "",
            "---",
            ""
        ]

        # 有效信号
        if valid_results:
            lines.append("## ✅ 有效信号")
            lines.append("")

            for r in valid_results:
                emoji = self.format_direction_emoji(r.signal['direction'])
                lines.append(f"### {emoji} {r.symbol} | {r.signal['pattern']} | {r.signal['grade']}级")
                lines.append("")
                lines.append(self.generate_summary_section(r))
                lines.append("")
                lines.append(self.generate_signal_table(r))
                lines.append("")
                lines.append("---")
                lines.append("")

        # 无效信号
        if include_invalid and invalid_results:
            lines.append("## ⚠️ 未通过筛选")
            lines.append("")

            for r in invalid_results:
                lines.append(f"### ⚪ {r.symbol}")
                lines.append("")
                lines.append(self.generate_invalid_section(r))
                lines.append("")
                lines.append("---")
                lines.append("")

        return "\n".join(lines)

    def generate_telegram_message(self, result: ScanResult) -> Optional[str]:
        """
        生成 Telegram 消息

        Args:
            result: ScanResult

        Returns:
            Telegram 格式消息 or None
        """
        if not result.is_valid or not result.signal:
            return None

        sig = result.signal
        direction = sig["direction"]

        emoji = self.format_direction_emoji(direction)
        direction_cn = "做多" if direction == "bullish" else "做空"

        trend_emoji = "✅" if result.trend.get("direction") == direction else "⚠️"
        rsi_emoji = "✅" if (
            (direction == "bullish" and result.rsi.get("status") == "oversold") or
            (direction == "bearish" and result.rsi.get("status") == "overbought")
        ) else "⚠️"

        lines = [
            f"{emoji} [{result.exchange.upper()}] {result.symbol} | {direction_cn} | {sig['pattern']} {sig['grade']}级",
            "",
            f"📊 趋势: {result.trend.get('direction', 'unknown')} {trend_emoji}",
            f"📉 RSI: {result.rsi.get('value', 0):.1f} ({result.rsi.get('status', 'neutral')}) {rsi_emoji}",
            "",
            f"🎯 入场: {sig['entry_price']:,.2f}",
            f"🛑 止损: {sig['stop_loss']:,.2f}",
            f"🏁 TP1: {sig['tp1']:,.2f} (RR 1:{sig['rr_tp1']}) → 平50%",
            f"🏁 TP2: {sig['tp2']:,.2f} (RR 1:{sig['rr_tp2']}) → 全平",
            "",
            f"⏰ {result.timestamp.strftime('%Y-%m-%d %H:%M')}",
        ]

        return "\n".join(lines)


def create_report(results: List[ScanResult], round_num: int = 1) -> SignalReport:
    """创建报告"""
    valid_count = len([r for r in results if r.is_valid and r.signal])

    return SignalReport(
        timestamp=datetime.now(),
        round_num=round_num,
        total_symbols=len(results),
        valid_signals=valid_count,
        results=results
    )
