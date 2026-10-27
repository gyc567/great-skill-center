# 质量门工具详解

> crapper / dryer / mutator / uml-viewer 四件套的完整参考。
> 全部 0BSD 许可，Copyright (C) 2026 Robert C. Martin。

---

## 1. crapper — CRAP 评分

### 公式

```
CRAP = CC² × (1 − coverage)³ + CC
```

- `CC` = 圈复杂度（cyclomatic complexity）
- `coverage` = 测试覆盖该函数的比例（0–1）
- 系数 `³` 让高复杂度 + 低覆盖的惩罚极重

### 手工验算

| CC | 覆盖率 | CRAP | 计算 |
|----|--------|------|------|
| 14 | 0% | **210.0** | 14²×1 + 14 = 210 |
| 6 | 0% | 42.0 | 36 + 6 |
| 4 | 0% | 20.0 | 16 + 4 |
| 1 | 100% | **1.0** | 1×0 + 1 |
| 3 | 14.3% | 8.7 | 9×0.577 + 3 |

### 风险分级

| 区间 | 风险 | 处置 |
|------|------|------|
| 1–5 | 低 | 通过 |
| 5–30 | 中 | 值得看一眼 |
| 30+ | 高 | 复杂且欠测，必须处理 |
| **> 10** | **ub-mode 门禁** | **不允许合并** |

### 支持语言与文件扩展名

| 语言 | 扩展名 |
|------|--------|
| Clojure | `.clj` `.cljc` `.cljs` `.bb` |
| Java | `.java` |
| Go | `.go` |
| TypeScript / JavaScript | `.ts` `.tsx` `.mts` `.cts` `.js` `.jsx` `.mjs` `.cjs` |
| Rust | `.rs` |
| Python | `.py` |

### 自动跳过的目录

```
.clj-kondo .git .hg .idea .metrics .svn .venv __pycache__
__tests__ build coverage dist node_modules out spec specs
target test testdata tests vendor venv
```

> ⚠️ **注意**：`test` / `tests` / `spec` 被跳过，所以覆盖率工具会自己去找测试。
> 想分析测试文件要**显式点名路径**。

### 关键参数

```bash
./crapper                          # 全项目
./crapper --no-coverage            # 只算复杂度（快，适合编辑器实时提示）
./crapper --use-existing-coverage  # 复用磁盘已有覆盖率，不重跑测试
./crapper --changed                # 只分析 git 新增/修改
./crapper src/demo src/ui         # 指定路径
./crapper combat                   # 路径片段过滤
./crapper --threshold 30           # 最高分超 30 时 exit 2
./crapper --coverage-command "..." # 自定义覆盖率命令
```

### 输出

**stdout**（按最差排序）：

```
CRAP Report
===========
Languages: go, python, typescript

Function                       Namespace          CC    Cov%     CRAP
---------------------------------------------------------
classify                       complex            14   0.0%     210.0
```

**`.metrics/crap.edn`**：

```clojure
{:entries [{:name "classify"
            :namespace "complex"
            :complexity 14
            :coverage 0.0
            :crap 210.0}]}
```

`nil` coverage 表示用了 `--no-coverage`，此时 CRAP 也是 `nil`。
**覆盖率报告里没提到的函数 = 0%**。

### 覆盖率命令（按语言自动选择）

| 语言 | 工具 |
|------|------|
| Python | `coverage` → lcov |
| Java | JaCoCo |
| Go | `go test -cover` |
| TypeScript | Jest / Vitest |
| Rust | `cargo llvm-cov` |
| Clojure | Cloverage |

可用 `--coverage-command` 覆盖。

---

## 2. dryer — 重复代码检测

### 算法

**Jaccard 相似度**（与 dry4clj 同一算法）：

```
score = 共享结构指纹数 / 两个形式出现过的全部指纹数
```

### 归一化规则

**保留**（结构特征）：

