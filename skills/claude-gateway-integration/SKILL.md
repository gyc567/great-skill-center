---
name: claude-gateway-integration
description: 接入 Claude Gateway（distill5.iwz.cc）——一个 Claude Code 代理网关/中转站。当用户需要用 Anthropic 兼容 API 跑 Claude Code、批量调用 Claude 模型、或想了解该网关的认证方式、套餐计费、模型清单、用量查询接口时使用。覆盖注册登录、创建客户端令牌、base_url 配置、curl/Python/SDK 接入示例、成本估算和常见坑。  Integrates with Claude Gateway (distill5.iwz.cc), an Anthropic-compatible Claude Code proxy gateway. Covers signup, client token creation, base_url setup, API usage examples, pricing, and known pitfalls.
---

# Claude Gateway 接入指南

> 品牌：AI Skills 创作小店
> 站点：`https://distill5.iwz.cc` · 后端服务名：`2coding-gateway-api`

---

## 一、这是什么（实测结论，2026-11-10）

**Claude Gateway** 是一个 **Claude Code 代理网关 / API 中转控制台**，**不是写作蒸馏服务**。

| 项 | 实测结果 |
|----|---------|
| 站点类型 | React SPA（`/assets/index-*.js`，2.16MB bundle） |
| 后端 | nginx 1.27.5 → `2coding-gateway-api` |
| 品牌名 | `Claude Gateway`（前端 i18n `brand.name`） |
| 标语 | "管理你的 Claude Code 使用，追踪成本，控制访问。" |
| **认证** | 邮箱验证码 / 密码；**新令牌需管理员审核（pending → approve）** |
| **协议** | **Anthropic Messages API 兼容** + OpenAI Responses API 兼容 |
| 计费 | 按 token，$ / MTok；支持订阅（共享账号池）或余额（按量） |
| 计费口径 | `p`=未缓存输入 `c`=输出 `cr`=缓存读 `cc`/`cc1h`=两类缓存写 |

### ⚠️ 站内搜索「蒸馏/写作/仿写」命中 **0 次**

该站**没有任何写作蒸馏功能**。想用它做"蒸馏"，只能把它当作 **Claude 模型的后端推理通道**。

---

## 二、核心 API 端点（全部实测）

### 推理端点（需客户端令牌）

| 端点 | 方法 | 说明 |
|------|------|------|
| `/v1/messages` | POST | **Anthropic Messages API**（主力） |
| `/v1/messages/count_tokens` | POST | token 计数 |
| `/v1/responses` | POST | OpenAI Responses API 兼容 |
| `/v1/moderations` | POST | 内容审核 |
| `/v1/mcp_servers` | GET | MCP 服务器列表 |

### 认证头

```http
x-api-key: sk-xxxxxxxx          # 或
Authorization: Bearer sk-xxxxxxxx
```

未带凭据时返回：
```json
{"error":"Unauthorized - provide client token via x-api-key or Authorization header"}
```
HTTP **401**

### 控制台 API（需登录 Cookie/Session）

| 端点 | 说明 |
|------|------|
| `/auth/send-code` · `/auth/verify-code` | 邮箱验证码登录 |
| `/auth/register-password` · `/auth/complete-register` | 密码注册 |
| `/auth/me` · `/auth/features` · `/auth/methods` | 账号信息 / 可用登录方式 |
| `/clients` | **创建客户端令牌**（POST `{name}` → 返回 `sk-` 令牌） |
| `/clients/:id/rotate` · `/clients/:id/suspend` · `/clients/:id/activate` | 令牌管理 |
| `/groups` · `/me/billing` · `/me/logs` | 分组 / 账单 / 日志 |
| `/subscription/subscribe` · `/subscription/activate` · `/subscription/preview` | 订阅 |
| `/plans` · `/billing` | 套餐 / 账单 |

### 公开端点（无需登录）

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/public/console-identifier` | GET | 控制台标识 |
| `/api/public/key-usage` | POST | **凭 token 查用量**（无需登录） |
| `/api/public/key-usage/logs` | POST | 用量明细日志 |
| `/api/public/key-usage/timeline` | POST | 用量时间线 |

---

## 三、接入流程

### Step 1：注册

1. 打开 `https://distill5.iwz.cc` → 登录/注册
2. **邮箱验证码**（`/auth/send-code` → `/auth/verify-code`）或密码注册
3. 可填**邀请码**（如 `SPRING-a3f8c2` 格式）——**邀请人和被邀请人双方都有奖励**
4. 首次注册填用户名完成账号

### Step 2：充值或订阅

