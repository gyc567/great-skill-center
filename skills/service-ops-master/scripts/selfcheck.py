#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
service-ops-master 自检脚本
校验 Skill 的完整性：frontmatter、26 项权益、话术库模板、ERIC 联系方式、关键数据。

用法：
    python3 scripts/selfcheck.py
    python3 scripts/selfcheck.py /path/to/service-ops-master
"""

import os
import re
import sys

SKILL_NAME = "service-ops-master"
AUTHOR = "ERIC"
BRAND = "AI Skills 创作小店"

# ERIC 联系方式（任一缺失即失败）
CONTACT_KEYS = {
    "邮箱": "gyc567@gmail.com",
    "Twitter": "EricBlock2100",
    "微信": "360369487",
    "Telegram": "t.me/fatoshi_block",
    "TG频道": "t.me/cryptochanneleric",
    "TG群": "t.me/btcgogopen",
    "YouTube": "0XBitFinance",
    "博客": "topdigg.com",
}

# 26 项权益的关键锚点（抽查代表性条目）
BENEFIT_ANCHORS = [
    "汽美服务", "飞机、高铁接送", "代步车", "酒后代驾", "接送孩子",
    "试乘试驾", "道路免费救援", "换鲜花", "极致贴心保洁", "卫生保洁护理",
    "体检", "摄影师", "私人教练", "创意布置", "私人家宴",
    "电影票", "干洗衣物", "宠物美容", "网红餐厅", "医院帮忙排队",
    "应急药物", "跑腿服务", "礼品包装",
]

# 话术库必须覆盖的模板章节
SCRIPT_SECTIONS = [
    "需求诊断", "方案确认", "进度播报", "交付瞬间", "跟进",
    "关系维护", "转介绍", "被推荐人", "成交后", "危机",
    "服务人员话术", "助理话术", "IP 内容",
]

# 关键数据点（防止内容被误删）
KEY_FACTS = [
    "90%", "98%", "75.3", "9 名助理", "15 名保洁", "5 名摄影师",
    "不能收用户的红包", "不能喝用户家里的水", "不能上用户的洗手间",
    "保洁团队手册", "银耳汤", "每一个出水孔",
]


def read(path):
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def check(results, name, ok, detail=""):
    results.append((name, ok, detail))
    return ok


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    results = []

    # ---------- 1. 文件结构 ----------
    skill_md = os.path.join(root, "SKILL.md")
    readme = os.path.join(root, "README.md")
    ref_dir = os.path.join(root, "references")
    sop = os.path.join(ref_dir, "sop-playbook.md")
    scripts_lib = os.path.join(ref_dir, "scripts-library.md")
    archive = os.path.join(ref_dir, "source-archive.md")

    for label, p in [("SKILL.md", skill_md), ("README.md", readme),
                     ("references/sop-playbook.md", sop),
                     ("references/scripts-library.md", scripts_lib),
                     ("references/source-archive.md", archive)]:
        check(results, f"文件存在: {label}", os.path.exists(p), p)

    skill = read(skill_md)
    readme_txt = read(readme)
    sop_txt = read(sop)
    lib_txt = read(scripts_lib)
    arc_txt = read(archive)

    # ---------- 2. frontmatter ----------
    fm_ok = skill.startswith("---")
    name_ok = f"name: {SKILL_NAME}" in skill
    brand_ok = BRAND in skill.split("---")[1] if fm_ok else False
    price_ok = "price: 3990" in skill
    author_ok = f"author: {AUTHOR}" in skill
    desc_ok = "description:" in skill and "极致服务" in skill
    for label, ok in [("frontmatter 分隔符", fm_ok), ("name 字段", name_ok),
                      ("brand 字段", brand_ok), ("price 字段(3990)", price_ok),
                      ("author 字段", author_ok), ("description 含触发词", desc_ok)]:
        check(results, f"SKILL.md {label}", ok)

    # ---------- 3. 26 项权益 ----------
    for anchor in BENEFIT_ANCHORS:
        check(results, f"权益含: {anchor}", anchor in skill or anchor in sop)

    # ---------- 4. 话术库章节 ----------
    for sec in SCRIPT_SECTIONS:
        check(results, f"话术库章节: {sec}", sec in lib_txt)

    # ---------- 5. 原话摘录保留 ----------
    for quote in ["同行都没有做的才算是服务", "和客户见面是一种耻辱",
                  "用得上或用不上是他的问题", "人的情绪是底层的操作系统",
                  "我们就把用户定义成用户了", "超级销售"]:
        check(results, f"原话保留: {quote[:14]}", quote in lib_txt or quote in skill)

    # ---------- 6. 关键数据 ----------
    for fact in KEY_FACTS:
        check(results, f"关键数据: {fact}", fact in skill or fact in sop or fact in arc_txt)

    # ---------- 7. ERIC 联系方式（每个 md 都要有） ----------
    md_files = [skill_md, readme, sop, scripts_lib, archive]
    for p in md_files:
        txt = read(p)
        missing = [k for k, v in CONTACT_KEYS.items() if v not in txt]
        check(results, f"联系方式完整: {os.path.basename(p)}",
              not missing, ("缺: " + ",".join(missing)) if missing else "")

    # ---------- 8. 品牌 ----------
    for p in md_files:
        txt = read(p)
        check(results, f"品牌名: {os.path.basename(p)}", BRAND in txt)

    # ---------- 9. 定制开发声明 ----------
    check(results, "README 含定制开发声明", "定制开发" in readme_txt)
    check(results, "README 含免费声明", "免费提供" in readme_txt)

    # ---------- 10. 版权/来源标注 ----------
    for p in [skill_md, readme, archive]:
        txt = read(p)
        check(results, f"来源标注: {os.path.basename(p)}",
              ("见实" in txt or "老纪" in txt or "豪车毒" in txt))

    # ---------- 输出 ----------
    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    failed = [(n, d) for n, ok, d in results if not ok]

    print("=" * 62)
    print(f"  service-ops-master 自检")
    print("=" * 62)
    print(f"  通过 {passed}/{total}")
    if failed:
        print("-" * 62)
        print("  未通过：")
        for n, d in failed:
            print(f"   ✗ {n}" + (f"  ({d})" if d else ""))
    print("=" * 62)
    print("  ✅ 全部通过" if not failed else f"  ❌ {len(failed)} 项未通过")
    print("=" * 62)
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
