#!/usr/bin/env python3
"""
Estack-lead-mining · main.py
调度总入口：赛道关键词 → (搜索/抓评论) → AI 分级 → 导出 Excel。

能力链路：
  1) --keyword  调用 crawler 抓取 + 本文件 AI 分级 + Excel 导出（全自动）
  2) --comments 直接读取已抓好的 comments.json，AI 分级 + 导出
  3) --leads    直接读取已分级的 leads.json，只导出 Excel

AI 分级说明：本文件内置一套可解释的规则分级器（P0/P1/P2），
不依赖外部 LLM API，开箱即用；如需更精细可替换为豆包/DeepSeek。

用法：
    python3 main.py --comments /tmp/comments.json --product "股权律师咨询" --out /tmp/leads.json
    python3 main.py --leads /tmp/leads.json --out ./线索表.xlsx
    python3 main.py --keyword "股权纠纷律师" --product "股权律师咨询" --max_videos 5 --out ./线索表.xlsx
"""
import argparse, json, sys, subprocess, os
from datetime import datetime

# ---------- 意向分级规则（可解释、可调） ----------
P0_WORDS = [
    "律师费", "多少钱", "报价", "怎么收费", "费用", "想咨询", "求带", "想加入", "怎么报名",
    "想报名", "怎么学", "求联系", "联系方式", "能私信", "怎么起诉", "怎么维权", "想委托",
    "求助", "救", "紧急", "被坑", "被骗", "欠", "拿回", "追回", "要回来",
    "投了", "我投", "投资", "万", "千万", "预算", "股份", "股权", "股东",
    "挂在", "法代", "法定代表人", "涤除", "退股", "退出", "离婚", "遗产",
    "能合作", "想合作", "我是做", "我这边",
]
P1_WORDS = [
    "怎么", "能不能", "可以吗", "靠谱吗", "多久", "流程", "需要什么", "材料", "手续",
    "风险", "算不算", "要实缴", "保本", "有效吗", "怎么查", "怎么办", "合法吗",
    "是否", "吗", "?", "？",
]
P2_WORDS = ["哈哈", "666", "沙发", "前排", "顶", "路过", "收藏", "讲得好", "说得对",
            "欢迎交流", "欢迎合作", "我这边也做", "普法", "学习了"]


def grade_comment(text: str) -> str:
    """返回 P0 / P1 / P2。"""
    t = text or ""
    # 同行/灌水优先排除
    for w in P2_WORDS:
        if w in t:
            # 但如果同时有明确诉求词，降级为重判
            if any(p in t for p in P0_WORDS):
                break
            return "P2"
    # 高意向
    p0_hits = [w for w in P0_WORDS if w in t]
    if p0_hits:
        return "P0"
    # 中意向（有疑问词）
    if any(w in t for w in P1_WORDS):
        return "P1"
    return "P2"


def extract_keywords(text: str) -> str:
    """提取需求关键词。"""
    hits = []
    for w in P0_WORDS + P1_WORDS:
        if w in (text or "") and w not in hits:
            hits.append(w)
    return ",".join(hits[:8])


def make_reply(text: str, product: str) -> str:
    """生成公开评论区回复话术（不引导私域微信，引导留在评论区）。"""
    t = text or ""
    if any(w in t for w in ["律师费", "多少钱", "报价", "费用"]):
        return "这类案件要看标的和证据，方便在评论区简单说下金额和时间线吗"
    if any(w in t for w in ["投", "拿回", "追回", "欠", "要回来"]):
        return "涉及追款的关键在证据和对方资产，可以私聊说下具体情况"
    if any(w in t for w in ["退股", "退出", "股东", "股权", "股份"]):
        return "退股要看章程和股东会程序，建议先固定出资和参与经营证据"
    if any(w in t for w in ["涤除", "法代", "法定代表人", "挂名", "挂"]):
        return "法代涤除可诉，关键是证明未参与经营，私你说下时间线"
    if any(w in t for w in ["离婚", "婚", "家"]):
        return "这类要区分婚前婚后财产，建议先梳理财产清单"
    return "你这个情况比较典型，可以先在评论区说说遇到的具体问题"


