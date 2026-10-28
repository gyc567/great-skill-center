# 参数量核验手册

> 为什么需要它：OpenRouter 的 `/models` 目录**不提供**结构化参数字段。
> 实测 2026-10-28：464 个模型、19 个免费、**0 个**带 `total_parameters` 或 `parameter_count`。
> 所以 `eligible` 池天然为空 —— 这是 fail-closed 设计的**正确**表现，不是 bug。

---

## 为什么要 ≥100B

| 规模 | 定位 | 子代理适用性 |
|------|------|-------------|
| < 10B | 边缘模型 | ❌ 工具调用和多步规划不可靠 |
| 10B–100B | 小型/中端 | ⚠️ 勉强可用，复杂任务容易跑偏 |
| **≥ 100B** | 旗舰 | ✅ 目标池 |
| 混合架构（如 550B-A55B） | 激活参数才是有效算力 | ⚠️ 总参数 ≠ 激活参数，需分开看 |

> ⚠️ **总参数 ≠ 激活参数**。MoE 模型（`-a55b` 这类后缀）总参数大但每次只激活一部分。
> 判断能力时，**激活参数**更接近实际表现，但「≥100B 总参数」作为门槛过滤是合理的粗筛。

---

## 核验路径（按可信度降序）

### 路径 1：官方模型卡 / 技术报告 ⭐⭐⭐

模型发布页、arXiv 技术报告、官方 blog。
这是唯一能把「已核实」写进 approved 池的依据。

### 路径 2：厂商 API 文档 ⭐⭐⭐

OpenAI / Anthropic / Google / Meta / NVIDIA / Mistral 的 models 页。
通常直接标注 "Parameter count" 或模型规模说明。

### 路径 3：HuggingFace `config.json` ⭐⭐

```bash
# 通用检查
curl -sL https://huggingface.co/<org>/<model>/raw/main/config.json | python3 -m json.tool
```

**看这些字段**：

| 字段 | 含义 |
|------|------|
| `num_parameters` | 总参数量（**若有，直接用**） |
| `architectures` | 模型结构（判断是否 MoE） |
| `num_experts` / `num_experts_per_tok` | MoE 专家数与每 token 激活数 |
| `hidden_size` | 隐藏维度 H |
| `num_hidden_layers` | 层数 L |
| `intermediate_size` | FFN 中间维度 |
| `vocab_size` | 词表大小 |

**MoE 激活参数估算**（以 Qwen / Mixtral 类为例）：

```
active_params ≈ hidden² × (layers × (attention + ffn_experts) + embed) × 2
```

太复杂时，用**更简单的判据**：

> 名字里的 `-a55b`、`-a3b` 这类后缀**通常就是激活参数量**（B = billion）。
> `nemotron-3-ultra-550b-a55b` → 总 550B，激活 55B。
> 55B 激活**达不到** 100B 激活门槛，但**总参数**达到了。

### 路径 4：粗算公式（仅用于排除）⭐

**只有当没有 `num_parameters` 时**：

```
params ≈ 12 × L × H²
```

- `L` = `num_hidden_layers`
- `H` = `hidden_size`

验证（Llama-3-70B：L=80, H=8192）：

```
12 × 80 × 8192² = 12 × 80 × 67,108,864 = 64,424,509,440 ≈ 64.4B
```

与实际 70B 接近（差在词表与 GQA 细节）。**可用于排除明显不合格的模型，
但绝不能作为「已核实」的依据。**

> ⚠️ MoE 架构不适用这个公式（激活参数远小于总参数）。

---

## 快速核验脚本

```bash
#!/usr/bin/env bash
# 用法: ./verify-params.sh <huggingface_org/model>
set -euo pipefail
MODEL="${1:?用法: $0 <org/model>}"
URL="https://huggingface.co/${MODEL}/raw/main/config.json"

curl -fsSL "$URL" | python3 -c "
import json, sys
c = json.load(sys.stdin)
n = c.get('num_parameters')
if n:
    print(f'num_parameters = {n:,}  ({n/1e9:.1f}B)  ← 直接采信')
else:
    L = c.get('num_hidden_layers'); H = c.get('hidden_size')
    if L and H:
        est = 12 * L * H * H
        print(f'粗算(12*L*H^2) = {est:,}  ({est/1e9:.1f}B)  ← 仅供排除')
    else:
        print('无 num_parameters，且缺 hidden_size/num_hidden_layers —— 需查官方文档')
print('architectures =', c.get('architectures'))
print('num_experts =', c.get('num_experts'), 'per_tok =', c.get('num_experts_per_tok'))
"
```

用法：

```bash
./verify-params.sh nvidia/Nemotron-3-Ultra-550B
```

---

## 写回 approved 池

核实后，把已核实的模型登记进 `~/.pi/agent/freetoken-bots.json`：

```bash
python3 - <<'PY'
import json, pathlib, datetime as dt

p = pathlib.Path.home() / '.pi' / 'agent' / 'freetoken-bots.json'
d = json.loads(p.read_text())

# ←← 换成你真正核实过的（id: 参数量 B）
verified = {
    'nvidia/nemotron-3-ultra-550b-a55b:free': 550.0,
}

ctx = {m['id']: m.get('context_length') for m in d.get('needs_parameter_verification', [])}
now = dt.datetime.now(dt.timezone.utc).isoformat()

d['eligible'] = [
    {'id': k, 'parameters_b': v, 'context_length': ctx.get(k),
     'verified_at': now, 'verification_source': 'official model card'}
    for k, v in verified.items()
]
d['needs_parameter_verification'] = [
    m for m in d.get('needs_parameter_verification', [])
    if m['id'] not in verified
]
p.write_text(json.dumps(d, indent=2, ensure_ascii=False))
print('approved 池:', len(d['eligible']), '| 待核实:', len(d['needs_parameter_verification']))
PY
```

**每次写回都记 `verified_at` 和 `verification_source`** —— 这样三个月后还能追溯依据。

---

## 判定标准表

| 情况 | 判定 |
|------|------|
| 官方文档明确写 "550B parameters" | ✅ 已核实，进 approved |
| HF `config.json` 有 `num_parameters: 550000000000` | ✅ 已核实，进 approved |
| 只有 ID 名字里的 `550b` | ❌ 只是线索，进 needs_verification |
| 只有粗算值 | ❌ 仅供排除 |
| 上下文长度 1M | ❌ 与参数量**无关**，不能推出 |
| 厂商未公布 | ❌ 留在 needs_verification |

---

## 复核纪律

1. **一条模型只核实一次**，记下来源
2. **模型升级/换版本 → 重新核实**（参数量可能变）
3. **free 资格和参数量是两件事** —— 免费会变，参数不会；但两者都要各自验证
4. **approved 池不代表「一定好用」** —— 还得过工具调用探针这一关


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

- 上游：`limin112/min-skill` → `skills/FreeToken-Bots`（v0.2.0，作者 limin112 / @MinLiBuilds）
  - `.claude-plugin/plugin.json` 声明 MIT；⚠️ 仓库根目录**无 LICENSE 文件**
- 依赖运行时：Pi `@earendil-works/pi-coding-agent`（**MIT**）
- API：OpenRouter 公开目录
