#!/usr/bin/env python3
"""
AI Sales Brain - 记录对话脚本

用法: python record.py [对话内容] [--customer 公司名] [--result success|failure|pending]
"""
import os
import sys
import json
import re
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(SKILL_DIR, 'data')
CONVERSATIONS_DIR = os.path.join(DATA_DIR, 'conversations')


def parse_args():
    """解析命令行参数"""
    args = {
        'content': '',
        'customer': None,
        'result': None,
        'objections': [],
        'strategies': []
    }

    # 简单解析
    content_parts = []
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '--customer' and i + 1 < len(sys.argv):
            args['customer'] = sys.argv[i + 1]
            i += 2
        elif arg == '--result' and i + 1 < len(sys.argv):
            result = sys.argv[i + 1].lower()
            if result in ['success', '失败', 's']:
                args['result'] = True
            elif result in ['failure', '失败', 'f']:
                args['result'] = False
            elif result in ['pending', '待定', 'p']:
                args['result'] = None
            i += 2
        elif arg == '--objection' and i + 1 < len(sys.argv):
            args['objections'].append(sys.argv[i + 1])
            i += 2
        elif arg == '--strategy' and i + 1 < len(sys.argv):
            args['strategies'].append(sys.argv[i + 1])
            i += 2
        else:
            content_parts.append(arg)
            i += 1

    args['content'] = ' '.join(content_parts)
    return args


def save_conversation(args):
    """保存对话记录"""
    today = datetime.now().strftime('%Y-%m-%d')
    customer_name = args['customer'] or '未知客户'

    # 生成文件名
    safe_name = re.sub(r'[^\w\s-]', '', customer_name).strip()
    safe_name = re.sub(r'\s+', '_', safe_name)
    filename = f"{today}_{safe_name}_{datetime.now().strftime('%H%M%S')}.json"
    filepath = os.path.join(CONVERSATIONS_DIR, filename)

    conversation = {
        'id': f"conv_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'date': today,
        'customer': customer_name,
        'content': args['content'],
        'type': 'objection_handling' if args['objections'] else 'general',
        'outcomes': {
            'success': args['result'],
            'objections_encountered': args['objections'],
            'strategies_used': args['strategies']
        },
        'created_at': datetime.now().isoformat()
    }

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(conversation, f, ensure_ascii=False, indent=2)

    return filepath


def update_customer_followup(customer_name):
    """更新客户跟进状态"""
    if not customer_name or customer_name == '未知客户':
        return None

    CUSTOMERS_DIR = os.path.join(DATA_DIR, 'customers')
    filepath = os.path.join(CUSTOMERS_DIR, f"{customer_name}.json")

    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            customer = json.load(f)

        customer['needs_followup'] = True
        customer['last_contact'] = datetime.now().strftime('%Y-%m-%d')

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(customer, f, ensure_ascii=False, indent=2)

        return filepath

    return None


def main():
    if len(sys.argv) < 2:
        print("用法: python record.py [对话内容] [--customer 公司名] [--result success|failure|pending]")
        print("示例: python record.py '客户说太贵了，用了ROI分析方案' --customer ABC科技 --result success")
        sys.exit(1)

    args = parse_args()

    if not args['content']:
        print("错误：对话内容不能为空")
        sys.exit(1)

    # 保存对话
    filepath = save_conversation(args)

    # 更新客户跟进状态
    customer_updated = update_customer_followup(args['customer'])

    print(f"✅ 对话已记录")
    print(f"📁 文件: {filepath}")

    if customer_updated:
        print(f"📝 客户 '{args['customer']}' 已标记为需要跟进")

    print("\n💡 运行 python evolve.py 更新策略成功率")


if __name__ == "__main__":
    main()