- 函数/方法名
- 运算符
- 树形结构
- 调用链形状

**丢弃**（偶然差异）：

- 局部变量名
- 字段名
- 字面量
- 关键字

### 例子

这两个函数得分 **1.0**（名字、局部变量、谓词、映射函数全不同）：

```clojure
(defn alpha [xs]
  (let [ys (filter odd? xs)]
    (map inc ys)))

(defn beta [items]
  (let [kept (filter even? items)]
    (map dec kept)))
```

```java
int alpha(int[] xs) {
  int[] ys = filter(xs, odd);
  return map(ys, inc);
}
```

```python
def beta(items):
    kept = filter(items, even)
    return map(kept, dec)
```

`(:kind m)` 与 `(:id row)` 是同一形状；`order.total` 与 `row.amount` 也是。

### 默认阈值

| 参数 | 默认 | 说明 |
|------|------|------|
| `--threshold N` | **0.82** | 最小相似度 |
| `--min-lines N` | 4 | 最小行数 |
| `--min-nodes N` | 20 | 最小归一化节点数 |

> 上面的 `alpha`/`beta` 例子虽然 1.0 分，但**默认跑不到** —— 它们只有 3 行，
> 低于 `--min-lines 4`。要抓这类小重复：`-–min-lines 3 --min-nodes 15`。

### 各语言比较单位

| 语言 | 比较单位 | 排除 |
|------|---------|------|
| Clojure | 每个顶层 form（`ns` 除外） | 非 `:clj` 的 reader-conditional 分支 |
| Java | 有方法体的方法 | 构造器、抽象方法、匿名/局部类内的方法 |
| Go | 有函数体的函数和方法 | 函数字面量留在外层函数内 |
| TypeScript | 函数、方法 | — |
| Rust | 函数、方法 | — |
| Python | 函数、方法 | — |

**只和同语言的形式比较。**

### 输出

```
DUPLICATE score=1.00
  src/complex.py:28-35
  src/complex.py:37-44
```

`.metrics/dry.edn`：

```clojure
{:candidates
 [{:score 0.890909090909
   :language "clojure"
   :left {:file "src/billing/invoice.clj", :start-line 3, :end-line 13}
   :right {:file "src/billing/receipt.clj", :start-line 3, :end-line 14}
   :left-nodes 158
   :right-nodes 166}]}
```

---

## 3. mutator — 变异测试

### 原理

改动源文件里的**一个可变异点**（运算符、边界值、常量），然后跑测试：

| 结果 | 含义 |
|------|------|
| **KILLED** | 测试失败 → 这个变异被抓住 ✅ |
| **SURVIVED** | 测试仍通过 → **测试没抓住这个 bug** ⚠️ |
| **UNCOVERED** | 覆盖率报告没命中这行 → 不跑 |

**存活变异体 = 你的测试套件的盲区。**

### 变异规则（按语言）

| 运算符 | 变异 |
|--------|------|
| `>` | `>=` |
| `<` | `<=` |
| `>=` | `>` |
| `<=` | `<` |
| `==` | `!=` |
| `!=` | `==` |
| `and` | `or` |
| `or` | `and` |
| `&&` | `\|\|` |
| `\|\|` | `&&` |
| `+` | `-` |
| `*` | `/` |
| `0` | `1` |
| `1` | `0` |

### 差分运行（关键特性）

**快照存在时默认是差分的**：

- 重跑**存活**的变异体
- 重跑**文本有变化**的函数里的所有变异点
- 未变函数里已 killed 的**不再重跑**

`--mutate-all` 忽略差分，全部重跑。`--since-last-run` 显式指定差分行为。

### Worker 模型

