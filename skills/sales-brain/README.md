# 🤖 AI Sales Brain

中文智能销售助手 - 将普通销售转变为顶级业绩者。

## 功能特性

### 💬 核心功能

| 功能 | 触发命令 | 说明 |
|------|---------|------|
| 会议准备 | `/会议 [公司名]` | 生成完整会议准备报告 |
| 异议处理 | `/异议 [描述]` | 按成功率排序的应对策略 |
| 每日简报 | `/简报` | 今日任务 + 表现分析 |
| 客户管理 | `/客户 add/view/list` | 客户信息管理 |
| 知识查询 | `/查 [关键词]` | 产品/竞品知识库 |
| 表现分析 | `/分析` | 30天销售表现报告 |

### 🧠 自进化系统

- **成功率驱动**：每次异议处理后记录效果
- **智能排序**：策略按实际成功率降序展示
- **持续优化**：样本量>=5时自动更新策略效果

## 快速开始

### 1. 初始化

```bash
cd skills/sales-brain
python scripts/setup.py
```

### 2. 配置 API Key

```bash
cp data/config.json.example data/config.json
# 编辑 config.json，填入您的 Anthropic API Key
```

### 3. 使用

在 Claude Code 中直接对话：

```
/会议 阿里巴巴
/异议 客户说太贵了
/简报
/分析
```

## 目录结构

```
sales-brain/
├── SKILL.md              # 主技能定义
├── README.md             # 本文件
├── scripts/
│   ├── setup.py         # 初始化
│   ├── meeting.py       # 会议准备
│   ├── objection.py     # 异议处理
│   ├── daily.py         # 每日简报
│   ├── record.py        # 记录对话
│   ├── evolve.py        # 自进化
│   ├── customer.py      # 客户管理
│   └── knowledge.py     # 知识查询
├── data/
│   ├── config.json.example
│   ├── objections.json   # 异议数据库
│   ├── talk_templates.json
│   ├── products.json
│   ├── competitors.json
│   ├── customers/       # 客户画像
│   ├── conversations/    # 对话记录
│   └── evolution/        # 自进化日志
└── templates/
```

## 数据说明

### 对话记录
- 存储位置：`data/conversations/`
- 命名格式：`{日期}_{客户}_{时间}.json`
- 包含：对话内容、使用的策略、处理结果

### 异议数据库
- 存储位置：`data/objections.json`
- 预置 5 大类别：价格、需求、时间、竞品、功能
- 每类别 3-5 条应对策略（含成功率数据）

### 客户画像
- 存储位置：`data/customers/`
- 包含：基本信息、痛点、拜访记录、跟进状态

## 数据安全

⚠️ **重要提醒**：
- `data/` 目录包含您的敏感商业数据
- 请定期备份该目录
- 不要将 `data/` 目录提交到 Git
- API Key 仅存储在本地，不会上传

## 常见问题

### Q: 提示"无法找到数据文件"
运行初始化：
```bash
python scripts/setup.py
```

### Q: 如何添加竞品信息？
编辑 `data/competitors.json`

### Q: 自进化多久更新一次？
每次运行 `/分析` 时自动更新

## 更新日志

### v1.0
- 初始版本
- 支持会议准备、异议处理、每日简报
- 自进化系统
- 客户管理

## License

MIT
