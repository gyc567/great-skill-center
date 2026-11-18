"""抖音评论抓取客户端 —— 一级评论 + 二级评论。

设计要点（均来自真实抓取验证）：
  * a_bogus 签名由纯 Python 实现（scripts/abogus.py），不依赖 Node.js。
  * **绝不能**往签名参数里塞随机 msToken —— 服务端会返回 HTTP 200
    但响应体为空，表现为「接口正常但没有评论」，极难排查。
  * 所有网络参数必须与签名时用的查询串**逐字节一致**（同样的顺序、
    同样的编码方式），否则同样会返回空响应。
"""

from __future__ import annotations

import asyncio
import json
import time
import urllib.parse
from dataclasses import dataclass, field, asdict
from typing import Any, AsyncIterator, Iterable

import httpx

from abogus import sign

COMMENT_URL = "https://www.douyin.com/aweme/v1/web/comment/list/"
REPLY_URL = COMMENT_URL + "reply/"

DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

# 网页端固定参数。顺序即签名顺序，改动需同步验证。
WEB_PARAMS: dict[str, str] = {
    "device_platform": "webapp",
    "aid": "6383",
    "channel": "channel_pc_web",
    "update_version_code": "170400",
    "pc_client_type": "1",
    "version_code": "190500",
    "version_name": "19.5.0",
    "cookie_enabled": "true",
    "screen_width": "2560",
    "screen_height": "1440",
    "browser_language": "zh-CN",
    "browser_platform": "Win32",
    "browser_name": "Chrome",
    "browser_version": "126.0.0.0",
    "browser_online": "true",
    "engine_name": "Blink",
    "engine_version": "126.0.0.0",
    "os_name": "Windows",
    "os_version": "10",
    "cpu_core_num": "24",
    "device_memory": "8",
    "platform": "PC",
    "downlink": "10",
    "effective_type": "4g",
    "round_trip_time": "50",
}

# 评论接口与回复接口使用同一组签名参数 (0, 1, 8)
SIGN_ARGS = (0, 1, 8)


