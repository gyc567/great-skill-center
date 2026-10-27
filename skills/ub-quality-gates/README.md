# 极致代码质量门大师 (ub-quality-gates)

> **Uncle Bob 的编程纪律 + 三个确定性质量门工具，一条命令守住复杂度、重复率和测试盲区。**

[![许可](https://img.shields.io/badge/许可-0BSD-blue)](https://opensource.org/licenses/0BSD)
[![语言](https://img.shields.io/badge/语言-Python%20%7C%20Shell-blue)]()
[![品牌](https://img.shields.io/badge/品牌-AI%20Skills%20创作小店-pink)](https://github.com/gyc567/great-skill-center)

---

## 🎯 这个 Skill 解决什么

写代码时最常见的三个问题，**都可以被自动检测**，而不是靠人肉 review：

| 问题 | 检测工具 | 判定 |
|------|---------|------|
| 函数太复杂、还没测试 | **crapper** | CRAP < 10 |
| 同一段逻辑抄了三遍 | **dryer** | 相似度 < 0.8 |
| 测试看着全绿，其实抓不住 bug | **mutator** | 变异体全部 killed |

**三条命令，全自动，数字说话。**

---

## 🧭 三个阶段

```
First Make It Work  →  Then Make It Right  →  Follow Practice
      先让它能跑              再让它正确            最后守纪律
```

### 阶段一：先让它能跑

- **Laziness Protocol** — 一个决定只住一个地方，能修最小就修最小
- **Foundational Thinking** — 逻辑之前先把数据形状定对
- **TDD** — 先写会失败的测试 → 看它以预期原因失败 → 最小改动让它通过
- **Redesign From First Principles** — 别把新需求硬挂在旧设计上
- **Attack the Premise** — 两个修复栽在同一道门上，先写出那个前提
- **Subtract Before You Add** — 加之前先减
- **Outcome-Oriented Execution** — 瞄准可检查的终态
- **Build the Lever** — 工作不一眼可明就造工具

**架构五条**：Model the Domain（让非法状态不可能）· Boundary Discipline（入口校验、内部信任）·
Type System Discipline（让非法值写不出来）· Make Operations Idempotent（跑两次结果相同）·
Separate Before Serializing Shared State（不共享可变状态）

### 阶段二：再让它正确

- **Fix Root Causes** — 只会掩盖崩溃的护栏不是修复
- **Test Behavior, Not Implementation** — 如果所有函数返回空它还能过，就扔掉
- **Refactoring** — 先钉住行为 → 改结构 → 证明行为没变
- **crapper / dryer / mutator** — 三个数字门禁

### 阶段三：守纪律

- **Keep a Log** — 记录每个动作和理由
- **Guard the Context Window** — 主线程保持精简，批量外发
- **Worktree Cleanup** — 找可安全删的，确认没在用，再回收
- **Commit and Push** — 小而有序，每个 commit 说清为什么/改了什么/怎么证明

---

## 🚀 安装

```bash
# 方式一：直接跑安装脚本
bash scripts/install-gates.sh

# 方式二：手动
git clone https://github.com/unclebob/crapper.git
git clone https://github.com/unclebob/dryer.git
git clone https://github.com/unclebob/mutator.git
cd crapper && python3 -m venv .venv && .venv/bin/pip install -e .
cd ../dryer   && python3 -m venv .venv && .venv/bin/pip install -e .
cd ../mutator && python3 -m venv .venv && .venv/bin/pip install -e . && .venv/bin/pip install -e ../crapper
```

**要求**：Python ≥ 3.11 · git

---

## 🎮 使用

```bash
cd 你的项目

# 一条命令跑完三道门
~/.ub-tools/ub-gates doctor .

# 单项调用
~/.ub-tools/ub-gates crap --changed        # 只看 git 改动
~/.ub-tools/ub-gates dry --threshold 0.9   # 更严的重复检测
~/.ub-tools/ub-gates mutate --scan         # 只列变异点
```

### 实际输出长这样

```
=== 1/3 复杂度与覆盖率 (CRAP) ===
CRAP Report
===========
Languages: go, python, typescript

Function                       Namespace    CC    Cov%     CRAP
------------------------------------------------------------
classify                       complex      14   22.2%    106.2   ← 超门禁
simple_add                     complex       1  100.0%      1.0   ← 健康

=== 2/3 重复代码 (dryer) ===
DUPLICATE score=1.00
  src/complex.py:28-35
  src/complex.py:37-44

=== 3/3 变异测试 (mutator) ===
Function            Namespace  Killed  Survived  Uncovered  Sites   Score
classify            complex         1        10          8     19   9.1%
simple_add          complex         1         0          0      1  100.0%
```

---

## 🔢 CRAP 是什么

```
CRAP = CC² × (1 − coverage)³ + CC
```

`CC` = 圈复杂度，`coverage` = 测试覆盖率。

| 分数 | 含义 | 动作 |
|------|------|------|
| 1–5 | 低风险 | 通过 |
| 5–30 | 值得看一眼 | 拆分或补测 |
| 30+ | 复杂且欠测 | 必须重构 + 补测试 |
| **> 10** | **ub-mode 门禁线** | **不允许合并** |

---

## 🌍 支持语言

**Clojure · Java · Go · TypeScript/JavaScript · Rust · Python**

一次运行自动识别语言，按语言套用各自的复杂度与覆盖率规则。

---

## 📦 包含内容

```
ub-quality-gates/
├── SKILL.md                      # 完整纪律 + 工具用法 + 12 条实测坑点
├── README.md
├── scripts/
│   └── install-gates.sh          # 一键安装（已实测干净复现，66 秒）
└── references/
    ├── tools-reference.md        # 四工具完整参考：公式、参数、规则、输出格式
    └── troubleshooting.md        # 排障手册：A~H 八类症状 → 解法
```

---

## ✅ 交付实测

| 项 | 结果 |
|----|------|
| crapper 单元测试 | **144 passed** |
| dryer 单元测试 | **80 passed** |
| mutator 单元测试 | **76 passed** |
| 多语言识别 | ✅ go / python / typescript 自动识别 |
| CC 计算 | ✅ classify=14, grade=6, Tier=4 |
| CRAP 公式验算 | ✅ 14²×(1-0)³+14 = **210** |
| 重复检测 | ✅ 精确命中埋设重复块 score=**1.00** |
| 变异测试 | ✅ simple_add **100% killed**；classify 1 killed / 10 survived / 8 uncovered |
| 安装脚本 | ✅ 干净目录复现，**66 秒零错误** |

---

## 📄 许可与来源

| 来源 | 许可 |
|------|------|
| 纪律理念 `unclebob/ub-mode` | 原仓库**无 LICENSE 文件** |
| `unclebob/crapper` / `dryer` / `mutator` / `uml-viewer` | **0BSD** © 2026 Robert C. Martin |
| 上游衍生 crap4clj / crap4java / crap4go / dry4clj / clj-mutate / mutate4go / mutate4java | 同一作者 |
| 理念参考 `@poteto` poteto-mode / pstack | 原仓库**已不可访问** |

0BSD 是最宽松的开源许可，允许自由使用、修改、商用、闭源分发。
本 Skill 为方法论与工具链封装，遵循 0BSD 宽松条款重新分发。

---

## 📞 定制化开发

如需**定制化开发**，可直接联系 ERIC：

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

---

## 🔗 相关

- **AI Skills 创作小店** — https://github.com/gyc567/great-skill-center
- 姊妹 Skill：`agent-reach`（互联网触达）、`requesting-code-review`（代码评审）

> 本 Skill 管**代码质量**（确定性门禁），`agent-reach` 管**信息获取**（互联网触达）。
> 一个告诉你"世界怎么了"，一个告诉你"你的代码写得对不对"。
