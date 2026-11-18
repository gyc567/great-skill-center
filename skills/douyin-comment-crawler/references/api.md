# 抖音评论接口说明

本文记录实测用到的接口与返回字段。所有请求均为 `GET`。

## 接口

### 一级评论

```text
GET https://www.douyin.com/aweme/v1/web/comment/list/
```

| 参数 | 说明 |
|---|---|
| `aweme_id` | 视频 ID |
| `cursor` | 游标，首个请求传 `0`，之后用响应里的 `cursor` |
| `count` | 每页条数，常用 20~50 |
| `item_type` | 固定 `0` |

### 二级回复

```text
GET https://www.douyin.com/aweme/v1/web/comment/list/reply/
```

| 参数 | 说明 |
|---|---|
| `item_id` | 视频 ID |
| `comment_id` | 父评论的 `cid` |
| `cursor` | 同上 |
| `count` | 同上 |
| `item_type` | 固定 `0` |

### 公共参数（web 端固定）

```
device_platform=webapp
aid=6383
channel=channel_pc_web
update_version_code=170400
pc_client_type=1
version_code=190500
version_name=19.5.0
cookie_enabled=true
screen_width=2560
screen_height=1440
browser_language=zh-CN
browser_platform=Win32
browser_name=Chrome
browser_version=126.0.0.0
browser_online=true
engine_name=Blink
engine_version=126.0.0.0
os_name=Windows
os_version=10
cpu_core_num=24
device_memory=8
platform=PC
downlink=10
effective_type=4g
round_trip_time=50
```

这些值参与 `a_bogus` 签名，改动后必须重新验证。

### 请求头

| 头 | 值 |
|---|---|
| `cookie` | 浏览器完整 cookie 串，**必须包含 `ttwid`** |
| `User-Agent` | 必须与签名时传入的 UA **完全一致** |
| `referer` | `https://www.douyin.com/` |
| `accept-language` | `zh-CN,zh;q=0.9` |

## 响应结构

```jsonc
{
  "status_code": 0,          // 0 = 成功
  "comments": [ ... ],        // 评论数组
  "cursor": 1730000000000,   // 下一页游标
  "has_more": 1,             // 是否还有下一页
  "total": 365890            // 评论总数
}
```

### 单条评论字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `cid` | string | 评论唯一 ID |
| `aweme_id` | string | 所属视频 ID |
| `text` | string | 评论正文（含 `[调皮]` 之类的表情占位符） |
| `digg_count` | int | 点赞数 |
| `create_time` | int | Unix 时间戳（秒） |
| `ip_label` | string | IP 属地，如「重庆」「广东」 |
| `reply_comment_total` | int | 该评论下的回复总数 |
| `reply_id` | string | 二级评论指向的父评论 ID；一级评论为 `"0"` |
| `reply_to_username` | string | 被回复者昵称（仅二级评论） |
| `image_list` | array | 评论附带图片，`origin_url.url_list[0]` 是原图 |
| `user.nickname` | string | 评论者昵称 |
| `user.sec_uid` | string | 用户唯一标识，用于拼主页链接 |
| `user.unique_id` | string | 用户的抖音号 |

主页链接格式：

```text
https://www.douyin.com/user/{sec_uid}
```

### 分页

`cursor` 初始传 `0`，之后把响应里的 `cursor` 原样传回。
`has_more` 为 0 时停止。

## 实测结果

在有效 cookie 下：

```text
一级 HTTP 200  len=186696
   status=0  comments=25  total=365890
   · '我做的算不算漂亮饭[调皮]'              digg=35    IP=重庆
   · '也夸夸我好吗？毕竟辛苦了大半天'          digg=36937 IP=江苏

二级 HTTP 200  len=5895
   status=0  comments=2  total=2
   · '@Aaa蟑螂恶霸'                        digg=0  IP=吉林
   · '@雪糕的甜味☀️🌻 @无言'                digg=1  IP=浙江
```

## 异常表现

| 现象 | 原因 | 处理 |
|---|---|---|
| HTTP 200，body 为空 | cookie 过期 / 缺 `ttwid` / 签名参数不一致 | 换 cookie；确认 UA 一致；确认无随机 msToken |
| HTTP 200，`status_code != 0` | 接口业务错误 | 读 `message` 字段 |
| HTTP 403 | 风控拦截 | 降低频率，等待后重试 |
| 部分评论的回复为空 | 单条回复失败 | 正常现象，已在客户端静默跳过 |

**重要**：HTTP 200 + 空 body 是「签名/会话问题」的典型信号，
不是「这个视频没有评论」。不要据此判断视频热度。

## 频率建议

- 请求间隔 ≥ 0.8 秒（客户端默认）
- 一次抓取一个视频，不要并发扫多个视频
- 遇到空响应先降速重试，而不是立刻加大 `count`

## 合规提示

抖音接口为平台私有接口，行为可能随平台策略调整而变化。
请控制频率、遵守目标平台服务条款与当地法律法规，仅用于合规的数据分析用途。
