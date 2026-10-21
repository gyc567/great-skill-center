#!/usr/bin/env python3
"""pv-test.py — pinned-video-master 自测

覆盖:
  - pv-check.py: 档案完整性、字数上限、钩子红线、浮夸词、数字溯源、CTA 缺失
  - pv-generate.py: 口播文本提取（表格格式）、请求体构造、档案元数据读取
  - 资源完整性: SKILL.md 路由指向的 references/templates/scripts 都存在
"""

import os
import subprocess
import sys
import tempfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECK = os.path.join(BASE, "scripts", "pv-check.py")
GENERATE = os.path.join(BASE, "scripts", "pv-generate.py")

PASS, FAIL = [], []


def run(args):
    r = subprocess.run([sys.executable] + args, capture_output=True, text=True, timeout=60)
    return r.returncode, r.stdout + r.stderr


def check(name, cond, detail=""):
    if cond:
        PASS.append(name)
        print(f"  ✅ {name}")
    else:
        FAIL.append(name)
        print(f"  ❌ {name}  {detail}")


DOSSIER_GOOD = """---
name: pinned-dossier
status: provisional
intake_step: done
language: zh
---

## identity（身份）
- 姓名：张伟
- 领域：跨境电商
- 一句话身份：做了八年外贸的老外贸

## history（过去经历）
1. 2018-2022 自己开厂做传感器，供货 300 家工厂

## current（现在在做什么）
- 带 20 个工厂做海外获客

## offering（能提供的服务）
- 服务/产品：外贸独立站搭建 + 获客陪跑
- 合作方式：年度顾问

## proof（可信证据）
- 数字成果：300 家工厂客户，累计出货额 2 亿

## presence（平台与风格）
- 主平台：小红书
- 语言：双语
- 画幅：9:16
"""

SCRIPT_GOOD = """# 30秒置顶视频脚本

| 段 | 时间 | 台词 | 字数 |
|---|---|---|---|
| 钩子 | 0-3s | 做了八年外贸，我见过最贵的错误是找错客户 | /12 |
| 身份 | 3-8s | 我是张伟，做跨境电商供应链的 | /20 |
| 背书 | 8-20s | 2018年我开厂做传感器，供货300家工厂 | /40 |
| 现状 | 20-27s | 现在我带20个工厂做海外获客 | /22 |
| 价值+CTA | 27-30s | 想找对海外客户，评论区扣「清单」 | /20 |
"""

SCRIPT_BAD = """# 脚本

| 段 | 时间 | 台词 | 字数 |
|---|---|---|---|
| 钩子 | 0-3s | 大家好我是张伟 | /12 |
| 身份 | 3-8s | 我是最专业的供应链专家 | /20 |
| 背书 | 8-20s | 我服务过9999家企业客户，做出了震惊行业的成绩 | /40 |
| 现状 | 20-27s | 现在我做跨境获客 | /22 |
| 价值+CTA | 27-30s | 关注我 | /20 |
"""


def main():
    tmp = tempfile.mkdtemp(prefix="pv-test-")
    d_good = os.path.join(tmp, "dossier-good.md")
    d_bad = os.path.join(tmp, "dossier-bad.md")
    s_good = os.path.join(tmp, "script-good.txt")
    s_bad = os.path.join(tmp, "script-bad.txt")
    for p, c in [(d_good, DOSSIER_GOOD), (d_bad, "## identity（身份）\n- 待补\n"),
                 (s_good, SCRIPT_GOOD), (s_bad, SCRIPT_BAD)]:
        with open(p, "w", encoding="utf-8") as f:
            f.write(c)

    print("\n[1] pv-check.py — 档案")
    code, out = run([CHECK, "--dossier", d_good, "--stage", "dossier"])
    check("完整档案通过", code == 0 and "全部通过" in out, out[:200])

    code, out = run([CHECK, "--dossier", d_bad, "--stage", "dossier"])
    check("残缺档案被拦", code == 1 and "缺少模块" in out, out[:200])

    print("\n[2] pv-check.py — 脚本")
    code, out = run([CHECK, "--dossier", d_good, "--script", s_good, "--stage", "full"])
    check("好脚本通过", code == 0 and "全部通过" in out, out[:300])
    check("字数统计在上限内", "/ 90" in out and "阻塞" not in out.split("中文字数")[1][:20], out[:300])

    code, out = run([CHECK, "--dossier", d_good, "--script", s_bad, "--stage", "full"])
    check("坏脚本被阻塞", code == 1 and "阻塞" in out, out[:300])
    check("检测自我介绍钩子", "自我介绍式开场" in out, out[:300])
    check("检测浮夸词", "浮夸词" in out, out[:300])
    check("检测绝对化用语", "绝对化" in out, out[:300])
    check("检测无出处数字", "找不到出处" in out, out[:300])

    print("\n[3] pv-generate.py — dry-run")
    code, out = run([GENERATE, "--dossier", d_good, "--script", s_good,
                      "--avatar-id", "A1", "--voice-id", "V1", "--dry-run"])
    check("dry-run 成功", code == 0, out[:300])
    check("提取到口播文本", "口播文本长度" in out and "做了八年外贸" in out, out[:400])
    check("请求体含 avatar_id", '"avatar_id": "A1"' in out, out[:600])
    check("画幅为竖屏", '"width": 1080' in out and '"height": 1920' in out, out[:600])
    check("语言为 zh", '"language": "zh"' in out, out[:600])
    check("时间列未混入口播", "0-3s" not in out.split('"input_text"')[1][:200]
          if '"input_text"' in out else False, out[:600])

    print("\n[4] 资源完整性")
    with open(os.path.join(BASE, "SKILL.md"), encoding="utf-8") as f:
        skill_md = f.read()
    for ref in ["references/task-intake.md", "references/task-script.md",
                "references/task-storyboard.md", "references/task-generate.md",
                "references/task-platform.md", "references/task-quality.md",
                "references/launch-zh-CN.md", "references/launch-en.md",
                "templates/dossier-template.md", "templates/script-template.md",
                "templates/storyboard-template.md", "scripts/pv-check.py",
                "scripts/pv-generate.py"]:
        check(f"存在 {ref}", os.path.exists(os.path.join(BASE, ref)))
    check("SKILL.md 含品牌", "brand: AI Skills 创作小店" in skill_md)
    check("SKILL.md 含价格", "price: 3990" in skill_md)
    check("SKILL.md 含六模块", "六模块档案" in skill_md)
    check("SKILL.md 含结构表", "30 秒结构" in skill_md)

    print("\n" + "=" * 56)
    print(f"通过 {len(PASS)} / 失败 {len(FAIL)}")
    if FAIL:
        print("失败项：")
        for f_ in FAIL:
            print(f"  - {f_}")
    print("=" * 56)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
