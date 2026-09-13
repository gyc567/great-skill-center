#!/usr/bin/env python3
"""
AI Sales Brain - 自进化脚本

分析对话记录，更新策略成功率
"""
import os
import json
from datetime import datetime, timedelta
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(SKILL_DIR, 'data')
CONVERSATIONS_DIR = os.path.join(DATA_DIR, 'conversations')
EVOLUTION_DIR = os.path.join(DATA_DIR, 'evolution')


def get_recent_conversations(days=30):
    """获取最近N天的对话记录"""
    conversations = []
    if os.path.exists(CONVERSATIONS_DIR):
        cutoff = datetime.now() - timedelta(days=days)
        for filename in os.listdir(CONVERSATIONS_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(CONVERSATIONS_DIR, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    conv = json.load(f)
                try:
                    conv_date = datetime.strptime(conv.get('date', '2020-01-01'), '%Y-%m-%d')
                    if conv_date >= cutoff:
                        conversations.append(conv)
                except Exception:
                    continue
    return conversations


def load_objections():
    """加载异议数据库"""
    with open(os.path.join(DATA_DIR, 'objections.json'), 'r', encoding='utf-8') as f:
        return json.load(f)


def save_objections(data):
    """保存异议数据库"""
    with open(os.path.join(DATA_DIR, 'objections.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def calculate_new_rate(old_rate, old_count, new_success):
    """计算新的成功率"""
    # 贝叶斯平滑：避免单次结果大幅影响
    alpha = 5  # 先验样本量
    beta = 2   # 先验成功/失败比例 5:2

    adjusted_old_count = old_count + alpha
    adjusted_success = int(old_rate * old_count * (old_count / adjusted_old_count)) if old_count > 0 else 0
    # 简化为直接计算
    new_success_count = int(old_rate * old_count) if old_count > 0 else 0

    # 新成功率 = (历史成功 + 本次成功) / (历史总数 + 1)
    return (new_success_count + (1 if new_success else 0)) / (old_count + 1)


def update_strategy_stats(conversations, objections_data):
    """更新策略统计数据"""
    updates = []

    for obj in objections_data['objections']:
        for strategy in obj['strategies']:
            strat_id = strategy['id']

            # 统计使用次数和成功率
            total = 0
            successes = 0

            for conv in conversations:
                if strat_id in conv.get('outcomes', {}).get('strategies_used', []):
                    total += 1
                    if conv.get('outcomes', {}).get('success') == True:
                        successes += 1

            if total > 0:
                old_rate = strategy['success_rate']
                new_rate = successes / total

                # 只有样本量>=5且变化>5%时才更新
                if total >= 5 and abs(new_rate - old_rate) > 0.05:
                    strategy['success_rate'] = round(new_rate, 2)
                    strategy['use_count'] = total
                    strategy['last_used'] = datetime.now().strftime('%Y-%m-%d')

                    updates.append({
                        'strategy_id': strat_id,
                        'old_rate': old_rate,
                        'new_rate': new_rate,
                        'total_uses': total
                    })

    return updates


def generate_evolution_report(conversations, objections_data):
    """生成自进化分析报告"""

    # 计算统计数据
    total = len(conversations)
    success = sum(1 for c in conversations if c.get('outcomes', {}).get('success') == True)
    failure = sum(1 for c in conversations if c.get('outcomes', {}).get('success') == False)
    pending = sum(1 for c in conversations if c.get('outcomes', {}).get('success') is None)

    success_rate = (success / total * 100) if total > 0 else 0

    # 异议类型分布
    objection_dist = defaultdict(int)
    for conv in conversations:
        for obj_id in conv.get('outcomes', {}).get('objections_encountered', []):
            objection_dist[obj_id] += 1

    # 策略使用排行
    strategy_usage = defaultdict(int)
    for conv in conversations:
        for strat_id in conv.get('outcomes', {}).get('strategies_used', []):
            strategy_usage[strat_id] += 1

    top_strategies = sorted(strategy_usage.items(), key=lambda x: x[1], reverse=True)[:5]

    # 生成报告
    report = f"""# 📈 销售表现分析

## 整体统计（近30天）
| 指标 | 数值 |
|------|------|
| 总对话数 | {total} |
| 成功 | {success} |
| 失败 | {failure} |
| 待定 | {pending} |
| 成功率 | {success_rate:.1f}% |

## 异议类型分布
"""

    if objection_dist:
        for obj_id, count in sorted(objection_dist.items(), key=lambda x: x[1], reverse=True):
            # 查找类别名
            category = obj_id
            for obj in objections_data.get('objections', []):
                if obj['id'] == obj_id:
                    category = obj.get('category', obj_id)
                    break
            report += f"- **{category}**: {count} 次\n"
    else:
        report += "_暂无异议记录_\n"

    report += "\n## 策略使用排行\n"
    if top_strategies:
        for i, (strat_id, count) in enumerate(top_strategies, 1):
            # 查找策略内容
            strategy_text = strat_id
            strategy_rate = 0
            for obj in objections_data.get('objections', []):
                for strat in obj.get('strategies', []):
                    if strat['id'] == strat_id:
                        strategy_text = strat.get('text', strat_id)[:50] + "..."
                        strategy_rate = strat.get('success_rate', 0)
                        break
            report += f"{i}. `{strat_id}` ×{count}（成功率 {strategy_rate*100:.0f}%）\n"
    else:
        report += "_暂无策略使用记录_\n"

    # 改进建议
    suggestions = []
    if success_rate < 50:
        suggestions.append("⚠️ 成功率偏低，建议回顾失败案例，找出问题模式")
    if pending > total * 0.3:
        suggestions.append("📝 待定结果过多，建议主动跟进确认")
    if not suggestions:
        suggestions.append("✅ 表现良好，继续保持")

    report += "\n## 改进建议\n" + "\n".join(f"- {s}" for s in suggestions)

    return report


def main():
    print("🔄 正在分析对话记录...\n")

    # 加载数据
    conversations = get_recent_conversations(30)
    objections_data = load_objections()

    if not conversations:
        print("📭 暂无对话记录，跳过分析")
        print("\n💡 使用 /记录 保存对话后再运行此分析")
        return

    # 更新策略统计
    updates = update_strategy_stats(conversations, objections_data)

    if updates:
        save_objections(objections_data)
        print(f"✅ 已更新 {len(updates)} 个策略的成功率：")
        for u in updates:
            print(f"   {u['strategy_id']}: {u['old_rate']*100:.0f}% → {u['new_rate']*100:.0f}%")
    else:
        print("📊 策略成功率无显著变化，无需更新")

    # 生成报告
    print("\n" + "="*50)
    report = generate_evolution_report(conversations, objections_data)
    print(report)

    # 保存月度报告
    month_key = datetime.now().strftime('%Y-%m')
    report_file = os.path.join(EVOLUTION_DIR, f"{month_key}_report.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            'generated_at': datetime.now().isoformat(),
            'period_days': 30,
            'conversations_count': len(conversations),
            'success_rate': sum(1 for c in conversations if c.get('outcomes', {}).get('success') == True) / max(len(conversations), 1),
            'updates': updates
        }, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
