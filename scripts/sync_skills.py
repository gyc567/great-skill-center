#!/usr/bin/env python3
"""统一同步 Skill 到所有 AI 工具目录 —— 单一真源，杜绝多端漂移。

背景（真实返工）：
  great-skill-center 里每个新 Skill 都要手动 cp 到 5 个目录
  （hermes / claude / openclaw / codex / agents）。做过一次就忘了下一次，
  于是出现"hermes 里有、claude 里没有"的幽灵安装。

用法：
    python3 scripts/sync_skills.py              # 同步全部
    python3 scripts/sync_skills.py --check      # 只检查差异（CI 友好，退出码 1 = 有漂移）
    python3 scripts/sync_skills.py cinecode    # 只同步指定 Skill
    python3 scripts/sync_skills.py --install    # 从上游源安装（需在 SKILL_SOURCES 中登记）
    python3 scripts/sync_skills.py --list       # 列出所有 Skill 及各端状态

零依赖，纯标准库。
"""

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILLS_SRC = REPO / "skills"

# 所有 AI 工具的 Skill 目录
TARGETS = [
    Path("/root/.hermes/skills"),
    Path("/root/.claude/skills"),
    Path("/root/.openclaw/skills"),
    Path("/root/.codex/skills"),
    Path("/root/.agents/skills"),
]

# 需要跳过的文件（体积大 / 可重建 / 机器相关）
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", ".pytest_cache"}
SKIP_SUFFIX = (".pyc", ".pyo", ".log")
# 这些 Skill 体积大，默认不参与同步（需 --include-large）
LARGE_THRESHOLD_MB = 8.0

# 上游安装源：name -> (git url, 子目录)
SKILL_SOURCES = {
    "cinecode": ("https://github.com/sarpstar/cinecode.git", None),
}


def skill_names():
    if not SKILLS_SRC.is_dir():
        return []
    return sorted(p.name for p in SKILLS_SRC.iterdir() if p.is_dir() and p.name not in SKIP_DIRS)


def dir_size_mb(path):
    total = 0
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
    return total / 1024 / 1024


def tool_label(path):
    """把 /root/.hermes/skills 显示成 hermes —— 目录名都一样，要区分开。"""
    p = Path(path)
    parts = p.parts
    for anchor in (".hermes", ".claude", ".openclaw", ".codex", ".agents"):
        if anchor in parts:
            return anchor.lstrip(".")
    return p.parent.name or str(p)


def fingerprint(path):
    """内容指纹 —— 忽略 mtime，只看文件内容，跨机器可比。"""
    h = hashlib.sha256()
    # os.walk 是惰性的，必须先收集全部结果再排序；只排 dirs 不足以固定顺序，
    # 因为 walk 的产出顺序取决于底层目录项顺序，跨机器可能不同。
    entries = []
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.endswith(SKIP_SUFFIX):
                continue
            entries.append(Path(root) / f)
    for fp in sorted(entries, key=lambda p: str(p.relative_to(path))):
        h.update(str(fp.relative_to(path)).encode())
        try:
            h.update(fp.read_bytes())
        except OSError:
            h.update(b"<unreadable>")
    return h.hexdigest()[:16]


def copy_skill(src, dst):
    """先删后拷 —— 避免上游删掉的文件残留在目标端。"""
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(*SKIP_DIRS, *SKIP_SUFFIX))


def sync(names, include_large=False, dry_run=False):
    changed, skipped, ok = [], [], []
    for name in names:
        src = SKILLS_SRC / name
        if not src.is_dir():
            continue
        size = dir_size_mb(src)
        if size > LARGE_THRESHOLD_MB and not include_large:
            skipped.append((name, f"{size:.1f}MB > {LARGE_THRESHOLD_MB}MB（用 --include-large）"))
            continue
        src_fp = fingerprint(src)
        for t in TARGETS:
            dst = t / name
            if dst.is_dir() and fingerprint(dst) == src_fp:
                ok.append((name, tool_label(t)))
                continue
            if dry_run:
                changed.append((name, tool_label(t), "DRY-RUN"))
                continue
            t.mkdir(parents=True, exist_ok=True)
            try:
                copy_skill(src, dst)
                changed.append((name, tool_label(t), f"{size:.1f}MB"))
            except Exception as e:  # noqa: BLE001
                print(f"  ✗ {name} → {t}: {e}", file=sys.stderr)
    return changed, skipped, ok


