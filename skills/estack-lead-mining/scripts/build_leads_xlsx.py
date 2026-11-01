#!/usr/bin/env python3
"""
Estack-lead-mining · scripts/build_leads_xlsx.py
把分级后的线索 JSON 写成带颜色分级、带【抖音主页链接超链接】的 xlsx。

输入 JSON 格式:
{
  "source": "来源说明",
  "product": "你卖的是什么",
  "leads": [
    {
      "level": "P0",             // P0 / P1 / P2
      "nickname": "澹台冷明",
      "sec_uid": "MS4wLjABAAAA...",
      "user_url": "https://www.douyin.com/user/MS4wLjABAAAA...",
      "comment": "我背了300万债务怎么处理",
      "video": "视频标题",
      "video_url": "https://www.douyin.com/video/...",
      "need_keywords": "300w债务,退股",
      "persona": "广东",
      "objection": "",
      "reply_suggestion": "300w标的要尽快面谈...",
      "action": "今天必回"
    }
  ],
  "summary": {"total": 22, "p0": 8, "p1": 11, "p2": 3, "top_needs": [...], "top_objections": []}
}

用法:
    python3 build_leads_xlsx.py --input /tmp/leads.json --output ./线索表.xlsx
"""
import argparse, json
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

P0_FILL = PatternFill("solid", fgColor="C6EFCE")  # 绿
P1_FILL = PatternFill("solid", fgColor="FFEB9C")  # 黄
P2_FILL = PatternFill("solid", fgColor="F2F2F2")  # 灰
HEAD_FILL = PatternFill("solid", fgColor="1F4E78")
HEAD_FONT = Font(color="FFFFFF", bold=True, size=11)
LINK_FONT = Font(color="0563C1", underline="single")
THIN = Side(border_style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical="top")

# 列：优先级/昵称/抖音主页链接/评论原文/意向/需求/画像/回复/来源视频/原视频链接/行动
COLUMNS = [
    ("优先级", 8),
    ("客户昵称", 14),
    ("抖音主页链接(点开找他)", 46),
    ("评论原文", 46),
    ("意向等级", 10),
    ("需求关键词", 24),
    ("客户画像", 16),
    ("推荐公开回复话术", 42),
    ("来源视频", 20),
    ("原视频链接", 42),
    ("行动", 12),
]

LEVEL_FILL = {"P0": P0_FILL, "P1": P1_FILL, "P2": P2_FILL}
LEVEL_NAME = {"P0": "P0高意向", "P1": "P1中意向", "P2": "P2低意向/同行"}
P2_MAX_ROWS = 30


def write_sheet(ws, leads, level):
    for j, (name, width) in enumerate(COLUMNS, 1):
        c = ws.cell(row=1, column=j, value=name)
        c.fill = HEAD_FILL; c.font = HEAD_FONT; c.border = BORDER
        c.alignment = Alignment(horizontal="center", vertical="center")
        ws.column_dimensions[get_column_letter(j)].width = width
    ws.row_dimensions[1].height = 24
    ws.freeze_panes = "A2"

    rows = [l for l in leads if l.get("level") == level]
    if level == "P2" and len(rows) > P2_MAX_ROWS:
        rows = rows[:P2_MAX_ROWS]

    for i, l in enumerate(rows, 2):
        values = [
            LEVEL_NAME.get(level, level),
            l.get("nickname", ""),
            l.get("user_url", ""),
            l.get("comment", ""),
            LEVEL_NAME.get(level, level),
            l.get("need_keywords", ""),
            l.get("persona", ""),
            l.get("reply_suggestion", ""),
            l.get("video", ""),
            l.get("video_url", ""),
            l.get("action", ""),
        ]
        for j, v in enumerate(values, 1):
            c = ws.cell(row=i, column=j, value=v)
            c.fill = LEVEL_FILL[level]
            c.border = BORDER
            c.alignment = WRAP
            # 抖音主页链接 / 原视频链接 加超链接
            if j == 3 and v:
                c.hyperlink = v
                c.font = LINK_FONT
            if j == 10 and v:
                c.hyperlink = v
                c.font = LINK_FONT
        ws.row_dimensions[i].height = 54


def write_summary(ws, data):
    s = data.get("summary", {})
    ws.column_dimensions["A"].width = 24
    ws.column_dimensions["B"].width = 70

    total = s.get("total", 0)
    p0 = s.get("p0", 0)
    p1 = s.get("p1", 0)
    p2 = s.get("p2", 0)
    p0_pct = round(p0 / max(total, 1) * 100, 1)

    rows = [
        ("数据来源", data.get("source", "")),
        ("你卖的产品", data.get("product", "")),
        ("生成时间", datetime.now().strftime("%Y-%m-%d %H:%M")),
        ("总评论数", total),
        ("P0 高意向", f"{p0} 条（占比 {p0_pct}%）"),
        ("P1 中意向", f"{p1} 条"),
        ("P2 低意向/同行", f"{p2} 条"),
        ("", ""),
        ("🔥 高频需求", " / ".join(s.get("top_needs", []))),
        ("⚠️ 最大顾虑", " / ".join(s.get("top_objections", []))),
        ("", ""),
        ("📌 行动建议", "今天先回 P0 全部 + P1 前 10 条。手动打开【抖音主页链接】列，在抖音内一对一沟通。"),
        ("", ""),
        ("⚠️ 合规提醒", "本表只用于人工参考。批量私信、群发、倒卖线索会导致封号+违法。"),
    ]
    for i, (k, v) in enumerate(rows, 1):
        a = ws.cell(row=i, column=1, value=k)
        b = ws.cell(row=i, column=2, value=v)
        a.font = Font(bold=True); a.alignment = WRAP; b.alignment = WRAP
        ws.row_dimensions[i].height = 26


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    wb = Workbook()
    ws0 = wb.active; ws0.title = "P0高意向"
    ws1 = wb.create_sheet("P1中意向")
    ws2 = wb.create_sheet("P2低意向样本")
    ws3 = wb.create_sheet("汇总洞察")

    write_sheet(ws0, data["leads"], "P0")
    write_sheet(ws1, data["leads"], "P1")
    write_sheet(ws2, data["leads"], "P2")
    write_summary(ws3, data)

    wb.save(args.output)
    print(f"OK -> {args.output}")


if __name__ == "__main__":
    main()
