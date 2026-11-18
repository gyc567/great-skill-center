---
name: douyin-comment-crawler
description: 抓取抖音视频的一级评论和二级评论（回复），导出 CSV/JSON，含评论内容、点赞数、用户昵称、抖音号、主页链接、IP 属地和回复关系。签名算法为纯 Python 实现（SM3+RC4），不依赖 Node.js。适合评论洞察、用户需求挖掘、竞品评论分析、舆情监测和选题调研。 Fetches Douyin video comments and nested replies with a pure-Python a_bogus signer (SM3+RC4, no Node.js required), exporting CSV/JSON with text, likes, author, IP region and reply relations.
---

# 抖音评论抓取 —— 一级评论 + 二级回复

> 品牌：AI Skills 创作小店

## 一、是什么

把一条抖音视频的评论区和二级回复完整拉下来，变成结构化表格。

```text
视频链接
  └─ 一级评论（正文、点赞、IP、回复数）
       └─ 二级回复（谁回复了谁、层级关系）
```

**核心价值**：评论是用户用真金白银写出来的话，比任何问卷都真实。抓下来做需求挖掘、选题灵感、竞品分析、舆情监控都直接可用。

## 二、快速开始

### 1. 准备 Cookie

抖音网页版接口需要登录态。从浏览器 F12 → Network → 任意请求 → Request Headers → 复制 `cookie` 整串。

存到**仓库外**的文件（第一行放完整 cookie 串）：

```bash
mkdir -p ~/.config/douyin-comments
# 粘贴你的 cookie 串，保存
nano ~/.config/douyin-comments/cookie.txt
```

### 2. 抓取

```bash
cd skills/douyin-comment-crawler
pip install -r requirements.txt

python scripts/cli.py \
  --aweme-id 7633646113853104116 \
  --cookie-file ~/.config/douyin-comments/cookie.txt \
  --with-replies \
  --output ./output
```

输出：

```text
output/comments_7633646113853104116.csv
output/comments_7633646113853104116.json
```

CSV 字段（UTF-8 BOM，Excel 直接打开不乱码）：

| 字段 | 说明 |
|---|---|
| 层级 | 一级评论 / 二级评论 |
| 评论ID | 抖音评论唯一 ID |
| 评论内容 | 评论区正文（含表情占位符） |
| 点赞数 | 该评论点赞量 |
| 评论时间 | 本地时区格式化时间 |
| 用户昵称 | 评论者昵称 |
| 用户抖音号 | 用户的 unique_id |
| 用户主页 | `https://www.douyin.com/user/{sec_uid}` |
| IP归属 | 评论者 IP 属地 |
| 回复总数 | 该一级评论下有多少条回复 |
| 回复给谁 | 二级评论中被回复的用户昵称 |
| 父评论ID | 二级评论所属的一级评论 ID |
| 图片 | 评论附带图片首图 URL（无则空） |

## 三、代码调用

```python
import asyncio
from douyin_client import DouyinCommentClient, load_cookie

async def main():
    cookie = load_cookie("~/.config/douyin-comments/cookie.txt")
    async with DouyinCommentClient(cookie) as client:
        async for c in client.iter_comments("7633646113853104116"):
            print(c.text, c.digg_count, c.ip_label)

asyncio.run(main())
```

只取某条评论的回复：

```python
async with DouyinCommentClient(cookie) as client:
    async for r in client.iter_replies(aweme_id, comment_id):
        print(r.text)
```

## 四、必须知道的三件事（踩坑记录）

### 1. 绝不要往签名参数里塞随机 msToken

上游常见写法是生成一个随机字符串当 `msToken` 加进 query，然后拿这个 query 去算签名。

**这会导致抖音返回 HTTP 200 但响应体为空**，表现成「接口能通但视频就是没评论」，极难定位。

实测对照：

| 变体 | 二级评论结果 |
|---|---|
| 含随机 msToken | 0 / 15 条 |
| 不含 msToken | **15 / 15 条** |

本 Skill 的 `WEB_PARAMS` 里刻意没有 `msToken`，`tests/test_crawler.py` 有回归测试守着这条。

### 2. 签名用的 query 串必须和实际请求逐字节一致

参数顺序、URL 编码方式都要一样。本 Skill 用同一个 dict 生成签名前的 query 和最终请求参数，避免两边跑偏。

