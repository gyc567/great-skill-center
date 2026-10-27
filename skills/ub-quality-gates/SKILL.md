---
name: ub-quality-gates
description: >
  Uncle Bob 编程纪律与确定性质量门工具链。写代码或改代码时使用：先让它能跑，再让它正确，最后守纪律。
  当用户要求 /ub-mode、需要代码质量门禁、CRAP 评分、重复代码检测、变异测试、
  或抱怨代码难懂/难测/有重复时触发。覆盖 Clojure/Java/Go/TypeScript/Rust/Python。
license: 0BSD
author: ERIC AI技术专家，专注于人工智能和自动化工具的研究与应用
brand: AI Skills 创作小店
version: 1.0.0
---

# 极致代码质量门大师 (ub-quality-gates)

> 上游理念来自 **Robert C. Martin**（Uncle Bob，《Clean Code》/《重构》作者）的
> `ub-mode` 纪律，配套三个 **0BSD 许可** 的确定性质量门工具。
> 品牌化改造：AI Skills 创作小店

---

## 🔧 工具链

| 工具 | 干什么 | 判定阈值 | 许可 |
|------|--------|---------|------|
| **crapper** | 圈复杂度 × 覆盖率 → **CRAP 评分** | `< 10` | 0BSD |
| **dryer** | 结构指纹 Jaccard 相似度 → **重复代码** | `< 0.8` | 0BSD |
| **mutator** | 变异测试 → **测试没抓住的 bug** | 全部 killed | 0BSD |
| **uml-viewer** | 可视化组件/覆盖率/CRAP/变异分数 | — | 随附 |

**支持语言**：Clojure · Java · Go · TypeScript/JavaScript · Rust · Python

**CRAP 公式**（与 crap4clj/crap4java/crap4go 完全一致）：

```
CRAP = CC² × (1 − coverage)³ + CC
```

| 分数 | 含义 | 动作 |
|------|------|------|
| 1–5 | 低风险 | 通过 |
| 5–30 | 值得看一眼 | 拆分或补测 |
| 30+ | 复杂且欠测 | 必须重构 + 补测试 |
| **> 10** | **ub-mode 门禁线** | **不允许合并** |

---

## 📐 三阶段纪律

```
First Make It Work  →  Then Make It Right  →  Follow Practice
     先让它能跑              再让它正确            最后守纪律
```

### 阶段一：First Make It Work（先让它能跑）

| 原则 | 要点 |
|------|------|
| **Laziness Protocol** | 一个决定只住在一个地方；能修好的就修最小的改动 |
| **Foundational Thinking** | 逻辑之前先把数据形状定对；先做对后面每一步都有帮助的事 |
| **TDD** | 先写会失败的测试 → 看它以预期原因失败 → 最小改动让它通过 |
| **Redesign From First Principles** | 别把新需求硬挂在旧设计上；先想"如果一开始就做会怎么做"，再分片交付 |
| **Attack the Premise** | 两个修复栽在同一道门上 → 用一句话写出那个前提，数清谁持失衡；**移除这个指派** |
| **Subtract Before You Add** | 加任何东西之前先减复杂度 |
| **Outcome-Oriented Execution** | 瞄准可检查的终态；中途可以断，但要计划好且能回滚 |
| **Build the Lever** | 工作不一眼可明就造工具；手工做一个单元，再让工具对齐这个单元 |

**架构五条**：

| 子项 | 要点 |
|------|------|
| Model the Domain | 让非法状态不可能存在；维护领域术语表 |
| Boundary Discipline | **数据进来时校验，内部信任**；业务逻辑放纯函数 |
| Type System Discipline | 让非法值写不出来；外部数据在入口解析一次；**不要 silence 编译器** |
| Make Operations Idempotent | 跑两次、或崩在半路后续跑，**结果状态相同** |
| Separate Before Serializing Shared State | 不共享可变状态就各给各的；要共享就一个写者，并在结构里强制 |

### 阶段二：Then Make It Right（再让它正确）

