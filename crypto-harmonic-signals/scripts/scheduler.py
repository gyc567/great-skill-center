"""定时任务调度器"""
import time
import threading
from datetime import datetime, time as dtime
from typing import List, Callable, Optional
from dataclasses import dataclass

from .scanner import Scanner
from .reporter import Reporter, create_report
from .alerter import TelegramAlerter
from .config import Config


@dataclass
class ScheduleEntry:
    """调度条目"""
    time_str: str  # "HH:MM"
    last_run: Optional[datetime] = None


class Scheduler:
    """定时调度器"""

    def __init__(self, config: Config = None,
                 scanner: Scanner = None,
                 alerter: TelegramAlerter = None):
        self.config = config or Config()
        self.scanner = scanner or Scanner(self.config)
        self.alerter = alerter
        self.reporter = Reporter()

        self.schedule: List[ScheduleEntry] = [
            ScheduleEntry(t) for t in self.config.schedule.times
        ]
        self.round_index = 0

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def _parse_time(self, time_str: str) -> dtime:
        """解析时间字符串"""
        parts = time_str.split(":")
        return dtime(int(parts[0]), int(parts[1]))

    def _should_run(self, entry: ScheduleEntry) -> bool:
        """检查是否应该运行"""
        if entry.last_run is None:
            return True

        now = datetime.now()
        today_target = self._parse_time(entry.time_str)

        # 今天已经运行过
        if entry.last_run.date() == now.date():
            return False

        # 检查是否到时间
        current_time = now.time()
        return current_time >= today_target

    def _run_scan(self, round_num: int):
        """执行扫描"""
        with self._lock:
            print(f"[{datetime.now()}] 开始第 {round_num} 轮扫描...")

            results = self.scanner.scan_all()
            valid_signals = self.scanner.get_valid_signals(results)

            print(f"  扫描完成: {len(valid_signals)}/{len(results)} 个有效信号")

            # 生成报告
            report = create_report(results, round_num)
            report_md = self.reporter.generate_markdown_report(report)
            print(f"  报告:\n{report_md[:500]}...")

            # 发送通知
            if self.alerter and self.alerter.is_configured():
                sent = self.alerter.send_report(valid_signals, round_num)
                print(f"  推送完成: {sent} 条")

            return report

    def _loop(self):
        """主循环"""
        while self._running:
            now = datetime.now()

            for i, entry in enumerate(self.schedule):
                if self._should_run(entry):
                    entry.last_run = now
                    self.round_index = i + 1
                    self._run_scan(self.round_index)

            # 每分钟检查一次
            time.sleep(60)

    def start(self, blocking: bool = True):
        """
        启动调度器

        Args:
            blocking: 是否阻塞
        """
        if self._running:
            return

        self._running = True
        print(f"[Scheduler] 启动，调度时间: {[e.time_str for e in self.schedule]}")

        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

        if blocking:
            try:
                while self._running:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stop()

    def stop(self):
        """停止调度器"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        print("[Scheduler] 停止")

    def run_once(self) -> dict:
        """
        执行一次扫描（用于手动触发）

        Returns:
            扫描结果摘要
        """
        with self._lock:
            self.round_index = (self.round_index % 3) + 1
            results = self.scanner.scan_all()
            summary = self.scanner.get_summary(results)

            if self.alerter and self.alerter.is_configured():
                valid = self.scanner.get_valid_signals(results)
                self.alerter.send_report(valid, self.round_index)

            return summary


def run_scheduler(config: Config = None,
                  bot_token: str = "",
                  chat_id: str = "",
                  blocking: bool = True):
    """
    运行调度器

    Args:
        config: 配置
        bot_token: Telegram Bot Token
        chat_id: Telegram Chat ID
        blocking: 是否阻塞
    """
    from .alerter import AlerterFactory

    scanner = Scanner(config)
    alerter = AlerterFactory.create_telegram(bot_token, chat_id)

    scheduler = Scheduler(
        config=config,
        scanner=scanner,
        alerter=alerter
    )

    scheduler.start(blocking=blocking)
