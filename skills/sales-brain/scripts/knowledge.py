#!/usr/bin/env python3
"""
AI Sales Brain - 知识查询脚本

用法: python knowledge.py [产品/话题]
"""
import os
import sys
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(SKILL_DIR, 'data')


def load_products():
    """加载产品知识"""
    with open(os.path.join(DATA_DIR, 'products.json'), 'r', encoding='utf-8') as f:
        return json.load(f)


def load_competitors():
    """加载竞品知识"""
    with open(os.path.join(DATA_DIR, 'competitors.json'), 'r', encoding='utf-8') as f:
        return json.load(f)


def search_knowledge(query, products_data, competitors_data):
    """搜索知识库"""
    query_lower = query.lower()
    results = {'products': [], 'competitors': []}

    # 搜索产品
    for prod in products_data.get('products', []):
        if (query_lower in prod.get('name', '').lower() or
            any(query_lower in f.lower() for f in prod.get('features', []))):
            results['products'].append(prod)

    # 搜索竞品
    for comp in competitors_data.get('competitors', []):
        if (query_lower in comp.get('name', '').lower() or
            any(query_lower in f.lower() for f in comp.get('features', []))):
            results['competitors'].append(comp)

    return results


def format_products(products):
    """格式化产品输出"""
    if not products:
        return None

    output = ""
    for prod in products:
        output += f"""
## 📦 {prod['name']}

**定价**: {prod.get('pricing', '未设置')}
**目标客户**: {prod.get('target', '未设置')}

### 核心功能
"""
        for feature in prod.get('features', []):
            output += f"- {feature}\n"

    return output


def format_competitors(competitors):
    """格式化竞品输出"""
    if not competitors:
        return None

    output = ""
    for comp in competitors:
        output += f"""
## 🆚 {comp['name']}

### 优势
{chr(10).join(f'- {s}' for s in comp.get('pros', []))}

### 劣势
{chr(10).join(f'- {s}' for s in comp.get('cons', []))}

### 与我们对比
{comp.get('comparison', '暂无对比信息')}
"""

    return output


def main():
    if len(sys.argv) < 2:
        print("用法: python knowledge.py [产品/话题关键词]")
        print("示例: python knowledge.py 销售管理")
        sys.exit(1)

    query = " ".join(sys.argv[1:])

    # 加载数据
    products_data = load_products()
    competitors_data = load_competitors()

    # 搜索
    results = search_knowledge(query, products_data, competitors_data)

    # 输出
    print(f"# 🔍 知识查询结果: {query}\n")

    products_output = format_products(results['products'])
    competitors_output = format_competitors(results['competitors'])

    if products_output:
        print("## 产品知识\n")
        print(products_output)

    if competitors_output:
        print("\n## 竞品信息\n")
        print(competitors_output)

    if not results['products'] and not results['competitors']:
        print("❌ 未找到相关知识")
        print("\n💡 请编辑 data/products.json 或 data/competitors.json 添加知识")


if __name__ == "__main__":
    main()
