"""Telegram 推送"""
import requests
from typing import Optional, List

from .scanner import ScanResult
from .reporter import Reporter


class TelegramAlerter:
    """Telegram 报警器"""

    def __init__(self, bot_token: str = "", chat_id: str = ""):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        self.reporter = Reporter()

    def is_configured(self) -> bool:
        """检查是否已配置"""
        return bool(self.bot_token and self.chat_id)

    def send_message(self, text: str, parse_mode: str = "Markdown") -> bool:
        """
        发送消息

        Args:
            text: 消息内容
            parse_mode: 解析模式

        Returns:
            是否成功
        """
        if not self.is_configured():
            return False

        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode
        }

        try:
            resp = requests.post(self.api_url, json=payload, timeout=10)
            return resp.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def send_signal(self, result: ScanResult) -> bool:
        """
        发送信号

        Args:
            result: ScanResult

        Returns:
            是否成功
        """
        message = self.reporter.generate_telegram_message(result)
        if not message:
            return False
        return self.send_message(message)

    def send_report(self, results: List[ScanResult], round_num: int = 1) -> int:
        """
        发送报告

        Args:
            results: ScanResult列表
            round_num: 扫描轮次

        Returns:
            发送成功的数量
        """
        sent_count = 0

        for r in results:
            if r.is_valid and r.signal:
                if self.send_signal(r):
                    sent_count += 1

        return sent_count

    def send_summary(self, total: int, valid: int, round_num: int) -> bool:
        """发送汇总消息"""
        message = (
            f"📊 扫描完成\n"
            f"轮次: 第 {round_num}/3 轮\n"
            f"有效信号: {valid}/{total}"
        )
        return self.send_message(message)


class AlerterFactory:
    """报警器工厂"""

    @staticmethod
    def create_telegram(bot_token: str = "", chat_id: str = "") -> TelegramAlerter:
        """创建 Telegram 报警器"""
        return TelegramAlerter(bot_token=bot_token, chat_id=chat_id)
