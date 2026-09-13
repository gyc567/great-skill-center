# kb-retriever — SkillPay 上架指南

## 商品信息

| 字段 | 内容 |
|------|------|
| 商品名称 | kb-retriever |
| 版本 | 1.0.1 |
| 定价 | ¥19.90 |
| 类目 | Retrieval / Local Knowledge Base |
| 作者 | Eric Guo |

## 商品描述

Local knowledge-base retriever with progressive search. Navigates layered data_structure.md indexes, enforces learn-before-process for PDF and Excel, bounds retrieval to at most five rounds, and answers with sources.

## 触发关键词（用户在 AI Agent 中输入这些词来激活 Skill）



## 安装包

直接上传此目录下的文件到 SkillPay：
- SKILL.md（必须）
- manifest.json（自动生成）
- README.md（如有）

或使用预打包文件：
```
/root/repos/skill-packages/kb-retriever.tar.gz
```

## 履约脚本

购买后用户会通过 `alipay-bot` 自动安装到 `~/.hermes/skills/kb-retriever/`。

## 上架步骤

1. 登录 https://skillpay.alipay.com → 我是创作者
2. 点击「上架新 Skill」
3. 填写以上商品信息
4. 上传安装包或直接粘贴 SKILL.md 内容
5. 设置价格 ¥19.90
6. 提交审核

## 合规提示

- SKILL.md 不得包含付费内容或诱导购买的话术
- 确保你有该 Skill 的全部知识产权
- 上架前完成 SkillPay 协议 + AI 按量付费协议签署

---
Generated at 2026-09-12T07:41:02.927825+00:00 UTC