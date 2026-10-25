# 短链与归因运营大师（link-ops-master）

> 每一个链接都应该能回答三个问题：**谁点的？点了之后做了什么？值不值得继续投？**

品牌：**AI Skills 创作小店**

---

## 这是什么

一套给 AI Agent 用的**链接归因运营方法论 + 可运行工具链**。不是"生成短链"这么简单——
它覆盖从命名规范、批量铺渠道、A/B 分流、转化回传，到读数据做投放决策的完整闭环。

```
投放素材 → 归因短链 → 落地页 → 转化回传 → 数据复盘 → 调整投放
```

---

## 组成

| 组成 | 说明 |
|------|------|
| `SKILL.md` | 主方法论：4 条核心原则 + 6 步工作流 + 7 条实测坑点 |
| `scripts/link_ops.py` | **零依赖** API 客户端，7 个子命令，支持 Dub / Bitly / TinyURL / 自定义 |

---

## 快速开始

```bash
export LINK_OPS_API_KEY=dub_xxx
export LINK_OPS_PROVIDER=dub

# 建一条带归因的短链
python3 scripts/link_ops.py create "https://your.site/landing" \
  --key promo-202610 \
  --utm-source wechat --utm-medium social \
  --utm-campaign 202610-launch --utm-content a

# 批量铺 5 个渠道
for src in wechat xiaohongshu douyin bilibili weibo; do
  python3 scripts/link_ops.py create "https://your.site/landing" \
    --key "202610-launch-$src" \
    --utm-source "$src" --utm-medium social --utm-campaign 202610-launch
done

# 回传转化（金额单位：分）
python3 scripts/link_ops.py track sale <linkId> --amount 9900 --customer "user@example.com"

# 读数据
python3 scripts/link_ops.py stats <linkId>
```

**不需要 API Key 也能用的命令：**

```bash
python3 scripts/link_ops.py urls "example.com/path?q=1"     # 解析 URL
python3 scripts/link_ops.py utm --source wechat --campaign spring --url example.com
python3 scripts/link_ops.py reserved stats                  # 保留 slug 检查
python3 scripts/link_ops.py domain "AI Skills 创作小店"      # 候选域名
```

---

## 7 条实测坑点

1. **保留 slug 会失败** —— 80+ 个词（`stats`/`api`/`pricing`/`admin`…）不能当短链 key，脚本已内置拦截
2. **裸域名必须补协议** —— `example.com` 会被部分平台拒绝
3. **二级后缀主域名** —— `shop.example.co.uk` 的主域名是 `example.co.uk`
4. **金额单位是「分」** —— `--amount 9900` = ¥99.00，传错不报错但 ROI 差 100 倍
5. **回传在转化成功页** —— 不在按钮点击时
6. **401 带结构化错误体** —— 含 `doc_url`，遇到权限问题直接点
7. **别在 CI 硬编码 API Key** —— 生产走 OAuth 2.0

---

## 为什么选 Dub

[dubinc/dub](https://github.com/dubinc/dub) 是 **24.9k⭐** 的开源链接归因平台（AGPL-3.0），
每月 200 万+ 链接、1 亿+ 点击。相对基础短链服务，它的差异在：

- **A/B 分流**（单链接内 10%~90% 流量分叉，最多 4 变体）
- **转化回传**（lead / sale / open / click）
- **UTM 结构化存储**（不是拼在 URL 里，是独立字段，可查）
- **自托管**（数据不出自己的服务器）
- **公开 OpenAPI 规范** + 官方 MCP 端点 `api.dub.co/?mcp`

---

## 📬 联系作者

**ERIC** — AI技术专家，专注于人工智能和自动化工具的研究与应用

| 渠道 | 链接 |
|------|------|
| 📧 邮箱 | [gyc567@gmail.com](mailto:gyc567@gmail.com) |
| 🐦 Twitter | [@EricBlock2100](https://twitter.com/EricBlock2100) |
| 💬 微信 | `360369487` |
| ✈️ Telegram | [@fatoshi_block](https://t.me/fatoshi_block) |
| 📢 Telegram 频道 | [@cryptochanneleric](https://t.me/cryptochanneleric) |
| 🔐 加密情报 TG 群 | [@btcgogopen](https://t.me/btcgogopen) |
| ▶️ YouTube | [@0XBitFinance](https://www.youtube.com/@0XBitFinance) |
| 🌐 个人技术博客 | [topdigg.com](https://topdigg.com) |

### 💼 定制化开发

需要把归因体系接进你的产品、换成你的渠道命名规范、或者做一套投放决策看板 ——
**直接联系我**。

常见方向：
- **渠道命名规范落地** —— 按你的业务定义 UTM 体系、批量生成规则、对账脚本
- **投放数据看板** —— 把多平台点击 + 转化回传到一处，按渠道/活动/素材看 ROI
- **联盟营销系统** —— 分级佣金、推广者链接、结算与对账
- **私有化部署** —— 自托管 Dub，链接与归因数据完全自持
- **与现有系统集成** —— 接 CMS、CRM、飞书/钉钉告警、BI 看板
- **团队培训** —— 内部投放规范文档与工具上手

> 本 Skill 免费使用。定制化开发、付费咨询与商业授权，请通过上表任一渠道直接联系 ERIC。

---

## 许可与来源

- **方法论与脚本**：本 Skill 由 AI Skills 创作小店（ERIC）编写
- **纯函数移植**：URL 处理、主域名提取、保留 slug 集合来自
  [dubinc/dub](https://github.com/dubinc/dub)（AGPL-3.0，© Dub Technologies, Inc.）的 `packages/utils`
- 平台：Dub 为开源项目，自托管参考[官方指南](https://dub.co/docs/self-hosting/guide)

---

<!-- ERIC-AUTHOR-INFO:START -->

## 📬 联系作者

**ERIC** — AI技术专家，专注于人工智能和自动化工具的研究与应用

| 渠道 | 链接 |
|------|------|
| 📧 邮箱 | [gyc567@gmail.com](mailto:gyc567@gmail.com) |
| 🐦 Twitter | [@EricBlock2100](https://twitter.com/EricBlock2100) |
| 💬 微信 | `360369487` |
| ✈️ Telegram | [@fatoshi_block](https://t.me/fatoshi_block) |
| 📢 Telegram 频道 | [@cryptochanneleric](https://t.me/cryptochanneleric) |
| 🔐 加密情报 TG 群 | [@btcgogopen](https://t.me/btcgogopen) |
| ▶️ YouTube | [@0XBitFinance](https://www.youtube.com/@0XBitFinance) |
| 🌐 个人技术博客 | [topdigg.com](https://topdigg.com) |

> 本 Skill 由 ERIC 免费提供。想深入交流或获取更多同类 Skill，欢迎通过上表任一渠道联系。

<!-- ERIC-AUTHOR-INFO:END -->
