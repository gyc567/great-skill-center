#!/usr/bin/env python3
"""
link-ops — 短链与链接归因 API 客户端

一个零依赖的短链/归因平台统一客户端。第一方实现是 Dub
(https://github.com/dubinc/dub, AGPL-3.0)，但接口设计对所有主流短链服务通用。

支持:
  - Dub (api.dub.co)          —— 完整功能：短链、UTM、A/B、标签、文件夹、分析、追踪事件
  - Bitly (api-ssl.bitly.com) —— 基础短链
  - TinyURL (tinyurl.com)     —— 基础短链（无需 API Key）
  - 自定义（任何兼容的 REST 短链服务）

认证:
  export LINK_OPS_API_KEY=dub_xxx     # Dub
  export LINK_OPS_API_KEY=bitly_xxx   # Bitly
  export LINK_OPS_PROVIDER=dub        # dub | bitly | tinyurl | custom

用法:
  python3 link_ops.py create "https://example.com" --key promo --utm-source wechat
  python3 link_ops.py list --limit 20
  python3 link_ops.py stats <linkId>
  python3 link_ops.py track lead <linkId> --amount 99 --customer "张三"
  python3 link_ops.py utm build --source wechat --campaign spring --term ai
  python3 link_ops.py domain suggest "AI Skills 创作小店"
  python3 link_ops.py reserved "stats"
  python3 link_ops.py urls "example.com/path?q=1"
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

API_BASE = {
    "dub": "https://api.dub.co",
    "bitly": "https://api-ssl.bitly.com/v4",
    "tinyurl": "https://tinyurl.com/api-create.php",
    "custom": os.environ.get("LINK_OPS_API_BASE", "https://api.dub.co"),
}

# Dub 保留 slug —— 不可作为短链 key（来自上游 reserved-slugs.ts）
RESERVED_SLUGS = {
    "dub", "va", "static", "stats", "share", "deeplink", "robots.txt", "undefined",
    "null", "proxy", "account", "api", "auth", "pricing", "about", "metatags",
    "blog", "changelog", "atom", "careers", "docs", "features", "contact", "terms",
    "privacy", "admin", "help", "new", "info", "demo", "discord", "reddit",
    "guides", "campaigns", "links", "workspaces", "settings", "analytics",
    "invites", "domains", "events", "referrals", "webhooks", "upgrade", "wrapped",
    "rewind", "invoices", "onboarding", "program", "programs", "partners",
    "payouts", "commissions", "sales", "resources", "messages", "marketplace",
    "fraud", "overview", "bounties", "earnings",
}

UTM_TAGS = ("utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content")


def provider() -> str:
    return os.environ.get("LINK_OPS_PROVIDER", "dub").strip().lower()


def api_key() -> str:
    key = os.environ.get("LINK_OPS_API_KEY", "").strip()
    if not key and provider() == "tinyurl":
        return ""
    if not key:
        die("缺少 API Key。请设置环境变量 LINK_OPS_API_KEY。")
    return key


def die(msg: str, code: int = 1):
    print(f"❌ {msg}", file=sys.stderr)
    sys.exit(code)


def request(method: str, path: str, body=None, query=None, raw=False):
    """统一的 HTTP 调用。Dub 用 Bearer token，Bitly 用 token query。"""
    prov = provider()
    base = API_BASE.get(prov, API_BASE["dub"]).rstrip("/")
    url = f"{base}{path}" if path.startswith("/") else f"{base}/{path}"

    if query:
        q = urllib.parse.urlencode({k: v for k, v in query.items() if v not in (None, "")})
        if q:
            url = f"{url}?{q}"

    headers = {"Accept": "application/json", "User-Agent": "link-ops/1.0"}
    payload = None

    if prov == "dub":
        headers["Authorization"] = f"Bearer {api_key()}"
        if body is not None:
            payload = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"
    elif prov == "bitly":
        url = f"{url}?token={api_key()}"
        if body is not None:
            payload = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"
    elif prov == "tinyurl":
        if body is not None:
            payload = urllib.parse.urlencode(body).encode()
            headers["Content-Type"] = "application/x-www-form-urlencoded"
    else:
        key = api_key()
        if key:
            headers["Authorization"] = f"Bearer {key}"
        if body is not None:
            payload = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=payload, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            text = resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:500]
        die(f"HTTP {e.code} {e.reason}\n{detail}")
    except urllib.error.URLError as e:
        die(f"网络错误: {e.reason}")

    if raw:
        return text
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


# --------------------------------------------------------------------------
# 纯函数（移植自 dubinc/dub packages/utils，无外部依赖）
# --------------------------------------------------------------------------

def normalize_url(url: str) -> str:
    """把裸域名补成 https://，与 Dub 的 getUrlFromString 行为一致。"""
    url = (url or "").strip()
    if not url:
        return ""
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url):
        return url
    if "." in url and " " not in url:
        return f"https://{url}"
    return url


