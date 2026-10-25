# UTM 归因命名规范

> 三个月的投放数据如果对不上账，问题 90% 出在这一层。

---

## 为什么要有规范

UTM 参数本身没有标准——任何字符串都能塞进 `utm_source`。没有规范的后果：

| 症状 | 根因 |
|------|------|
| 报表里出现 `wechat` / `WeChat` / `Wechat` 三个来源 | 大小写不统一 |
| 同一活动散成 5 个 campaign | 活动名手填无模板 |
| `utm_source=xhs1` 没人知道是什么 | 用临时代号当来源 |
| 报表永远对不上广告平台的数据 | 参数位置或命名与平台侧不一致 |

---

## 五层参数模型

```
?utm_source=wechat          ← 谁带来的（渠道）
&utm_medium=social          ← 什么类型（渠道大类）
&utm_campaign=202610-launch ← 哪次活动（时间 + 活动名）
&utm_term=beginner         ← 面向谁（人群/内容角度）
&utm_content=video-a       ← 哪条素材（具体版本）
```

### 每层的填写规则

| 参数 | 必填 | 取值来源 | 规则 |
|------|------|---------|------|
| `utm_source` | ✅ | 渠道清单 | 小写、连字符分隔、**一次一个渠道** |
| `utm_medium` | ✅ | 渠道大类 | 固定枚举，见下表 |
| `utm_campaign` | ✅ | 活动名 | `YYYYMM-<活动名>`，**日期前缀必带** |
| `utm_term` | ❌ | 人群/内容角度 | 关键词，不要放渠道 |
| `utm_content` | ❌ | 素材版本 | 单字符或短代号：`a`/`b`/`carousel-1` |

### `utm_medium` 固定枚举

```
social      社交媒体（微信/小红书/微博/B站/抖音…）
email       邮件
cpc         付费搜索
referral    外部推荐/合作方
qr          线下二维码
qr          线下二维码
banner      横幅广告
affiliate   联盟推广
```

> 固定枚举的价值：半年后你能在报表里一键筛出"所有社交渠道"，而不用逐个 source 匹配。

---

## 命名规范落地流程

### Step 1 — 列出渠道清单

先穷举，再定规范。**不要边投放边想名字。**

```
微信朋友圈 / 微信群 / 微信公众号 / 小红书 / 抖音 / B站 / 微博 / 知乎 / newsletter / 官网 banner / 线下二维码 / KOL 合作
```

### Step 2 — 归入 medium

| source | medium |
|--------|--------|
| wechat-moments | social |
| wechat-group | social |
| wechat-official | social |
| xiaohongshu | social |
| douyin | social |
| bilibili | social |
| weibo | social |
| zhihu | social |
| newsletter | email |
| banner-main | banner |
| qr-store | qr |
| kol-xxx | affiliate |

### Step 3 — 定 campaign 模板

```
格式：YYYYMM-<活动名>
示例：202610-launch / 202610-blackfriday / 202611-yr-end
```

带日期前缀的好处：按时间排序天然正确，跨年活动不会混在一起。

### Step 4 — 定 content 规范

素材代号要能对应到具体文件：

```
a          → 第一个版本
b          → 第二个版本
video-01   → 视频第 1 条
carousel-1 → 图文第 1 组
```

### Step 5 — 写进文档并交接

一张表发给所有投放的人：

| 渠道 | source | medium | 素材 | content |
|------|--------|--------|------|---------|
| 小红书 | xiaohongshu | social | 视频 1 | video-01 |
| 小红书 | xiaohongshu | social | 视频 2 | video-02 |
| 微信群 | wechat-group | social | 海报 A | a |
| 线下 | qr-store | qr | 台卡 | a |

---

## 常见错误

| 错误 | 后果 | 正确做法 |
|------|------|---------|
| `utm_source=WeChat` | 与 `wechat` 被算成两个来源 | 全部小写 |
| `utm_source=wechat-moments-2026` | 渠道、渠道类型、日期全塞一起 | 拆到 source/medium/campaign |
| `utm_source=xhs1` | 三个月后没人知道 | 用真实渠道名 |
| campaign 手填 | 出现 `10月launch`/`oct-launch`/`Launch10` | 强制模板 |
| 一个 source 塞多个渠道 | 无法拆渠道效果 | 一个 source 一个渠道 |
| 忘记 utm_medium | 报表里分不出 social 和 email | 必填 |

---

## 与短链 key 的配合

**短链 key 和 UTM 都要能自解释。** 短链 key 是人看的（贴到海报上、被扫、被记错），
UTM 是机器看的（进报表）。两者互为备份：

```
https://your.domain/202610-launch-xhs     ← 人看：活动+渠道
  ?utm_source=xiaohongshu&utm_medium=social&utm_campaign=202610-launch&utm_content=video-01
                                              ↑ 机器看：完整五层
```

**注意**：slug 里不要重复 UTM 已有的全部信息——slug 保持**短**（要贴海报、要手打），
完整维度交给 UTM。slug 只需要 `活动-渠道` 足够定位。

---

## 短链 key 的约束

1. **不能是保留字** —— `stats`、`api`、`pricing`、`admin`、`links`、`workspaces` 等 80+ 个
2. **长度适中** —— 太长没法贴海报，控制在 30 字符内
3. **只允许字母数字和连字符** —— 避免特殊字符在二维码/手打时出错
4. **同活动用同前缀** —— `202610-launch-xxx`，方便批量查询和删除
5. **不用中文** —— 部分平台对非 ASCII 的 key 支持不好

检查工具：

```bash
python3 scripts/link_ops.py reserved stats      # 查保留字
```

---

## 命名规范检查清单

上线前逐条过：

- [ ] 每个渠道在清单里有且只有一个 source
- [ ] medium 取自固定枚举
- [ ] campaign 全部符合 `YYYYMM-<活动名>`
- [ ] content 能对应到具体素材文件
- [ ] 全部小写、无空格
- [ ] 短链 key 查过保留字
- [ ] 短链 key 在 30 字符内
- [ ] 规范表已发给所有投放的人

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
