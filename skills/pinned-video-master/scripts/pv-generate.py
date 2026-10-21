#!/usr/bin/env python3
"""pv-generate.py — 调用 HeyGen 生成 30 秒置顶视频

用法:
  export HEYGEN_API_KEY=...
  python3 pv-generate.py \\
    --script scripts/final-script.txt \\
    --avatar-id <AVATAR_ID> \\
    --voice-id <VOICE_ID> \\
    --output out/pinned-video.mp4

  # 只打印请求体，不调用 API
  python3 pv-generate.py --script s.txt --avatar-id A --voice-id V --dry-run

  # 从档案读语言与画幅
  python3 pv-generate.py --dossier pinned-dossier.md --script s.txt --avatar-id A --voice-id V

API:
  POST https://api.heygen.com/v2/video/generate
  GET  https://api.heygen.com/v2/video/{video_id}
  Header: X-Api-Key: $HEYGEN_API_KEY
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

API_BASE = "https://api.heygen.com"
CREATE_PATH = "/v2/video/generate"
STATUS_PATH = "/v2/video/{video_id}"
POLL_INTERVAL = 10
POLL_TIMEOUT = 900


def http(method, url, api_key, payload=None):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("X-Api-Key", api_key)
    req.add_header("Accept", "application/json")
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            body = r.read().decode("utf-8", "ignore")
            try:
                return r.status, json.loads(body)
            except json.JSONDecodeError:
                return r.status, {"raw": body[:500]}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")
        try:
            return e.code, json.loads(body)
        except json.JSONDecodeError:
            return e.code, {"error": body[:500]}
    except urllib.error.URLError as e:
        return 0, {"error": str(e)}


def extract_speech(text):
    """从脚本文件里抽出纯口播文本。

    支持表格格式： | 钩子 | 0-3s | 台词 | 字数 |
    去掉段名列、时间列、字数统计列，保留台词。
    """
    lines = []
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith(">"):
            continue
        if s.startswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            cells = [c for c in cells if c]
            if not cells:
                continue
            if all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                continue
            if any(re.search(r"(台词|画面|字幕|字数|词数|word|时间|依据|来源|Source)", c, re.I) for c in cells):
                continue
            # 去掉末列字数统计（形如 /12 或 12/20）
            if len(cells) >= 2 and re.fullmatch(r"[\d/.\s]*", cells[-1]):
                cells = cells[:-1]
            # 去掉首列段名
            if len(cells) >= 2 and re.search(
                    r"(钩子|身份|背书|现状|价值|Hook|Identity|Proof|Now|Value)", cells[0], re.I):
                cells = cells[1:]
            # 去掉时间列（0-3s / 0-3秒 / 3-8s）
            cells = [c for c in cells if not re.fullmatch(r"\d+\s*[-~到]\s*\d+\s*[s秒]?", c)]
            for c in cells:
                c = re.sub(r"^\*+|\*+$", "", c).strip()
                if c and not re.fullmatch(r"[\d/.\s%]*", c):
                    lines.append(c)
            continue
        if re.match(r"^[-*]\s*[-*]\s*$", s):
            continue
        if re.search(r"(字数|word count|上限|依据|来源|Source|avatar_id|voice_id|dimension|speed|language)\s*[:：]?", s, re.I):
            continue
        if s in {"中文", "英文", "English", "English Version", "中文版"}:
            continue
        s = re.sub(r"^\*+|\*+$", "", s).strip()
        if s:
            lines.append(s)
    return " ".join(lines)


def read_dossier_meta(path):
    """从档案 frontmatter 读 language / 画幅。"""
    meta = {"language": "zh", "width": 1080, "height": 1920}
    if not path or not os.path.exists(path):
        return meta
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end > 0:
            for line in text[3:end].splitlines():
                k, _, v = line.partition(":")
                k = k.strip().lower()
                v = v.strip().strip("\"'")
                if k == "language":
                    meta["language"] = "en" if v.lower().startswith("en") else "zh"
                elif k in ("width", "height"):
                    try:
                        meta[k] = int(v)
                    except ValueError:
                        pass
    body = text
    if "9:16" in body and meta["width"] == 1080:
        pass
    elif "16:9" in body:
        meta["width"], meta["height"] = 1920, 1080
    return meta


def build_payload(speech, avatar_id, voice_id, meta, speed, caption, background):
    return {
        "video_inputs": [
            {
                "character": {
                    "type": "avatar",
                    "avatar_id": avatar_id,
                    "avatar_style": "normal",
                    "voice": {
                        "type": "audio",
                        "input_text": speech,
                        "voice_id": voice_id,
                        "speed": speed,
                    },
                },
                "background": {
                    "type": "color",
                    "value": background,
                },
            }
        ],
        "dimension": {"width": meta["width"], "height": meta["height"]},
        "language": meta["language"],
        "caption": caption,
    }


def main():
    ap = argparse.ArgumentParser(description="生成置顶视频（HeyGen）")
    ap.add_argument("--script", required=True, help="逐字稿文件路径")
    ap.add_argument("--dossier", help="档案路径（用于读语言/画幅）")
    ap.add_argument("--avatar-id", required=True)
    ap.add_argument("--voice-id", required=True)
    ap.add_argument("--output", default="out/pinned-video.mp4")
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--caption", action="store_true", help="生成带字幕版本")
    ap.add_argument("--background", default="#FFFFFF")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--timeout", type=int, default=POLL_TIMEOUT)
    args = ap.parse_args()

    if not os.path.exists(args.script):
        print(f"[FAIL] 找不到脚本文件: {args.script}")
        return 1

    with open(args.script, encoding="utf-8") as f:
        speech = extract_speech(f.read())
    if not speech:
        print("[FAIL] 未从脚本中提取到口播文本")
        return 1

    meta = read_dossier_meta(args.dossier)
    payload = build_payload(speech, args.avatar_id, args.voice_id, meta,
                            args.speed, args.caption, args.background)

    print(f"口播文本长度: {len(speech)} 字符")
    print(f"画幅: {meta['width']}x{meta['height']}  语言: {meta['language']}")

    if args.dry_run:
        print("\n--- 请求体（dry-run，未调用 API）---")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    api_key = os.environ.get("HEYGEN_API_KEY")
    if not api_key:
        print("[FAIL] 环境变量 HEYGEN_API_KEY 未设置")
        print("       export HEYGEN_API_KEY=<你的 key>")
        return 1

    status, resp = http("POST", API_BASE + CREATE_PATH, api_key, payload)
    if status not in (200, 201):
        print(f"[FAIL] 创建视频失败 HTTP {status}")
        print(json.dumps(resp, ensure_ascii=False, indent=2)[:1200])
        return 1

    if not isinstance(resp, dict):
        print("[FAIL] 响应格式异常")
        print(str(resp)[:800])
        return 1
    data_field = resp.get("data")
    data_field = data_field if isinstance(data_field, dict) else {}
    video_id = data_field.get("video_id") or resp.get("video_id")
    if not video_id:
        print("[FAIL] 响应中没有 video_id")
        print(json.dumps(resp, ensure_ascii=False, indent=2)[:1200])
        return 1
    print(f"视频任务已创建: {video_id}")

    elapsed = 0
    video_url = None
    while elapsed < args.timeout:
        time.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL
        st, sresp = http("GET", API_BASE + STATUS_PATH.format(video_id=video_id), api_key)
        if st != 200:
            print(f"[WARN] 查询失败 HTTP {st}，继续重试")
            continue
        data = sresp.get("data") if isinstance(sresp, dict) else None
        data = data if isinstance(data, dict) else {}
        vstatus = data.get("status") or (sresp.get("status") if isinstance(sresp, dict) else None) or "unknown"
        print(f"  [{elapsed:>4}s] status={vstatus}")
        if vstatus == "completed":
            video_url = data.get("video_url") or (sresp.get("video_url") if isinstance(sresp, dict) else None)
            break
        if vstatus == "failed":
            print("[FAIL] 生成失败:")
            print(json.dumps(sresp, ensure_ascii=False, indent=2)[:1200])
            return 1

    if not video_url:
        print(f"[FAIL] 超时（{args.timeout}s）仍未完成。可稍后重试查询，video_id={video_id}")
        return 1

    os.makedirs(os.path.dirname(os.path.abspath(args.output)) or ".", exist_ok=True)
    try:
        with urllib.request.urlopen(video_url, timeout=300) as r, \
                open(args.output, "wb") as out:
            while True:
                chunk = r.read(1 << 16)
                if not chunk:
                    break
                out.write(chunk)
    except Exception as e:
        print(f"[FAIL] 下载视频失败: {e}")
        print(f"       视频仍可在 HeyGen 控制台查看: video_id={video_id}")
        print(f"       直链: {video_url}")
        return 1

    size = os.path.getsize(args.output)
    print(f"\n✅ 视频已生成: {args.output} ({size/1024/1024:.2f} MB)")
    print(f"   video_id: {video_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