def get_apex_domain(url: str) -> str:
    """取主域名，正确处理 co.uk / vercel.app 这类二级后缀。"""
    try:
        from urllib.parse import urlparse
        host = urlparse(url.replace(r"^[a-zA-Z]+://", "https://"), scheme="https").hostname or ""
    except Exception:
        return ""
    if not host:
        return ""
    if host == "youtu.be":
        return "youtube.com"
    parts = host.split(".")
    if len(parts) > 2:
        # 二级 TLD（co.uk、com.ua）
        if parts[-2] in {"co", "com", "org", "net", "gov", "edu", "ac"} and len(parts[-1]) == 2:
            return ".".join(parts[-3:])
        # 建站平台子域
        if ".".join(parts[-2:]) in {"vercel.app", "netlify.app", "pages.dev", "web.app"}:
            return ".".join(parts[-3:])
        return ".".join(parts[-2:])
    return host


def link_constructor(domain: str, key: str, pretty: bool = False) -> str:
    """拼出短链 URL。key 为 _root 时不带路径段。"""
    if not domain:
        return ""
    url = f"https://{domain}"
    if key and key != "_root":
        url = f"{url}/{key}"
    return url.replace("https://", "") if pretty else url


def slug_is_reserved(slug: str) -> bool:
    return (slug or "").strip().lower() in RESERVED_SLUGS


def build_utm(source: str = "", medium: str = "", campaign: str = "",
              term: str = "", content: str = "") -> dict:
    """构造 UTM 参数（只包含非空项）。"""
    pairs = {"utm_source": source, "utm_medium": medium, "utm_campaign": campaign,
             "utm_term": term, "utm_content": content}
    return {k: v for k, v in pairs.items() if v}


def apply_utm(url: str, utm: dict) -> str:
    """把 UTM 参数合并进 URL（覆盖同名旧参数）。"""
    if not utm:
        return url
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}{urllib.parse.urlencode(utm)}"


def suggest_domain(name: str) -> str:
    """从品牌名生成候选短链域名。移植自 Dub 的 generateDomainFromName。"""
    import re
    slug = re.sub(r"[^a-z0-9]+", "", (name or "").lower())
    if len(slug) < 3:
        return ""
    return f"{slug}.link"


# --------------------------------------------------------------------------
# 命令
# --------------------------------------------------------------------------

def cmd_create(a):
    url = normalize_url(a.url)
    if not url:
        die("URL 不能为空")

    body = {"url": url}
    if a.key:
        if slug_is_reserved(a.key):
            die(f"'{a.key}' 是保留 slug，不能用作短链 key")
        body["key"] = a.key
    if a.domain:
        body["domain"] = a.domain
    if a.title:
        body["title"] = a.title
    if a.tag:
        body["tagNames"] = [a.tag]

    utm = build_utm(a.utm_source, a.utm_medium, a.utm_campaign, a.utm_term, a.utm_content)
    if utm:
        body["utm"] = utm

    if provider() == "bitly":
        res = request("POST", "/shorten", body)
        out = {"shortLink": res.get("short_link"), "url": res.get("long_url")}
    elif provider() == "tinyurl":
        res = request("POST", "", {"url": url}, raw=True)
        out = {"shortLink": res.strip()}
    else:
        res = request("POST", "/links", body)
        out = {
            "id": res.get("id"),
            "shortLink": res.get("shortLink") or res.get("url"),
            "url": res.get("url"),
            "key": res.get("key"),
            "domain": res.get("domain"),
            "qrCode": res.get("qrCode"),
        }
    print(json.dumps(out, ensure_ascii=False, indent=2))


def cmd_list(a):
    if provider() == "bitly":
        res = request("GET", "/shorten", query={"limit": a.limit})
        items = [{"key": i.get("id"), "shortLink": i.get("short_link"),
                   "url": i.get("long_url"), "clicks": i.get("clicks")} for i in res.get("short_links", [])]
    else:
        res = request("GET", "/links", query={"pageSize": a.limit, "page": a.page})
        items = res if isinstance(res, list) else res.get("links", res.get("data", []))
        items = [{"id": i.get("id"), "key": i.get("key"), "shortLink": i.get("shortLink"),
                   "url": i.get("url"), "clicks": i.get("clicks"), "createdAt": i.get("createdAt")}
                  for i in items]
    print(json.dumps({"count": len(items), "links": items}, ensure_ascii=False, indent=2))


