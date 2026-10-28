# 免费模型路由大师 (free-model-router)

> 每天扫描 OpenRouter 免费模型，**fail-closed** 地给子代理配「零花费」路由。
> 不会误触收费版，不会默默移除你的配置，不会因为一次限流就判模型死刑。

[![许可](https://img.shields.io/badge/许可-MIT-blue)](https://opensource.org/licenses/MIT)
[![语言](https://img.shields.io/badge/语言-Python3%20%7C%20Bash-blue)]()
[![品牌](https://img.shields.io/badge/品牌-AI%20Skills%20创作小店-pink)](https://github.com/gyc567/great-skill-center)

---

## 🎯 解决什么

给子代理（child agent）配模型时，最怕两件事：

| 怕 | 这个 Skill 怎么防 |
|----|------------------|
| **手滑路由到付费版** | fail-closed 解析：ID 不在最新免费名单 → **拒绝调用** |
| **默默丢掉 `:free` 后缀** | 自动纠正 + **大声告警**（静默丢掉会扣费） |

外加：

- ✅ 每天自动刷新免费名单（免费资格是动态的）
- ✅ 严格的双重零价判定（含 cache / request 价格）
- ✅ 参数量人工核验方法论（不靠名字猜）
- ✅ **独立的工具调用探针**（普通对话通过 ≠ 支持工具）
- ✅ Pi 集成体检 + 同步提案

---

## 🔑 关键洞察：OpenRouter 是 Pi 的内置 provider

**这是本 Skill 最重要的发现，上游版本没讲透。**

Pi（`@earendil-works/pi-coding-agent`，MIT）**内置** OpenRouter provider。
配好 `OPENROUTER_API_KEY` 后，`pi --list-models` **自动列出全部可用模型**。

**实测数据**（2026-10-28）：

| 指标 | 数值 |
|------|------|
| OpenRouter 目录总模型 | 464 |
| 免费模型 | 19 |
| Pi 列出的 OpenRouter 模型 | **401** |
| 免费 ∩ Pi 已列出 | **16** |
| 免费但 Pi 未列出 | 3（音频 / 安全分类模型，**非聊天**） |

**结论：绝大多数情况根本不需要改 `models.json`。**
`sync` 会明确告诉你 `openrouter_is_builtin_provider: true` 和 `proposed_additions: []`。

---

## 🚀 快速开始

```bash
# 0. 装 Pi（前置）
curl -fsSL https://pi.dev/install.sh | sh
pi --version

# 1. 体检
python3 scripts/radar.py doctor

# 2. 扫描
python3 scripts/radar.py scan

# 3. 看 Pi 已有哪些
python3 scripts/radar.py pi-models

# 4. 探针（需 key）
export OPENROUTER_API_KEY=...
python3 scripts/radar.py probe --model 'cohere/north-mini-code:free'
python3 scripts/radar.py probe-tools --model 'cohere/north-mini-code:free'

# 5. 同步提案
python3 scripts/radar.py sync --dry-run
```

### doctor 输出长这样

```json
{
  "pi_on_path": true,
  "pi_version": "1.4.0",
  "openrouter_key_set": false,
  "cache_age_hours": 0.13,
  "free_count": 19,
  "eligible_count": 0,
  "needs_verification_count": 16,
  "pi_openrouter_models": 401,
  "free_models_already_in_pi": 16,
  "advice": [
    "未设置 OPENROUTER_API_KEY（probe 需要）",
    "eligible 为空是正常的：OpenRouter /models 目录不提供结构化参数字段。"
  ]
}
```

---

## ⚠️ 必读：eligible 为空是正常的

OpenRouter 的 `/models` 目录**不提供**结构化参数字段（实测 464 个模型、0 个带参数字段）。
所以 `eligible` 池天然为空 —— 这是 **fail-closed 设计的正确表现**，不是 bug。

参数量必须**人工核实**，方法见 [`references/parameter-verification.md`](references/parameter-verification.md)：

```bash
# HuggingFace 快速核验
curl -sL https://huggingface.co/<org>/<model>/raw/main/config.json | \
  python3 -c "import json,sys; c=json.load(sys.stdin); print(c.get('num_parameters'))"

# 粗算（仅供排除，不能作为核实依据）
params ≈ 12 × layers × hidden_size²
```

---

## ⏰ 必配：每天 08:00 定时扫描

**这个 Skill 自己不会扫描。** 免费名单会过期。

```cron
0 8 * * * /绝对路径/scripts/daily-scan.sh >> ~/freetoken-scan.log 2>&1
```

> **安装时必须明确告诉用户**：
> 「这个 skill 需要每天早上 8 点跑一次扫描定时任务，不配的话免费名单会过期，它自己不会动。」

脚本会自动输出变化摘要：

```
🆕 新上架的免费模型:
   + xxx:free
❌ 下架 / 不再免费的模型:
   - yyy:free
📋 待人工核实参数量 (16 个):
   ? nvidia/nemotron-3-ultra-550b-a55b:free  ctx=1000000  [ID 线索: 550.0B]
```

---

## 🔒 fail-closed 解析实测

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

## 🧪 工具能力必须单独探

```bash
$ python3 scripts/radar.py probe-tools --model 'xxx:free'
{
  "ok": true,
  "tool_called": true,
  "function": "get_weather",
  "classification": "ok"
}
```

`tool_called: false` = 工具支持**未获证明**，不能进子代理池。

### 错误分类

| `classification` | 动作 |
|------------------|------|
| `rate_limited_temporary` | 稍后重试，**不要**标记不可用 |
| `quota_exhausted` | 当天免费额度用完 |
| `payment_required` | 免费资格失效 |
| `unauthorized` | key 有问题 |

---

## 📦 包含内容

```
free-model-router/
├── SKILL.md                                # 完整纪律 + 命令速查 + 10 条实测坑
├── README.md
├── scripts/
│   ├── radar.py                            # 核心：发现/解析/探针/同步（零依赖）
│   └── daily-scan.sh                       # 每日 08:00 定时扫描 + 变化摘要
├── references/
│   └── parameter-verification.md           # 参数量核验方法论（含 HF 脚本）
└── tests/
    └── test_radar.py                       # 19 项测试
```

---

## ✅ 交付实测

| 项 | 结果 |
|----|------|
| 单元测试 | ✅ **19 passed**（上游 7 + 新增 12） |
| 真实 API 扫描 | ✅ 464 总模型 / 19 免费 / 0 带参数字段 |
| fail-closed 拒绝付费模型 | ✅ exit 2，拒绝调用 |
| `:free` 后缀自动纠正 | ✅ 大声告警 + 纠正成功 |
| Pi 集成 | ✅ Pi 1.4.0 装好，401 模型自动列出 |
| 免费 ∩ Pi | ✅ **16/19** 直接可用 |
| doctor 体检 | ✅ 8 项指标全出 |
| sync 提案 | ✅ `proposed_additions: []`（无需改 models.json） |
| 定时脚本 | ✅ 变化检测、ID 线索、待核实清单全部正常 |
| 报告文件权限 | ✅ 0600，原子写无残留 |
| 网络抖动 | ✅ 加重试（2 次指数退避）+ sync 用缓存 |

---

## 📄 许可与来源

| 来源 | 许可 |
|------|------|
| `limin112/min-skill` → `skills/FreeToken-Bots`（v0.2.0，作者 @MinLiBuilds） | `.claude-plugin` 声明 **MIT**；⚠️ 仓库根目录**无 LICENSE 文件** |
| Pi `@earendil-works/pi-coding-agent` | **MIT**，Node ≥ 22.19 |
| OpenRouter `/api/v1/models` | 公开目录，无需 key |

> ⚠️ 上游仓库根目录没有 LICENSE 文件，只在 `.claude-plugin/plugin.json` 里声明 MIT。
> 商业化前建议向作者确认授权。

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
- 姊妹 Skill：`agent-reach`（互联网触达）、`ub-quality-gates`（代码质量门禁）、`mimo-api-reference`（MiMo 备选编程模型）