- 同一文件的变异体**并行**跑；默认每核一个 worker
- `--max-workers` 设上限；实际取 `min(上限, 核数, 选中点数)`
- **文件仍是一个一个处理**
- 每个 worker 是 `target/mutation-workers` 下的目录
  - 被变异的文件是**私有副本**
  - 通过相对导入到达该文件的模块也**被复制**，让 Node 解析到私有副本
  - 树的其他部分**软链接**
  - **原始文件不动**
  - 该文件的变异体跑完后 overlay 被删除
- **基线**测试在真实树上**先跑一次**，然后 worker 才启动
- 变异命令在 worker 内跑，cwd 与真实树相同，相对路径（如 `src`、`./pkg`）指向 overlay
- 旧版本中断残留的 `target/mutator-backup/` 副本会在非 scan 运行时被还原

### 命名空间与函数名来源

**必须从 crapper 来**（`mutator` 依赖同级的 `crapper`）。命名规则：

| 语言 | `:namespace` | `:name` |
|------|-------------|---------|
| Clojure | `ns` | `defn` / `defn-` 名字 |
| Java | `package.Class` | 方法名 |
| Go | 包导入路径 或 `import/path.Receiver` | 函数/方法名 |
| TypeScript | 点分模块路径 或 `module.Class` | 函数/方法名 |
| Rust | `crate::module` 或 `crate::module::Type` | 函数/方法名 |
| Python | 点分模块路径 或 `module.Class` | 函数/方法名 |

`defn-` 是 Clojure 的私有形式。

### 输出

```
Function            Namespace  Killed  Survived  Uncovered  Sites   Score
-------------------------------------------------------------------------
classify            complex         1        10          8     19   9.1%
simple_add          complex         1         0          0      1  100.0%
```

**Score = killed / (killed + survived)** —— 存活算分母，uncovered 不算。

`.metrics/mutate/<namespace>.edn`：

```clojure
{:version 1
 :source "src/demo/board.py"
 :namespace "demo.board.Board"
 :outcomes {"[\"src/demo/board.py\",\"demo.board.Board\",\"defn/place\",10,11,\">\",\">=\"]" :survived}
 :forms [{:id "defn/place"
          :kind "defn"
          :file "src/demo/board.py"
          :line 2
          :end-line 4
          :hash "…"
          :killed 1
          :survived 1
          :uncovered 0
          :sites 2}]}
```

`:sites` 是函数内**全部**变异点（含 uncovered）。为 0 时 uml-viewer 显示 `---no mutation sites---`。

### 退出码

| 码 | 含义 |
|----|------|
| 0 | 全部执行的变异体都被 killed |
| 2 | **基线测试失败** |
| 3 | **有变异体存活** |

基线失败时**不会重写快照**。

---

## 4. uml-viewer — 可视化

- 活 UML 类图查看器，由 EDN 驱动
- 按 `:namespace` 分组，把 `:name` 拼到每个 operation
- 画组件、覆盖率、CRAP、变异分数、依赖方向
- 依赖 **Clojure + Quil**（`DEPS` 里有 `quil/quil`），需要本机有 JVM 工具链
- 加载器脚本 `uml` 期待 `../uml-viewer` 同级目录，或设 `UML_VIEWER_ROOT` 环境变量

> 💡 只想要门禁数字的话，**不需要装 uml-viewer**。它只是可视化层。

---

## 5. 三门组合的正确使用顺序

```
1. crapper  →  找复杂度高且没测到的函数
        ↓
2. dryer    →  找该拆的结构性重复
        ↓
3. mutator  →  验证测试到底抓不抓得住
```

**典型闭环**：

```
crapper 报  classify  CC=14, cov=22%, CRAP=106.2
    ↓
拆分 classify → 三个小函数，各自 CRAP < 10
    ↓
mutator 报  1 killed / 10 survived / 8 uncovered
    ↓
补测试覆盖那 10 个存活点 → 全部 killed
    ↓
dryer 报    两处结构相似 0.89
    ↓
抽公共函数 → 重复消失
```

**门禁线**：`crapper --threshold 10` 返回 2 = 不允许合并。


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
