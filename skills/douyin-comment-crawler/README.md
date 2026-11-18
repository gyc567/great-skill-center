# 抖音评论抓取 —— 一级评论 + 二级回复

> 品牌：AI Skills 创作小店

抓取抖音视频评论区的**一级评论**和**二级回复**，导出结构化 CSV / JSON。

签名算法为**纯 Python 实现**（SM3 + RC4），**不需要 Node.js、不需要 execjs**。

## 特性

| 特性 | 说明 |
|---|---|
| 一级评论 | 正文、点赞数、昵称、抖音号、主页、IP 属地、回复数 |
| 二级回复 | 支持，可选开启，带「回复给谁」和父评论 ID |
| 分页 | 自动翻页，`has_more` / `cursor` 处理 |
| 导出 | CSV（UTF-8 BOM，Excel 直开）+ JSON |
| 依赖 | 只需 `httpx`（Python 3.9+） |
| 签名 | 纯标准库实现，零外部依赖 |

## 安装

```bash
cd skills/douyin-comment-crawler
pip install -r requirements.txt
```

Python 3.9+，无需 Node.js。

## 使用

### 准备 Cookie

抖音网页版接口需要登录态。浏览器 F12 → Network → 任意请求 → Request Headers → 复制 `cookie` 整串。

```bash
mkdir -p ~/.config/douyin-comments
echo '粘贴你的完整 cookie 串' > ~/.config/douyin-comments/cookie.txt
chmod 600 ~/.config/douyin-comments/cookie.txt
```

### 抓取

```bash
python scripts/cli.py \
  --aweme-id 7633646113853104116 \
  --cookie-file ~/.config/douyin-comments/cookie.txt \
  --with-replies \
  --output ./output
```

### 命令行参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `--aweme-id` | 必填 | 视频 ID（分享链接里的数字） |
| `--cookie-file` | `~/.config/douyin-comments/cookie.txt` | Cookie 文件 |
| `--with-replies` | 关 | 抓二级回复 |
| `--count` | 30 | 每页条数 |
| `--max-comments` | 无 | 最多抓多少条一级评论 |
| `--output` | `./output` | 输出目录 |
| `--format` | both | csv / json / both |
| `--timeout` | 30 | 单请求超时（秒） |
| `--min-interval` | 0.8 | 请求最小间隔（秒），调低易触发风控 |
| `--quiet` | 关 | 只输出文件路径 |

### 作为库使用

```python
import asyncio
from scripts.douyin_client import DouyinCommentClient, load_cookie

async def main():
    cookie = load_cookie("~/.config/douyin-comments/cookie.txt")
    async with DouyinCommentClient(cookie) as client:
        comments = await client.fetch_all(
            "7633646113853104116", with_replies=True
        )
        for c in comments:
            print(f"[{'二级' if c.level == 2 else '一级'}] {c.text} ({c.digg_count}赞, {c.ip_label})")

asyncio.run(main())
```

## 测试

```bash
python3 -m unittest discover -s tests -v
```

离线测试，不联网。覆盖 SM3 标准向量、RC4 往返、base64 长度规则、签名结构、评论解析、CSV/JSON 导出，以及「不得引入随机 msToken」的回归测试。

## 三个必须知道的坑

### 1. 随机 msToken 会让接口返回空响应

上游常见写法是生成随机字符串当 `msToken` 加进 query 并参与签名。这会让抖音返回 **HTTP 200 但响应体为空**，看起来像「接口正常但没评论」。

实测：含随机 msToken 时二级评论 0/15；不含时 15/15。

### 2. 签名 query 串必须和实际请求逐字节一致

参数顺序和 URL 编码方式都要一致。本项目用同一份 dict 生成签名前 query 和请求参数。

### 3. SM3 里 TT1 用 W1[j]，TT2 用 W[j]

写反不会报错，只是摘要全错 → 签名被拒 → 空响应。`abogus.py` 已用 OpenSSL / Node 的 SM3 标准向量交叉验证。

## 安全

- Cookie 只从文件读取，不接受命令行明文（不进 shell history / `ps`）
- Cookie 不打印、不写入输出文件
- 仓库内不含任何真实凭据

## 上游来源与许可

能力方向参考 [alphaply/DouyinComments](https://github.com/alphaply/DouyinComments)（约 216 star）。该仓库**未声明许可证**，其签名逻辑源自 `ShilongLee/Crawler` 的「非商业使用许可证 1.0」（禁止商业使用）。

因此本项目**未复制上游任何代码**，签名部分依据公开标准算法（SM3 / GB/T 32905-2016、RC4、base64）**独立重写**。

详见 `LICENSE` 文件中的 ATTRIBUTION NOTICE。

## 定制化开发

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
