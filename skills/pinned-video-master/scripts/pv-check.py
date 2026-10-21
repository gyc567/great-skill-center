#!/usr/bin/env python3
"""pv-check.py — 置顶视频档案与脚本体检工具

用法:
  python3 pv-check.py --dossier pinned-dossier.md --stage pre-generate
  python3 pv-check.py --script script.txt --stage script
  python3 pv-check.py --dossier pinned-dossier.md --script script.txt --stage full

检查项:
  - 档案六模块完整性
  - 脚本字数 / 词数上限
  - 五段结构完整性
  - 钩子是否为自我介绍式开场
  - 浮夸词检测
  - 绝对化用语检测
  - 数字是否可在档案 proof 中找到出处
退出码: 0 = 全部通过, 1 = 有阻塞项
"""

import argparse
import os
import re
import sys

MODULES = ["identity", "history", "current", "offering", "proof", "presence"]
SECTION_KEYS = ["钩子", "身份", "背书", "现状", "价值"]
SECTION_KEYS_EN = ["Hook", "Identity", "Proof", "Now", "Value"]

BOILERPLATE_HOOKS = [
    "大家好", "很高兴认识", "hello everyone", "hi everyone", "hey guys",
    "欢迎来到", "welcome to", "self-introduction",
]
HYPE_WORDS = [
    "震惊", "惊呆", "必看", "99%", "99％", "所有人都", "绝对", "史上最",
    "shocking", "everyone must", "guaranteed", "no one tells",
]
ABSOLUTE_WORDS = [
    "最好的", "第一", "唯一", "最专业", "国家级", "顶级",
    "best in", "the only", "number one", "world-class",
]
CTA_HINTS = ["关注", "私信", "评论", "留言", "找我", "联系我", "清单",
             "follow", "dm me", "comment", "reach out", "guide"]


