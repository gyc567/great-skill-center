---
name: social-post-writer
description: 中文社媒帖子撰写引擎。读取 voice-profile，按选题生成带 hook 的完整帖子。支持5种结构框架（PAS/AIDA/BAB/STAR/SLAY）和6种 hook 策略。触发词：写帖子、帮我写一篇、draft a post、写公众号、写小红书。
version: 1.0.0
author: Dex Digital Factory
license: MIT
metadata:
  hermes:
    tags: [social-media, writing, content, chinese, wechat]
    related_skills: [voice-builder, content-ideation, platform-adapter]
---

# 社媒帖子撰写引擎 (Social Post Writer)

## Overview

一站式帖子撰写。先读取 `voice-profile.md`（由 voice-builder 生成）确保风格一致，然后根据用户选题生成高质量帖子。

核心流程：
1. 读取声音档案
2. 确认选题 + 框架
3. 生成 3 个 hook 供选择
4. 撰写正文
5. 适配平台格式

## When to Use

触发词：
- "帮我写一篇关于 X 的帖子"
- "写帖子" / "draft a post"
- "把这个选题展开"
- "写公众号文章"
- "写小红书文案"

## 工作流程

### Step 1: 读取声音档案

用 `mcp_orbitos_vault_read` 读取 `30_知识库/voice-profile.md`。

如果不存在，暂停并让用户先运行 voice-builder。

### Step 2: 确认选题和框架

如果用户只给了主题（如"帮我写一篇关于 AI 的帖子"），先用 `clarify` 追问：

```
"确认一下：
- 选题角度：[从 content-ideation 的选题中选，或让用户给]
- 目标平台：[公众号/小红书/LinkedIn/Twitter]
- 想要什么感觉：[犀利观点/实用教程/故事共鸣]
- 长度：[300字以内 / 500-800字 / 1000+字]"
```

如果用户已经给了具体选题，直接进入 Step 3。

### Step 3: 生成 Hook（开头）

Hook 是第一句话。reader 在 0.5 秒内决定要不要继续看。

从以下 6 种策略中选 3 个最合适的，生成 3 个候选 hook 让用户选：

| # | 策略 | 示例模板 |
|---|------|---------|
| 1 | **反常识** | "大多数人以为 X，但真相是 Y。" |
| 2 | **数据冲击** | "X% 的人正在用错误的方式做 Y。" |
| 3 | **痛点共鸣** | "你是不是也试过 X，结果 Y？" |
| 4 | **悬念/好奇** | "我最近发现一个秘密，关于 X..." |
| 5 | **故事开头** | "3 年前我还不会 X，今天我却..." |
| 6 | **直接断言** | "X 是 Y 领域最被低估的能力。" |

用 `clarify` 让用户从 3 个候选中选 1 个，或直接选最优的。

### Step 4: 选择正文结构框架

根据内容类型推荐框架，用 `clarify` 确认：

| 框架 | 全称 | 结构 | 最适合 |
|------|------|------|--------|
| **PAS** | Problem-Agitate-Solve | 痛点→放大→方案 | 干货教程、工具推荐 |
| **AIDA** | Attention-Interest-Desire-Action | 吸引→兴趣→渴望→行动 | 营销、转化向 |
| **BAB** | Before-After-Bridge | 以前→现在→方法 | 个人成长、转型故事 |
| **STAR** | Situation-Task-Action-Result | 情境→任务→行动→结果 | 职场、项目复盘 |
| **SLAY** | Story-Lesson-Application-You | 故事→教训→应用→呼吁 | 情感共鸣、观点输出 |

### Step 5: 撰写完整帖子

按照 voice-profile 的风格 + 选定的结构 + hook 撰写完整帖子。

输出格式：

```
## [标题/主题]

[Hook — 选定的开头句]

[正文 — 按选定框架展开]

[CTA — 结尾行动呼吁/互动引导]

---
**发布时间建议**：[平台最佳发文时间]
**配图建议**：[匹配的图片风格]
**标签**：#标签1 #标签2 #标签3
```

### Step 6: 平台格式微调

根据目标平台做最后调整：

- **微信公众号**：段落间空行，每段不超过 3 行，适当使用 emoji 和加粗
- **小红书**：开头空 2 格，多用 emoji 分行，加话题标签，限制 1000 字
- **LinkedIn**：英文为主或中英双语，第一行用空白行留悬念，多分段
- **Twitter/X**：线程格式（1/8），每条约 200 字

## Common Pitfalls

1. **跳过声音档案**：不读 voice-profile 直接写，风格必然跑偏。必须 STEP 1 先读。
2. **Hook 太平**："今天我们来聊聊 X" — 这种开头等于自杀。Hook 必须有情绪张力。
3. **正文太长不分段**：公众号超过 4 行的段落读者直接跳过。微信排版 = 短段落 + 空行。
4. **没有 CTA**：结尾一定要引导互动——"你怎么看？"、"转发给有需要的朋友"等。
5. **AI 味太重**：避免"在当今时代"、"综上所述"、"值得注意的是" — 这些词一出现就暴露是 AI 写的。

## AI味剔除清单

写完后自查，删除以下表达：
- "在当今...的时代背景下"
- "综上所述"
- "值得注意的是"
- "不可否认"
- "从某种程度上来说"
- 连续三个以上的"我们"开头
- 段落开头用"首先...其次...最后"（太教科书）

替换为：
- 口语化短句
- 反问句增加对话感
- 具体案例代替抽象论述
- 你的真实口癖（从 voice-profile 提取）

## Verification Checklist

- [ ] voice-profile 已读取
- [ ] Hook 有情绪张力（不是陈述句开头）
- [ ] 正文框架明确（PAS/AIDA/BAB/STAR/SLAY 之一）
- [ ] 已剔除 AI 味表达
- [ ] CTA 清晰
- [ ] 平台格式已适配