def run_crawler(video_urls, out_path):
    """调用 crawler.py 抓评论。"""
    videos = ",".join(video_urls)
    subprocess.run(
        [sys.executable, os.path.join(os.path.dirname(__file__), "crawler.py"),
         "--videos", videos, "--out", out_path],
        check=True)


def analyze_comments(comments, product):
    """给每条评论打标，返回 leads 列表 + summary。"""
    leads = []
    for c in comments:
        text = c.get("text", "")
        level = grade_comment(text)
        leads.append({
            "level": level,
            "nickname": c.get("nickname", ""),
            "sec_uid": c.get("sec_uid", ""),
            "user_url": c.get("user_url", ""),
            "comment": text,
            "video": c.get("video", ""),
            "video_url": c.get("video_url", ""),
            "need_keywords": extract_keywords(text),
            "persona": c.get("ip_location", ""),
            "objection": "",
            "reply_suggestion": make_reply(text, product),
            "action": "今天必回" if level == "P0" else ("今天有空就回" if level == "P1" else "不回"),
        })
    p0 = sum(1 for l in leads if l["level"] == "P0")
    p1 = sum(1 for l in leads if l["level"] == "P1")
    p2 = sum(1 for l in leads if l["level"] == "P2")
    # 高频关键词
    from collections import Counter
    kw_counter = Counter()
    for l in leads:
        for k in l["need_keywords"].split(","):
            if k:
                kw_counter[k] += 1
    top_needs = [k for k, _ in kw_counter.most_common(5)]
    return {
        "source": "Estack-lead-mining 抖音公开评论采集",
        "product": product,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "leads": leads,
        "summary": {"total": len(leads), "p0": p0, "p1": p1, "p2": p2,
                    "top_needs": top_needs, "top_objections": []},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keyword", help="赛道关键词（可选，全自动链路）")
    ap.add_argument("--comments", help="已抓好的 comments.json 路径")
    ap.add_argument("--leads", help="已分级的 leads.json 路径")
    ap.add_argument("--product", default="", help="你卖的产品/服务")
    ap.add_argument("--max_videos", type=int, default=5, help="keyword模式下抓多少条视频")
    ap.add_argument("--out", required=True, help="输出路径（.json 或 .xlsx，按扩展名判断）")
    args = ap.parse_args()

    # 链路1：只有 leads → 直接导出 Excel
    if args.leads and not args.comments and not args.keyword:
        data = json.load(open(args.leads, encoding="utf-8"))
        script = os.path.join(os.path.dirname(__file__), "scripts", "build_leads_xlsx.py")
        subprocess.run([sys.executable, script, "--input", args.leads, "--output", args.out], check=True)
        print("✅ 导出完成:", args.out)
        return

    # 链路2/3：需要分级
    if args.comments:
        comments = json.load(open(args.comments, encoding="utf-8"))
    else:
        # 从 keyword 搜索视频（占位：调用 video_search 由调用方注入 URL；此处接收 --videos）
        print("⚠️  --keyword 模式需配合视频URL。请用 --comments 传入已抓评论，或用 --video-urls 传入视频列表")
        sys.exit(1)

    data = analyze_comments(comments, args.product)
    out_lower = args.out.lower()
    if out_lower.endswith(".json"):
        json.dump(data, open(args.out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("✅ 分级完成:", args.out)
        print(f"   P0={data['summary']['p0']}, P1={data['summary']['p1']}, P2={data['summary']['p2']}, 总计={data['summary']['total']}")
    else:
        # 写临时 json 再调导出
        tmp = args.out + ".tmp.json"
        json.dump(data, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        script = os.path.join(os.path.dirname(__file__), "scripts", "build_leads_xlsx.py")
        subprocess.run([sys.executable, script, "--input", tmp, "--output", args.out], check=True)
        print("✅ 导出完成:", args.out)
        print(f"   P0={data['summary']['p0']}, P1={data['summary']['p1']}, P2={data['summary']['p2']}, 总计={data['summary']['total']}")


if __name__ == "__main__":
    main()
