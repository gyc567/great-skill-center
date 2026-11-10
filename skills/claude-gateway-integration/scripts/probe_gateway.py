#!/usr/bin/env python3
"""Claude Gateway 端点探测 —— 不需要任何凭据，验证网关是否可达、端点是否存在。

用途：
    1. 部署前确认网关可达
    2. 排查"是不是网关挂了"还是"是我的 key 有问题"
    3. 文档过期时重新核对端点

只用标准库，零依赖。默认不发送任何真实请求内容。

用法:
    python3 probe_gateway.py                 # 跑全部检查
    python3 probe_gateway.py --base https://distill5.iwz.cc
    python3 probe_gateway.py --json
"""

import argparse
import json
import sys
import urllib.error
import urllib.request

DEFAULT_BASE = "https://distill5.iwz.cc"

# 端点 -> (方法, 需要凭据?)
PROBES = [
    ("/",                "GET",  False, "站点外壳"),
    ("/api/health",      "GET",  False, "后端健康检查"),
    ("/api/public/console-identifier", "GET", False, "控制台标识"),
    ("/v1/messages",     "POST", True,  "Anthropic Messages API"),
    ("/v1/messages/count_tokens", "POST", True, "token 计数"),
    ("/v1/responses",    "POST", True,  "OpenAI Responses API"),
    ("/v1/moderations",  "POST", True,  "内容审核"),
    ("/v1/mcp_servers",  "GET",  True,  "MCP 服务器列表"),
    ("/api/public/key-usage", "POST", False, "公开用量查询"),
]

FAKE_KEY = "sk-probe-invalid-do-not-use"


def probe(base, path, method, needs_key, desc):
    url = base.rstrip("/") + path
    headers = {"Content-Type": "application/json", "User-Agent": "gateway-probe/1.0"}
    if needs_key:
        headers["x-api-key"] = FAKE_KEY
        headers["anthropic-version"] = "2023-06-01"
    body = None
    if method == "POST":
        body = json.dumps({
            "model": "claude-sonnet-4-6",
            "max_tokens": 1,
            "messages": [{"role": "user", "content": "probe"}],
            "token": FAKE_KEY,
            "input": "probe",
        }).encode()
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        r = urllib.request.urlopen(req, timeout=20)
        code, payload, ctype = r.status, r.read(400), r.headers.get("content-type", "")
    except urllib.error.HTTPError as e:
        code, payload, ctype = e.code, e.read(400), e.headers.get("content-type", "")
    except Exception as e:
        return {"path": path, "method": method, "desc": desc, "status": "ERR",
                "note": str(e)[:120], "ok": False}
    text = payload.decode("utf-8", "replace")
    is_json = "json" in ctype
    # SPA fallback：200 + text/html + 短内容 = 该路径无后端路由
    spa_fallback = (code == 200 and "text/html" in ctype and len(text) < 1200)
    # 401 = 端点存在且要求鉴权（正常）
    # 404 + JSON not_found = 路由存在但参数无效
    if path == "/":
        # 站点外壳本身就是 SPA HTML，不适用 SPA 回退判定
        verdict, ok = "站点外壳（正常）", True
    elif code == 401:
        verdict, ok = "端点存在，需鉴权（预期）", True
    elif code == 404 and is_json:
        verdict, ok = "路由存在，参数无效（预期）", True
    elif code == 200 and is_json:
        verdict, ok = "端点开放且返回 JSON", True
    elif spa_fallback:
        verdict, ok = "SPA 回退，无后端路由", False
    else:
        verdict, ok = f"返回 HTTP {code}", code < 500
    return {"path": path, "method": method, "desc": desc, "status": code,
            "verdict": verdict, "ok": ok, "sample": text[:120].replace("\n", " ")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=DEFAULT_BASE)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    results = [probe(args.base, p, m, k, d) for p, m, k, d in PROBES]

    if args.json:
        print(json.dumps({"base": args.base, "results": results}, ensure_ascii=False, indent=2))
        return 0 if all(r["ok"] for r in results) else 1

    print("Claude Gateway 端点探测")
    print("=" * 66)
    print(f"目标: {args.base}")
    print("=" * 66)
    for r in results:
        mark = "✓" if r["ok"] else "✗"
        st = r["status"]
        print(f"  {mark} [{str(st):>4}] {r['method']:<4} {r['path']}")
        print(f"        {r['desc']} — {r.get('verdict') or r.get('note')}")
    ok = sum(1 for r in results if r["ok"])
    print("-" * 66)
    print(f"通过 {ok}/{len(results)}")
    print("说明: 401/404-JSON 均为预期（端点存在）；SPA 回退说明路径无后端路由。")
    return 0 if ok == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