| 原则 | 要点 |
|------|------|
| **Fix Root Causes** | 复现 → 修因；**只会掩盖崩溃的护栏不是修复** |
| **Sequence into Verifiable Units** | 做完一个小单元先验证，再开下一个 |
| **Test Behavior, Not Implementation** | 测试像用户那样调用代码、检查用户能看到的结果；**如果所有函数都返回空它还能过，就扔掉** |
| **Crapper** | 每个函数 CRAP < 10，靠拆分、补测，或两者 |
| **Dryer** | 消除相似度 ≥ 0.8 的重复结构 |
| **Mutator** | 补上没覆盖的；杀掉存活变异体；删掉死代码 |
| **Refactoring** | 先钉住行为 → 改结构 → 证明行为没变 |

### 阶段三：Practice（守纪律）

| 原则 | 要点 |
|------|------|
| **Keep a Log** | 记录每个动作和理由，完成时报告这份 log |
| **Guard the Context Window** | 主线程保持精简，批量工作外发，只留摘要 |
| **Worktree Cleanup** | 找可安全删除的 → 确认没有在用的 → 回收磁盘；未提交的等决策 |
| **Commit and Push** | 小而有序地频繁提交；每个 commit 说清**为什么、改了什么、怎么证明的**；最后推主线 |

---

## 🚀 快速开始

### 1. 安装工具链

```bash
bash scripts/install-gates.sh
```

装到 `~/.ub-tools/`，生成统一入口 `~/.ub-tools/ub-gates`。

| 环境变量 | 默认 | 说明 |
|---------|------|------|
| `UB_TOOLS_DIR` | `~/.ub-tools` | 工具安装目录 |
| `UB_SKILL_DIR` | `~/.hermes/skills/ub-mode` | Skill 更新目录 |

### 2. 一条命令跑完三道门

```bash
cd 你的项目
~/.ub-tools/ub-gates doctor .
```

输出三段：CRAP 报告 → 重复代码 → 变异测试。CRAP > 10 时退出码为 2。

### 3. 单项调用

```bash
~/.ub-tools/ub-gates crap --changed          # 只分析 git 改动
~/.ub-tools/ub-gates crap --no-coverage src  # 只看复杂度
~/.ub-tools/ub-gates dry --threshold 0.9     # 更严的重复检测
~/.ub-tools/ub-gates mutate --scan           # 只列变异点不跑测试
```

### 4. 直接用工具

```bash
cd /path/to/crapper && ./crapper --threshold 10
cd /path/to/dryer   && ./dryer
cd /path/to/mutator && ./mutator --since-last-run
```

---

## 🔑 关键参数速查

### crapper
| 参数 | 作用 |
|------|------|
| `--root <path>` | 项目根，指标写这里（默认 cwd） |
| `--source-root <path>` | 只走这棵树（可重复） |
| `--changed` | 只分析 git 新增/修改的文件 |
| `--no-coverage` | 只算复杂度，CRAP 为 N/A |
| `--use-existing-coverage` | 读磁盘上已有覆盖率，不重跑测试 |
| `--coverage-command <cmd>` | 自定义覆盖率命令 |
| `--threshold <n>` | 最高分超阈值时退出码 2 |

### dryer
| 参数 | 作用 |
|------|------|
| `--threshold N` | 最小相似度，默认 **0.82** |
| `--min-lines N` | 最小行数，默认 4 |
| `--min-nodes N` | 最小归一化节点数，默认 20 |
| `--edn` / `--text` | 输出格式 |
| `--changed` | 只比较 git 改动的 |

### mutator
| 参数 | 作用 |
|------|------|
| `--scan` | 只列变异点，不跑测试不写指标 |
| `--mutate-all` | 连已 killed 的也重跑 |
| `--since-last-run` | 只跑存活变异体和新写的函数（**默认**） |
| `--lines <n,n>` | 只变异指定行 |
| `--no-coverage` | 所有点都视为已覆盖 |
| `--test-command <cmd>` | 自定义测试命令 |
| `--max-workers N` | 并发上限（默认每核一个） |

**退出码**：`0` 全部 killed · `2` 基线测试失败 · `3` 有变异体存活

---

## 📁 产出文件

| 文件 | 内容 |
|------|------|
| `.metrics/crap.edn` | CRAP 快照（uml-viewer 读） |
| `.metrics/dry.edn` | 重复代码候选 |
| `.metrics/mutate/<ns>.edn` | 变异测试快照（按命名空间分文件） |

