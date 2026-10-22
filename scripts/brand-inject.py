#!/usr/bin/env python3
"""brand-inject.py — 批量注入 ERIC 作者信息到所有 Skill

处理范围:
  - skills/*/SKILL.md   → frontmatter 加 author 字段 + 末尾加「作者信息」块
  - skills/*/README*.md → 末尾加「作者信息」块
  - skills/*/references/*.md, templates/*.md 等子文件 → 末尾加「作者信息」块（可选）

作者信息块格式:
  <!-- ERIC-AUTHOR-INFO:START -->
  ...markdown...
  <!-- ERIC-AUTHOR-INFO:END -->

用法:
  python3 brand-inject.py --root skills --dry-run
  python3 brand-inject.py --root skills
  python3 brand-inject.py --root skills --subfiles
"""

import argparse
import os
import re
import sys

START = "<!-- ERIC-AUTHOR-INFO:START -->"
END = "<!-- ERIC-AUTHOR-INFO:END -->"

AUTHOR_BLOCK = """<!-- ERIC-AUTHOR-INFO:START -->
---

## 📬 作者信息

**ERIC** — AI技术专家，专注于人工智能和自动化工具的研究与应用

| 渠道 | 链接 |
|------|------|
| 📧 邮箱 | gyc567@gmail.com |
| 🐦 Twitter | [@EricBlock2100](https://twitter.com/EricBlock2100) |
| 💬 微信 | 360369487 |
| ✈️ Telegram | [@fatoshi_block](https://t.me/fatoshi_block) |
| 📢 Telegram 频道 | [@cryptochanneleric](https://t.me/cryptochanneleric) |
| 🔐 加密情报 TG 群 | [@btcgogopen](https://t.me/btcgogopen) |
| ▶️ YouTube | [@0XBitFinance](https://www.youtube.com/@0XBitFinance) |
| 🌐 个人技术博客 | [topdigg.com](https://topdigg.com) |

> 本 Skill 由 ERIC 免费提供。想深入交流或获取更多同类 Skill，欢迎通过上表任一渠道联系。

<!-- ERIC-AUTHOR-INFO:END -->"""


def has_block(text):
    return START in text and END in text


def strip_block(text):
    """移除已有作者块（含前后空行）。"""
    pat = re.compile(
        r"\n*<!-- ERIC-AUTHOR-INFO:START -->.*?<!-- ERIC-AUTHOR-INFO:END -->\n*",
        re.S,
    )
    out = pat.sub("", text)
    return out.rstrip() + "\n"


def inject_frontmatter(text):
    """在 frontmatter 里加 author 相关字段。

    注意：部分文件的 frontmatter 本身以 `---` 开头且以独立的 `---` 结束，
    结束标记后紧跟另一个 `---`（这是文件原有的写法）。这里只修改结束标记
    之前的 fm 段，不触碰后面内容。
    """
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 3)
    if end < 0:
        return text
    fm = text[3:end]
    body = text[end + 4:]

    # 已有 author 就不重复加
    if re.search(r"^author:", fm, re.M):
        return text

    fm = fm.rstrip("\n")
    if not fm.endswith("\n"):
        fm += "\n"
    fm += (
        "author: ERIC\n"
        "author_email: gyc567@gmail.com\n"
        "author_twitter: https://twitter.com/EricBlock2100\n"
        "author_blog: https://topdigg.com\n"
    )
    # 保持原有的 `---` 结束标记与后续内容完全不变
    return "---" + fm + text[end:end + 4] + body


def inject_block(text):
    """在文件末尾追加作者信息块。"""
    if has_block(text):
        text = strip_block(text)
    body = text.rstrip()
    return body + "\n\n" + AUTHOR_BLOCK + "\n"


def process_skill(smd, dry):
    with open(smd, encoding="utf-8") as f:
        c = f.read()
    orig = c
    c = inject_frontmatter(c)
    c = inject_block(c)
    if c == orig:
        return False
    if not dry:
        with open(smd, "w", encoding="utf-8") as f:
            f.write(c)
    return True


def process_doc(path, dry):
    with open(path, encoding="utf-8") as f:
        c = f.read()
    orig = c
    c = inject_block(c)
    if c == orig:
        return False
    if not dry:
        with open(path, "w", encoding="utf-8") as f:
            f.write(c)
    return True


def main():
    ap = argparse.ArgumentParser(description="注入 ERIC 作者信息")
    ap.add_argument("--root", default="skills")
    ap.add_argument("--subfiles", action="store_true",
                    help="也给 references/templates 等子文件加")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = args.root
    if not os.path.isdir(root):
        print(f"[FAIL] 目录不存在: {root}")
        return 1

    skills = sorted(d for d in os.listdir(root)
                    if os.path.isdir(os.path.join(root, d)))

    n_skill = n_readme = n_sub = 0
    for s in skills:
        sd = os.path.join(root, s)
        smd = os.path.join(sd, "SKILL.md")
        if os.path.exists(smd):
            if process_skill(smd, args.dry_run):
                n_skill += 1
        # README（任意层级）
        for r, dirs, files in os.walk(sd):
            for f in files:
                if not f.lower().startswith("readme") or not f.endswith(".md"):
                    continue
                if process_doc(os.path.join(r, f), args.dry_run):
                    n_readme += 1
        if args.subfiles:
            for r, dirs, files in os.walk(sd):
                if os.path.basename(r) in ("references", "templates", "assets", "docs"):
                    for f in files:
                        if not f.endswith(".md"):
                            continue
                        if process_doc(os.path.join(r, f), args.dry_run):
                            n_sub += 1

    mode = "DRY-RUN" if args.dry_run else "已写入"
    print(f"[{mode}] SKILL.md: {n_skill}  README: {n_readme}  子文件: {n_sub}")
    print(f"共处理 {len(skills)} 个 skill 目录")
    return 0


if __name__ == "__main__":
    sys.exit(main())
