---
name: free-model-router
description: >
  发现并安全使用 OpenRouter 零成本模型，为子代理（child agent）配置免费模型路由。
  当用户提到 OpenRouter、Pi、免费 token、免费模型、免费模型路由、零成本模型、
  子代理省 token 时触发。含 fail-closed 解析、参数量核验、工具调用探测与 Pi 集成。
license: MIT
author: ERIC AI技术专家，专注于人工智能和自动化工具的研究与应用
brand: AI Skills 创作小店
version: 1.0.0
---

# 免费模型路由大师 (free-model-router)

> 每天扫描 OpenRouter 免费模型，fail-closed 地给子代理配「零花费」路由。
> 品牌化改造：AI Skills 创作小店
> 上游：`limin112/min-skill` 的 `FreeToken-Bots`（作者 limin112 / @MinLiBuilds）

---

## ⚠️ 三条铁律

### 1. 免费的定义是**双重零价**

```
pricing.prompt == 0  且  pricing.completion == 0
且显式的 request / input_cache_read / input_cache_write 也必须为 0
```

**免费资格是动态的** —— OpenRouter 会随时下架或给免费模型重新定价。
所以名单**必须每天刷新**，过期名单绝不能授权调用。

### 2. 只信**已核实**的参数量

只有**已核实**总参数量 ≥ 100B 的模型才进 approved 池。

> 🚫 **绝不**从模型名字、上下文长度、模型家族推测参数量。
> 🚫 **绝不**把「名字里写着 550b」当作核实 —— 那只是线索。
> OpenRouter 的 `/models` 目录**不提供**结构化参数字段（实测 464 个模型、19 个免费、
> 0 个带参数字段），所以 `eligible` 为空是**正常且正确**的行为。
> 参数量必须**人工核实**（方法见下方 references）。

### 3. 绝不自动路由到付费模型

- 手输的模型 ID 一律不信 —— 必须对最新扫描结果做 **fail-closed 解析**
- 缺 `:free` 后缀时**自动纠正 + 大声告警**（静默丢掉 `:free` 会路由到**同一模型的付费版**）
- 402、配额耗尽、限流，**都不是**移除用户已有 Pi 配置的理由
- 绝不在 Git 里放 key，绝不打印 key 值

---

## 🚀 快速开始

```bash
# 0. 装 Pi（前置，缺一不可）
curl -fsSL https://pi.dev/install.sh | sh
# 或：npm install -g @earendil-works/pi-coding-agent   （需 Node ≥ 22.19）
pi --version

# 1. 环境体检
python3 scripts/radar.py doctor

# 2. 扫描免费模型
python3 scripts/radar.py scan

# 3. 看 Pi 已有哪些可用（关键：OpenRouter 是 Pi 内置 provider）
python3 scripts/radar.py pi-models

# 4. 探针（需要 OPENROUTER_API_KEY）
OPENROUTER_API_KEY=... python3 scripts/radar.py probe --model 'cohere/north-mini-code:free'
OPENROUTER_API_KEY=... python3 scripts/radar.py probe-tools --model 'cohere/north-mini-code:free'

# 5. 生成 Pi 同步提案
python3 scripts/radar.py sync --dry-run
```

---

## 💡 关键洞察：OpenRouter 是 Pi 的**内置 provider**

**这是本 Skill 最重要的发现，也是上游版本没讲透的。**

Pi（`@earendil-works/pi-coding-agent`，MIT）**内置**了 OpenRouter provider。
配好 `OPENROUTER_API_KEY` 后，`pi --list-models` 会**自动列出**全部可用模型：

```
provider    model                          context  max-out  thinking
openrouter  ~anthropic/claude-opus-latest  1M       128K     yes
openrouter  nvidia/nemotron-3-ultra-550b-a55b:free  1.0M  128K  yes
...
```

**实测数据**（本机 2026-10-28）：

| 指标 | 数值 |
|------|------|
| OpenRouter 目录总模型 | 464 |
| 免费模型 | 19 |
| Pi 列出的 OpenRouter 模型 | **401** |
| 免费模型 ∩ Pi 已列出 | **16** |
| 免费但 Pi 未列出 | 3（`google/lyria-3-*` 音频、`nvidia/nemotron-3.5-content-safety:free` 安全分类模型 —— **非聊天模型**） |

**结论：绝大多数情况下根本不需要改 `models.json`。**
上游 Skill 说的「sync 需要验证 Pi schema」是**保守且过时的**判断 ——
`sync` 现在只输出提案，标注 `openrouter_is_builtin_provider: true`，
`proposed_additions` 通常是空数组。

---

## 📊 三个池子

| 池子 | 含义 | 能否进 Pi 同步 |
|------|------|--------------|
| `eligible` | 免费 + tools + **已核实** ≥100B | ✅ 首选 |
| `needs_parameter_verification` | 免费 + tools，但**参数量未核实** | ⚠️ 需人工核实后手动放行 |
| `free_ids` | 所有免费模型的精确 ID | 仅作解析白名单 |

