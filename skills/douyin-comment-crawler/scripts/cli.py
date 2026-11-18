#!/usr/bin/env python3
"""抖音评论抓取命令行入口。

示例::

    python scripts/cli.py --aweme-id 7633646113853104116 \\
        --cookie-file ~/.config/douyin-comments/cookie.txt \\
        --with-replies --output ./output

安全约定：
  * cookie 只从文件读取，不接受命令行明文参数，避免进入 shell history / ps 输出；
  * cookie 不会被打印、不会写入输出文件；
  * 输出目录默认只写 csv / json，不写 cookie。
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from douyin_client import (  # noqa: E402
    DouyinApiError,
    DouyinCommentClient,
    EmptyResponseError,
    load_cookie,
    to_csv_rows,
    to_json,
)

DEFAULT_COOKIE_PATH = os.path.expanduser(
    "~/.config/douyin-comments/cookie.txt"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="抓取抖音视频评论与二级评论",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例:\n"
            "  python scripts/cli.py --aweme-id 7633646113853104116 \\\n"
            "      --cookie-file ~/.config/douyin-comments/cookie.txt \\\n"
            "      --with-replies --output ./output\n"
        ),
    )
    parser.add_argument("--aweme-id", required=True, help="视频 ID（分享链接里的数字）")
    parser.add_argument(
        "--cookie-file",
        default=DEFAULT_COOKIE_PATH,
        help=f"cookie 文件路径（首行为完整 cookie 串），默认 {DEFAULT_COOKIE_PATH}",
    )
    parser.add_argument(
        "--with-replies",
        action="store_true",
        help="同时抓取二级评论",
    )
    parser.add_argument("--count", type=int, default=30, help="每页条数，默认 30")
    parser.add_argument(
        "--max-comments",
        type=int,
        default=None,
        help="最多抓取多少条一级评论（调试用）",
    )
    parser.add_argument(
        "--output",
        default="./output",
        help="输出目录，默认 ./output",
    )
    parser.add_argument(
        "--format",
        choices=["csv", "json", "both"],
        default="both",
        help="输出格式，默认 both",
    )
    parser.add_argument(
        "--timeout", type=float, default=30.0, help="单请求超时秒数，默认 30"
    )
    parser.add_argument(
        "--min-interval",
        type=float,
        default=0.8,
        help="两次请求最小间隔秒数，默认 0.8（调低易触发风控）",
    )
    parser.add_argument(
        "--quiet", action="store_true", help="只输出结果文件路径"
    )
    return parser


async def run(args: argparse.Namespace) -> int:
    cookie_path = Path(args.cookie_file).expanduser()
    if not cookie_path.exists():
        print(
            f"错误：找不到 cookie 文件 {cookie_path}\n"
            f"请先创建该文件，第一行写入浏览器里的完整 cookie 串。",
            file=sys.stderr,
        )
        return 2

    try:
        cookie = load_cookie(str(cookie_path))
    except (OSError, ValueError) as exc:
        print(f"错误：读取 cookie 失败 —— {exc}", file=sys.stderr)
        return 2

    out_dir = Path(args.output).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        async with DouyinCommentClient(
            cookie,
            timeout=args.timeout,
            min_interval=args.min_interval,
        ) as client:
            comments = await client.fetch_all(
                args.aweme_id,
                with_replies=args.with_replies,
                count=args.count,
                max_comments=args.max_comments,
            )
    except EmptyResponseError as exc:
        print(
            f"错误：抖音返回空响应 —— {exc}\n"
            "常见原因：cookie 过期，或 cookie 中缺少 ttwid。",
            file=sys.stderr,
        )
        return 3
    except DouyinApiError as exc:
        print(f"错误：抖音接口返回业务错误 —— {exc}", file=sys.stderr)
        return 3
    except (OSError, ValueError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1

    if not args.quiet:
        level1 = sum(1 for c in comments if c.level == 1)
        level2 = len(comments) - level1
        print(f"完成：一级评论 {level1} 条，二级评论 {level2} 条")

    written: list[str] = []
    if args.format in ("csv", "both"):
        csv_path = out_dir / f"comments_{args.aweme_id}.csv"
        rows = to_csv_rows(comments)
        if rows:
            with open(csv_path, "w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)
        else:
            csv_path.write_text("", encoding="utf-8")
        written.append(str(csv_path))

    if args.format in ("json", "both"):
        json_path = out_dir / f"comments_{args.aweme_id}.json"
        json_path.write_text(to_json(comments), encoding="utf-8")
        written.append(str(json_path))

    for path in written:
        print(path)
    return 0


def main() -> int:
    args = build_parser().parse_args()
    try:
        return asyncio.run(run(args))
    except KeyboardInterrupt:
        print("\n已中断", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
