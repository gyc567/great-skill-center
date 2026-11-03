#!/usr/bin/env bash
# ============================================================================
# charles-video-maker 一键安装
#
# 安装内容：
#   1. 系统依赖检查（ffmpeg / node / python）
#   2. 隔离 Python 环境（playwright + numpy + scipy + soundfile）
#   3. Playwright Chromium
#   4. Anatomy 的 Node 依赖（react / react-dom / typescript / esbuild）
#
# 用法：
#   bash scripts/setup.sh                 # 只做检查
#   bash scripts/setup.sh --install       # 完整安装
#   VENV_DIR=~/.venvs/cvm bash scripts/setup.sh --install
# ============================================================================
set -uo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${VENV_DIR:-$HOME/.venvs/charles-video-maker}"
NODE_DEPS="${NODE_DEPS:-$HOME/.cache/charles-node-deps}"
INSTALL="${1:-}"

say()  { printf '\033[1;36m▸\033[0m %s\n' "$*"; }
ok()   { printf '\033[1;32m✔\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m!\033[0m %s\n' "$*"; }
die()  { printf '\033[1;31m✖\033[0m %s\n' "$*" >&2; exit 1; }

# ---- 1. 系统依赖 -----------------------------------------------------------
say "检查系统依赖"
MISSING=0
for b in ffmpeg ffprobe node python3; do
  if command -v "$b" >/dev/null 2>&1; then
    ok "$b  $(command -v "$b")"
  else
    warn "$b 缺失"
    MISSING=1
  fi
done
if [ "$MISSING" = 1 ]; then
  warn "系统依赖不全。Debian/Ubuntu: apt install ffmpeg nodejs python3 python3-venv"
  warn "macOS: brew install ffmpeg node python@3.11"
fi

NODE_MAJOR="$(node -v 2>/dev/null | sed 's/^v\([0-9]*\).*/\1/')"
if [ -n "$NODE_MAJOR" ] && [ "$NODE_MAJOR" -lt 20 ]; then
  warn "Node $(node -v) —— Anatomy 需要 ≥ 20.10"
fi

if [ "$INSTALL" != "--install" ]; then
  echo
  say "只检查模式完成。加 --install 执行完整安装。"
  exit 0
fi

# ---- 2. Python 隔离环境 ----------------------------------------------------
say "准备 Python 隔离环境 $VENV_DIR"
if [ ! -x "$VENV_DIR/bin/python" ]; then
  BASE_PY=""
  for c in python3.12 python3.11 python3; do
    if command -v "$c" >/dev/null 2>&1; then BASE_PY="$c"; break; fi
  done
  [ -n "$BASE_PY" ] || die "找不到 python3"
  "$BASE_PY" -m venv "$VENV_DIR" || die "venv 创建失败"
  ok "venv 已创建"
fi

say "安装 Python 依赖（playwright / numpy / scipy / soundfile）"
"$VENV_DIR/bin/pip" install -q --disable-pip-version-check --upgrade pip >/dev/null 2>&1
if "$VENV_DIR/bin/pip" install -q --disable-pip-version-check \
     playwright numpy scipy soundfile >/dev/null 2>&1; then
  ok "Python 依赖就绪 ($("$VENV_DIR/bin/python" -c 'import playwright,numpy,scipy,soundfile;print("ok")' 2>/dev/null))"
else
  warn "Python 依赖安装失败。voice/mix.py 需要 scipy，douyin_radar.py 需要 playwright"
fi

# ---- 3. Playwright 浏览器 --------------------------------------------------
say "安装 Playwright Chromium"
if "$VENV_DIR/bin/playwright" install chromium >/dev/null 2>&1; then
  ok "Chromium 就绪"
else
  warn "Chromium 安装失败 —— 渲染会失败。可手动跑：$VENV_DIR/bin/playwright install chromium"
fi

# ---- 4. Anatomy 的 Node 依赖 ----------------------------------------------
say "准备 Anatomy Node 依赖 $NODE_DEPS"
if [ ! -d "$NODE_DEPS/node_modules" ]; then
  mkdir -p "$NODE_DEPS"
  if npm install --prefix "$NODE_DEPS" --no-audit --no-fund --ignore-scripts \
       react@19.3.0 react-dom@19.3.0 typescript@5.9.3 esbuild@0.28.2 >/dev/null 2>&1; then
    ok "Node 依赖就绪"
  else
    warn "Node 依赖安装失败 —— anatomy 的 React 示例会不可用"
  fi
else
  ok "Node 依赖已存在"
fi

# ---- 5. 自检 ---------------------------------------------------------------
echo
say "自检"
"$VENV_DIR/bin/python" "$SKILL_DIR/scripts/check_env.py" 2>&1 | sed 's/^/  /' || true

cat <<EOF

$(ok "安装完成")

  Skill 目录 : $SKILL_DIR
  Python 环境: $VENV_DIR
  Node 依赖  : $NODE_DEPS

  用法：
    export PATH="$VENV_DIR/bin:\$PATH"
    cd 你的项目
    python3 "$SKILL_DIR/scripts/render.py" index.html out.mp4 --size 1080x1920 --fps 30 --duration 12

  可选组件（按需下载，不装也能用）：
    sh "$SKILL_DIR/scripts/lemo/setup.sh" deps     # Lemo-Opuscar 风格库 + Kokoro 配音
    # Gemini CLI（文案生成）：AGY_BIN=/path/to/agy，默认 ~/.local/bin/agy
    # 微信语音识别（ASR）：faster_whisper 或 mlx_whisper（Mac）

EOF
