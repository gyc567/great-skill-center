#!/usr/bin/env python3
"""给 story-studio 加「AI Skills 创作小店」品牌横幅与 ERIC 联系方式。

严格遵守 PROJECT_RULES.md：
  * **不改**运行时标识 —— skill 名 `story-studio`、命令 `$story-studio`、
    数据目录 `~/.local/share/story-studio`、`%LOCALAPPDATA%\\story-studio`、
    临时目录前缀 `.story-studio-install-`、TTS uid `story-studio` 一律保留；
  * **不改**事实性上游来源 —— 作者 konlu、仓库地址、赞助信息、致谢段落；
  * 只改用户可见的标题与叙述文案，并在入口加品牌横幅 + 联系方式；
  * **不遮蔽**原许可声明 —— CC BY-NC-SA 4.0 必须原样保留，
    并显式追加「非商用」说明，不能让人误以为可以商业分发。

幂等：重复执行不会重复插入横幅。
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "skills" / "story-studio"

BRAND = "AI Skills 创作小店"

BANNER = f"""<!-- {BRAND} 分发版 -->
> 📦 本 Skill 由 **{BRAND}** 整理分发，版权归原作者 konlu 所有（CC BY-NC-SA 4.0）。
> 如需定制化开发，可直接联系 ERIC —— 邮箱 gyc567@gmail.com · 微信 360369487 · Telegram @fatoshi_block
"""

BANNER_MD = f"""> 📦 **本 Skill 由 {BRAND} 整理分发**，版权归原作者 konlu 所有。
> 许可：CC BY-NC-SA 4.0（署名-非商业性使用-相同方式共享），**仅供学习研究与非商业创作**。
> 如需定制化开发，可直接联系 ERIC —— 邮箱 gyc567@gmail.com · 微信 360369487 · Telegram @fatoshi_block
"""

# 用户可见文案：品牌前缀式替换。保留运行时标识。
TEXT_SUBS = [
    ("# 🎬 Story Studio · 故事工坊", f"# 🎬 {BRAND} · 故事工坊"),
    ("**Story Studio（故事工坊）**", f"**{BRAND} · 故事工坊**"),
    ("**Story Studio 把这一整套", f"**{BRAND} 把这一整套"),
    ("Story Studio 内置了两个完整", f"{BRAND} 内置了两个完整"),
    ("Story Studio 提供两条极其顺畅", f"{BRAND} 提供两条极其顺畅"),
    ("Story Studio 会直接生成", f"{BRAND} 会直接生成"),
    ("Story Studio 内部通过", f"{BRAND} 内部通过"),
    ("Story Studio 内置的启动器", f"{BRAND} 内置的启动器"),
    ("🎬 Story Studio · 故事工坊 一键安装器", f"🎬 {BRAND} · 故事工坊 一键安装器"),
]

# 运行时标识，必须原样保留
RUNTIME_MARKERS = [
    "story-studio",
    "$story-studio",
    ".local/share/story-studio",
    "%LOCALAPPDATA%\\story-studio",
    ".story-studio-install-",
]


def insert_after_frontmatter(text: str, block: str) -> str:
    """在 YAML frontmatter 之后插入横幅；没有 frontmatter 则插到最前。"""
    if block.strip() in text:
        return text
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            cut = end + len("\n---\n")
            return text[:cut] + "\n" + block + text[cut:]
    return block + "\n" + text


def main() -> int:
    if not ROOT.exists():
        print(f"未找到 {ROOT}", file=sys.stderr)
        return 1

    changed = []
    before: dict[str, str] = {}

    for rel in ("SKILL.md", "README.md"):
        path = ROOT / rel
        if not path.exists():
            continue
        original = path.read_text(encoding="utf-8")
        before[rel] = original
        text = original

        for old, new in TEXT_SUBS:
            text = text.replace(old, new)

        # 入口横幅
        block = BANNER_MD if rel == "SKILL.md" else BANNER
        text = insert_after_frontmatter(text, block)

        if text != original:
            path.write_text(text, encoding="utf-8")
            changed.append(rel)

    print(f"品牌化完成：{', '.join(changed) if changed else '无变化'}")

    # 校验：原本存在的运行时标识，改动后必须仍然存在
    for rel, original in before.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        missing = [m for m in RUNTIME_MARKERS if m in original and m not in text]
        if missing:
            print(f"❌ {rel} 丢失运行时标识：{missing}", file=sys.stderr)
            return 1
    print("✅ 运行时标识校验通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
