# Dub API 速查表

> 基于开源项目 [dubinc/dub](https://github.com/dubinc/dub)（AGPL-3.0）的公开 OpenAPI 规范整理。
> API Base: `https://api.dub.co` | 认证: `Authorization: Bearer <API_KEY>`
> 完整规范: `https://api.dub.co/?mcp` （MCP 客户端可直接消费）

---

## 端点总览

### Analytics (1)

| Method | Path | 说明 |
|--------|------|------|
| `GET` | `/analytics` | Retrieve analytics for a link, a domain, or the authenticated workspace. |

### Bounties (3)

| Method | Path | 说明 |
|--------|------|------|
| `GET` | `/bounties/{bountyId}/submissions` | List bounty submissions |
| `POST` | `/bounties/{bountyId}/submissions/{submissionId}/approve` | Approve a bounty submission |
| `POST` | `/bounties/{bountyId}/submissions/{submissionId}/reject` | Reject a bounty submission |

### Commissions (4)

| Method | Path | 说明 |
|--------|------|------|
| `POST` | `/commissions` | Create commission |
| `GET` | `/commissions` | List all commissions |
| `PATCH` | `/commissions/bulk` | Bulk update commissions |
| `PATCH` | `/commissions/{id}` | Update a commission |

### Customers (4)

| Method | Path | 说明 |
|--------|------|------|
| `GET` | `/customers` | List all customers |
| `GET` | `/customers/{id}` | Retrieve a customer |
| `PATCH` | `/customers/{id}` | Update a customer |
| `DELETE` | `/customers/{id}` | Delete a customer |

### Discount Codes (3)

| Method | Path | 说明 |
|--------|------|------|
| `GET` | `/discount-codes` | List discount codes |
| `POST` | `/discount-codes` | Create a discount code |
| `DELETE` | `/discount-codes/{idOrCode}` | Delete a discount code |

### Domains (6)

| Method | Path | 说明 |
|--------|------|------|
| `POST` | `/domains` | Create a domain |
| `GET` | `/domains` | List all domains |
| `POST` | `/domains/register` | Register a domain |
| `GET` | `/domains/status` | Check the availability of one or more domains |
| `PATCH` | `/domains/{slug}` | Update a domain |
| `DELETE` | `/domains/{slug}` | Delete a domain |

### Embed Tokens (1)

| Method | Path | 说明 |
|--------|------|------|
| `POST` | `/tokens/embed/referrals` | Create a referrals embed token |

### Events (1)

| Method | Path | 说明 |
|--------|------|------|
| `GET` | `/events` | List all events |

### Folders (4)

| Method | Path | 说明 |
|--------|------|------|
| `POST` | `/folders` | Create a folder |
| `GET` | `/folders` | List all folders |
| `PATCH` | `/folders/{id}` | Update a folder |
| `DELETE` | `/folders/{id}` | Delete a folder |

### Links (10)

| Method | Path | 说明 |
|--------|------|------|
| `POST` | `/links` | Create a link |
| `GET` | `/links` | List all links |
| `POST` | `/links/bulk` | Bulk create links |
| `PATCH` | `/links/bulk` | Bulk update links |
| `DELETE` | `/links/bulk` | Bulk delete links |
| `GET` | `/links/count` | Retrieve links count |
| `GET` | `/links/info` | Retrieve a link |
| `PUT` | `/links/upsert` | Upsert a link |
| `PATCH` | `/links/{linkId}` | Update a link |
| `DELETE` | `/links/{linkId}` | Delete a link |

### Partners (8)

| Method | Path | 说明 |
|--------|------|------|
| `POST` | `/partners` | Create or update a partner |
| `GET` | `/partners` | List all partners |
| `GET` | `/partners/analytics` | Retrieve analytics for a partner |
| `POST` | `/partners/ban` | Ban a partner |
| `POST` | `/partners/deactivate` | Deactivate a partner |
| `POST` | `/partners/links` | Create a link for a partner |
| `GET` | `/partners/links` | Retrieve a partner's links. |
| `PUT` | `/partners/links/upsert` | Upsert a link for a partner |

### Payouts (1)

| Method | Path | 说明 |
|--------|------|------|
| `GET` | `/payouts` | List all payouts |

### Program Applications (3)

| Method | Path | 说明 |
|--------|------|------|
| `GET` | `/program-applications` | List all program applications |
| `POST` | `/program-applications/approve` | Approve a partner application |
| `POST` | `/program-applications/reject` | Reject a partner application |

### QR Codes (1)

| Method | Path | 说明 |
|--------|------|------|
| `GET` | `/qr` | Retrieve a QR code |

### Tags (4)

| Method | Path | 说明 |
|--------|------|------|
| `POST` | `/tags` | Create a tag |
| `GET` | `/tags` | List all tags |
| `PATCH` | `/tags/{id}` | Update a tag |
| `DELETE` | `/tags/{id}` | Delete a tag |

### Track (3)

| Method | Path | 说明 |
|--------|------|------|
| `POST` | `/track/lead` | Track a lead |
| `POST` | `/track/open` | Track a deep link open event |
| `POST` | `/track/sale` | Track a sale |

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
