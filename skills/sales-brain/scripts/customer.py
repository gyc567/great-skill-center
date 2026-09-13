#!/usr/bin/env python3
"""
AI Sales Brain - 客户管理脚本

用法:
  python customer.py add [公司名] [--contact 联系人] [--industry 行业] [--size 规模]
  python customer.py list
  python customer.py view [公司名]
  python customer.py update [公司名] [--field 值]
  python customer.py delete [公司名]
"""
import os
import sys
import json
import re
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(SKILL_DIR, 'data')
CUSTOMERS_DIR = os.path.join(DATA_DIR, 'customers')


def parse_args():
    """解析命令行参数"""
    args = {
        'action': None,
        'company': None,
        'contact': None,
        'industry': None,
        'size': None,
        'field': None,
        'value': None
    }

    if len(sys.argv) < 2:
        return args

    args['action'] = sys.argv[1].lower()

    if args['action'] in ['add', 'view', 'update', 'delete']:
        if len(sys.argv) > 2:
            args['company'] = sys.argv[2]

    # 解析可选参数
    i = 3
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '--contact' and i + 1 < len(sys.argv):
            args['contact'] = sys.argv[i + 1]
            i += 2
        elif arg == '--industry' and i + 1 < len(sys.argv):
            args['industry'] = sys.argv[i + 1]
            i += 2
        elif arg == '--size' and i + 1 < len(sys.argv):
            args['size'] = sys.argv[i + 1]
            i += 2
        elif arg == '--field' and i + 1 < len(sys.argv):
            args['field'] = sys.argv[i + 1]
            i += 2
        elif arg == '--value' and i + 1 < len(sys.argv):
            args['value'] = sys.argv[i + 1]
            i += 2
        else:
            i += 1

    return args


def get_customer_file(company_name):
    """获取客户文件路径"""
    safe_name = re.sub(r'[^\w\s-]', '', company_name).strip()
    safe_name = re.sub(r'\s+', '_', safe_name)
    return os.path.join(CUSTOMERS_DIR, f"{safe_name}.json")


def load_customer(company_name):
    """加载客户数据"""
    filepath = get_customer_file(company_name)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def save_customer(company_name, data):
    """保存客户数据"""
    filepath = get_customer_file(company_name)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return filepath


def add_customer(args):
    """添加新客户"""
    if not args['company']:
        print("错误：必须提供公司名称")
        return

    existing = load_customer(args['company'])
    if existing:
        print(f"⚠️ 客户 '{args['company']}' 已存在，使用 update 命令修改")
        return

    customer = {
        'id': f"cust_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'name': args['company'],
        'contact': args.get('contact'),
        'industry': args.get('industry'),
        'size': args.get('size'),
        'pain_points': [],
        'meets': [],
        'needs_followup': False,
        'created_at': datetime.now().strftime('%Y-%m-%d'),
        'updated_at': datetime.now().strftime('%Y-%m-%d')
    }

    filepath = save_customer(args['company'], customer)
    print(f"✅ 客户 '{args['company']}' 创建成功")
    print(f"📁 文件: {filepath}")


def list_customers():
    """列出所有客户"""
    if not os.path.exists(CUSTOMERS_DIR):
        print("📭 暂无客户记录")
        return

    customers = []
    for filename in os.listdir(CUSTOMERS_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(CUSTOMERS_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                customers.append(json.load(f))

    if not customers:
        print("📭 暂无客户记录")
        return

    print(f"# 👥 客户列表（共 {len(customers)} 个）\n")

    # 按最近更新时间排序
    customers.sort(key=lambda x: x.get('updated_at', ''), reverse=True)

    for c in customers:
        status = "📌" if c.get('needs_followup') else "  "
        meets = len(c.get('meets', []))
        print(f"{status} {c['name']} | {c.get('industry', '未分类')} | {meets}次拜访 | 更新:{c.get('updated_at', 'N/A')}")


def view_customer(company_name):
    """查看客户详情"""
    customer = load_customer(company_name)

    if not customer:
        print(f"❌ 未找到客户 '{company_name}'")
        return

    print(f"""
# 🏢 {customer['name']}

## 基本信息
- **联系人**: {customer.get('contact', '未设置')}
- **行业**: {customer.get('industry', '未设置')}
- **规模**: {customer.get('size', '未设置')}
- **创建时间**: {customer.get('created_at', 'N/A')}
- **最后更新**: {customer.get('updated_at', 'N/A')}

## 痛点
{chr(10).join(f'- {p}' for p in customer.get('pain_points', [])) or '_暂无记录_'}

## 拜访记录
""")

    meets = customer.get('meets', [])
    if meets:
        for meet in meets[-5:]:  # 最近5次
            print(f"### 📅 {meet.get('date', 'N/A')}")
            print(f"- 总结: {meet.get('summary', 'N/A')}")
            outcomes = meet.get('outcomes', [])
            if outcomes:
                print(f"- 成果: {', '.join(outcomes)}")
            print()
    else:
        print("_暂无拜访记录_")

    if customer.get('needs_followup'):
        print("\n📌 **需要跟进**")


def update_customer(args):
    """更新客户信息"""
    if not args['company']:
        print("错误：必须提供公司名称")
        return

    customer = load_customer(args['company'])
    if not customer:
        print(f"❌ 未找到客户 '{args['company']}'")
        return

    # 更新字段
    if args['contact']:
        customer['contact'] = args['contact']
    if args['industry']:
        customer['industry'] = args['industry']
    if args['size']:
        customer['size'] = args['size']
    if args['field'] and args['value']:
        customer[args['field']] = args['value']

    customer['updated_at'] = datetime.now().strftime('%Y-%m-%d')

    filepath = save_customer(args['company'], customer)
    print(f"✅ 客户 '{args['company']}' 更新成功")
    print(f"📁 文件: {filepath}")


def delete_customer(company_name):
    """删除客户"""
    filepath = get_customer_file(company_name)

    if not os.path.exists(filepath):
        print(f"❌ 未找到客户 '{company_name}'")
        return

    confirm = input(f"⚠️ 确定要删除客户 '{company_name}' 吗？(y/N): ")
    if confirm.lower() == 'y':
        os.remove(filepath)
        print(f"✅ 客户 '{company_name}' 已删除")
    else:
        print("已取消")


def add_meeting(company_name, meet_data):
    """添加拜访记录"""
    customer = load_customer(company_name)
    if not customer:
        return None

    if 'meets' not in customer:
        customer['meets'] = []

    customer['meets'].append(meet_data)
    customer['updated_at'] = datetime.now().strftime('%Y-%m-%d')

    return save_customer(company_name, customer)


def main():
    args = parse_args()

    if not args['action']:
        print("""
# 👥 AI Sales Brain - 客户管理

## 用法

```bash
# 添加客户
python customer.py add [公司名] --contact [联系人] --industry [行业] --size [规模]

# 列出所有客户
python customer.py list

# 查看客户详情
python customer.py view [公司名]

# 更新客户
python customer.py update [公司名] --field [字段名] --value [值]

# 删除客户
python customer.py delete [公司名]
```

## 字段说明
- `contact`: 联系人
- `industry`: 行业
- `size`: 规模
- `needs_followup`: 是否需要跟进 (true/false)
        """)
        return

    if args['action'] == 'add':
        add_customer(args)
    elif args['action'] == 'list':
        list_customers()
    elif args['action'] == 'view':
        view_customer(args['company'])
    elif args['action'] == 'update':
        update_customer(args)
    elif args['action'] == 'delete':
        delete_customer(args['company'])
    else:
        print(f"❌ 未知操作: {args['action']}")


if __name__ == "__main__":
    main()