def check(names):
    """检查漂移，返回有差异的列表。"""
    drift = []
    for name in names:
        src = SKILLS_SRC / name
        if not src.is_dir():
            continue
        if dir_size_mb(src) > LARGE_THRESHOLD_MB:
            continue
        src_fp = fingerprint(src)
        for t in TARGETS:
            dst = t / name
            if not dst.is_dir():
                drift.append((name, tool_label(t), "缺失"))
            elif fingerprint(dst) != src_fp:
                drift.append((name, tool_label(t), "内容不一致"))
    return drift


def install(name, dest_root):
    """从上游 git 源安装到仓库 skills/ 目录。"""
    if name not in SKILL_SOURCES:
        print(f"未知上游源: {name}（在 SKILL_SOURCES 中登记）", file=sys.stderr)
        return 1
    url, subdir = SKILL_SOURCES[name]
    tmp = Path("/tmp") / f"skill-src-{name}"
    if tmp.exists():
        shutil.rmtree(tmp)
    r = subprocess.run(["git", "clone", "--depth", "1", url, str(tmp)],
                       capture_output=True, text=True, timeout=900)
    if r.returncode != 0:
        print(f"克隆失败: {r.stderr[:400]}", file=sys.stderr)
        return 1
    src = tmp / subdir if subdir else tmp
    dest = dest_root / name
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest, ignore=shutil.ignore_patterns(*SKIP_DIRS, *SKIP_SUFFIX))
    print(f"✅ 已安装 {name} → {dest}（{dir_size_mb(dest):.1f}MB）")
    return 0


def main():
    ap = argparse.ArgumentParser(description="统一同步 Skill 到所有 AI 工具目录")
    ap.add_argument("names", nargs="*", help="指定 Skill 名（默认全部）")
    ap.add_argument("--check", action="store_true", help="只检查漂移，不修改")
    ap.add_argument("--dry-run", action="store_true", help="显示将要做的变更")
    ap.add_argument("--include-large", action="store_true", help="包含大体积 Skill")
    ap.add_argument("--install", action="store_true", help="从上游源安装")
    ap.add_argument("--list", action="store_true", help="列出所有 Skill")
    args = ap.parse_args()

    names = args.names or skill_names()

    if args.list:
        print(f"{'Skill':45} {'大小':>8}  各端状态")
        print("-" * 90)
        for n in names:
            src = SKILLS_SRC / n
            if not src.is_dir():
                continue
            size = dir_size_mb(src)
            present = sum(1 for t in TARGETS if (t / n).is_dir())
            flag = "✅" if present == len(TARGETS) else ("⚠️ " if present else "❌")
            print(f"{flag} {n:42} {size:6.1f}MB  {present}/{len(TARGETS)}")
        return 0

    if args.install:
        rc = 0
        for n in (args.names or list(SKILL_SOURCES)):
            rc |= install(n, SKILLS_SRC)
        return rc

    if args.check:
        drift = check(names)
        if not drift:
            print(f"✅ 无漂移 —— {len(names)} 个 Skill 在全部 {len(TARGETS)} 个工具目录中一致")
            return 0
        print(f"❌ 发现 {len(drift)} 处漂移：")
        for name, target, why in drift:
            print(f"   - {name} → {target}  ({why})")
        print("\n修复: python3 scripts/sync_skills.py")
        return 1

    changed, skipped, ok = sync(names, include_large=args.include_large, dry_run=args.dry_run)
    prefix = "[DRY-RUN] " if args.dry_run else ""
    for name, target, size in changed:
        print(f"  {prefix}同步 {name} → {target}  ({size})")
    for name, why in skipped:
        print(f"  ⏭  跳过 {name} — {why}")
    print(f"\n完成：变更 {len(changed)}，已一致 {len(ok)}，跳过 {len(skipped)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
