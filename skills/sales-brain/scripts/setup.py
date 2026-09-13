#!/usr/bin/env python3
"""
AI Sales Brain - 初始化设置脚本

首次使用时运行此脚本进行初始化。
"""
import os
import json
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(SKILL_DIR, 'data')

def create_default_files():
    """创建默认数据文件"""

    # 1. config.json.example
    config_example = {
        "api_key": "YOUR_ANTHROPIC_API_KEY_HERE",
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 4096
    }

    # 2. objections.json - 预置异议数据库
    objections = {
        "objections": [
            {
                "id": "obj_price",
                "keyword": ["太贵", "价格高", "贵", "预算", "买不起", "太贵了"],
                "category": "价格",
                "strategies": [
                    {
                        "id": "strat_001",
                        "text": "分解成本，强调 ROI。计算使用我们方案后每年节省的成本，展示长期价值。",
                        "success_rate": 0.85,
                        "use_count": 120,
                        "last_used": None
                    },
                    {
                        "id": "strat_002",
                        "text": "对比竞品价格，说明性价比。我们不是最贵的，但性价比最高。",
                        "success_rate": 0.72,
                        "use_count": 89,
                        "last_used": None
                    },
                    {
                        "id": "strat_003",
                        "text": "提供分期付款或阶梯定价，降低客户初期投入压力。",
                        "success_rate": 0.68,
                        "use_count": 45,
                        "last_used": None
                    },
                    {
                        "id": "strat_004",
                        "text": "强调免费试用期，让客户先体验价值再决定。",
                        "success_rate": 0.65,
                        "use_count": 67,
                        "last_used": None
                    }
                ]
            },
            {
                "id": "obj_need",
                "keyword": ["不需要", "没需求", "考虑中", "不需要", "没兴趣", "再看看"],
                "category": "需求",
                "strategies": [
                    {
                        "id": "strat_101",
                        "text": "通过提问发现潜在痛点：'您目前是怎么处理XXX的？' 引导客户自己意识到问题。",
                        "success_rate": 0.78,
                        "use_count": 95,
                        "last_used": None
                    },
                    {
                        "id": "strat_102",
                        "text": "分享同行业成功案例，让客户看到同行是如何解决问题的。",
                        "success_rate": 0.70,
                        "use_count": 72,
                        "last_used": None
                    },
                    {
                        "id": "strat_103",
                        "text": "提供免费诊断或评估服务，让客户亲身体验价值。",
                        "success_rate": 0.62,
                        "use_count": 38,
                        "last_used": None
                    }
                ]
            },
            {
                "id": "obj_time",
                "keyword": ["没时间", "太忙", "之后再说", "现在不方便", "改天"],
                "category": "时间",
                "strategies": [
                    {
                        "id": "strat_201",
                        "text": "强调快速实施：'只需要30分钟介绍，就能帮您节省大量时间'。",
                        "success_rate": 0.75,
                        "use_count": 88,
                        "last_used": None
                    },
                    {
                        "id": "strat_202",
                        "text": "提供异步资料：'我先把资料发您，有空时看看，有问题随时问我'。",
                        "success_rate": 0.68,
                        "use_count": 56,
                        "last_used": None
                    },
                    {
                        "id": "strat_203",
                        "text": "约定具体时间：'这周三下午2点，您方便吗？我只占用您15分钟'。",
                        "success_rate": 0.55,
                        "use_count": 34,
                        "last_used": None
                    }
                ]
            },
            {
                "id": "obj_competitor",
                "keyword": ["在用", "比你们好", "其他家", "竞品", "已经选了"],
                "category": "竞品",
                "strategies": [
                    {
                        "id": "strat_301",
                        "text": "差异化对比：'他们的优势是XXX，我们的优势是YYY，您更看重哪方面？'",
                        "success_rate": 0.72,
                        "use_count": 63,
                        "last_used": None
                    },
                    {
                        "id": "strat_302",
                        "text": "开放心态：'可以了解下他们给您什么方案吗？我帮您分析下是否满足需求'。",
                        "success_rate": 0.58,
                        "use_count": 41,
                        "last_used": None
                    },
                    {
                        "id": "strat_303",
                        "text": "未来导向：'如果将来有需求变化，我们方案的扩展性会更好'。",
                        "success_rate": 0.48,
                        "use_count": 27,
                        "last_used": None
                    }
                ]
            },
            {
                "id": "obj_feature",
                "keyword": ["功能不够", "不能满足", "缺少", "不支持", "能不能"],
                "category": "功能",
                "strategies": [
                    {
                        "id": "strat_401",
                        "text": " roadmap 展示：'这个功能我们 Q2 会上线，我可以帮您加入提前测试名单'。",
                        "success_rate": 0.70,
                        "use_count": 52,
                        "last_used": None
                    },
                    {
                        "id": "strat_402",
                        "text": "变劣势为优势：'虽然我们不做XXX，但我们的YYY做得更深，能更好解决您的问题'。",
                        "success_rate": 0.65,
                        "use_count": 44,
                        "last_used": None
                    },
                    {
                        "id": "strat_403",
                        "text": "集成能力说明：'我们可以和您现有的XXX系统集成，实现完整解决方案'。",
                        "success_rate": 0.60,
                        "use_count": 33,
                        "last_used": None
                    }
                ]
            }
        ]
    }

    # 3. talk_templates.json
    talk_templates = {
        "opening": [
            {"id": "op_001", "text": "您好，我是XXX的銷售顧問。今天想和您聊聊如何在XXX方面幫助貴公司提升效率。", "scene": "首次拜訪"},
            {"id": "op_002", "text": "張總，您好！感謝抽出時間。上次我們聊到貴公司在XXX方面有些挑戰，今天想具體看看能怎麼幫上忙。", "scene": "二次拜訪"},
            {"id": "op_003", "text": "李總好！這次聯繫是想和您分享一個和我們合作的公司遇到的類似問題，以及他們的解決方案。", "scene": "價值提案"},
            {"id": "op_004", "text": "王總，感謝您抽空。我們這次不講產品，先聊聊您目前最關心的幾個問題。", "scene": "consultative"},
            {"id": "op_005", "text": "您好陳總，聽說貴公司最近在XXX方面有擴展計劃，我們的方案可能很適合。", "scene": "引薦場景"}
        ],
        "closing": [
            {"id": "cl_001", "text": "基於今天的討論，我建議我們可以做一個詳細的評估方案，您覺得怎麼樣？", "action": "評估提案"},
            {"id": "cl_002", "text": "我們的方案對貴公司來說，預計能在XXX方面提升30%以上的效率。", "action": "價值總結"},
            {"id": "cl_003", "text": "如果今天確定的話，我們可以這週就啟動，您身邊有其他相關負責人可以一起參與嗎？", "action": "決策人確認"},
            {"id": "cl_004", "text": "那我們約定下週再做一次深入演示，把您團隊相關的同事一起叫上，可以嗎？", "action": "擴大參與"}
        ],
        "discovery": [
            {"id": "di_001", "question": "目前貴公司在XXX方面是怎麼處理的？", "purpose": "了解現狀"},
            {"id": "di_002", "question": "您最希望解決的問題是什麼？", "purpose": "確定痛點"},
            {"id": "di_003", "question": "這個問題對貴公司的業務影響有多大？", "purpose": "評估緊迫性"},
            {"id": "di_004", "question": "您之前有嘗試過什麼解決方案嗎？結果如何？", "purpose": "了解經驗"},
            {"id": "di_005", "question": "如果這個問題解決了，對您來說最大的價值是什麼？", "purpose": "確認動機"}
        ]
    }

    # 4. products.json
    products = {
        "products": [
            {
                "id": "prod_001",
                "name": "企业级销售管理系统",
                "features": [
                    "智能客户画像",
                    "销售流程自动化",
                    "实时数据分析",
                    "团队协作工具",
                    "移动端支持"
                ],
                "pricing": "¥2999/月起",
                "target": "中大型企业"
            }
        ]
    }

    # 5. competitors.json
    competitors = {
        "competitors": []
    }

    # 保存文件
    files = {
        'config.json.example': config_example,
        'objections.json': objections,
        'talk_templates.json': talk_templates,
        'products.json': products,
        'competitors.json': competitors
    }

    for filename, data in files.items():
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ 创建: {filepath}")


def create_directories():
    """创建目录结构"""
    dirs = [
        os.path.join(DATA_DIR, 'customers'),
        os.path.join(DATA_DIR, 'conversations'),
        os.path.join(DATA_DIR, 'evolution')
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"✅ 创建目录: {d}")


def print_welcome():
    """打印欢迎信息"""
    print("\n" + "="*50)
    print("🎯 AI Sales Brain 初始化向导")
    print("="*50)
    print(f"\n📁 数据目录: {DATA_DIR}")
    print("\n📋 下一步操作:")
    print("1. 复制 config.json.example 为 config.json")
    print("2. 在 config.json 中填入您的 Anthropic API Key")
    print("3. 开始使用 /帮助 查看所有命令\n")


def main():
    print("🚀 开始初始化 AI Sales Brain...\n")
    create_directories()
    create_default_files()
    print_welcome()


if __name__ == "__main__":
    main()
