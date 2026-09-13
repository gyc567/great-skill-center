#!/usr/bin/env python3
"""
AI Sales Brain - 每日简报脚本

用法: python daily.py
"""
import os
import json
from datetime import datetime, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(SKILL_DIR, 'data')
CUSTOMERS_DIR = os.path.join(DATA_DIR, 'customers')
CONVERSATIONS_DIR = os.path.join(DATA_DIR, 'conversations')


def get_recent_conversations(days=7):
    """获取最近N天的对话记录"""
    conversations = []
    if os.path.exists(CONVERSATIONS_DIR):
        cutoff = datetime.now() - timedelta(days=days)
        for filename in os.listdir(CONVERSATIONS_DIR):
            if filename.endswith('.json'):
                try:
                    filepath = os.path.join(CONVERSATIONS_DIR, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        conv = json.load(f)
                    conv_date = datetime.strptime(conv.get('date', '2020-01-01'), '%Y-%m-%d')
                    if conv_date >= cutoff:
                        conversations.append(conv)
                except Exception:
                    continue
    return conversations


def get_pending_customers():
    """获取需要跟进的客户"""
    pending = []
    if os.path.exists(CUSTOMERS_DIR):
        for filename in os.listdir(CUSTOMERS_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(CUSTOMERS_DIR, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    customer = json.load(f)
                # 检查是否有待跟进标记
                if customer.get('needs_followup', False):
                    pending.append(customer)
    return pending


def calculate_stats(conversations):
    """计算统计数据"""
    if not conversations:
        return {
            'total': 0,
            'success_count': 0,
            'failure_count': 0,
            'pending_count': 0,
            'success_rate': 0
        }

    success = sum(1 for c in conversations if c.get('outcomes', {}).get('success') == True)
    failure = sum(1 for c in conversations if c.get('outcomes', {}).get('success') == False)
    pending = sum(1 for c in conversations if c.get('outcomes', {}).get('success') is None)

    total = len(conversations)
    rate = (success / total * 100) if total > 0 else 0

    return {
        'total': total,
        'success_count': success,
        'failure_count': failure,
        'pending_count': pending,
        'success_rate': rate
    }


def get_top_strategies(conversations):
    """获取最常用的策略"""
    strategy_count = {}
    for conv in conversations:
        for strat_id in conv.get('outcomes', {}).get('strategies_used', []):
            strategy_count[strat_id] = strategy_count.get(strat_id, 0) + 1

    # 排序并返回前3
    sorted_strats = sorted(strategy_count.items(), key=lambda x: x[1], reverse=True)
    return sorted_strats[:3]


def load_objections():
    """加载异议数据"""
    with open(os.path.join(DATA_DIR, 'objections.json'), 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_daily_report():
    """生成每日简报"""
    today = datetime.now()
    today_str = today.strftime('%Y年%m月%d日')

    # 获取数据
    conversations = get_recent_conversations(7)
    pending_customers = get_pending_customers()
    stats = calculate_stats(conversations)
    top_strats = get_top_strategies(conversations)

    # 任务列表
    tasks = []
    if pending_customers:
        tasks.append(f"📞 跟进 {len(pending_customers)} 个待跟进客户")
    if stats['pending_count'] > 0:
        tasks.append(f"📝 确认 {stats['pending_count']} 个待定结果")

    if not tasks:
        tasks.append("🆕 开发新客户")

    # 优先级分析
    priority = ""
    if stats['failure_count'] > stats['success_count']:
        priority = "⚠️ 近期失败较多，建议回顾异议处理策略"
    elif stats['success_rate'] >= 70:
        priority = "✅ 表现良好，保持当前策略"
    else:
        priority = "📊 需要关注成功率，有较大提升空间"

    # 最近表现
    recent_perf = f"""- 总对话数：{stats['total']} 次
- 成功率：{stats['success_rate']:.0f}%
- 成功：{stats['success_count']} | 失败：{stats['failure_count']} | 待定：{stats['pending_count']}"""

    # 改进建议
    suggestions = []
    if stats['total'] < 3:
        suggestions.append("增加客户接触频率，每天至少 2-3 次有效沟通")
    if stats['success_rate'] < 50:
        suggestions.append("分析失败案例，找出共性问题，针对性改进话术")
    if stats['pending_count'] > 2:
        suggestions.append("及时确认待定结果，不要让客户悬太久")

    if not suggestions:
        suggestions.append("持续优化，尝试新策略突破瓶颈")

    output = f"""# 📊 {today_str} 销售简报

## 今日任务
{chr(10).join(f'- {t}' for t in tasks)}

## 优先级分析
{priority}

## 最近7天表现
{recent_perf}

## 常用策略
{', '.join(f'`{s[0]}` x{s[1]}' for s in top_strats) if top_strats else '暂无数据'}

## 改进建议
{chr(10).join(f'{i+1}. {s}' for i, s in enumerate(suggestions))}

---
💡 使用 `/分析` 查看更详细的月度分析报告
"""

    return output


def main():
    print(generate_daily_report())


if __name__ == "__main__":
    main()
