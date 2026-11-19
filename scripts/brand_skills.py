#!/usr/bin/env python3
"""给安装到 great-skill-center 的第三方 Skill 加品牌横幅与联系方式。

原则（遵循 PROJECT_RULES.md）：
  * **不改动**运行时标识 —— 目录名、CLI 命令、包名、API 端点、协议标识一律保留；
  * **保留**上游作者署名 —— MIT / Apache-2.0 要求；
  * 只在用户可见的文档入口加我们的品牌横幅和 ERIC 联系方式。

用法：
    python3 scripts/brand_skills.py skills/<name> [...] [--dry-run]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

BRAND = "AI Skills 创作小店"

BANNER = f"""> **{BRAND}** 整理版 · 上游项目经许可保留原署名与许可证
>
> 本 Skill 由 {BRAND} 收录整理，能力方向来自上游开源项目。
> 运行时命令、工具名、路径与协议标识均保持原样以确保可用性。
"""

CONTACT = f"""
---

## 定制化开发

如需定制化开发，可直接联系 ERIC：

- **ERIC AI 技术专家**，专注于人工智能和自动化工具的研究与应用
- 邮箱：`gyc567@gmail.com`
- Twitter：`@EricBlock2100`
- 微信：`360369487`
- Telegram：`https://t.me/fatoshi_block`
- Telegram 频道：`https://t.me/cryptochanneleric`
- 加密情报 TG 群：`https://t.me/btcgogopen`
- YouTube：`@0XBitFinance`
- 博客：`topdigg.com`
"""

# 这些文件是用户可见入口，需要品牌横幅
ENTRY_NAMES = ("README.md", "SKILL.md")

# 不能改的运行时标识（即便含上游品牌词）
RUNTIME_PATTERNS = (
    "higgsfield.ai",
    "api.higgsfield",
    "hyperframes",
    "HyperFrames",
    "@hyperframes/",
    "npx hyperframes",
    "bunx hyperframes",
    "higgsfield-",
    "higgsfield ",
)


def find_entries(root: Path) -> list[Path]:
    """收集一个 skill 目录下所有用户可见入口文件。"""
    entries: list[Path] = []
    for name in ENTRY_NAMES:
        candidate = root / name
        if candidate.is_file():
            entries.append(candidate)
    # 子 skill 目录里的 SKILL.md
    for skill_md in sorted(root.rglob("SKILL.md")):
        if ".git" in skill_md.parts:
            continue
        if skill_md.parent != root:
            entries.append(skill_md)
    return entries


def has_banner(text: str) -> bool:
    return BRAND in text


def apply_banner(path: Path) -> bool:
    """在文件顶部插入横幅。返回是否改动。"""
    text = path.read_text(encoding="utf-8")
    if has_banner(text):
        return False

    lines = text.split("\n")
    # README 从第一个标题开始；SKILL.md 要跳过 YAML frontmatter
    insert_at = 0
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                insert_at = i + 1
                break
        else:
            insert_at = 0
    else:
        # 跳过开头的标题行，插到标题之后
        for i, line in enumerate(lines):
            if line.startswith("#"):
                insert_at = i + 1
                break
        else:
            insert_at = 0

    block = ["", BANNER.rstrip(), ""]
    new_lines = lines[:insert_at] + block + lines[insert_at:]
    path.write_text("\n".join(new_lines), encoding="utf-8")
    return True


def apply_contact(path: Path) -> bool:
    """在文件末尾追加联系方式。返回是否改动。"""
    text = path.read_text(encoding="utf-8")
    if "gyc567@gmail.com" in text:
        return False
    path.write_text(text.rstrip() + "\n" + CONTACT, encoding="utf-8")
    return True


def brand_skill(root: Path, dry_run: bool = False) -> dict[str, int]:
    stats = {"files": 0, "banner": 0, "contact": 0}
    for entry in find_entries(root):
        stats["files"] += 1
        if dry_run:
            text = entry.read_text(encoding="utf-8")
            if not has_banner(text):
                stats["banner"] += 1
            if "gyc567@gmail.com" not in text:
                stats["contact"] += 1
            continue
        if apply_banner(entry):
            stats["banner"] += 1
        if apply_contact(entry):
            stats["contact"] += 1
    return stats


def main() -> int:
    parser = argparse.ArgumentParser(description="给第三方 Skill 加品牌横幅")
    parser.add_argument("paths", nargs="+", help="skill 目录")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    total = {"files": 0, "banner": 0, "contact": 0}
    for raw in args.paths:
        root = Path(raw)
        if not root.is_dir():
            print(f"跳过（不是目录）: {root}")
            continue
        stats = brand_skill(root, dry_run=args.dry_run)
        print(
            f"{root.name:<26} 入口 {stats['files']:>2} 个 | "
            f"新横幅 {stats['banner']:>2} | 新联系方式 {stats['contact']:>2}"
        )
        for key in total:
            total[key] += stats[key]

    print(
        f"\n合计：入口 {total['files']} 个 | 新横幅 {total['banner']} | "
        f"新联系方式 {total['contact']}"
    )
    if args.dry_run:
        print("（dry-run，未实际写入）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