def read(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return f.read()


def parse_dossier(text):
    """解析档案，返回 {module: content} 与 frontmatter 状态。"""
    if text is None:
        return {}, {}
    fm = {}
    body = text
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end > 0:
            raw = text[3:end]
            body = text[end + 4:]
            for line in raw.splitlines():
                if ":" in line:
                    k, _, v = line.partition(":")
                    fm[k.strip()] = v.strip().strip("\"'")
    mods = {}
    current = None
    buf = []
    for line in body.splitlines():
        m = re.match(r"^##\s+([a-z]+)\s*(（.*?）)?\s*$", line)
        if m and m.group(1) in MODULES:
            if current:
                mods[current] = "\n".join(buf).strip()
            current = m.group(1)
            buf = []
        elif current:
            buf.append(line)
    if current:
        mods[current] = "\n".join(buf).strip()
    return mods, fm


def strip_non_speech(text):
    """从脚本文本中抽出可读的口播内容。

    支持两种格式：
      1) 表格行  | 钩子 | 0-3s | 台词... | 字数 |  → 取除首列(段名)与末列(字数)外的单元格
      2) 纯文本行 → 直接使用
    去掉标题、模板提示行。
    """
    lines = []
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#"):
            continue
        if s.startswith(">"):
            continue
        if s.startswith("|"):
            # 表格行
            cells = [c.strip() for c in s.strip("|").split("|")]
            cells = [c for c in cells if c]
            if not cells:
                continue
            # 表头 / 分隔行
            if all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                continue
            if any(re.search(r"(台词|画面|字幕|字���|词数|word|时间|依据|来源|Source)", c, re.I) for c in cells):
                continue
            # 去掉首列段名与末列字数统计
            if len(cells) >= 2 and re.fullmatch(r"[\d/.\s]*", cells[-1]):
                cells = cells[:-1]
            if len(cells) >= 2 and re.search(
                    r"(钩子|身份|背书|现状|价值|Hook|Identity|Proof|Now|Value)", cells[0], re.I):
                cells = cells[1:]
            for c in cells:
                c = re.sub(r"^\*+|\*+$", "", c).strip()
                if c and not re.fullmatch(r"[\d/.\s%]*", c):
                    lines.append(c)
            continue
        # 纯文本行
        if re.match(r"^[-*]\s*[-*]\s*$", s):
            continue
        if re.search(r"(字数|word count|上限|依据|来源|Source|avatar_id|voice_id|dimension|speed|language)\s*[:：]?", s, re.I):
            continue
        if s in {"中文", "英文", "English", "English Version", "中文版"}:
            continue
        s = re.sub(r"^\*+|\*+$", "", s).strip()
        if s:
            lines.append(s)
    return "\n".join(lines)


def count_cn_chars(text):
    """中文口播字数：汉字 + 中文标点（标点不计入停顿）。"""
    t = re.sub(r"[\s]", "", text)
    han = re.findall(r"[\u4e00-\u9fff]", t)
    return len(han)


def count_en_words(text):
    return len(re.findall(r"[A-Za-z']+", text))


def check_dossier(mods, fm, issues):
    status = fm.get("status", "unknown")
    if status == "in_progress":
        issues.append(("BLOCK", "档案状态为 in_progress", "先完成建档（task-intake.md）"))
    missing = []
    empty = []
    for mod in MODULES:
        if mod not in mods:
            missing.append(mod)
        else:
            content = mods[mod]
            filled = [
                l for l in content.splitlines()
                if l.strip() and not l.strip().startswith(">") and l.strip() != "-"
            ]
            if not filled or all("待补" in l for l in filled):
                empty.append(mod)
    if missing:
        issues.append(("BLOCK", f"档案缺少模块: {', '.join(missing)}", "补齐档案结构"))
    if empty:
        issues.append(("WARN", f"档案模块为空/待补: {', '.join(empty)}",
                       "空模块对应段落必须留白或改用过程描述，不得编造"))
    return status


def check_script(text, mods, issues):
    if text is None:
        issues.append(("BLOCK", "未提供脚本文本", "先产出逐字稿"))
        return {}

    body = strip_non_speech(text)
    zh_len = count_cn_chars(body)
    en_words = count_en_words(body)
    stats = {"zh_chars": zh_len, "en_words": en_words}

    # 结构检查
    present = [k for k in SECTION_KEYS if k in text] + \
              [k for k in SECTION_KEYS_EN if k in text]
    if len(present) < 5:
        issues.append(("WARN", f"脚本段落不完整（识别到 {len(present)}/5 段）",
                       "按钩子/身份/背书/现状/价值 五段输出"))

    # 钩子
    first_lines = [l.strip() for l in text.splitlines() if l.strip()][:12]
    joined = " ".join(first_lines).lower()
    for bp in BOILERPLATE_HOOKS:
        if bp in joined:
            issues.append(("BLOCK", f"钩子含自我介绍式开场「{bp}」",
                           "钩子必须指向人群或反常识"))
            break

    # 浮夸词
    for w in HYPE_WORDS:
        if w.lower() in joined:
            issues.append(("WARN", f"脚本含浮夸词「{w}」", "删除或换成具体事实"))
            break

    # 绝对化
    for w in ABSOLUTE_WORDS:
        if w.lower() in text.lower():
            issues.append(("WARN", f"脚本含绝对化用语「{w}」", "改成有边界的表述"))
            break

    # CTA
    if not any(c in text.lower() for c in CTA_HINTS):
        issues.append(("WARN", "未检测到明确 CTA", "结尾补一句具体动作"))

    # 数字溯源：年份(19xx/20xx)与结构数字不算业务数据；
    # 溯源范围 = proof + history + current + offering（任何提到该数字的档案段落都可作出处）
    source_text = " ".join(mods.get(k, "") for k in ("proof", "history", "current", "offering"))
    source_nums = set(re.findall(r"\d+", source_text))
    body_nums = set(re.findall(r"\d+", body))
    ignore = {"30", "3", "5", "8", "20", "27"}
    unsourced = sorted(
        n for n in body_nums
        if n not in source_nums
        and n not in ignore
        and n != "0"                                   # 分段时间轴里的 0
        and not re.fullmatch(r"(19|20)\d{2}", n)        # 年份
    )
    if unsourced:
        issues.append(("WARN", f"数字在档案中找不到出处: {', '.join(unsourced[:6])}",
                       "核实数字来源；档案无出处则从脚本移除"))

    # 字数
    if zh_len > 90:
        issues.append(("WARN", f"中文字数 {zh_len} 超出 90 字上限", "删字，不要加时长"))
    if en_words > 75:
        issues.append(("WARN", f"英文词数 {en_words} 超出 75 词上限", "删词，不要加时长"))

    return stats


def main():
    ap = argparse.ArgumentParser(description="置顶视频档案与脚本体检")
    ap.add_argument("--dossier")
    ap.add_argument("--script")
    ap.add_argument("--stage", default="full",
                    choices=["dossier", "script", "full", "pre-generate"])
    args = ap.parse_args()

    dossier_text = read(args.dossier) if args.dossier else None
    script_text = read(args.script) if args.script else None

    if args.dossier and dossier_text is None:
        print(f"[FAIL] 找不到档案文件: {args.dossier}")
        return 1

    mods, fm = parse_dossier(dossier_text) if dossier_text else ({}, {})
    issues = []
    stats = {}

    if args.stage in ("dossier", "full", "pre-generate"):
        if dossier_text is None:
            issues.append(("BLOCK", "未提供档案路径", "加 --dossier"))
        else:
            check_dossier(mods, fm, issues)

    if args.stage in ("script", "full", "pre-generate"):
        if script_text is None:
            issues.append(("BLOCK", "未提供脚本路径", "加 --script"))
        else:
            stats = check_script(script_text, mods, issues)

    # 输出
    print("=" * 56)
    print("置顶视频体检报告")
    print("=" * 56)
    if stats:
        print(f"中文字数: {stats.get('zh_chars', 0)} / 90")
        print(f"英文词数: {stats.get('en_words', 0)} / 75")
        print("-" * 56)

    blocks = [i for i in issues if i[0] == "BLOCK"]
    warns = [i for i in issues if i[0] == "WARN"]

    if not issues:
        print("✅ 全部通过，可以进入下一步。")
    else:
        for lvl, msg, fix in blocks:
            print(f"[阻塞] {msg}\n        → {fix}")
        for lvl, msg, fix in warns:
            print(f"[提醒] {msg}\n        → {fix}")

    print("-" * 56)
    print(f"阻塞 {len(blocks)} 项 / 提醒 {len(warns)} 项")
    if args.stage == "pre-generate" and blocks:
        print("结论：暂不可生成成片。")
        return 1
    print("结论：可继续。" if not blocks else "结论：需先解决阻塞项。")
    return 1 if blocks else 0


if __name__ == "__main__":
    sys.exit(main())