**`needs_parameter_verification` 里的 `size_hint_b` 只是线索**（从 ID 里的 `550b` 读出），
**不能**当作核实结果。

---

## 🔍 参数量核验方法

因为 OpenRouter 目录不给结构化参数字段，人工核验是必经环节。**按可信度排序**：

| 优先级 | 来源 | 可信度 |
|--------|------|--------|
| 1 | 官方模型卡 / 技术报告 | ⭐⭐⭐ 最高 |
| 2 | 厂商文档页（model card、API 文档） | ⭐⭐⭐ |
| 3 | HuggingFace 仓库的 `config.json`（`num_parameters` / `hidden_size × layers`） | ⭐⭐ |
| 4 | 第三方模型数据库 | ⭐ 需交叉验证 |

### HuggingFace 快速核验

```bash
# 通用：看 config.json 里的结构
curl -sL https://huggingface.co/<org>/<model>/raw/main/config.json | \
  python3 -c "import json,sys; c=json.load(sys.stdin); print({k:c.get(k) for k in ['model_type','hidden_size','num_hidden_layers','num_attention_heads','vocab_size','intermediate_size']})"

# 部分模型直接给总参数
curl -sL https://huggingface.co/<org>/<model>/raw/main/config.json | \
  python3 -c "import json,sys; c=json.load(sys.stdin); print(c.get('num_parameters'))"
```

**粗算公式**（仅当没有 `num_parameters` 时）：

```
params ≈ 12 × L × H²      （L = 层数, H = hidden_size，fp16 训练常用近似）
```

> ⚠️ 粗算只能**排除**明显不合格的模型，不能作为「已核实」的依据。
> 满足 100B 门槛时，仍需官方来源确认。

### 核验后写回

```bash
# 人工核实后，把已核实的模型登记到 approved 池
python3 - <<'PY'
import json, pathlib, datetime as dt
p = pathlib.Path.home()/'.pi'/'agent'/'freetoken-bots.json'
d = json.loads(p.read_text())
verified = {'nvidia/nemotron-3-ultra-550b-a55b:free': 550.0}   # ← 你核实过的
d['eligible'] = [{'id': k, 'parameters_b': v,
                  'context_length': 262144, 'verified_at': dt.datetime.now().isoformat()}
                 for k, v in verified.items()]
d['needs_parameter_verification'] = [
    m for m in d['needs_parameter_verification'] if m['id'] not in verified]
p.write_text(json.dumps(d, indent=2, ensure_ascii=False))
print('approved 池已更新:', len(d['eligible']))
PY
```

---

## 🧪 探针：普通对话 ≠ 工具支持

**普通 completion 探针不能证明模型支持工具调用。**
子代理候选必须**单独**探测真实 tool call：

```bash
OPENROUTER_API_KEY=... python3 scripts/radar.py probe-tools --model 'xxx:free'
```

返回：

```json
{
  "ok": true,
  "tool_called": true,
  "function": "get_weather",
  "model": "xxx:free",
  "classification": "ok"
}
```

`tool_called: false` 表示模型答了话但没调工具 —— **工具支持未获证明**，不能进子代理池。

### 错误分类（区分临时 vs 硬性）

| `classification` | 含义 | 动作 |
|------------------|------|------|
| `ok` | 正常 | 可用 |
| `rate_limited_temporary` | 429 临时限流 | 稍后重试，**不要**标记模型不可用 |
| `quota_exhausted` | 429 且配额耗尽 | 当天的免费额度用完 |
| `payment_required` | 402 | 免费资格已失效 |
| `unauthorized` | 401 | key 有问题 |

> 💡 **不要**因为一次 429 就把模型从名单里删掉。
> ChatGPT 里的提醒/看护**不能**修改那台机器 —— 必须确认是持续性错误才能标记不可用。

---

## 🔒 fail-closed 模型解析

```
用户给的 ID ──┬─ 精确匹配 free_ids ────────────→ 原样使用
               ├─ 缺 :free，补后缀后匹配 ───────→ 自动纠正 + 大声告警
               └─ 其他 ─────────────────────────→ 抛 NotFreeError，拒绝探针
```

实测：

```
$ python3 scripts/radar.py probe --model 'x/paid-model'
error: "x/paid-model" is not a verified-free OpenRouter model ID.
Probe refused: calling it could incur charges.
EXIT=2

$ python3 scripts/radar.py probe --model 'cohere/north-mini-code'
WARNING: "cohere/north-mini-code" is not a verified-free model ID;
using verified-free "cohere/north-mini-code:free" instead.
Calling "cohere/north-mini-code" directly would use the PAID variant.
```

---

## ⏰ 定时扫描（必须配，不是可选）

**这个 Skill 自己不会扫描。** 免费模型名单会过期。

