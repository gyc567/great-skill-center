# T+N 契约复盘同步入口

仅面向已登录的本人创作者后台。它从到期的 `待复盘` 契约中读取严格的「平台作品映射」，只同步映射到的抖音、小红书、视频号作品；不会按标题猜测、不会扫描全量作品、不会改契约状态，也不会回复、点赞或删除平台内容。

先检查今天应复盘什么（不写文件、不访问平台）：

```bash
python3 scripts/ip-review-sync.py "/你的/IP工作目录"
```

在三个独立浏览器 Profile 已登录且本地适配器已安装后，才实际同步：

```bash
python3 scripts/ip-review-sync.py "/你的/IP工作目录" --sync \
  --douyin-profile ip-douyin \
  --xiaohongshu-profile ip-xiaohongshu \
  --weixin-channels-profile ip-weixin-channels
```

成功后写入仅当前用户可读的 `ip-evidence/review/contract-evidence.json`。它只是到期复盘的输入；状态仍是 `待复盘`，必须由创作者完成复盘并确认后才可按既有规则改为 `已复盘`。

契约没有唯一作品 ID 映射时会返回 `awaiting_mapping`，不会采集任何作品。

<!-- ERIC-AUTHOR-INFO:START -->
---

## 📬 作者信息

**ERIC** — AI技术专家，专注于人工智能和自动化工具的研究与应用

| 渠道 | 链接 |
|------|------|
| 📧 邮箱 | gyc567@gmail.com |
| 🐦 Twitter | [@EricBlock2100](https://twitter.com/EricBlock2100) |
| 💬 微信 | 360369487 |
| ✈️ Telegram | [@fatoshi_block](https://t.me/fatoshi_block) |
| 📢 Telegram 频道 | [@cryptochanneleric](https://t.me/cryptochanneleric) |
| 🔐 加密情报 TG 群 | [@btcgogopen](https://t.me/btcgogopen) |
| ▶️ YouTube | [@0XBitFinance](https://www.youtube.com/@0XBitFinance) |
| 🌐 个人技术博客 | [topdigg.com](https://topdigg.com) |

> 本 Skill 由 ERIC 免费提供。想深入交流或获取更多同类 Skill，欢迎通过上表任一渠道联系。

<!-- ERIC-AUTHOR-INFO:END -->
