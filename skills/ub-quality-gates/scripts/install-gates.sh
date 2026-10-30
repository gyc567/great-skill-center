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
# mutator 用它自己 venv 的 python 跑测试（找不到项目 .venv 时回落 sys.executable），
# 所以 pytest / coverage 必须装进 mutator 的 venv，否则基线测试直接失败。
if [ -x "$TOOLS_DIR/mutator/.venv/bin/python" ]; then
  say "为 mutator 补齐 pytest / coverage"
  "$TOOLS_DIR/mutator/.venv/bin/pip" install -q --disable-pip-version-check pytest coverage >/dev/null 2>&1 \
    && ok "mutator 测试依赖已就绪" \
    || warn "mutator 依赖安装失败，变异测试的基线会失败"
fi

# ---- 共享 Python 环境（coverage + pytest）--------------------------------
say "准备共享 Python 环境"
PYENV="$TOOLS_DIR/pyenv"
if [ ! -x "$PYENV/bin/python" ]; then
  BASE_PY=""
  for c in /usr/bin/python3 /usr/local/bin/python3; do
    if command -v "$c" >/dev/null 2>&1; then BASE_PY="$c"; break; fi
  done
  [ -n "$BASE_PY" ] || { warn "找不到系统 python3，共享环境跳过"; }
  if [ -n "$BASE_PY" ]; then
    "$BASE_PY" -m venv "$PYENV" >/dev/null 2>&1 \
      && "$PYENV/bin/pip" install -q --disable-pip-version-check coverage pytest >/dev/null 2>&1 \
      && ok "共享环境就绪 ($("$PYENV/bin/python" -c "import coverage;print(coverage.__version__)" 2>/dev/null))" \
      || warn "共享环境创建失败，Python 覆盖率将按 0% 计"
  fi
else
  ok "共享环境已存在"
fi

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
ensure_python() {
  # crapper/mutator 用项目内 .venv/bin/python，否则回落到 PATH 的 python3。
  # 若回落到的 python3 没有 pip（典型：Hermes venv）或受 PEP 668 保护，
  # 覆盖率会静默变 0%。所以优先用我们自建的共享环境。
  if [ -x "\$TOOLS_DIR/pyenv/bin/python" ]; then
    echo "\$TOOLS_DIR/pyenv/bin/python"; return 0
  fi
  for c in /usr/bin/python3 /usr/local/bin/python3 python3; do
    if command -v "\$c" >/dev/null 2>&1; then
      if "\$c" -c "import coverage" >/dev/null 2>&1; then echo "\$c"; return 0; fi
    fi
  done
  echo python3
}

has_coverage() {
  "\${1:-python3}" -c "import coverage" >/dev/null 2>&1
}

# 共享 Python 环境前置到 PATH —— crapper/mutator 会用 PATH 里的 python3
# 跑测试与覆盖率。放到 case 之前，所有分支都生效。
if [ -x "\$TOOLS_DIR/pyenv/bin/python3" ]; then
  export PATH="\$TOOLS_DIR/pyenv/bin:\$PATH"
fi

case "\${1:-doctor}" in
  crap)    shift; exec "\$TOOLS_DIR/crapper/.venv/bin/python" -m crapper   "\$@" ;;
  dry)     shift; exec "\$TOOLS_DIR/dryer/.venv/bin/python"   -m dryer    "\$@" ;;
  mutate)  shift; exec "\$TOOLS_DIR/mutator/.venv/bin/python" -m mutator  "\$@" ;;
  doctor)
    ROOT="\${2:-$PWD}"
    echo "=== 0/3 Python 覆盖率环境 ==="
    PY="\$(ensure_python)"
    echo "  使用 Python : \$PY"
    if has_coverage "\$PY"; then
      echo "  coverage    : 可用"
    else
      echo "  coverage    : 缺失 —— 尝试安装"
      "\$PY" -m pip install --disable-pip-version-check -q coverage >/dev/null 2>&1 \
        && echo "  coverage    : 已安装" \
        || echo "  coverage    : 安装失败（Python 覆盖率将按 0% 计）"
    fi
    # 把共享环境放到 PATH 最前面。
    # 不要软链 <项目>/.venv/bin/python —— 软链会让 Python 找不到同目录的
    # pyvenv.cfg，sys.prefix 退回 base python，venv 的 site-packages 丢失，
    # coverage 反而不可用（实测踩过）。
    echo "  PATH 前置   : \$TOOLS_DIR/pyenv/bin"
    echo
    echo "=== 1/3 复杂度与覆盖率 (CRAP) ==="
    ( cd "\$ROOT" && PATH="\$(dirname "\$PY"):\$PATH" "\$TOOLS_DIR/crapper/.venv/bin/python" -m crapper --threshold 10 ) || true
    echo
    echo "=== 2/3 重复代码 (dryer) ==="
    ( cd "\$ROOT" && "\$TOOLS_DIR/dryer/.venv/bin/python" -m dryer ) || true
    echo
    echo "=== 3/3 变异测试 (mutator) ==="
    ( cd "\$ROOT" && PATH="\$(dirname "\$PY"):\$PATH" "\$TOOLS_DIR/mutator/.venv/bin/python" -m mutator ) || true
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
