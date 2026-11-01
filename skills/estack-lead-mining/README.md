# Estack-lead-mining

抖音评论客户线索挖掘 Skill —— 把大V评论区里有购买意向的人，连同他们的**抖音主页链接**一起捞出来，导出 Excel。

**一句话流程**：赛道关键词 → 找爆款视频 → 抓公开评论（带 sec_uid）→ AI 分意向 → 出带抖音号的 Excel。

## 能力

1. **抓公开评论**：输入抖音视频链接，抓取平台未登录可见的公开评论，每条含评论者**抖音主页链接**（sec_uid）。
2. **AI 意向分级**：P0高意向 / P1中意向 / P2低意向/同行。
3. **需求画像**：提取需求关键词、地域。
4. **回复话术**：为每条 P0/P1 生成公开评论区回复话术。
5. **导出 Excel**：带抖音主页链接超链接、按意向分 sheet、颜色分级。

## 快速开始

```bash
# 0. 安装依赖
pip install -r requirements.txt

# 1. 抓评论（一个或多个视频）
python3 crawler.py --videos "https://www.douyin.com/video/7676028838417059099,https://www.douyin.com/video/7610356701983722761" --out /tmp/comments.json

# 2. AI 分级
python3 main.py --comments /tmp/comments.json --product "股权律师咨询" --out /tmp/leads.json

# 3. 导出 Excel
python3 main.py --leads /tmp/leads.json --out ./线索表.xlsx
```

## 目录结构

```
Estack-lead-mining/
├── SKILL.md                  # Skill 说明（本文件同义）
├── crawler.py                # 抓公开评论（含 sec_uid 抖音主页链接）
├── main.py                   # AI 分级 + 调度入口
├── scripts/
│   └── build_leads_xlsx.py   # 导出带抖音主页链接的 Excel
├── requirements.txt
└── examples/
```

## 合规边界

- ✅ 只读平台**公开可见**的评论与主页标识。
- ❌ 不自动私信、不批量骚扰、不破解登录态、不抓非公开数据。
- 所有跟进必须**人工一对一**在抖音内进行。

## 输出字段

每条线索：客户昵称 / 抖音主页链接 / 评论原文 / 意向等级 / 需求关键词 / 客户画像 / 推荐公开回复 / 来源视频 / 原视频链接 / 行动建议
