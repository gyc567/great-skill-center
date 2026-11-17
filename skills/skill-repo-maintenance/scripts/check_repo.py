#!/usr/bin/env python3
"""仓库一致性闸门 —— 在提交前把"人工目测才发现"的问题全部变成机器拦截。

背景（真实返工）：
  1. README 里写"124 个 Skill"，实际目录里已有 136 个 —— 每次新增都要手改三个地方
     （正文计数 / badge / 分类合计），漏一处就漂移，没人发现。
  2. 新 Skill 手动 cp 到 5 个工具目录，cp 一次忘一次 —— 实测 543 处漂移。
  3. 凭据（token/cookie/key）靠人眼扫 —— 一旦漏进仓库就是安全事故。
  4. SKILL.md 的 frontmatter name 必须等于目录名 —— 改名后忘了改 frontmatter 就失效。
  5. SKILL.md 必须存在且在 Skill 根目录 —— 打包成 zip 发出去才发现就晚了。

用法：
    python3 scripts/check_repo.py            # 全部检查，退出码 1 = 有问题
    python3 scripts/check_repo.py --fix      # 能自动修的自动修（README 计数）
    python3 scripts/check_repo.py --quiet    # CI 模式，只输出问题
"""

import argparse
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILLS = REPO / "skills"
README = REPO / "README.md"

# ---- 凭据扫描规则（宁可误报也不漏报）----
CRED_PATTERNS = [
    (r"ghp_[A-Za-z0-9]{30,}", "GitHub personal access token"),
    (r"github_pat_[A-Za-z0-9_]{50,}", "GitHub fine-grained PAT"),
    (r"sk-ant-api\d{2}-[A-Za-z0-9\-_]{20,}", "Anthropic API key"),
    (r"sk-[A-Za-z0-9]{32,}", "OpenAI/通用 API key"),
    (r"AKIA[0-9A-Z]{16}", "AWS access key id"),
    (r"AIza[0-9A-Za-z\-_]{35}", "Google API key"),
    (r"xox[baprs]-[A-Za-z0-9\-]{10,}", "Slack token"),
    (r"eyJ[A-Za-z0-9\-_]{20,}\.[A-Za-z0-9\-_]{20,}\.[A-Za-z0-9\-_]{20,}", "JWT"),
    (r"(?i)(api[_-]?key|secret|passwd|password|token|cookie)\s*[=:]\s*['\"][^'\"\s]{16,}['\"]",
     "疑似硬编码凭据"),
]
# 允许出现的占位/示例
ALLOW = re.compile(
    r"(REDACTED|xxxxxxxx|your[_-]?key|YOUR_KEY|placeholder|\[REDACTED\]|<[^>]{0,40}>|"
    r"sk-test|sk-invalid|sk-fake|sk-probe|example\.com|api\.x\.com|127\.0\.0\.1|localhost)",
    re.I,
)
# 允许出现凭据的文件（本来就是配置示例目录）
ALLOW_FILES = re.compile(r"(^|/)(tests?|examples?)/|\.example\.|sample|template|\.md$")

TEXT_EXT = {".md", ".py", ".js", ".mjs", ".cjs", ".json", ".sh", ".yaml", ".yml", ".toml", ".txt", ".html", ".csv"}


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.fixes = []

    def err(self, check, msg, path=None):
        self.errors.append((check, msg, path))

    def warn(self, check, msg, path=None):
        self.warnings.append((check, msg, path))

    def fix(self, msg):
        self.fixes.append(msg)


def skill_dirs():
    if not SKILLS.is_dir():
        return []
    return sorted(p for p in SKILLS.iterdir() if p.is_dir() and not p.name.startswith("."))


def check_frontmatter(rep):
    """每个 Skill 必须有 SKILL.md，且 frontmatter name == 目录名。"""
    for d in skill_dirs():
        sm = d / "SKILL.md"
        if not sm.is_file():
            rep.err("frontmatter", "缺少 SKILL.md", d.relative_to(REPO))
            continue
        text = sm.read_text(encoding="utf-8", errors="replace")
        if not text.startswith("---"):
            rep.err("frontmatter", "SKILL.md 缺少 YAML frontmatter", d.relative_to(REPO))
            continue
        m = re.search(r"^name:\s*(\S+)\s*$", text[:1200], re.M)
        if not m:
            rep.err("frontmatter", "frontmatter 缺少 name 字段", d.relative_to(REPO))
        elif m.group(1) != d.name:
            rep.err("frontmatter",
                    f"name ({m.group(1)}) != 目录名 ({d.name})", d.relative_to(REPO))
        if not re.search(r"^description:", text[:4000], re.M):
            rep.warn("frontmatter", "缺少 description 字段", d.relative_to(REPO))