**快照让 mutator 变成差分的**：函数文本没变，已 killed 的变异体不用重跑。

---

## ⚠️ 实测坑点（血泪经验）

| # | 坑 | 症状 | 解法 |
|---|-----|------|------|
| 1 | **mutator 必须在项目根运行** | `Skipping ...; it is outside <tool dir>` | `cd 项目根 && python -m mutator src` |
| 2 | **mutator 依赖 crapper** | `ImportError: cannot import name ... from crapper` | `pip install -e ../crapper`（同��级目录） |
| 3 | **覆盖率文件位置固定** | 全部 UNCOVERED | 必须是 `target/coverage/**/lcov.info` 或 `coverage/**/lcov.info` |
| 4 | **CRAP 公式验证** | 怀疑算错 | CC=14, cov=0% → 14²×1+14 = **210** ✅ |
| 5 | **CRAP > 10 会 exit 2** | CI 突然红 | 这是**门禁生效**，不是崩溃 |
| 6 | **coverage 未装** | `Python coverage will score 0%` | 工具会自动尝试装；失败则手动装 coverage |
| 7 | **TS/Go 覆盖率需要项目文件** | `No package.json; skipping TypeScript coverage` | 需要 `package.json` / `go.mod` |
| 8 | **dryer 默认跳过大块** | 三行的重复找不到 | `--min-lines 3 --min-nodes 15` |
| 9 | **Python 需 `conftest.py`/`pytest.ini`** | rootdir 猜错，导入失败 | 项目根放 `pytest.ini` 写 `testpaths = tests` |
| 10 | **UPSTREAM `test.sh` 有 f-string bug** | Python 3.12+ 语法错误 | 手动 `pytest tests/` + `ruff` + `mypy` |
| 11 | **crapper 自身 2 个测试需 uml-viewer** | `FileNotFoundError: uml` | 克隆 uml-viewer 到同级，或忽略这 2 个 |
| 12 | **pip 装 editable 会报 hermes 依赖冲突警告** | 一堆 `not installed` | **venv 隔离，正常**，不是真错误 |

---

## 🧪 质量验证记录（本 Skill 交付时实测）

| 项 | 结果 |
|----|------|
| crapper 单元测试 | **144 passed**（2 failed 需 uml-viewer 同级） |
| dryer 单元测试 | **80 passed** |
| mutator 单元测试 | **76 passed**（装 crapper 后全绿） |
| 多语言识别 | ✅ go / python / typescript 自动识别 |
| CC 计算 | ✅ classify=14, grade=6, Tier=4 |
| CRAP 公式 | ✅ 14²×(1-0)³+14 = 210 |
| 重复检测 | ✅ 精确命中埋设的重复块 score=1.00 |
| 变异测试 | ✅ simple_add 100% killed；classify 1 killed/10 survived/8 uncovered |
| 安装脚本 | ✅ 干净目录复现，66 秒零错误 |

---

## 📌 与 Agent Reach 等工具的协同

本 Skill 管**代码质量**（确定性门禁），`agent-reach` 管**信息获取**（互联网触达）。
两者互补：一个告诉你"世界怎么了"，一个告诉你"你的代码写得对不对"。

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

## 📄 许可与来源

- **纪律理念**：`unclebob/ub-mode`（GitHub，**原仓库无 LICENSE 文件**）
- **工具**：`unclebob/crapper` · `unclebob/dryer` · `unclebob/mutator` · `unclebob/uml-viewer`
  —— 全部 **BSD Zero Clause License (0BSD)**，Copyright (C) 2026 Robert C. Martin
- **上游衍生**：crapper 承 crap4clj / crap4java / crap4go；dryer 承 dry4clj；
  mutator 承 clj-mutate / mutate4go / mutate4java —— 均出自同一作者
- **理念参考**：`@poteto` 的 poteto-mode / pstack 规则（**原仓库已不可访问**，ub-mode 自述"loosely based on portions of"）
- 本 Skill 为**方法论与工具链封装**，遵循 0BSD 的宽松条款重新分发