@dataclass
class Comment:
    """一条评论（一级或二级通用）。"""

    cid: str
    aweme_id: str
    text: str
    digg_count: int
    create_time: int
    nickname: str
    sec_uid: str
    unique_id: str
    ip_label: str
    reply_comment_total: int = 0
    reply_id: str = "0"
    reply_to_username: str | None = None
    level: int = 1
    images: list[str] = field(default_factory=list)

    @classmethod
    def from_raw(cls, raw: dict[str, Any], aweme_id: str, level: int = 1) -> "Comment":
        user = raw.get("user") or {}
        images: list[str] = []
        for img in raw.get("image_list") or []:
            url_list = (img.get("origin_url") or {}).get("url_list") or []
            if url_list:
                images.append(url_list[0])
        return cls(
            cid=str(raw.get("cid", "")),
            aweme_id=str(raw.get("aweme_id") or aweme_id),
            text=raw.get("text") or "",
            digg_count=int(raw.get("digg_count") or 0),
            create_time=int(raw.get("create_time") or 0),
            nickname=user.get("nickname") or "",
            sec_uid=user.get("sec_uid") or "",
            unique_id=user.get("unique_id") or "",
            ip_label=raw.get("ip_label") or "",
            reply_comment_total=int(raw.get("reply_comment_total") or 0),
            reply_id=str(raw.get("reply_id") or "0"),
            reply_to_username=raw.get("reply_to_username"),
            level=level,
            images=images,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _build_query(params: dict[str, Any]) -> str:
    """生成签名前用的查询串。

    顺序必须与最终发出的请求参数顺序一致；这里统一用 quote 对值做
    编码，签名与请求都复用同一个 dict，避免两边顺序/编码不一致。
    """
    return "&".join(
        f"{k}={urllib.parse.quote(str(v), safe='')}" for k, v in params.items()
    )


class DouyinCommentClient:
    """抖音评论客户端。

    用法::

        async with DouyinCommentClient(cookie) as client:
            async for c in client.iter_comments(aweme_id):
                print(c.text)
    """

    def __init__(
        self,
        cookie: str,
        *,
        user_agent: str = DEFAULT_UA,
        timeout: float = 30.0,
        min_interval: float = 0.8,
        max_retries: int = 2,
    ) -> None:
        if not cookie or not cookie.strip():
            raise ValueError("cookie 不能为空")
        self.cookie = cookie.strip()
        self.user_agent = user_agent
        self.timeout = timeout
        self.min_interval = min_interval
        self.max_retries = max_retries
        self._client: httpx.AsyncClient | None = None
        self._last_request = 0.0

    async def __aenter__(self) -> "DouyinCommentClient":
        self._client = httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            headers={
                "cookie": self.cookie,
                "User-Agent": self.user_agent,
                "referer": "https://www.douyin.com/",
                "accept-language": "zh-CN,zh;q=0.9",
            },
        )
        return self

    async def __aexit__(self, *exc: Any) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _throttle(self) -> None:
        elapsed = time.monotonic() - self._last_request
        if elapsed < self.min_interval:
            await asyncio.sleep(self.min_interval - elapsed)
        self._last_request = time.monotonic()

    async def _get(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        """发起一次带签名的 GET，并返回解析后的 JSON。

        空响应体（抖音风控的直接表现）会抛出 EmptyResponseError，
        由调用方决定是否重试或降级。
        """
        assert self._client is not None, "请在 async with 块内使用"
        query = _build_query(params)
        signed = dict(params)
        signed["a_bogus"] = sign(query, self.user_agent, SIGN_ARGS)

        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            await self._throttle()
            try:
                response = await self._client.get(url, params=signed)
            except Exception as exc:  # 网络层异常
                last_error = exc
                await asyncio.sleep(1.0 * (attempt + 1))
                continue

            if not response.text:
                last_error = EmptyResponseError(
                    "抖音返回空响应体 —— 通常是 msToken/签名参数不一致导致的风控"
                )
                await asyncio.sleep(1.0 * (attempt + 1))
                continue

            try:
                payload = response.json()
            except ValueError as exc:
                last_error = exc
                break

            status = payload.get("status_code")
            if status not in (0, None):
                raise DouyinApiError(
                    f"接口返回 status_code={status} message={payload.get('message')!r}"
                )
            return payload

        raise last_error or DouyinApiError("请求失败且未取得明确错误")

    async def iter_comments(
        self, aweme_id: str, *, count: int = 30, max_pages: int = 100
    ) -> AsyncIterator[Comment]:
        """迭代某视频的一级评论。"""
        cursor = "0"
        for _ in range(max_pages):
            params: dict[str, Any] = {
                "aweme_id": str(aweme_id),
                "cursor": cursor,
                "count": str(count),
                "item_type": 0,
            }
            params.update(WEB_PARAMS)
            payload = await self._get(COMMENT_URL, params)
            for raw in payload.get("comments") or []:
                yield Comment.from_raw(raw, str(aweme_id), level=1)
            if not payload.get("has_more"):
                return
            cursor = str(payload.get("cursor") or 0)

    async def iter_replies(
        self,
        aweme_id: str,
        comment_id: str,
        *,
        count: int = 30,
        max_pages: int = 50,
    ) -> AsyncIterator[Comment]:
        """迭代某条一级评论下的二级评论。"""
        cursor = "0"
        for _ in range(max_pages):
            params: dict[str, Any] = {
                "cursor": cursor,
                "count": str(count),
                "item_type": 0,
                "item_id": str(aweme_id),
                "comment_id": str(comment_id),
            }
            params.update(WEB_PARAMS)
            payload = await self._get(REPLY_URL, params)
            for raw in payload.get("comments") or []:
                yield Comment.from_raw(raw, str(aweme_id), level=2)
            if not payload.get("has_more"):
                return
            cursor = str(payload.get("cursor") or 0)

    async def fetch_all(
        self,
        aweme_id: str,
        *,
        with_replies: bool = True,
        count: int = 30,
        max_comments: int | None = None,
    ) -> list[Comment]:
        """抓取一级评论（可选二级评论），返回扁平列表。"""
        result: list[Comment] = []
        parents: list[Comment] = []
        async for comment in self.iter_comments(aweme_id, count=count):
            result.append(comment)
            parents.append(comment)
            if max_comments is not None and len(result) >= max_comments:
                break

        if with_replies:
            for parent in parents:
                if parent.reply_comment_total <= 0:
                    continue
                try:
                    async for reply in self.iter_replies(
                        aweme_id, parent.cid, count=count
                    ):
                        result.append(reply)
                except (DouyinApiError, EmptyResponseError):
                    # 单条回复失败不影响整体
                    continue
        return result


class DouyinApiError(RuntimeError):
    """抖音接口返回了业务错误。"""


class EmptyResponseError(RuntimeError):
    """抖音返回 HTTP 200 但响应体为空（典型的签名/风控问题）。"""


def load_cookie(path: str) -> str:
    """从文件读取 cookie。

    约定：第一行是完整 cookie 串。文件应位于仓库之外，
    例如 ~/.config/douyin-comments/cookie.txt。
    """
    with open(path, "r", encoding="utf-8") as handle:
        first = handle.readline().strip()
    if not first:
        raise ValueError(f"cookie 文件为空: {path}")
    return first


def to_csv_rows(comments: Iterable[Comment]) -> list[dict[str, Any]]:
    """转成 CSV 行（字段名中文化，便于直接交付）。"""
    rows = []
    for c in comments:
        rows.append(
            {
                "层级": "二级评论" if c.level == 2 else "一级评论",
                "评论ID": c.cid,
                "评论内容": c.text,
                "点赞数": c.digg_count,
                "评论时间": time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(c.create_time)
                )
                if c.create_time
                else "",
                "用户昵称": c.nickname,
                "用户抖音号": c.unique_id,
                "用户主页": f"https://www.douyin.com/user/{c.sec_uid}"
                if c.sec_uid
                else "",
                "IP归属": c.ip_label,
                "回复总数": c.reply_comment_total,
                "回复给谁": c.reply_to_username or "",
                "父评论ID": c.reply_id if c.level == 2 else "",
                "图片": c.images[0] if c.images else "",
            }
        )
    return rows


def to_json(comments: Iterable[Comment]) -> str:
    return json.dumps(
        [c.to_dict() for c in comments], ensure_ascii=False, indent=2
    )