- **订阅（共享账号池）**：月卡 / 日卡 / 次卡
- **余额（按量计费）**：充值个人余额，用多少扣多少
- 未充值时页面提示："订阅共享账号或充值个人余额后即可使用"

### Step 3：创建客户端令牌

```http
POST /clients
Content-Type: application/json

{"name": "my-client"}
```

响应包含 `token`（`sk-` 开头）。

> ⚠️ **令牌明文只完整展示一次**，立即保存。
> ⚠️ **新令牌状态为 `pending`，需管理员审核通过（approve）后才能使用。**

### Step 4：配置客户端

**Claude Code CLI**（`~/.claude/settings.json`）：
```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://distill5.iwz.cc",
    "ANTHROPIC_AUTH_TOKEN": "sk-你的令牌"
  }
}
```

**Python（Anthropic SDK）**：
```python
from anthropic import Anthropic

client = Anthropic(
    base_url="https://distill5.iwz.cc",
    api_key="sk-你的令牌",   # 会作为 x-api-key 发送
)
resp = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "你好"}],
)
print(resp.content[0].text)
```

**curl**：
```bash
curl -X POST https://distill5.iwz.cc/v1/messages \
  -H "x-api-key: sk-你的令牌" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4-6",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "你好"}]
  }'
```

**OpenAI SDK（走 /v1/responses）**：
```python
from openai import OpenAI
client = OpenAI(base_url="https://distill5.iwz.cc/v1", api_key="sk-你的令牌")
```

---

## 四、可用模型（实测自前端 bundle）

| 模型 ID | 层级 |
|---------|------|
| `claude-opus-4-7` | Opus |
| `claude-sonnet-5` | Sonnet |
| `claude-sonnet-4-6` | Sonnet |
| `claude-haiku-4-5-20251001` | Haiku |

> 实际准入由**账号 / 分组 / 订阅**三层规则决定，不一定全部可用。

---

## 五、额度与计费

### 滚动额度窗口

| Key | 含义 |
|-----|------|
| `limit_5h_usd` | 每 **5 小时**滚动额度 |
| `limit_1d_usd` | 每日额度 |
| `limit_7d_usd` | 每周额度 |
| `limit_30d_usd` | 每 30 天额度 |

另有 `limit_ms`（超时）、`limit_percent`、`limit_sample_count`。

### 计费公式（前端原文）

> 表达式独立决定价格，单价单位为**美元/百万 token**。
> `p` 为未缓存输入，`c` 为输出，`cr` 为缓存读，`cc`/`cc1h` 为两类缓存写；`len` 为完整输入长度。
> 支持条件判断、min/max 和白名单参数 `speed` 等。

**总额 = 基准小计 × 分组倍率**

### 额度来源

| `consumed_plan_type` | 含义 |
|---------------------|------|
| `pool` | 订阅（共享账号池） |
| `quota` | 余额（按量） |

---

## 六、查用量（无需登录）

```bash
curl -X POST https://distill5.iwz.cc/api/public/key-usage \
  -H "Content-Type: application/json" \
  -d '{"token":"sk-你的令牌"}'
```

返回包含：5 小时周期 / 本周周期 / 累计 的**请求数、token 数、费用、剩余额度、下次重置时间、状态**。

- 404 → 令牌无效或暂无数据
- 429 → 请求过于频繁

**明细与时间线**：
```bash
POST /api/public/key-usage/logs    {"token":"sk-...","limit":50,...}
POST /api/public/key-usage/timeline {"token":"sk-...","group_by":"day|hour",...}
```

> 💡 **这是最实用的公开功能** —— 手上有一堆不知道哪来的 `sk-` 令牌，可以直接查它们是不是这个网关的。

---

## 七、想用它跑「写作蒸馏」的正确姿势

站点本身没有蒸馏功能，但它的 `/v1/messages` 是标准 Anthropic 协议，**可以直接作为 writing-dna-skill 的推理后端**。

### 方式 A：让 writing-dna-skill 走这个网关

```bash
export ANTHROPIC_BASE_URL=https://distill5.iwz.cc
export ANTHROPIC_AUTH_TOKEN=sk-你的令牌
# 然后正常使用 Claude Code / Claude CLI / Anthropic SDK
```

Claude Code 会自动走 `ANTHROPIC_BASE_URL`，所有 6 层蒸馏调用都经由该网关计费。

### 方式 B：脚本批量蒸馏

```python
import os
from anthropic import Anthropic

client = Anthropic(
    base_url="https://distill5.iwz.cc",
    api_key=os.environ["ANTHROPIC_AUTH_TOKEN"],
)

def distill_layer(article: str, layer: str) -> str:
    r = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": f"[{layer}] 分析以下文章：\n\n{article}"}],
    )
    return r.content[0].text
```

