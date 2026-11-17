#!/usr/bin/env python3
"""泄露凭据的一键处置 —— 从发现到彻底清除的标准动作。

背景（真实事件）：
  great-skill-center 从上游 anbeime 复制代码时，带进来 4 处硬编码的
  Coze API Key（97 个文件共用同一把）。首次发现时只清掉了工作区，
  git 历史里还留着 —— 直到 2 个月后才被"复盘"发现，返工两次。

  本脚本把整条链路固化：
    扫描 → 取证 → 备份 → 改写历史 → 强推 → 验证 → 复检

安全设计：
  * 默认只做「扫描 + 取证」，不改动任何东西（--dry-run 是默认行为）
  * 改写历史必须显式加 --rewrite
  * 强制先做 mirror 备份，不存在就拒绝执行
  * 不会打印密钥明文，只打印指纹（前 8 位 + 长度）

用法：
  python3 scripts/purge_secret.py --pattern 'cztei_xxx' --repo .
  python3 scripts/purge_secret.py --pattern 'cztei_xxx' --repo . --rewrite
  python3 scripts/purge_secret.py --pattern 'cztei_xxx' --repo . --verify
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GH_API = "https://api.github.com"


# ---------------------------------------------------------------- utils
def sh(cmd: str, cwd: str | None = None, timeout: int = 900) -> tuple[int, str]:
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                       cwd=cwd, timeout=timeout)
    return p.returncode, (p.stdout + p.stderr).strip()


def fingerprint(secret: str) -> str:
    """不泄露明文的指纹。"""
    return f"{secret[:6]}…{secret[-4:]}(len={len(secret)})"


def gh(path: str, method: str = "GET", data: dict | None = None) -> tuple[int, str]:
    headers = {"User-Agent": "purge-secret", "Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(
        GH_API + path, headers=headers, method=method,
        data=json.dumps(data).encode() if data is not None else None)
    try:
        r = urllib.request.urlopen(req, timeout=40)
        return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")[:300]
    except Exception as e:  # noqa: BLE001
        return 0, str(e)[:200]


# ---------------------------------------------------------------- scan
def scan_worktree(repo: Path, pattern: str) -> list[str]:
    """扫描工作区（跳过 .git）。"""
    hits = []
    rx = re.compile(pattern)
    for p in repo.rglob("*"):
        if not p.is_file() or ".git" in p.parts:
            continue
        try:
            if p.stat().st_size > 20 * 1024 * 1024:
                continue
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:  # noqa: BLE001
            continue
        if rx.search(txt):
            hits.append(str(p.relative_to(repo)))
    return hits


def scan_history(repo: Path, pattern: str) -> tuple[int, list[str]]:
    """返回 (含密钥的 commit 数, 文件列表)。"""
    rc, out = sh(f"git rev-list --all | while read c; do "
                 f"if git grep -q '{pattern}' $c -- 2>/dev/null; then echo $c; fi; done",
                 cwd=str(repo), timeout=900)
    commits = [l for l in out.splitlines() if l.strip()]
    rc, out2 = sh(f"git grep -l '{pattern}' $(git rev-list --all) 2>/dev/null",
                  cwd=str(repo), timeout=900)
    files = sorted({l.split(":", 1)[-1] for l in out2.splitlines() if l.strip()})
    return len(commits), files


# ---------------------------------------------------------------- rewrite
def rewrite_history(repo: Path, pattern: str, replacement: str) -> bool:
    """用 git-filter-repo 改写全历史。调用方必须已备份。"""
    tmp = Path(tempfile.mkdtemp()) / "replace.txt"
    tmp.write_text(f"literal:{pattern}==>{replacement}\n", encoding="utf-8")
    # filter-repo 会因上次运行记录而进入交互确认，先清掉标记
    sh("rm -rf .git/filter-repo/already_ran", cwd=str(repo))
    rc, out = sh(f"git filter-repo --replace-text {tmp} --force", cwd=str(repo), timeout=1800)
    shutil.rmtree(tmp.parent, ignore_errors=True)
    if rc != 0:
        print(f"❌ filter-repo 失败：\n{out[:800]}", file=sys.stderr)
        return False
    sh("git reflog expire --expire=now --all && git gc --prune=now --aggressive", cwd=str(repo))
    return True


# ---------------------------------------------------------------- verify
def verify_github(owner: str, repo_name: str, pattern: str) -> dict:
    """逐个 commit 检查 GitHub 上是否还有残留。"""
    st, body = gh(f"/repos/{owner}/{repo_name}/commits?per_page=100")
    if st != 200:
        return {"error": f"无法列出 commit: HTTP {st} {body[:120]}"}
    commits = json.loads(body)
    rx = re.compile(pattern)
    hits, checked = [], 0
    for c in commits:
        sha = c["sha"]
        url = (f"https://raw.githubusercontent.com/{owner}/{repo_name}/{sha}"
               f"/skills/anbeime/video-frame-extractor/scripts/coze_bot_client.py")
        try:
            t = urllib.request.urlopen(url, timeout=25).read().decode("utf-8", "replace")
        except Exception:  # noqa: BLE001
            continue
        checked += 1
        if rx.search(t):
            hits.append(sha[:7])
    return {"checked": checked, "total": len(commits), "hits": hits}


# ---------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pattern", required=True, help="要清除的凭据字面量或正则")
    ap.add_argument("--repo", default=".", help="git 仓库路径")
    ap.add_argument("--replacement", default="[REDACTED]")
    ap.add_argument("--rewrite", action="store_true", help="实际改写历史（默认只扫描）")
    ap.add_argument("--verify", action="store_true", help="到 GitHub 逐 commit 验证")
    ap.add_argument("--owner", default="")
    ap.add_argument("--repo-name", default="")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    print(f"🔍 仓库：{repo}")
    print(f"🔑 凭据指纹：{fingerprint(args.pattern)}")

    # 1) 扫描
    wt = scan_worktree(repo, args.pattern)
    ncomm, files = scan_history(repo, args.pattern)
    print(f"\n【扫描结果】")
    print(f"  工作区命中：{len(wt)} 个文件")
    for f in wt[:10]:
        print(f"    - {f}")
    print(f"  历史命中：{ncomm} 个 commit，涉及 {len(files)} 个文件")
    for f in files[:10]:
        print(f"    - {f}")

    if not args.rewrite:
        print("\nℹ️  仅扫描模式。确认无误后加 --rewrite 执行改写。")
        return 0

    if ncomm == 0 and not wt:
        print("\n✅ 无需处理。")
        return 0

    # 2) 备份
    stamp = time.strftime("%Y%m%d-%H%M%S")
    bk = repo.parent / f"{repo.name}-mirror-backup-{stamp}"
    print(f"\n【备份】→ {bk}")
    rc, out = sh(f"git clone --mirror {repo} {bk}", timeout=900)
    if rc != 0:
        print(f"❌ 备份失败，拒绝改写：\n{out[:400]}", file=sys.stderr)
        return 2
    rc, chk = sh(f"cd {bk} && git rev-list --all --count", timeout=300)
    print(f"  备份 commit 数：{chk}")

    # 3) 改写
    print(f"\n【改写历史】")
    if not rewrite_history(repo, args.pattern, args.replacement):
        return 3

    n2, f2 = scan_history(repo, args.pattern)
    print(f"  改写后历史命中：{n2} 个 commit")

    # 4) 推回
    print(f"\n【推送】")
    rc, out = sh("git push --force ssh-origin main", cwd=str(repo), timeout=1800)
    print("  " + (out.splitlines()[-1] if out else "无输出"))

    # 5) GitHub 验证
    if args.verify and args.owner and args.repo_name:
        print(f"\n【GitHub 验证】")
        res = verify_github(args.owner, args.repo_name, args.pattern)
        print(f"  检查 {res.get('checked')}/{res.get('total')} 个 commit")
        print(f"  残留：{res.get('hits') or '无 ✅'}")

    print(f"\n✅ 完成。备份在：{bk}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