def cmd_stats(a):
    res = request("GET", f"/links/{a.link_id}")
    if not isinstance(res, dict):
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return
    out = {k: res.get(k) for k in
           ("id", "key", "shortLink", "url", "clicks", "uniqueClicks", "totalClicks",
            "lastClickedAt", "createdAt", "title")}
    out["analytics"] = res.get("analytics") or res.get("topCountries") or None
    print(json.dumps(out, ensure_ascii=False, indent=2))


def cmd_track(a):
    """回传转化事件（lead / sale / open / click）。"""
    if provider() != "dub":
        die("事件回传目前仅支持 Dub（其它平台请用各自的转化回传接口）")
    body = {"customer": a.customer} if a.customer else {}
    if a.amount is not None:
        body["amount"] = a.amount
    if a.event == "lead":
        res = request("POST", f"/track/lead/{a.link_id}", body)
    elif a.event == "sale":
        res = request("POST", f"/track/sale/{a.link_id}", body)
    elif a.event == "open":
        res = request("POST", f"/track/open/{a.link_id}", body)
    else:
        res = request("POST", f"/track/click/{a.link_id}", body)
    print(json.dumps(res, ensure_ascii=False, indent=2))


def cmd_utm(a):
    utm = build_utm(a.source, a.medium, a.campaign, a.term, a.content)
    out = {"utm": utm, "query": urllib.parse.urlencode(utm)}
    if a.url:
        out["url"] = apply_utm(normalize_url(a.url), utm)
    print(json.dumps(out, ensure_ascii=False, indent=2))


def cmd_domain(a):
    print(json.dumps({"name": a.name, "suggestions": [suggest_domain(a.name)]},
                     ensure_ascii=False, indent=2))


def cmd_reserved(a):
    print(json.dumps({"slug": a.slug, "reserved": slug_is_reserved(a.slug)},
                     ensure_ascii=False, indent=2))


def cmd_urls(a):
    url = normalize_url(a.url)
    print(json.dumps({
        "input": a.url,
        "normalized": url,
        "apexDomain": get_apex_domain(url),
        "host": urllib.parse.urlparse(url).hostname,
        "path": urllib.parse.urlparse(url).path,
        "params": dict(urllib.parse.parse_qsl(urllib.parse.urlparse(url).query)),
    }, ensure_ascii=False, indent=2))


def main():
    p = argparse.ArgumentParser(description="短链与链接归因 API 客户端")
    p.add_argument("--provider", choices=["dub", "bitly", "tinyurl", "custom"],
                   help="覆盖 LINK_OPS_PROVIDER")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("create", help="创建短链")
    c.add_argument("url")
    c.add_argument("--key", help="自定义短链 key（不能是保留 slug）")
    c.add_argument("--domain", help="短链域名（需已在平台配置）")
    c.add_argument("--title", help="链接标题")
    c.add_argument("--tag", help="标签名")
    c.add_argument("--utm-source", default="")
    c.add_argument("--utm-medium", default="")
    c.add_argument("--utm-campaign", default="")
    c.add_argument("--utm-term", default="")
    c.add_argument("--utm-content", default="")
    c.set_defaults(func=cmd_create)

    l = sub.add_parser("list", help="列出短链")
    l.add_argument("--limit", type=int, default=20)
    l.add_argument("--page", type=int, default=1)
    l.set_defaults(func=cmd_list)

    s = sub.add_parser("stats", help="查看单条短链统计")
    s.add_argument("link_id")
    s.set_defaults(func=cmd_stats)

    t = sub.add_parser("track", help="回传转化事件")
    t.add_argument("event", choices=["lead", "sale", "open", "click"])
    t.add_argument("link_id")
    t.add_argument("--amount", type=float, help="金额（分）")
    t.add_argument("--customer", help="客户标识（邮箱/ID）")
    t.set_defaults(func=cmd_track)

    u = sub.add_parser("utm", help="构造 UTM 参数")
    u.add_argument("--source", default="")
    u.add_argument("--medium", default="")
    u.add_argument("--campaign", default="")
    u.add_argument("--term", default="")
    u.add_argument("--content", default="")
    u.add_argument("--url", help="原始 URL，会合并 UTM")
    u.set_defaults(func=cmd_utm)

    d = sub.add_parser("domain", help="从品牌名生成候选短链域名")
    d.add_argument("name")
    d.set_defaults(func=cmd_domain)

    r = sub.add_parser("reserved", help="检查 slug 是否为保留字")
    r.add_argument("slug")
    r.set_defaults(func=cmd_reserved)

    ur = sub.add_parser("urls", help="解析 URL（补协议、取主域名、拆参数）")
    ur.add_argument("url")
    ur.set_defaults(func=cmd_urls)

    a = p.parse_args()
    if a.provider:
        os.environ["LINK_OPS_PROVIDER"] = a.provider
    a.func(a)


if __name__ == "__main__":
    main()
