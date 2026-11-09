#!/usr/bin/env python3
"""FABE 话术校验器 —— 检查一段话术是否真正走完 F→A→B→E 四级递进。

设计目标：机械可验证，不依赖模型判断。凡是能用规则查出来的，
就不该让另一个模型（或人）凭感觉判断。

用法:
    python3 validate_fabe.py script.md
    python3 validate_fabe.py script.md --json
    python3 validate_fabe.py --demo          # 内置示例自检

退出码: 0 = 通过, 1 = 存在 FAIL
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

# --------------------------------------------------------------------------
# 证据类型词典 —— E 环节必须落到具体可出示的东西
# --------------------------------------------------------------------------
EVIDENCE_TYPES = {
    "检测报告": ("检测报告", "质检报告", "检验报告", "检测数据", "SGS", "CNAS", "第三方检测"),
    "测试报告": ("测试报告", "自检测试", "测试结果", "测试套件", "验收报告"),
    "案例": ("案例", "客户案例", "实测视频", "买家秀", "用户实测", "使用记录", "真实案例"),
    "凭证文件": ("保单", "合同", "条款", "协议", "证书", "发票", "保修卡", "说明书"),
    "数据表格": ("现金价值表", "价格表", "费率表", "参数表", "对照表", "数据表", "后台截图", "实测数据"),
    "演示": ("演示", "试用", "实测", "现场", "免费体验", "demo"),
    "评价": ("评价", "好评", "口碑", "评分", "认证", "获奖", "权威"),
    "对比": ("对比", "横向", "vs", "VS", "优于", "差距"),
    "公开背书": ("报道", "报道过", "上榜", "官方", "权威机构", "排行榜"),
}

# 受益词 —— B 环节要落到"客户本人"身上
BENEFIT_MARKERS = (
    # 第二人称
    "你", "您", "您家", "您能", "你可以", "你能", "咱们",
    # 直接指向客户/持有人
    "客户", "您和", "持有人", "投保人", "受益人", "家长", "孩子",
    # 变化量（省/少/免/降/提）
    "省", "少", "免", "不用", "无需", "降低", "减少", "提升", "增加",
    # 具体处境改善
    "更", "减轻", "缓解", "压力", "负担", "担心", "顾虑", "安心", "踏实",
    "自由", "灵活", "方便", "省心", "轻松", "体面", "从容",
)

# 优势词 —— A 环节讲"这特点能干什么"
ADVANTAGE_MARKERS = ("可以", "能够", "能", "支持", "实现", "做到", "相比", "比", "更", "无需", "不用", "自动", "一键", "一次", "同时")

# 纯客观特征词 —— 如果 A 里全是这些，说明只是把 F 重说了一遍
OBJECTIVE_TOKENS = ("材质", "尺寸", "重量", "容量", "电压", "功率", "型号", "品牌", "产地", "颜色", "厚度", "长度", "宽度", "配置", "参数", "规格")

# 反模式：把 E 说成"很专业""品质保证"这类空话
WEAK_EVIDENCE = ("品质保证", "质量保证", "优质服务", "专业团队", "值得信赖", "口碑好", "销量第一", "行业领先", "值得拥有", "品质卓越", "业界领先", "专业可靠")

# 反模式：空泛的 Benefit 开头
WEAK_BENEFIT_PREFIX = ("提升效率", "降低成本", "优化体验", "更高效", "更专注", "更有创造力", "赋能", "打造闭环", "全方位", "一体化")


@dataclass
class Line:
    """一段话术中的一个 F/A/B/E 单元。"""

    level: str           # F / A / B / E
    text: str
    line_no: int = 0
    issues: list[str] = field(default_factory=list)

    @property
    def tokens(self) -> set[str]:
        return set(re.findall(r"[一-鿿]{2,}", self.text))


def split_units(text: str) -> list[Line]:
    """把话术文本切成 F/A/B/E 单元。

    支持两种写法:
      1. 带标签:  "F: 这是增额终身寿险"  /  "F：..."  /  "**F** ..." /  "- **F** ..."
      2. 靠顺序: 连续四个非空段落按 F,A,B,E 顺序推断
    """
    raw = text.split("\n")
    labeled: list[Line] = []
    unlabeled: list[Line] = []

    for i, ln in enumerate(raw, 1):
        s = ln.strip()
        if not s:
            continue
        # 去掉 markdown 列表符号和加粗
        s2 = re.sub(r"^[-*+]\s+", "", s)
        s2 = s2.replace("**", "").replace("`", "").strip()
        m = re.match(r"^[FABE]\s*[:：.、\-]?\s*(.+)$", s2, re.I)
        if m and m.group(1).strip():
            labeled.append(Line(level=m.group(0)[0].upper(), text=m.group(1).strip(), line_no=i))
        elif s2 and not s2.startswith("#"):
            unlabeled.append(Line(level="", text=s2, line_no=i))

    if labeled:
        return labeled
    # 无标签：按出现顺序 F,A,B,E 推断（最多 4 个）
    order = ["F", "A", "B", "E"]
    for idx, u in enumerate(unlabeled[:4]):
        u.level = order[idx]
    return unlabeled[:4]


def check_fact_repetition(f: Line, a: Line) -> None:
    """检查 A 是否只是把 F 重说了一遍 —— 最常见的 F/A 混淆。"""
    ft, at = f.tokens, a.tokens
    if not ft or not at:
        return
    overlap = ft & at
    ratio = len(overlap) / len(at) if at else 0
    obj_hits = [t for t in OBJECTIVE_TOKENS if t in a.text]
    if ratio >= 0.5 and len(overlap) >= 2:
        a.issues.append(
            f"A 环节与 F 环节词重叠 {ratio:.0%}（{', '.join(sorted(overlap)[:4])}），"
            f"疑似把产品特征复述成优势 —— A 必须回答“这个特点能干什么”"
        )
    if obj_hits and not any(m in a.text for m in ADVANTAGE_MARKERS):
        a.issues.append(
            f"A 环节只有客观参数（{', '.join(obj_hits)}）没有能力描述 —— "
            f"“{a.text[:24]}”还在说“是什么”，应该改成“能做什么”"
        )


def check_benefit(b: Line, has_a: bool) -> None:
    """检查 B 是否真的落在客户身上。"""
    if not any(m in b.text for m in BENEFIT_MARKERS):
        b.issues.append(
            "B 环节没有出现客户视角的表述（你/您/省/少/免/不用…）—— "
            "Benefit 是“对我有什么好处”，不是继续说产品"
        )
    for w in WEAK_BENEFIT_PREFIX:
        if b.text.startswith(w):
            b.issues.append(
                f"B 环节以“{w}”开头 —— 这是最典型的 AI 空话，"
                f"要换成具体的、能被客户感知到的变化"
            )


def check_evidence(e: Line) -> None:
    """检查 E 是否落到可出示的实物证据。"""
    hits = [name for name, kws in EVIDENCE_TYPES.items() if any(k in e.text for k in kws)]
    if not hits:
        e.issues.append(
            "E 环节没有指出具体证据类型 —— 必须说清楚拿什么证明"
            "（检测报告 / 案例 / 保单条款 / 现金价值表 / 实测视频…）"
        )
    # 空话：每个词只报一次
    seen: set[str] = set()
    for w in WEAK_EVIDENCE:
        if w in e.text and w not in seen:
            seen.add(w)
            e.issues.append(f"E 环节出现空话“{w}” —— 换成可出示的具体材料")
    if re.search(r"(很多客户|不少用户|大家都说|客户普遍)", e.text) and not hits:
        e.issues.append("E 环节只有模糊的“很多客户”，没有可核验的证据")


def validate(text: str) -> dict:
    units = split_units(text)
    result = {
        "units": [],
        "checks": [],
        "pass": False,
    }

    levels = {u.level for u in units}
    # 检查 1: 四级齐全
    missing = [x for x in "FABE" if x not in levels]
    result["checks"].append({
        "name": "四级齐全",
        "ok": not missing,
        "detail": "缺少 " + "".join(missing) if missing else "F/A/B/E 四级齐全",
    })

    f = next((u for u in units if u.level == "F"), None)
    a = next((u for u in units if u.level == "A"), None)
    b = next((u for u in units if u.level == "B"), None)
    e = next((u for u in units if u.level == "E"), None)

    if f and a:
        check_fact_repetition(f, a)
    if b:
        check_benefit(b, bool(a))
    if e:
        check_evidence(e)

    # 检查 2: A 不复述 F
    a_bad = a and any("疑似把产品特征复述" in i or "只有客观参数" in i for i in a.issues)
    result["checks"].append({
        "name": "A 不复述 F",
        "ok": not a_bad,
        "detail": a.issues[0] if a_bad else "A 与 F 递进正常",
    })

    # 检查 3: B 落到客户
    b_bad = b and any("客户视角" in i or "空话" in i for i in b.issues)
    result["checks"].append({
        "name": "B 落到客户",
        "ok": not b_bad,
        "detail": b.issues[0] if b_bad else "B 表述指向客户收益",
    })

    # 检查 4: E 可出示
    e_bad = e and any("证据类型" in i or "空话" in i or "模糊" in i for i in e.issues)
    result["checks"].append({
        "name": "E 可出示",
        "ok": not e_bad,
        "detail": e.issues[0] if e_bad else "E 指向具体证据",
    })

    # 检查 5: 无空话
    allissues = [i for u in units for i in u.issues]
    result["checks"].append({
        "name": "无空话套话",
        "ok": not allissues,
        "detail": f"共 {len(allissues)} 处问题" if allissues else "未检出空话",
    })

    for u in units:
        result["units"].append({
            "level": u.level,
            "text": u.text,
            "line": u.line_no,
            "issues": u.issues,
        })

    result["pass"] = all(c["ok"] for c in result["checks"])
    result["issue_count"] = len(allissues)
    return result


DEMO = """- F：自带热风烘干滚刷
- A：洗完不会潮湿、不容易发霉异味
- B：你不用手动拆开晾晒滚刷，更省心，家里更卫生
- E：产品检测报告、买家实测视频
"""


def main() -> int:
    ap = argparse.ArgumentParser(description="FABE 话术校验器")
    ap.add_argument("script", nargs="?", help="话术文件（Markdown）")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--demo", action="store_true", help="运行内置示例自检")
    args = ap.parse_args()

    if args.demo:
        text = DEMO
    else:
        if not args.script:
            ap.print_help()
            return 2
        p = Path(args.script)
        if not p.exists():
            print(f"✗ 文件不存在: {p}", file=sys.stderr)
            return 2
        text = p.read_text(encoding="utf-8")

    res = validate(text)

    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0 if res["pass"] else 1

    print("FABE 话术校验")
    print("=" * 56)
    for u in res["units"]:
        mark = "✓" if not u["issues"] else "✗"
        print(f"  {mark} {u['level']}: {u['text'][:60]}")
        for i in u["issues"]:
            print(f"      → {i}")
    print("-" * 56)
    for c in res["checks"]:
        mark = "✓" if c["ok"] else "✗"
        print(f"  {mark} {c['name']}: {c['detail']}")
    print("=" * 56)
    if res["pass"]:
        print("PASS 全部机械校验通过")
        return 0
    print(f"FAIL {res['issue_count']} 处问题")
    return 1


if __name__ == "__main__":
    sys.exit(main())
