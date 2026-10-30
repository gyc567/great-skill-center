# 规则溯源：ub-mode ← pstack ← Uncle Bob

> ub-mode 的纪律不是凭空来的。这份文档把三个来源的关系查清楚，
> 避免把 poteto / Lauren Tan 的规则误称为 Robert C. Martin 的原创。

---

## 一、三个来源

| 来源 | 地址 | 许可 | 作者 | 角色 |
|------|------|------|------|------|
| **pstack** | `github.com/cursor/plugins` → `pstack/` | **MIT**（`plugin.json` 明示） | **poteto = Lauren Tan**（Cursor React Compiler 团队） | **规则原始出处** |
| **ub-mode** | `github.com/unclebob/ub-mode` | ⚠️ **无 LICENSE** | **Robert C. Martin** | **浓缩版 + 工具绑定** |
| **三个质量门工具** | `github.com/unclebob/{crapper,dryer,mutator}` | **0BSD** | Robert C. Martin | **Uncle Bob 原创** |

> ⚠️ **poteto 的 `pstack` 独立仓库已 404**（`github.com/poteto/pstack` 与
> `github.com/poteto/poteto-mode` 均不可访问）。但 pstack 的完整源码
> **作为官方插件收录在 `github.com/cursor/plugins` 仓库里**（`pstack/` 目录），
> 版本 0.15.36，MIT 许可。**这就是溯源的可验证锚点。**

---

## 二、ub-mode 自述的来源

ub-mode 的 README 第 3 个 commit（`826dab6`，2026-10-25，作者本人）写得清清楚楚：

> `ub-mode` … **is loosely based on portions of @poteto's rules** (`poteto-mode` / `pstack`),
> **reduced** and paired with deterministic quality-gate tools

两个关键词：

- **loosely based on portions** —— 部分改编，不是全部照搬
- **reduced** —— 浓缩

### ub-mode 完整提交历史（4 个 commit，同一天）

```
7d7720c | 2026-10-25 | Robert C. Martin | Initial commit of ub-mode skill
ff4e602 | 2026-10-25 | Robert C. Martin | Document companion tool repositories in README
826dab6 | 2026-10-25 | Robert C. Martin | Note that ub-mode is loosely based on portions of @poteto's rules
57a8bdd | 2026-10-25 | Robert C. Martin | Remove crap4clj and clj-mutate references from README
```

**全部 4 个 commit 都在 2026-10-25** —— ub-mode 是 pstack 之后一次性提炼出来的快照。

---

## 三、逐条比对：24 条原则的精确映射

pstack 有 **24 个** `principle-*` skill。ub-mode 有 **24 条**原则（去掉 3 个阶段标题 + Architecture 容器标题）。

### ✅ 15 条完全对应（pstack 有 principle skill，ub-mode 同名）

| pstack skill | ub-mode 原则 | 阶段 |
|---|---|---|
| principle-laziness-protocol | Laziness Protocol | First Make it Work |
| principle-foundational-thinking | Foundational Thinking | First Make it Work |
| principle-redesign-from-first-principles | Redesign From First Principles | First Make it Work |
| principle-attack-the-premise | Attack the Premise | First Make it Work |
| principle-subtract-before-you-add | Subtract Before You Add | First Make it Work |
| principle-outcome-oriented-execution | Outcome-Oriented Execution | First Make it Work |
| principle-build-the-lever | Build the Lever | First Make it Work |
| principle-model-the-domain | Model the Domain | Architecture |
| principle-boundary-discipline | Boundary Discipline | Architecture |
| principle-type-system-discipline | Type System Discipline | Architecture |
| principle-make-operations-idempotent | Make Operations Idempotent | Architecture |
| principle-separate-before-serializing-shared-state | Separate Before Serializing Shared State | Architecture |
| principle-fix-root-causes | Fix Root Causes | Then Make it Right |
| principle-sequence-verifiable-units | Sequence work into verifiable units | Then Make it Right |
| principle-test-behavior-not-implementation | Test Behavior, Not Implementation | Then Make it Right |
| principle-guard-the-context-window | Guard the Context Window | Practice |

### 🔁 3 条措辞不同但对应同一原则

| ub-mode | pstack | 说明 |
|---|---|---|
| **TDD** | `Prove It Works` + `Sequence Work into Verifiable Units` | ub-mode 把测试驱动提到了更前面 |
| **Refactoring** | `poteto-mode/playbooks/refactoring.md` | pstack 把它放在 playbook 而非 principle |
| **Worktree Cleanup** | `poteto-mode/playbooks/worktree-cleanup.md` | 同上 |

### ⭐ 3 条是 Uncle Bob 原创（pstack 完全没有）

| ub-mode 原则 | 说明 |
|---|---|
| **Crapper** | pstack 完全没有。ub-mode 引入 `CRAP < 10` 硬阈值 |
| **Dryer** | pstack 完全没有。ub-mode 引入重复率 `< 0.8` 硬阈值 |
| **Mutator** | pstack 完全没有。ub-mode 引入变异测试（覆盖盲区、存活变异体、删死代码） |

**这就是 ub-mode 真正的差异化价值：把抽象原则绑定到三个确定性工具上。**
pstack 的 24 条是「应该怎样想」，ub-mode 补上了「怎样量化验证」。

