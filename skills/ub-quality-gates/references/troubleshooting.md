# 排障手册

> 实测中真实踩过的坑。按症状查。

---

## A. 环境与安装

### A1. `ImportError: cannot import name 'crapper' from mutator`

**原因**：`mutator` 的函数名和命名空间**全部来自 `crapper`**（`src/mutator/crapper_link.py` 的 `ensure_crapper`）。

**解法**：

```bash
# mutator 和 crapper 必须是同级目录
cd ~/repos
git clone https://github.com/unclebob/crapper.git
git clone https://github.com/unclebob/mutator.git
cd mutator
python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/pip install -e ../crapper     # ← 关键
```

验证：

```bash
.venv/bin/python -c "from mutator.capper_link import ensure_crapper; ensure_crapper(); print('OK')"
```

### A2. `FileNotFoundError: '/path/to/crapper/uml'`

**原因**：`crapper` 仓库里的 `uml` 加载脚本找不到 `../uml-viewer`（Clojure 项目）。

**影响**：**只影响 crapper 的 2 个单元测试**（`test_project_snapshot_is_readable_as_crap4clj_edn`、
`test_uml_loader_rejects_a_missing_viewer`），不影响实际使用。

**解法**（二选一）：

```bash
# 1. 克隆 uml-viewer 到同级
git clone https://github.com/unclebob/uml-viewer.git
export UML_VIEWER_ROOT=~/repos/uml-viewer

# 2. 忽略这 2 个测试
.venv/bin/python -m pytest tests/ --deselect tests/test_cli.py::test_project_snapshot_is_readable_as_crap4clj_edn \
  --deselect tests/test_cli.py::test_uml_loader_rejects_a_missing_viewer
```

> uml-viewer 需要 **Clojure + Quil + JVM**，只要门禁数字的话不用装。

### A3. `pip install -e .` 报一堆 `hermes-agent requires X, which is not installed`

**这是正常的**。pip 在扫描系统 site-packages 时看到了 hermes 的依赖元数据，但我们在 `.venv` 里。

**判断依据**：只要最后出现 `Successfully installed ...` 就没事。真正的错误长这样：

```
ERROR: Could not find a version that satisfies the requirement xxx
```

### A4. `ModuleNotFoundError: No module named pip`

**原因**：某些 venv（如 hermes 自带的 `/root/hermes-agent/venv`）不带 pip。

**解法**：用标准 `python3 -m venv` 建的 venv；或 `python3 -m ensurepip` 补上。

### A5. `No module named coverage` / `Python coverage will score 0%`

**原因**：项目环境里没装 `coverage`。工具会**自动尝试安装**，失败就退化成 0% 覆盖率 —— 这会让 CRAP 分数虚高（因为 `(1-0)³=1`）。

**解法**：

```bash
cd 项目根
python3 -m pip install coverage
# 或用工具的自动安装路径
```

> ⚠️ **这会让 CRAP 分数失真**，别把 0% 当真值。

---

## B. 运行位置

### B1. `Skipping src/foo.py; it is outside <tool dir>`

**原因**：`mutator` **必须在项目根运行**。它把参数解析成相对项目根的路径。

**解法**：

```bash
cd 你的项目
/path/to/mutator/.venv/bin/python -m mutator src
```

> `crapper` 和 `dryer` 支持用 `--root` 指定项目根，位置宽松些；
> `mutator` 反而更严格。

### B2. dryer's `cd` 陷阱

同样建议在项目根跑：

```bash
cd 项目根 && /path/to/dryer/.venv/bin/python -m dryer
```

---

## C. 覆盖率

### C1. 全部显示 UNCOVERED

**原因**：覆盖率文件**位置不对**。工具只认这两个 glob：

```
target/coverage/**/lcov.info
coverage/**/lcov.info
```

**解法**：

```bash
# 手动生成到正确位置
cd 项目根
python3 -m coverage run --source=src -m pytest -q tests/
python3 -m coverage lcov -o target/coverage/python/lcov.info
```

或者用 `--coverage-command` 让你自己的命令写到正确位置。

### C2. `No go.mod; skipping Go coverage` / `No package.json; skipping TypeScript coverage`

**原因**：工具靠项目标志文件决定怎么跑对应语言的覆盖率。

**解法**：确保项目根有 `go.mod` / `package.json`，且测试命令能被工具猜到。
或者用 `--coverage-command` 显式指定。

### C3. Python rootdir 猜错导致 import 失败

**症状**：mutator 报 `Baseline failed for src/foo.py: ... No module named pytest`，
或 `ModuleNotFoundError: No module named 'src'`。

**解法**：项目根放 `pytest.ini`：

```ini
[pytest]
testpaths = tests
```

