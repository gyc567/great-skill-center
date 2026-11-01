#!/usr/bin/env python3
"""
Estack-lead-mining · crawler.py
抓取抖音视频评论区【公开可见】评论，含评论者抖音主页链接(sec_uid)。

数据来源：iesdouyin.com/web/api/v2/comment/list/（移动端公开评论接口）
说明：该接口返回的正是浏览器不登录也能看到的公开评论；sec_uid 是用户主页的公开标识。
      不破解签名、不绕过登录、不抓非公开数据。

用法：
    python3 crawler.py --video "https://www.douyin.com/video/7676028838417059099" --out /tmp/comments.json
    python3 crawler.py --videos "vid1,vid2,vid3" --out /tmp/comments.json   # 多个视频ID逗号分隔

输出 JSON：
    [
      {
        "video": "视频标题(若有)",
        "video_url": "https://www.douyin.com/video/7676028838417059099",
        "nickname": "评论者昵称",
        "sec_uid": "MS4wLjABAAAA...",
        "user_url": "https://www.douyin.com/user/MS4wLjABAAAA...",
        "text": "评论文本",
        "create_time": 1720000000,
        "digg_count": 12,
        "ip_location": "广东"
      }, ...
    ]
"""
import argparse, json, re, time, sys
import requests

MOBILE_UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
             "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1")

HEADERS = {
    "User-Agent": MOBILE_UA,
    "Referer": "https://www.douyin.com/",
    "Accept": "application/json, text/plain, */*",
}

COMMENT_API = "https://www.iesdouyin.com/web/api/v2/comment/list/"
MAX_PAGES = 5          # 每视频最多翻页数
COMMENTS_PER_PAGE = 20
SLEEP_BETWEEN = 1.2    # 每个请求间隔秒数（礼貌限速）


def extract_video_id(url: str) -> str:
    """从抖音视频URL/分享链接里抽出纯数字ID。"""
    m = re.search(r"(\d{15,20})", url)
    if m:
        return m.group(1)
    raise ValueError(f"无法从 {url} 提取视频ID")


def fetch_video_comments(video_id: str, video_url: str, video_name: str = "") -> list:
    """抓取单个视频的公开评论。"""
    out = []
    cursor = 0
    for page in range(MAX_PAGES):
        params = {"aweme_id": video_id, "cursor": cursor, "count": COMMENTS_PER_PAGE}
        try:
            r = requests.get(COMMENT_API, headers=HEADERS, params=params, timeout=15)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            print(f"  [warn] 第{page+1}页请求失败: {e}")
            break

        comments = data.get("comments") or []
        if not comments:
            break

        for c in comments:
            user = c.get("user") or {}
            sec_uid = user.get("sec_uid", "")
            if not sec_uid or not c.get("text"):
                continue
            out.append({
                "video": video_name,
                "video_url": video_url,
                "nickname": user.get("nickname", ""),
                "sec_uid": sec_uid,
                "user_url": f"https://www.douyin.com/user/{sec_uid}",
                "text": c.get("text", ""),
                "create_time": c.get("create_time", 0),
                "digg_count": c.get("digg_count", 0),
                "ip_location": c.get("ip_label", "") or c.get("label", ""),
            })

        cursor = data.get("cursor", cursor + COMMENTS_PER_PAGE)
        has_more = data.get("has_more", 0)
        print(f"  [ok] 视频{video_id} 第{page+1}页抓到{len(comments)}条, has_more={has_more}")
        if not has_more:
            break
        time.sleep(SLEEP_BETWEEN)
    return out


def main():
    ap = argparse.ArgumentParser(description="Estack-lead-mining 抖音公开评论抓取器")
    ap.add_argument("--video", help="单个抖音视频URL")
    ap.add_argument("--videos", help="多个视频URL，逗号分隔")
    ap.add_argument("--out", required=True, help="输出JSON路径")
    args = ap.parse_args()

    urls = []
    if args.video:
        urls = [args.video]
    if args.videos:
        urls += [u.strip() for u in args.videos.split(",") if u.strip()]
    if not urls:
        print("请提供 --video 或 --videos")
        sys.exit(1)

    all_comments = []
    for i, url in enumerate(urls, 1):
        try:
            vid = extract_video_id(url)
            print(f"\n[{i}/{len(urls)}] 抓取视频 {vid} ...")
            comments = fetch_video_comments(vid, url)
            all_comments.extend(comments)
            print(f"  累计: {len(all_comments)} 条")
        except Exception as e:
            print(f"[err] 处理 {url} 失败: {e}")
        time.sleep(SLEEP_BETWEEN)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(all_comments, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 完成，共 {len(all_comments)} 条评论 -> {args.out}")


if __name__ == "__main__":
    main()
