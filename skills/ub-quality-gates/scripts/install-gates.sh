#!/usr/bin/env bash
# ============================================================================
# ub-quality-gates — Uncle Bob 质量门工具链一键安装
#
# 安装三个确定性质量门工具：
#   crapper  — CRAP 评分（复杂度 + 覆盖率）
#   dryer    — 重复代码检测（Jaccard 结构指纹）
#   mutator  — 变异测试（找出测试没抓住的 bug）
#
# 全部为 Uncle Bob (Robert C. Martin) 的 0BSD 许可，可自由商用。
# ============================================================================
set -euo pipefail

TOOLS_DIR="${UB_TOOLS_DIR:-$HOME/.ub-tools}"
BRANCH="${UB_TOOLS_BRANCH:-master}"

say() { printf '\033[1;36m▸\033[0m %s\n' "$*"; }
ok()  { printf '\033[1;32m✔\033[0m %s\n' "$*"; }
die() { printf '\033[1;31m✘\033[0m %s\n' "$*" >&2; exit 1; }

# ---- 前置检查 --------------------------------------------------------------
command -v git >/dev/null || die "需要 git"
command -v python3 >/dev/null || die "需要 python3"
PY_VER=$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])')
if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)'; then
  die "需要 Python >= 3.11（当前 $PY_VER）"
fi
ok "Python $PY_VER"

mkdir -p "$TOOLS_DIR"

# ---- 克隆 ------------------------------------------------------------------
clone() {
  local name="${1:?}"
  local url="${2:?}"
  local dest="$TOOLS_DIR/$name"
  if [ -d "$dest/.git" ]; then
    say "$name 已存在，尝试更新"
    git -C "$dest" pull --ff-only >/dev/null 2>&1 || say "$name 更新失败，使用现有版本"
  else
    say "克隆 $name"
    git clone --depth 20 "$url" "$dest" >/dev/null 2>&1 || die "克隆 $name 失败"
  fi
}

clone crapper   https://github.com/unclebob/crapper.git
clone dryer     https://github.com/unclebob/dryer.git
clone mutator   https://github.com/unclebob/mutator.git

# ---- 安装 ------------------------------------------------------------------
install_tool() {
  local name="${1:?}"
  local dest="$TOOLS_DIR/$name"
  say "安装 $name"
  ( cd "$dest" && python3 -m venv .venv && .venv/bin/pip install -q --upgrade pip >/dev/null 2>&1 )
  ( cd "$dest" && .venv/bin/pip install -q -e . ) || die "$name 安装失败"
  ok "$name 已安装"
}

install_tool crapper
install_tool dryer
install_tool mutator

# mutator 依赖 crapper 的命名空间与函数名，必须能 import 到
say "链接 mutator -> crapper"
( cd "$TOOLS_DIR/mutator" && .venv/bin/pip install -q -e "$TOOLS_DIR/crapper" ) \
  && ok "mutator 已链接 crapper" \
  || say "mutator 链接 crapper 失败（mutator 将无法读取函数名）"

# ---- 生成包装脚本 ----------------------------------------------------------
say "生成统一入口 $TOOLS_DIR/ub-gates"
cat > "$TOOLS_DIR/ub-gates" <<EOF
#!/usr/bin/env bash
# ub-gates — 统一调用三个质量门工具
#   ub-gates crap    [crapper 参数]   复杂度 + 覆盖率 CRAP 评分
#   ub-gates dry     [dryer 参数]    重复代码检测
#   ub-gates mutate  [mutator 参数]  变异测试
#   ub-gates doctor  [项目根]        三工具体检 + 质量报告
set -uo pipefail
TOOLS_DIR="$TOOLS_DIR"
case "\${1:-doctor}" in
  crap)    shift; exec "\$TOOLS_DIR/crapper/.venv/bin/python" -m crapper   "\$@" ;;
  dry)     shift; exec "\$TOOLS_DIR/dryer/.venv/bin/python"   -m dryer    "\$@" ;;
  mutate)  shift; exec "\$TOOLS_DIR/mutator/.venv/bin/python" -m mutator  "\$@" ;;
  doctor)
    ROOT="\${2:-$PWD}"
    echo "=== 1/3 复杂度与覆盖率 (CRAP) ==="
    ( cd "\$ROOT" && "\$TOOLS_DIR/crapper/.venv/bin/python" -m crapper --threshold 10 ) || true
    echo
    echo "=== 2/3 重复代码 (dryer) ==="
    ( cd "\$ROOT" && "\$TOOLS_DIR/dryer/.venv/bin/python" -m dryer ) || true
    echo
    echo "=== 3/3 变异测试 (mutator) ==="
    ( cd "\$ROOT" && "\$TOOLS_DIR/mutator/.venv/bin/python" -m mutator ) || true
    ;;
  *) echo "用法: ub-gates {crap|dry|mutate|doctor} [参数]" >&2; exit 2 ;;
esac
EOF
chmod +x "$TOOLS_DIR/ub-gates"
ok "统一入口已生成"

# ---- 安装 Skill ------------------------------------------------------------
SKILL_DIR="${UB_SKILL_DIR:-$HOME/.hermes/skills/ub-mode}"
if [ -d "$SKILL_DIR" ] || [ -f "$SKILL_DIR/SKILL.md" ]; then
  say "更新 Skill 到 $SKILL_DIR"
  mkdir -p "$SKILL_DIR"
  curl -fsSL https://raw.githubusercontent.com/unclebob/ub-mode/master/SKILL.md -o "$SKILL_DIR/SKILL.md" \
    || say "SKILL.md 下载失败，保留现有版本"
fi

echo
ok "安装完成"
echo
echo "  工具目录 : $TOOLS_DIR"
echo "  统一入口 : $TOOLS_DIR/ub-gates"
echo
echo "  用法："
echo "    cd 你的项目"
echo "    $TOOLS_DIR/ub-gates doctor ."
echo
echo "  单项调用："
echo "    $TOOLS_DIR/ub-gates crap --changed"
echo "    $TOOLS_DIR/ub-gates dry --threshold 0.9"
echo "    $TOOLS_DIR/ub-gates mutate --scan"