以及空的 `conftest.py`（让 pytest 把项目根加进 `sys.path`）。

### C4. lcov 路径是绝对路径但源码是相对路径

工具的 `_suffix_rank` 会做**路径后缀匹配**，所以 `/abs/path/src/foo.py` 和 `src/foo.py` 通常能对上。
如果还对不上，检查 lcov 里的 `SF:` 行是不是指向了真实文件。

---

## D. 阈值与退出码

### D1. CI 突然红：`exit 2`

**不是崩溃**。`crapper --threshold N` 在最高分超过 N 时**故意**返回 2。

| 工具 | 退出码 |
|------|--------|
| crapper | 0 正常 · **2 超阈值** |
| mutator | 0 全 killed · **2 基线失败** · **3 有存活** |
| dryer | 0 正常 |

### D2. mutator `exit 2` = 基线测试失败

**含义**：**不是**变异体的问题，是你**原本的测试就挂了**。

**解法**：先修好基线。基线失败时快照不会被重写。

### D3. dryer 找不到三行的重复

**原因**：默认 `--min-lines 4 --min-nodes 20`。

**解法**：

```bash
./dryer --min-lines 3 --min-nodes 15
```

### D4. CRAP 分数比预期高

检查两点：

1. **覆盖率是不是真的 0%**（见 A5）
2. **CC 是不是被高估** —— 复杂函数里的 `elif`/`and`/`or` 每个都加 1

公式是 `CC² × (1-cov)³ + CC`，**CC 的平方**让高复杂度惩罚极重。这是设计意图：
高复杂 + 欠测 = 必须重构。

---

## E. 快照与差分

### E1. mutator 每次都重跑全部变异体

**原因**：快照路径没找到，或 `.metrics/mutate/` 被清掉了。

**检查**：

```bash
ls -la .metrics/mutate/
```

快照按命名空间分文件，Java 有内部类、Go 有函数+方法时会写多个文件。

### E2. 改了函数但 mutator 没重跑它

**正常行为**。差分规则是"**文本有变化**的函数"才重跑。
如果你改了函数但文本没变（比如改了外部依赖），需要 `--mutate-all`。

### E3. Go 同包多个文件共享快照

Go 同一 package 的文件共享一份快照，重跑其中一个会保留另一个的形式。
这是有意的 —— 避免互相覆盖。

---

## F. 上游测试

### F1. `test.sh` 报 f-string 语法错误

**症状**：

```
SyntaxError: f-string expression part cannot include a backslash
```

**原因**：上游 `test.sh` 里的内联 Python 用了 f-string 里带反斜杠，这在 **Python 3.12+ 才是合法**的，
但 3.11 及以下非法。

**解法**：**别用 `test.sh`**，手动跑：

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/python -m pytest tests/ -q
.venv/bin/python -m ruff check .
.venv/bin/python -m mypy src/
```

> 官方实测：crapper 144 passed、dryer 80 passed、mutator 76 passed、ruff 通过、mypy 无 issue。

### F2. mutator 的 43 个测试失败

**几乎总是** A1（缺 crapper）。装上就好。

---

## G. 快速诊断清单

```bash
# 1. 工具能跑吗
/path/to/crapper/.venv/bin/python -m crapper --help

# 2. 依赖链接对吗
/path/to/mutator/.venv/bin/python -c "from mutator.crapper_link import ensure_crapper; ensure_crapper(); print('OK')"

# 3. 覆盖率文件在吗
ls target/coverage/**/lcov.info coverage/**/lcov.info 2>/dev/null

# 4. 变异点识别对吗（不跑测试）
cd 项目根 && /path/to/mutator/.venv/bin/python -m mutator --scan src

# 5. 语言识别对吗
cd 项目根 && /path/to/crapper/.venv/bin/python -m crapper --no-coverage src
```

---

## H. 一页速查

| 症状 | 一句话解法 |
|------|-----------|
| `cannot import name crapper` | mutator 里 `pip install -e ../crapper` |
| `it is outside <tool dir>` | `cd 项目根` 再跑 |
| 全部 UNCOVERED | lcov 放到 `target/coverage/**/lcov.info` |
| `No module named coverage` | 装 coverage，否则 CRAP 虚高 |
| `No module named pytest` | 项目根加 `pytest.ini` + `conftest.py` |
| exit 2 (crapper) | 超阈值 = 门禁生效 |
| exit 2 (mutator) | 基线测试挂了，先修测试 |
| exit 3 (mutator) | 有变异体存活 = 测试有盲区 |
| 找不到小重复 | `--min-lines 3 --min-nodes 15` |
| `test.sh` 语法错 | 手动 pytest，别用 test.sh |
| CRAP 高得离谱 | 先确认覆盖率不是假的 0% |


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