```cron
0 8 * * * /usr/bin/python3 /绝对路径/scripts/radar.py scan
```

> **安装时必须明确告诉用户**：
> 「这个 skill 需要每天早上 8 点跑一次扫描定时任务，不配的话免费名单会过期，它自己不会动。」

每次运行要比对上一次报告，**明确报出**：

- 🆕 新上架的免费模型
- ❌ 下架的模型
- 💰 重新定价（不再免费）的模型
- 🔄 `eligible` 池的变化

---

## 🧩 Pi 集成工作流

| 步 | 动作 |
|----|------|
| 0 | 确认 `pi` 在 PATH 且 `pi --version` 正常 |
| 1 | 检查 `~/.pi/agent/settings.json`、`models.json`，以及 `pi --list-models`（**不泄露 key**） |
| 2 | 扫描；从可信文档核实参数量；**只有已核实的 ≥100B** 才进 approved 池 |
| 3 | 探针：先普通对话，**再单独探真实 tool call**；区分 429 临时限流与硬性配额耗尽 |
| 4 | 核对模型 ID、provider 兼容性、context/max-token；**生成 diff，不覆盖** Ling 自定义 provider 或 `enabledModels` |
| 5 | **必须获得用户明确批准**再应用；先备份 → 原子写 → `python3 -m json.tool` 校验 → `pi --list-models` → `pi -p 'say pong' --no-extensions </dev/null`；失败则回滚 |
| 6 | Muse/Grokbot/Dot 用受控 shell 子代理调用；先确认宿主机支持执行本地 Pi 命令、共享工作区访问和结果捕获；**绝不在没有鉴权的情况下把 Pi 的 shell/API 暴露到公网** |
| 7 | 大任务前**问用户用哪个模型**；自动回退必须用户先 opt-in；**结果不确定时绝不重放有副作用的动作** |

**所有无人值守的 `pi -p` 调用必须用 `</dev/null`。**

---

## 📁 命令速查

| 命令 | 作用 |
|------|------|
| `radar.py doctor` | 环境体检：Pi 在不在、缓存新不新、有没有 key、免费名单多少 |
| `radar.py scan` | 扫描 OpenRouter 免费模型，写 `~/.pi/agent/freetoken-bots.json`（0600） |
| `radar.py status` | 打印当前报告 |
| `radar.py probe --model ID` | 普通对话探针（fail-closed 解析） |
| `radar.py probe-tools --model ID` | 真实工具调用探针 |
| `radar.py pi-models` | 列出 Pi 可用模型 + 与免费名单的交集 |
| `radar.py sync --dry-run` | 生成 Pi 同步提案（**不写盘**） |

**报告文件**：`~/.pi/agent/freetoken-bots.json`，权限 **0600**，原子写（临时文件 + `os.replace` + `fsync`）。

---

## ⚠️ 实测坑点

| # | 坑 | 解法 |
|---|-----|------|
| 1 | **`eligible` 永远为空** | 正常！OpenRouter `/models` 不给参数字段，必须人工核实（见上方方法） |
| 2 | **Pi 二进制在云主机会丢** | `~/.pi/agent/` 配置保留，`pi` 不在 PATH 就重装 |
| 3 | **`pi --list-models` 需要 key** | 无 key 时 Pi 列全部模型；有 key 时只列该 key 可用的 |
| 4 | **未列出的免费模型** | 3 个是音频/安全分类模型，**非聊天模型**，子代理用不上 |
| 5 | **网络抖动导致 scan 挂起** | 已加重试（2 次，指数退避）；sync 优先用缓存 |
| 6 | **手输 ID 少 `:free`** | 自动纠正 + 告警；**静默丢掉会扣费** |
| 7 | **429 不等于模型挂了** | 看 `classification`，区分临时限流与配额耗尽 |
| 8 | **文件权限** | 报告必须 0600；原子写不落临时文件 |
| 9 | **上游仓库无 LICENSE 文件** | `.claude-plugin` 声明 MIT，但根目录无 LICENSE —— 商业化前需确认 |
| 10 | **不要照抄上游 sync 的悲观判断** | OpenRouter 是 Pi 内置 provider，`proposed_additions` 通常为空 |

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

- 上游：`limin112/min-skill` → `skills/FreeToken-Bots`（作者 limin112 / @MinLiBuilds）
  - 上游 `.claude-plugin/plugin.json` 声明 **MIT**；但仓库根目录**无 LICENSE 文件** —— 商业化前建议向作者确认
  - 上游版本 v0.2.0
- 依赖运行时：**Pi**（`@earendil-works/pi-coding-agent`，**MIT**，Node ≥ 22.19）
- API：OpenRouter 公开目录（`/api/v1/models`，无需 key）
- 本 Skill 为方法论与脚本封装，保留上游 fail-closed 设计理念并补完参数量核验、工具探测、Pi 内置 provider 集成
