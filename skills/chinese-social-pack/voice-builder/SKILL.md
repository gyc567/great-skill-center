---
name: voice-builder
description: 中文内容声音建模。通过采访+写作样本分析，生成 `voice-profile.md` 作为所有下游社媒技能的写作基础。触发词：建立我的声音、学习我的写作风格、训练声音模型、分析我的文风、build my voice。
version: 1.0.0
author: Dex Digital Factory
license: MIT
metadata:
  hermes:
    tags: [social-media, content, voice, writing, chinese]
    related_skills: [content-ideation, social-post-writer, platform-adapter]
---

# 声音建模器 (Voice Builder)

## Overview

从用户采访和写作样本中提取个人内容声音，生成 `voice-profile.md`。这个文件是所有下游社媒技能的基础——每篇帖子都会先读取它来确保风格一致。

输出文件保存到 OrbitOS vault 的 `30_知识库/voice-profile.md`。

## When to Use

触发词：
- "建立我的声音" / "build my voice"
- "学习我的写作风格" / "learn my voice"
- "训练声音模型" / "train on my writing"
- "分析我的文风"
- 用户丢进来一批文章样本

## 工作流程

### Step 1: 收集写作样本

如果用户还没有提供样本，用 `clarify` 工具询问：

> "请提供 3-5 篇你最有代表性的内容（公众号文章、LinkedIn 帖子、微博、newsletter 等任意格式），我好分析你的写作风格。"

如果用户已直接发送了样本，跳过这步直接分析。

### Step 2: 深度采访（4 轮，用 clarify 工具）

用 `clarify` 工具分 4 轮采访，每轮 3-4 个问题：

**第 1 轮：身份与定位**
```json
[
  {"question": "你做什么的？用一句话自我介绍（职业/领域/身份）。", "choices": []},
  {"question": "你的目标读者是谁？（比如：创业者、AI从业者、宝妈、程序员...）", "choices": []},
  {"question": "读者关注你最主要的原因是什么？（获取信息/学技能/找共鸣/娱乐）", "choices": []},
  {"question": "你希望读者看完你的内容后产生什么行动或感受？", "choices": []}
]
```

**第 2 轮：内容风格**
```json
[
  {"question": "你的内容风格偏好？（可多选）", "choices": ["干货教学型", "个人故事型", "观点评论型", "清单汇总型"]},
  {"question": "语气调性？", "choices": ["专业严肃", "轻松幽默", "温暖治愈", "犀利毒舌", "冷静理性"]},
  {"question": "内容长度偏好？", "choices": ["短文（300字以内）", "中篇（300-800字）", "长文（800-2000字）", "深度长文（2000+）"]},
  {"question": "有没有常用的口头禅、惯用句式、或标志性表达？如有请写下。", "choices": []}
]
```

**第 3 轮：话题边界**
```json
[
  {"question": "你最常写的3个话题领域？", "choices": []},
  {"question": "有什么话题你绝不碰的？（敏感话题、不擅长领域等）", "choices": []},
  {"question": "你是否使用个人经历/故事作为素材？频率如何？", "choices": ["经常，这是我的核心风格", "偶尔，碰到合适的才用", "几乎不，我偏好客观论述"]}
]
```

**第 4 轮：发布习惯**
```json
[
  {"question": "你的主要发布平台？", "choices": ["微信公众号", "知乎", "小红书", "LinkedIn", "Twitter/X", "微博", "其他"]},
  {"question": "发布频率？", "choices": ["日更", "每周2-3篇", "每周1篇", "不定时"]},
  {"question": "你在标题/开头有什么特定技巧吗？（比如你常用的hook方式）", "choices": []},
  {"question": "有没有你特别欣赏的创作者或参考账号？可提1-3个。", "choices": []}
]
```

### Step 3: 分析写作样本

读取用户提供的 3-5 篇样本，从以下维度分析：

1. **句式特征**：句子长短？多用短句还是长句？排比/反问/设问的频率？
2. **词汇偏好**：惯用词、高频词、专业术语密度、中英夹杂程度
3. **结构模式**：开头方式（提问/数据/故事/观点）、行文节奏、结尾风格
4. **情感调性**：理性vs感性、距离感vs亲切感、攻击性vs温和性
5. **独特标识**：口头禅、惯用标点（感叹号？省略号？）、排版习惯

### Step 4: 生成 voice-profile.md

综合采访+样本分析，用 `mcp_orbitos_vault_write` 写入以下模板：

```markdown
---
tags: [voice-profile, content]
created: YYYY-MM-DD
---

# 内容声音档案

## 身份画像
- **一句话定位**：
- **核心领域**：
- **目标读者**：
- **读者期待**：

## 风格指南
- **语气**：
- **句式**：
- **长度**：
- **结构模板**：

## 语言指纹
- **高频词**：
- **惯用句式**：
- **标志性表达**：
- **标点偏好**：

## 内容边界
- **常写话题**：
- **避雷话题**：
- **个人故事使用**：

## 发布习惯
- **主平台**：
- **频率**：
- **Hook 偏好**：

## 参考对标
- 
```

## Common Pitfalls

1. **采访太多轮**：严格控制在 4 轮以内，不要加额外问题。
2. **跳过样本分析**：样本分析是声音建模的核心，不能只靠采访。
3. **voice-profile 太泛**：避免「专业」「有趣」这种空洞描述。要具体到句式、词汇、结构。
4. **忘记保存到 vault**：必须用 `mcp_orbitos_vault_write` 保存，路径 `30_知识库/voice-profile.md`。

## Verification Checklist

- [ ] 4 轮采访全部完成
- [ ] 3-5 篇样本已分析
- [ ] voice-profile.md 已保存到 vault
- [ ] 档案中包含具体的句式、词汇、口癖（非泛泛描述）
- [ ] 用户确认档案准确
