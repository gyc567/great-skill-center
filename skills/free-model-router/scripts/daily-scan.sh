#!/usr/bin/env bash
# ============================================================================
# 免费模型定时扫描 —— 每天 08:00 跑一次，比对上次报告并输出变化摘要
#
# 安装 crontab：
#   0 8 * * * /绝对路径/scripts/daily-scan.sh >> ~/freetoken-scan.log 2>&1
# ============================================================================
set -uo pipefail

RADAR="${RADAR_PATH:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/radar.py}"
PYTHON="${PYTHON_BIN:-python3}"
CACHE="${RADAR_CACHE:-$HOME/.pi/agent/freetoken-bots.json}"
PREV="${PREV_SNAPSHOT:-$HOME/.pi/agent/.freetoken-prev.json}"

[ -f "$RADAR" ] || { echo "找不到 radar.py: $RADAR" >&2; exit 1; }

# 保留上一次快照用于比对
if [ -f "$CACHE" ]; then
  cp -f "$CACHE" "$PREV" 2>/dev/null || true
fi

echo "=========================================="
echo "免费模型扫描 @ $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo "=========================================="

# 扫描；失败不覆盖旧缓存
if ! "$PYTHON" "$RADAR" scan > /tmp/freetoken-scan.json 2>/tmp/freetoken-scan.err; then
  echo "!! 扫描失败，保留旧名单："
  cat /tmp/freetoken-scan.err >&2
  exit 1
fi

"$PYTHON" - "$PREV" /tmp/freetoken-scan.json <<'PY'
import json, sys

def load(p):
    try:
        with open(p) as f:
            return json.load(f)
    except Exception:
        return {}

prev = load(sys.argv[1])
cur = load(sys.argv[2])

old_ids = set(prev.get('free_ids', []))
new_ids = set(cur.get('free_ids', []))
old_elig = {m['id'] for m in prev.get('eligible', [])}
new_elig = {m['id'] for m in cur.get('eligible', [])}

added = sorted(new_ids - old_ids)
removed = sorted(old_ids - new_ids)
elig_added = sorted(new_elig - old_elig)
elig_removed = sorted(old_elig - new_elig)

print(f"免费模型总数: {len(new_ids)}  (上次 {len(old_ids)})")
if not prev:
    print("(首次运行，以上次为基线建立)")
print()

if added:
    print("🆕 新上架的免费模型:")
    for m in added:
        print(f"   + {m}")
else:
    print("🆕 新上架: 无")

if removed:
    print("\n❌ 下架 / 不再免费的模型:")
    for m in removed:
        print(f"   - {m}")
else:
    print("\n❌ 下架: 无")

if elig_added:
    print("\n🎯 新进 approved 池 (已核实 ≥100B):")
    for m in elig_added:
        print(f"   ★ {m}")
if elig_removed:
    print("\n⚠️  掉出 approved 池:")
    for m in elig_removed:
        print(f"   ✗ {m}")

pending = cur.get('needs_parameter_verification', [])
if pending:
    print(f"\n📋 待人工核实参数量 ({len(pending)} 个):")
    for m in pending:
        hint = m.get('size_hint_b')
        hint_s = f"  [ID 线索: {hint}B]" if hint else ""
        print(f"   ? {m['id']}  ctx={m.get('context_length')}{hint_s}")

print()
print("💡 下一批待核实的核实方法见 references/parameter-verification.md")
PY

echo
echo "✅ 扫描完成 @ $(date '+%H:%M:%S')"
