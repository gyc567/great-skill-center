# Claude Gateway 接入指南 · claude-gateway-integration

> **实测分析 `https://distill5.iwz.cc` 的完整接入方案。**
> 这是一个 Claude Code 代理网关 —— 不是写作蒸馏服务，但**可以作为蒸馏的推理后端**。
> 品牌化改造：AI Skills 创作小店

[![许可](https://img.shields.io/badge/许可-MIT-blue)](https://opensource.org/licenses/MIT)
[![依赖](https://img.shields.io/badge/依赖-零%20纯标准库-blue)]()
[![实测](https://img.shields.io/badge/端点探测-9%2F9%20通过-green)]()
[![品牌](https://img.shields.io/badge/品牌-AI%20Skills%20创作小店-pink)](https://github.com/gyc567/great-skill-center)

---

## ⚡ 一句话结论

> **distill5.iwz.cc 是「Claude Gateway」—— 一个 Anthropic 兼容的 Claude Code 代理网关。**
> 它**没有**任何写作蒸馏功能（站内「蒸馏/写作/仿写」命中 **0 次**），
> 但它的 `/v1/messages` 是标准 Anthropic 协议，**改一个 base_url 就能让 writing-dna-skill 全程走它**。

---

## 🔍 实测发现速览

| 发现 | 证据 |
|------|------|
| 后端服务名 | `/api/health` → `{"status":"ok","service":"2coding-gateway-api"}` |
| 真实品牌名 | 前端 i18n `brand.name` = **"Claude Gateway"** |
| 标语 | "管理你的 Claude Code 使用，追踪成本，控制访问。" |
| Anthropic 协议 | `/v1/messages` 401 提示 `provide client token via x-api-key or Authorization header` |
| OpenAI 兼容 | `/v1/responses` 同样 401 |
| 内容审核 | `/v1/moderations` |
| MCP 支持 | `/v1/mcp_servers` |
| **令牌需审批** | 前端原文："新令牌状态为 pending，**需管理员审核通过后才能使用**" |
| 免登录查用量 | `/api/public/key-usage` POST |
| 邀请奖励 | 邀请码格式 `SPRING-a3f8c2`，**双方都有奖励** |
| 计费口径 | `$ / MTok`；`p`未缓存输入 `c`=输出 `cr`=缓存读 `cc`/`cc1h`=两类缓存写 |
| 额度窗口 | `limit_5h_usd` / `limit_1d_usd` / `limit_7d_usd` / `limit_30d_usd` |
| 可用模型 | `claude-opus-4-7` / `claude-sonnet-5` / `claude-sonnet-4-6` / `claude-haiku-4-5-20251001` |

---

## 📁 目录结构

```
claude-gateway-integration/
├── SKILL.md                        # 完整接入指南（11 节）
├── README.md                       # 本文件
├── LICENSE                         # MIT
└── scripts/
    └── probe_gateway.py            # 端点探测（零依赖，9 项检查）
```

---

## 🚀 快速开始

### 1️⃣ 探测网关是否可达

```bash
python3 scripts/probe_gateway.py
```

**实测输出（2026-11-10）**：
```
  ✓ [ 200] GET  /                          站点外壳（正常）
  ✓ [ 200] GET  /api/health                端点开放且返回 JSON
  ✓ [ 200] GET  /api/public/console-identifier
  ✓ [ 401] POST /v1/messages               端点存在，需鉴权（预期）
  ✓ [ 401] POST /v1/messages/count_tokens
  ✓ [ 401] POST /v1/responses
  ✓ [ 401] POST /v1/moderations
  ✓ [ 401] GET  /v1/mcp_servers
  ✓ [ 404] POST /api/public/key-usage      路由存在，参数无效（预期）
通过 9/9
```

> 💡 **这个脚本的用途**：区分「网关挂了」和「我的 key 有问题」。
> 401 = 端点正常只是缺凭据；404-JSON = 路由在但参数错；SPA 回退 = 路径不存在。

### 2️⃣ 三步接入

```bash
# Step 1: 注册（邮箱验证码或密码）→ https://distill5.iwz.cc
#         可填邀请码，双方都有奖励

# Step 2: 充值或订阅
#         - 订阅：月卡/日卡/次卡（共享账号池）
#         - 余额：按量计费

# Step 3: 创建客户端令牌
curl -X POST https://distill5.iwz.cc/clients \
  -H "Content-Type: application/json" \
  -b "session=<你的登录cookie>" \
  -d '{"name":"my-client"}'
# → 返回 sk- 开头的 token（明文只显示一次！）
# ⚠️ 新令牌是 pending 状态，需管理员审核通过才能用
```

### 3️⃣ 让 writing-dna-skill 走这个网关

```bash
export ANTHROPIC_BASE_URL=https://distill5.iwz.cc
export ANTHROPIC_AUTH_TOKEN=sk-你的令牌
```

**就这两行。** Claude Code 会自动读取 `ANTHROPIC_BASE_URL`，
writing-dna-skill 的 6 层蒸馏调用**全部**经由该网关计费。

### 4️⃣ Python SDK 接入

```python
from anthropic import Anthropic

client = Anthropic(
    base_url="https://distill5.iwz.cc",
    api_key="sk-你的令牌",
)
resp = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "你好"}],
)
print(resp.content[0].text)
```

---

## 💰 成本估算（6 层蒸馏）

| 场景 | 输入 token | 输出 token | 估算成本 |
|------|-----------|-----------|---------|
| 单篇 L1 表层分析 | ~3,000 | ~2,000 | 约 $0.1 |
| 6 层完整蒸馏（1 篇） | ~18,000 | ~12,000 | 约 $0.6 |
| 6 层完整蒸馏（20 篇语料） | ~360,000 | ~240,000 | **约 $12** |

> ⚠️ 实际单价取决于该网关的**模型定价 + 分组倍率**，用 `/api/public/key-usage` 实测最准。

---

## ⚠️ 五个必须知道的坑

| # | 坑 | 后果 |
|---|-----|------|
| 1 | **新令牌是 `pending` 状态** | 管理员不批准就**完全用不了** —— 这是最大的接入障碍 |
| 2 | **令牌明文只显示一次** | 刷新页面就永久丢失，只能 rotate |
| 3 | **SPA fallback 干扰探测** | 大量不存在的路径也返回 **200 + 772 字节 HTML**。判真伪要看 `content-type` |
| 4 | **`/auth/features` 等 GET 返回 HTML** | 这些是 SPA 路由，要拿数据必须走带 session 的 XHR |
| 5 | **无安全响应头** | 未见 HSTS / X-Frame-Options / CSP |

**其他**：
- `/api/public/key-usage` 有**限流**（实测第 9 次请求返回 429）
- 订阅模式下是**共享账号池**，可能触发上游限流；余额按量模式更稳
- 模型实际准入由**账号/分组/订阅**三层规则决定，不一定全部可用

---

## ⚖️ 合规提示

- 该站是**第三方服务**，与 Anthropic 官方无关。使用前确认其**服务条款、隐私政策、资质**。
- 通过网关发送的内容**会离开本机**，经站点运营方和上游账号池处理 —— **不要发送敏感数据、客户数据、未公开稿件**。
- 站点含 `cc-disguise`（Claude Code 伪装）、`TLS 指纹` 等**绕过上游检测**的技术手段 —— **商用前需自行评估服务条款风险**。

---

## 📊 与其他方案对比

| 维度 | Claude Gateway | 直连 Anthropic | 其他中转站 |
|------|---------------|---------------|-----------|
| 协议 | Anthropic + OpenAI 双兼容 | Anthropic 官方 | 多数只有 OpenAI |
| Claude Code 直接用 | ✅ 只改 base_url | ✅ | 需转接层 |
| 内容审核 | ✅ `/v1/moderations` | 官方有 | 多数无 |
| MCP 支持 | ✅ `/v1/mcp_servers` | 官方 | 少数有 |
| 免登录查用量 | ✅ | ❌ | 少数有 |
| 令牌需审批 | ⚠️ **是** | ❌ | 多数否 |
| 费用 | 网关定价 + 倍率 | 官方定价 | 网关定价 |

---

## 📜 许可与来源

| 项 | 说明 |
|----|------|
| **作者** | ERIC（AI Skills 创作小店） |
| **许可** | MIT License |
| **原创性** | 本 Skill 为**原创编写** —— 基于 2026-11-10 对公开站点的实测探测结果 |
| **数据来源** | 站点公开 HTML / JS bundle / API 响应；**未使用任何凭据**，未登录，未创建任何账号 |

---

## 📞 定制化开发

如需**定制化开发**（批量蒸馏流水线、网关健康监控、成本优化路由、多网关故障转移、蒸馏产物入库），可直接联系 ERIC：

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
- 配套 Skill：`writing-dna-skill`（6 层写作蒸馏，本网关可作其推理后端）
