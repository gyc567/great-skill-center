# Profit Atlas 评测与案例库

> 上游 [Cheerfay/profit-atlas](https://github.com/Cheerfay/profit-atlas) 的评测基线与完整研究成果。
> **MIT** · Copyright (c) 2026 Profit Atlas contributors · 上游 commit `bc4709f`

这个目录不是 Agent Skill，而是两个研究 Skill 的**证据与验收资产**。

---

## 📁 内容

### `evals/` —— 评测口径

| 文件 | 内容 |
|------|------|
| `profit-atlas-benchmark-v0.1.md` | **Benchmark v0.1** —— 两个固定提示词、五个维度各 0–2 分、带 raw baseline 的作者自评 |
| `baseline-industry.md` | 行业研究的无 Skill 基线 |
| `baseline-company.md` | 企业研究的无 Skill 基线 |
| `industry-profit-pool-research.md` | 行业 Skill 的验收标准 |
| `company-value-chain-review.md` | 企业 Skill 的验收标准 |
| `regression-v0.1.md` | 回归测试口径 |
| `runs/2026-10-22/` | **两份原始基线输出**（未使用 Skill 的裸跑结果，保留原样）|

### `examples/` —— 完整研究成果

| 文件 | 内容 |
|------|------|
| `industry/automotive-profit-pool-test-result-zh.md` | **中国新能源汽车产业链利润池（2023—2025）** —— 中文，170 行 |
| `industry/automotive-profit-pool-test-result-en.md` | 同上英文版，172 行 |
| `industry/automotive-generalization-test.md` | 无汽车专项模块时的泛化测试 |
| `industry/game-industry-profit-pool-zh.md` | **游戏行业利润池** —— 344 行，最完整的一份 |
| `company/catl-value-chain-review-en.md` | **宁德时代两层价值链复盘** —— 77 行 |

---

## 📊 Benchmark 结果（作者自评，诚实版）

| 任务 | 条件 | 覆盖 | 来源 | 标签 | 计算 | 结论 | 总分/10 |
|------|------|-----:|-----:|-----:|-----:|-----:|---------:|
| 中国新能源利润池 | 无 Skill | 1 | 1 | 2 | 2 | 2 | **8** |
| 中国新能源利润池 | 用 Skill | 2 | 2 | 2 | 2 | 2 | **10** |
| 宁德时代经济性 | 无 Skill | 1 | 2 | 2 | 2 | 2 | **9** |
| 宁德时代经济性 | 用 Skill | 2 | 2 | 2 | 2 | 2 | **10** |

> 📌 上游明确声明：这是**两个提示词的作者自评过程评测**，不是模型排行榜，
> 也不声称「不用 Skill 就做不好研究」。观察到的优势是**结构更稳定、证据边界更明确**。

---

## ✨ 为什么值得一起收

1. **raw baseline 是罕见的诚实资产** —— 直接对比就能看出 Skill 到底改变了什么
2. **完整案例带一手来源链接** —— 学方法论不如看一份真做出来的报告
3. **游戏行业案例 344 行** —— 覆盖一个上游没做专项模块的行业，看泛化能力

---

## 📞 定制化开发

如需**定制化开发**（行业专项模块、评测扩展、报告模板定制），可直接联系 ERIC：

| 项 | 联系方式 |
|----|---------|
| **作者定位** | ERIC AI技术专家，专注于人工智能和自动化工具的研究与应用 |
| 邮箱 | `gyc567@gmail.com` |
| Twitter | `@EricBlock2100` |
| 微信 | `360369487` |
| Telegram | https://t.me/fatoshi_block |
| Telegram 频道 | https://t.me/cryptochanneleric |
| 加密情报 TG 群 | https://t.me/btcgogopen |
| YouTube 频道 | `@0XBitFinance` |
| 个人技术博客 | `topdigg.com` |

> **品牌**：AI Skills 创作小店
> 如需定制化开发，可直接联系 ERIC。