### 3. 签名算法：TT1 用 W1[j]，TT2 用 W[j]

这是 SM3（GB/T 32905-2016）最容易写错的地方。写反了不会报错，只是算出的摘要全错 —— **签名会被服务端拒绝，然后你看到的就是空响应**。

本 Skill 的 `abogus.py` 已用 OpenSSL/Node 的 SM3 标准向量交叉验证：

```text
"abc"      → 66c7f0f4...ba8e0  ✓
"abcd"*16  → debe9ff9...5732  ✓
""         → 1ab21d83...aa2b  ✓
"a"*1000   → f4bedca9...046f  ✓
```

跑测试：

```bash
python3 -m unittest discover -s tests -v
```

## 五、参数说明

| 参数 | 默认值 | 说明 |
|---|---|---|
| `--aweme-id` | 必填 | 视频 ID。分享链接 `douyin.com/video/7633646113853104116` 里的数字 |
| `--cookie-file` | `~/.config/douyin-comments/cookie.txt` | Cookie 文件路径 |
| `--with-replies` | 关 | 是否抓二级回复 |
| `--count` | 30 | 每页条数 |
| `--max-comments` | 无 | 最多抓多少条一级评论（调试用） |
| `--output` | `./output` | 输出目录 |
| `--format` | both | csv / json / both |
| `--min-interval` | 0.8 | 两次请求最小间隔秒数。**调低容易触发风控** |

## 六、稳定性说明

| 场景 | 表现 |
|---|---|
| Cookie 有效 | 正常返回评论、分页 |
| Cookie 过期 | 报「抖音返回空响应」，退出码 3 |
| 缺少 `ttwid` | 同样报空响应。抖音要求 cookie 里带 `ttwid` |
| 频繁请求 | 空响应概率上升。默认 0.8s 间隔，别调太低 |
| 某条评论的回复取不到 | 静默跳过该条，不影响整体抓取 |

**退出码约定**：

- `0` 成功
- `1` 参数/IO 错误
- `2` cookie 文件问题
- `3` 抖音接口返回空响应或业务错误

## 七、安全约定

- Cookie **只从文件读取**，不接受命令行明文参数（避免进 shell history 和 `ps` 输出）
- Cookie 不会被打印，不会写进 CSV/JSON
- 输出目录默认不含凭据
- 建议把 cookie 文件权限设为 `600`：

```bash
chmod 600 ~/.config/douyin-comments/cookie.txt
```

- 本 Skill 仓库内**不含任何真实 cookie**

## 八、目录结构

```text
douyin-comment-crawler/
├── SKILL.md
├── README.md
├── LICENSE
├── requirements.txt
├── scripts/
│   ├── abogus.py          # 纯 Python 签名：SM3 + RC4 + 自定义 base64
│   ├── douyin_client.py   # 客户端：评论/回复抓取、解析、导出
│   └── cli.py             # 命令行入口
├── tests/
│   └── test_crawler.py    # 离线测试，不联网
└── references/
    ├── algorithm.md        # 签名算法原理与踩坑
    └── api.md              # 接口字段说明
```

## 九、上游来源与合规

- 能力方向参考了社区项目 [alphaply/DouyinComments](https://github.com/alphaply/DouyinComments)（约 216 star）。
- **该仓库未声明许可证**，其签名逻辑又源自 `ShilongLee/Crawler` 的「非商业使用许可证 1.0」，明确禁止商业使用。
- 因此本 Skill **没有复制上游任何代码**，而是用公开标准算法（SM3 / GB/T 32905-2016、RC4、base64）**独立重写**了签名实现。
- 抖音接口属于平台私有接口，可能随平台策略变化而失效；使用时请遵守目标平台的服务条款与当地法律法规，控制频率、仅用于合规的数据分析用途。

## 十、定制化开发

如需定制化开发，可直接联系 ERIC：

- **ERIC AI 技术专家**，专注于人工智能和自动化工具的研究与应用
- 邮箱：`gyc567@gmail.com`
- Twitter：`@EricBlock2100`
- 微信：`360369487`
- Telegram：`https://t.me/fatoshi_block`
- Telegram 频道：`https://t.me/cryptochanneleric`
- 加密情报 TG 群：`https://t.me/btcgogopen`
- YouTube：`@0XBitFinance`
- 博客：`topdigg.com`