### 成本估算

| 场景 | 输入 token | 输出 token | 估算 |
|------|-----------|-----------|------|
| 单篇 L1 表层分析 | ~3,000 | ~2,000 | 约 $0.1 |
| 6 层完整蒸馏（1 篇） | ~18,000 | ~12,000 | 约 $0.6 |
| 6 层完整蒸馏（20 篇语料） | ~360,000 | ~240,000 | **约 $12** |

> ⚠️ 实际单价取决于该网关的**模型定价 + 分组倍率**，用 `/api/public/key-usage` 实测最准。

---

## 八、常见坑

| 坑 | 说明 |
|----|------|
| **令牌 pending 状态** | 新建令牌默认 `pending`，**管理员不批准就用不了**。这是最大的接入障碍 |
| **明文只显示一次** | 创建令牌后立刻保存，刷新就看不到了 |
| **`/auth/features` 等返回 HTML** | 这些是 SPA 路由，GET 会返回 772 字节外壳；要拿数据得用带 session 的 XHR |
| **SPA fallback 干扰探测** | 很多不存在的路径也返回 **200 + 772 字节 HTML**。判断真实端点要看 `content-type` 或 JSON body |
| **`/api/public/*` 的 404** | 返回 `{"error":"not_found"}`（JSON）而非 HTML —— 说明路由存在但参数不对 |
| **无安全响应头** | 未见 `Strict-Transport-Security` / `X-Frame-Options` / `CSP` |
| **端点无 OpenAPI 文档** | `/openapi.json`、`/docs` 都返回 SPA 外壳，没有官方 API 文档 |
| **共享账号池的波动** | 订阅模式下上游是共享账号，可能触发限流；余额按量模式更稳 |

---

## 九、与其他中转站对比

| 维度 | Claude Gateway | 直连 Anthropic | 其他中转站 |
|------|---------------|---------------|-----------|
| 协议 | Anthropic + OpenAI 双兼容 | Anthropic 官方 | 多数只有 OpenAI 格式 |
| Claude Code 直接用 | ✅ 只改 base_url | ✅ | 需转接层 |
| 审核 | ✅ `/v1/moderations` | 官方有 | 多数无 |
| MCP 支持 | ✅ `/v1/mcp_servers` | 官方 | 少数有 |
| 免登录查用量 | ✅ `/api/public/key-usage` | ❌ | 少数有 |
| 令牌需审批 | ⚠️ **是** | ❌ | 多数否 |
| 费用 | 网关定价 + 倍率 | 官方定价 | 网关定价 |

---

## 十、法律与合规提示

- 该站是**第三方服务**，与 Anthropic 官方无关。使用前确认其**服务条款、隐私政策、资质**。
- 通过网关发送的内容**会离开本机**，经站点运营方和上游账号池处理 —— **不要发送敏感数据、客户数据、未公开稿件**。
- 付费前确认**退款规则、额度重置周期、超额计费**。
- 站点含 `cc-disguise`（Claude Code 伪装）、`TLS 指纹` 等功能 —— 这些是**绕过上游检测**的技术手段，**商用前需自行评估服务条款风险**。

---

## 十一、验证记录（2026-11-10 实测）

| 检查 | 结果 |
|------|------|
| `/` HTTP 状态 | 200，772 字节 SPA 外壳 |
| `/assets/index-*.js` | 200，2,161,283 字节 |
| `/api/health` | `{"status":"ok","service":"2coding-gateway-api",...}` ✅ |
| `/v1/messages` 无凭据 | 401 + 明确错误文案 ✅ |
| `/v1/messages/count_tokens` 无凭据 | 401 ✅ |
| `/v1/moderations` 无凭据 | 401 ✅ |
| `/v1/responses` 无凭据 | 401 ✅ |
| `/v1/mcp_servers` 无凭据 | 401 ✅ |
| `/api/public/console-identifier` | 200 JSON `{"value":""}` ✅ |
| `/api/public/key-usage` 无效 token | 404 JSON `{"error":"not_found"}` ✅ |
| `/auth/features` GET | 200 但返回 SPA HTML（需 XHR）|
| 站内「蒸馏/写作/仿写」命中 | **0 次** → 确认非写作服务 ✅ |
| 安全响应头 | 未见 HSTS / X-Frame-Options / CSP |

---

> **品牌**：AI Skills 创作小店
> 如需定制化开发，可直接联系 ERIC：gyc567@gmail.com