### ➕ 3 条 pstack 有但 ub-mode 未收录（pstack 的 24 − ub-mode 的 24）

| pstack 原则 | 一句话 |
|---|---|
| **Minimize Reader Load** | 读者的认知负荷（层数 + 状态）才是真的复杂度，LOC/CC 都只是代理指标 |
| **Experience First** | 实现便利 vs 用户体验冲突时，选用户体验 |
| **Exhaust the Design Space** | 没有先例时做 2–3 个竞争原型再选 |
| **Explain the Number** | 报数字前先说清「为什么不是双倍」，并排除它测的是别的东西 |
| **Migrate Callers Then Delete Legacy APIs** | 迁移调用方的同一波里删掉旧 API，不留兼容层 |
| **Prove It Works** | 验证真实产物，不信代理指标、不信自我报告、不信「能编译」 |
| **Never Block on the Human** | 可逆的工作直接做再汇报；不可逆的（force-push、删生产数据）才要确认 |
| **Encode Lessons in Structure** | 说第二遍的建议应该固化成 lint / 检查 / 脚本，而不是更多文字 |

> 💡 **这 8 条是本商品化版本的增值内容** —— ub-mode 没收录，
> 但它们与 Uncle Bob 的纪律完全同源（同一份 pstack，MIT 许可），
> 且能补足 ub-mode 的空白（尤其 **Explain the Number** 与 **Prove It Works**，
> 直接对应「不要相信没验证的数字」——这与三个质量门工具的精神一致）。

---

## 四、浓缩程度对比

**pstack 原文**（`principle-laziness-protocol/SKILL.md`，全 605 字节）：

```markdown
# Laziness Protocol

- **Consolidate decisions.** Do not repeat the same choice in several places. Put it behind
  one source of truth and pass the result as a simple flag.
- **Minimize the diff.** Make the smallest change that solves the problem. Fewer lines
  beat "elegant" boilerplate.
```

**ub-mode 浓缩版**（同一条，2 个 bullet）：

```markdown
## Laziness Protocol

* One decision lives in one place.
* Ship the smallest edit that solves the problem.
```

散文式 → bullet 式，**保留了全部语义，砍掉了修辞**。这是典型的 "reduced"。

---

## 五、许可边界（重要）

| 组件 | 许可 | 可商用？ | 能否原文搬运 |
|---|---|---|---|
| pstack 原则 | **MIT**（明文） | ✅ 可以 | ✅ 可以，保留版权声明 |
| crapper / dryer / mutator | **0BSD** | ✅ 可以 | ✅ 可以 |
| **ub-mode 本体** | ⚠️ **无 LICENSE 文件** | ❌ **不确定** | ❌ **不应直接原文搬运** |

### GitHub API 判定记录

```
unclebob/ub-mode      license = None   ← 无 LICENSE
unclebob/crapper      license = 0BSD
unclebob/dryer        license = 0BSD
unclebob/mutator      license = 0BSD
cursor/plugins        license = None   ← 根目录无 LICENSE，但 pstack/plugin.json 明示 MIT
poteto/pstack         HTTP 404        ← 独立仓库已不存在
poteto/poteto-mode    HTTP 404        ← 同上
```

### 本商品化版本的做法

- ❌ **不**逐字复制 ub-mode 的 SKILL.md
- ✅ **引用** pstack 的 MIT 原则（MIT 允许，保留声明）
- ✅ **引用** 三个 0BSD 工具的用法与阈值
- ✅ 重新组织为**可执行的纪律 + 可验证的工具流程**
- ✅ 明确标注每一部分的来源与作者

**这就是为什么本 Skill 不叫 `ub-mode` 而叫 `ub-quality-gates`** ——
它卖的是「三道确定性质量门 + 纪律执行流程」，不是 ub-mode 的原文副本。

---

## 六、正确署名写法

推荐：

> 本 Skill 的纪律框架融合了 **Robert C. Martin**（Uncle Bob）的 ub-mode
> 与 **poteto（Lauren Tan）** 的 pstack 原则集，并绑定 Uncle Bob 的
> 三个 0BSD 质量门工具。

**不要写**：

> ❌ 「Uncle Bob 的 24 条原创原则」—— 其中 15 条来自 pstack
> ❌ 「Robert C. Martin 提出的 CRAP 阈值」—— CRAP 指标本身源于
>    Microsoft Research 的 Research:CRAP 论文，工具实现是 Uncle Bob 的

---

## 七、事实速查

| 事实 | 值 |
|------|-----|
| pstack 作者 | poteto / Lauren Tan（Cursor，React Compiler 团队，Meta / Netflix 经历） |
| pstack 版本 | 0.15.36 |
| pstack 原则数 | 24 |
| ub-mode 原则数 | 24（15 条同名对应 + 3 条措辞差异 + 3 条工具原创 + 3 条 playbook 衍生） |
| pstack 独有（ub-mode 未收） | 8 条 |
| ub-mode 独有（pstack 没有） | Crapper / Dryer / Mutator 三条工具纪律 |
| ub-mode 星数（2026-10-30） | ⭐ 4,692（创建后 5 天） |
| cursor/plugins 星数 | ⭐ 14,587 |
| pstack 独立仓库 | ❌ 404，源码在 cursor/plugins |

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
