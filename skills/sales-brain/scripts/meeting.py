#!/usr/bin/env python3
"""
AI Sales Brain - 会议准备脚本

用法: python meeting.py [公司名] [联系人]
"""
import os
import sys
import json
import re
from datetime import datetime, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(SKILL_DIR, 'data')
CUSTOMERS_DIR = os.path.join(DATA_DIR, 'customers')


def load_talk_templates():
    """加载话术模板"""
    with open(os.path.join(DATA_DIR, 'talk_templates.json'), 'r', encoding='utf-8') as f:
        return json.load(f)


def load_customer(company_name):
    """加载客户信息"""
    # 搜索匹配的客户文件
    if os.path.exists(CUSTOMERS_DIR):
        for filename in os.listdir(CUSTOMERS_DIR):
            if company_name.lower() in filename.lower():
                filepath = os.path.join(CUSTOMERS_DIR, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
    return None


def generate_meeting_prep(company_name, contact=None, customer_data=None):
    """生成会议准备"""

    # 公司名分析（简化版，实际可以接入企查查等API）
    industry_keywords = {
        "科技": ["科技", "技术", "软件", "互联网", "IT", "AI", "数据"],
        "金融": ["金融", "银行", "保险", "证券", "基金", "投资"],
        "制造": ["制造", "生产", "工厂", "工业", "机械", "设备"],
        "零售": ["零售", "电商", "商贸", "商店", "超市", "门店"],
        "医疗": ["医疗", "健康", "医院", "医药", "生物", "器械"],
        "教育": ["教育", "培训", "学校", "学院", "在线教育"],
        "物流": ["物流", "运输", "快递", "仓储", "供应链"]
    }

    # 简单行业推断
    detected_industry = "通用"
    for industry, keywords in industry_keywords.items():
        if any(k in company_name for k in keywords):
            detected_industry = industry
            break

    # 生成痛点推测
    pain_point_templates = {
        "科技": ["团队协作效率", "研发流程优化", "技术债务", "代码质量管理"],
        "金融": ["合规风险管理", "客户数据安全", "审批流程效率", "监管报告"],
        "制造": ["生产效率", "设备维护", "质量控制", "供应链协同"],
        "零售": ["客户获取成本", "复购率提升", "库存周转", "全渠道体验"],
        "医疗": ["患者体验", "诊疗效率", "医保合规", "病历管理"],
        "教育": ["学员转化率", "完课率", "师资管理", "个性化学习"],
        "物流": ["配送效率", "成本控制", "客户满意度", "车辆调度"]
    }

    pain_points = pain_point_templates.get(detected_industry, ["运营效率", "成本控制", "客户满意度"])

    # 谈话要点
    talk_points = [
        f"了解 {detected_industry} 行业的最新趋势",
        f"探讨贵公司在 {pain_points[0]} 方面的现状",
        "确认具体的业务痛点和期望目标",
        "介绍我们方案的核心价值"
    ]

    # 可能的异议
    possible_objections = [
        f"我们目前在用其他供应商，需要评估",
        f"预算明年才到位",
        f"需要先内部讨论"
    ]

    # 话术模板
    templates = load_talk_templates()
    opening_template = templates['opening'][0]['text']

    # 历史记录
    history = ""
    if customer_data and 'meets' in customer_data:
        history = f"\n## 历史拜访记录\n"
        for meet in customer_data['meets'][-3:]:
            history += f"- **{meet['date']}**: {meet.get('summary', 'N/A')}\n"

    output = f"""# 📅 {company_name} 会议准备

## 公司概况
- **行业**：{detected_industry}
- **联系人**：{contact or '待确认'}
- **准备时间**：{datetime.now().strftime('%Y-%m-%d %H:%M')}

## 痛点推测
{chr(10).join(f'- {p}' for p in pain_points)}

## 谈话要点
{chr(10).join(f'{i+1}. {p}' for i, p in enumerate(talk_points))}

## 可能遇到的异议
{chr(10).join(f'- {o}' for o in possible_objections)}

## 建议开场白
> {opening_template.replace('XXX', company_name)}

## 结束动作建议
- 确认下一步具体行动
- 约定下次沟通时间
- 交换关键决策人联系方式

{history if history else ''}
---
💡 建议：会议结束后使用 `/记录"总结..."` 保存会议要点
"""

    return output


def main():
    if len(sys.argv) < 2:
        print("用法: python meeting.py [公司名] [联系人（可选）]")
        sys.exit(1)

    company_name = sys.argv[1]
    contact = sys.argv[2] if len(sys.argv) > 2 else None

    # 尝试加载已有客户数据
    customer_data = load_customer(company_name)

    # 生成准备
    output = generate_meeting_prep(company_name, contact, customer_data)
    print(output)


if __name__ == "__main__":
    main()
