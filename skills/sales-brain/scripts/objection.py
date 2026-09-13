#!/usr/bin/env python3
"""
AI Sales Brain - 异议处理脚本

用法: python objection.py [异议描述]
"""
import os
import sys
import json
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(SKILL_DIR, 'data')


def load_objections():
    """加载异议数据库"""
    with open(os.path.join(DATA_DIR, 'objections.json'), 'r', encoding='utf-8') as f:
        return json.load(f)


def match_objection(user_input, objections_data):
    """匹配异议类型"""

    user_input_lower = user_input.lower()

    for obj in objections_data['objections']:
        for keyword in obj['keyword']:
            if keyword in user_input_lower:
                return obj
    return None


def sort_strategies(strategies):
    """按成功率排序"""
    return sorted(strategies, key=lambda x: x['success_rate'], reverse=True)


def format_rate(rate):
    """格式化成功率"""
    return f"{rate * 100:.0f}%"


def get_medal(emoji=True, index=0):
    """获取奖牌emoji"""
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"] if emoji else ["第一", "第二", "第三", "第四", "第五"]
    return medals[index] if index < len(medals) else str(index + 1)


def generate_response(user_objection, matched_objection):
    """生成异议处理响应"""

    strategies = sort_strategies(matched_objection['strategies'])

    output = f"""# 💬 异议处理方案

## 客户异议：{user_objection}
**类别**：{matched_objection['category']}

---

## 推荐策略（按成功率排序）

"""

    for i, strategy in enumerate(strategies[:5]):
        medal = get_medal(index=i)
        rate = format_rate(strategy['success_rate'])
        count = strategy['use_count']

        output += f"""### {medal} 方案{i+1}（成功率 {rate}，已用 {count} 次）

{strategy['text']}

"""

    output += """---
💡 请告诉我这个方案的效果：
**【成功】/【失败】/【待定】**

收到回复后我会记录结果用于优化后续建议。
"""

    return output


def generate_no_match_response(user_objection):
    """无法匹配时的响应"""
    return f"""# 💬 异议处理方案

## 客户异议：{user_objection}

抱歉，我目前没有针对这类异议的预置策略。

**建议处理方向**：
1. 深入了解客户顾虑的具体原因
2. 通过提问引导客户自己找到答案
3. 记录这个异议场景，我会学习如何处理

**请描述客户更具体的问题，我来帮您分析。**
"""


def main():
    if len(sys.argv) < 2:
        print("用法: python objection.py [异议描述]")
        sys.exit(1)

    user_objection = " ".join(sys.argv[1:])

    # 加载数据
    objections_data = load_objections()

    # 匹配异议
    matched = match_objection(user_objection, objections_data)

    if matched:
        output = generate_response(user_objection, matched)
    else:
        output = generate_no_match_response(user_objection)

    print(output)


if __name__ == "__main__":
    main()