def check_readme_counts(rep, fix=False):
    """README 里的 Skill 计数必须与实际目录数一致。"""
    if not README.is_file():
        rep.err("readme", "README.md 不存在")
        return
    text = README.read_text(encoding="utf-8")
    actual = len(skill_dirs())

    m = re.search(r"\*\*(\d+) 个可直接投产", text)
    if not m:
        rep.err("readme", "README 缺少「N 个可直接投产」计数声明")
    elif int(m.group(1)) != actual:
        old = m.group(1)
        if fix:
            text = text.replace(f"**{old} 个可直接投产", f"**{actual} 个可直接投产")
            text = re.sub(r"badge/Skills-\d+-", f"badge/Skills-{actual}-", text)
            README.write_text(text, encoding="utf-8")
            rep.fix(f"README 计数 {old} → {actual}")
        else:
            rep.err("readme", f"声明 {old} 个，实际 {actual} 个（--fix 可自动修）")

    for b in re.findall(r"badge/Skills-(\d+)-", text):
        if int(b) != actual and not fix:
            rep.err("readme", f"badge 写 {b}，实际 {actual}")
    if fix:
        # 修完重新读一遍确认
        text2 = README.read_text(encoding="utf-8")
        for b in re.findall(r"badge/Skills-(\d+)-", text2):
            if int(b) != actual:
                rep.err("readme", f"badge 修复失败：{b} != {actual}")


def check_category_counts(rep):
    """README 分类表格里的条目数必须等于实际 Skill 数。"""
    if not README.is_file():
        return
    text = README.read_text(encoding="utf-8")
    listed = set()
    for m in re.finditer(r"^\|\s*`([a-z0-9][a-z0-9\-_]*)`\s*\|", text, re.M):
        listed.add(m.group(1))
    actual = {d.name for d in skill_dirs()}
    missing = actual - listed
    extra = listed - actual
    if missing:
        rep.err("readme",
                f"{len(missing)} 个 Skill 未在 README 表格中列出：{sorted(missing)[:8]}"
                f"{' ...' if len(missing) > 8 else ''}")
    if extra:
        rep.warn("readme", f"{len(extra)} 个表格条目无对应目录：{sorted(extra)[:8]}")


def check_credentials(rep):
    """扫描仓库内的硬编码凭据。"""
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in {".git", "node_modules", "__pycache__", ".venv"}]
        for f in files:
            p = Path(root) / f
            if p.suffix.lower() not in TEXT_EXT:
                continue
            rel = p.relative_to(REPO)
            if ALLOW_FILES.search(str(rel)):
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for pat, label in CRED_PATTERNS:
                for hit in re.finditer(pat, text):
                    snippet = hit.group(0)
                    if ALLOW.search(snippet):
                        continue
                    line = text[:hit.start()].count("\n") + 1
                    rep.err("secrets", f"疑似{label}（第 {line} 行）", rel)


def check_sync(rep):
    """各工具目录是否与仓库一致 —— 复用 sync_skills 的指纹逻辑。"""
    sync_py = REPO / "scripts" / "sync_skills.py"
    if not sync_py.is_file():
        return
    import importlib.util
    spec = importlib.util.spec_from_file_location("sync_skills", sync_py)
    if spec is None or spec.loader is None:
        rep.warn("sync", "无法加载 sync_skills")
        return
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as e:  # noqa: BLE001
        rep.warn("sync", f"无法加载 sync_skills: {e}")
        return
    drift = mod.check([d.name for d in skill_dirs()])
    if drift:
        by_skill = {}
        for name, target, why in drift:
            by_skill.setdefault(name, []).append(f"{target}({why})")
        rep.err("sync", f"{len(drift)} 处漂移，涉及 {len(by_skill)} 个 Skill："
                        f"{list(by_skill)[:6]}"
                        f"{' ...' if len(by_skill) > 6 else ''}"
                        f" —— 修复: python3 scripts/sync_skills.py")


def check_license(rep):
    """每个 Skill 必须有 LICENSE（对外分发的前提）。"""
    for d in skill_dirs():
        if not (d / "LICENSE").is_file():
            rep.warn("license", "缺少 LICENSE 文件", d.relative_to(REPO))


def check_eric(rep):
    """对外分发的 Skill 必须有 ERIC 联系方式（项目规则）。"""
    for d in skill_dirs():
        readme = d / "README.md"
        if not readme.is_file():
            continue
        text = readme.read_text(encoding="utf-8", errors="replace")
        if "gyc567@gmail.com" not in text and "ERIC" not in text:
            rep.warn("contact", "README 缺少 ERIC 联系方式/署名", d.relative_to(REPO))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true", help="自动修复能修的（README 计数）")
    ap.add_argument("--quiet", action="store_true", help="只输出问题")
    args = ap.parse_args()

    rep = Report()
    check_frontmatter(rep)
    check_readme_counts(rep, fix=args.fix)
    check_category_counts(rep)
    check_credentials(rep)
    check_license(rep)
    check_eric(rep)
    check_sync(rep)

    if not args.quiet:
        print("仓库一致性闸门")
        print("=" * 68)
        for f in rep.fixes:
            print(f"  🔧 已修复: {f}")

    if rep.errors:
        print(f"\n❌ {len(rep.errors)} 个错误：")
        for check, msg, path in rep.errors:
            where = f" [{path}]" if path else ""
            print(f"   [{check}]{where} {msg}")
    if rep.warnings:
        print(f"\n⚠️  {len(rep.warnings)} 个警告：")
        for check, msg, path in rep.warnings[:30]:
            where = f" [{path}]" if path else ""
            print(f"   [{check}]{where} {msg}")
        if len(rep.warnings) > 30:
            print(f"   ... 另有 {len(rep.warnings) - 30} 条")

    if not rep.errors and not rep.warnings:
        print("\n✅ 全部检查通过")
    elif not rep.errors:
        print(f"\n✅ 无错误（{len(rep.warnings)} 条警告）")
    else:
        print("\n修复: python3 scripts/check_repo.py --fix && python3 scripts/sync_skills.py")

    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
