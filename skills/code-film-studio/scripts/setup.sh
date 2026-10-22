#!/bin/sh
# AI Skills 创作小店 · 代码电影工作室 (code-film-studio)
#   sh setup.sh                    准备风格库并打印 LIB=<路径>
#   sh setup.sh deps [voice] [music]
#                                  安装依赖: core = Node 包 + headless 浏览器 + Python 核心层;
#                                  voice = TTS 与语音校验 (+ 英文语音模型); music = pluck.py (numba)
#   sh setup.sh demo <slug>        拉取某个风格的样片源码与海报（仅供参考）
# 风格库随本 Skill 一起分发，位于 skill 目录下的 library/。
# CODE_FILM_STUDIO_HOME = 风格库工作目录（默认: skill 目录下的 library/）。
set -e

# 1. Which library: $CODE_FILM_STUDIO_HOME, else the bundled library/ next to this script,
#    else ~/lemo-opuscar
is_lib() { [ -f "$1/AGENTS.md" ] && [ -d "$1/core/render" ]; }
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
SKILL_DIR=$(cd "$SCRIPT_DIR/.." && pwd)
if [ -n "$CODE_FILM_STUDIO_HOME" ]; then LIB=$CODE_FILM_STUDIO_HOME
elif is_lib "$SKILL_DIR/library"; then LIB=$SKILL_DIR/library
elif top=$(git rev-parse --show-toplevel 2>/dev/null) && is_lib "$top"; then LIB=$top
else LIB=$HOME/lemo-opuscar
fi
case "$LIB" in /*) ;; *) LIB=$(pwd)/$LIB ;; esac
REPO=${CODE_FILM_STUDIO_REPO:-https://github.com/gyc567/great-skill-center.git}

# Our clone skips demo sources, the gallery and big images; what `setup.sh demo` added stays.
# git < 2.35 has no --no-cone: then the whole library is checked out.
apply_sparse() {
  set -- '/*' '!/styles/*/demo/' '!/styleboard/' '!/docs/frames/' '!/docs/cover.jpg' '!/docs/opuscar98.jpg' '!/styles/*/poster.jpg' \
    $(git -C "$LIB" sparse-checkout list 2>/dev/null | grep -E '^/styles/[^/*]+/(demo/|poster\.jpg)$' || true)
  git -C "$LIB" sparse-checkout set --no-cone "$@" 2>/dev/null || git -C "$LIB" sparse-checkout disable || true
}

if [ "$(git -C "$LIB" config --get lemo.managed 2>/dev/null)" = true ]; then
  # our own clone (nothing of the user's lives in it): match main, whatever happened upstream
  [ "$(git -C "$LIB" remote get-url origin 2>/dev/null)" = "$REPO" ] || git -C "$LIB" remote set-url origin "$REPO"
  if err=$(git -C "$LIB" fetch --quiet --depth 1 origin main 2>&1 && git -C "$LIB" reset --quiet --hard FETCH_HEAD 2>&1); then apply_sparse
  else echo "! could not update $LIB (offline?); using the local copy. git: $err" | head -3; fi
elif ! is_lib "$LIB"; then
  [ -e "$LIB" ] && [ -n "$(ls -A "$LIB" 2>/dev/null)" ] && { echo "✗ $LIB exists but is not the AI Skills 创作小店 风格库. Set LEMO_OPUSCAR_HOME to another folder."; exit 1; }
  command -v git >/dev/null || { echo "✗ git is needed to download the library"; exit 1; }
  echo "↓ downloading the style library into $LIB"
  git clone --quiet --depth 1 --filter=blob:none --sparse --branch main "$REPO" "$LIB" || { rm -rf "$LIB"; echo "✗ download failed (offline?)"; exit 1; }
  apply_sparse
  git -C "$LIB" config lemo.managed true
fi
LIB=$(cd "$LIB" && pwd -P)

# Installed packages are tracked by content: a marker holds a checksum of the files they came from (and the Python
# version), so a changed package.json or requirements file triggers a reinstall.
sig() { cat "$@" 2>/dev/null | cksum | cut -d' ' -f1; }
pysig() { echo "$(sig "$1")-$("$LIB/.venv/bin/python" -V 2>&1 | cut -d. -f1,2)"; }
req() { [ "$1" = core ] && echo "$LIB/requirements.txt" || echo "$LIB/requirements-$1.txt"; }
node_ok() { [ "$(cat "$LIB/node_modules/.lemo-ok" 2>/dev/null)" = "$(sig "$LIB/package.json" "$LIB/package-lock.json")" ]; }
py_ok() { [ "$(cat "$LIB/.venv/.lemo-$1" 2>/dev/null)" = "$(pysig "$(req "$1")")" ]; }
# a Python 3.11+ for the venv when uv is absent; kokoro-onnx (voice tier) needs < 3.14, so those come first
find_py() {
  for c in python3.12 python3.13 python3.11 python3; do
    "$c" -c 'import sys; sys.exit(sys.version_info < (3, 11))' 2>/dev/null && { echo "$c"; return 0; }
  done
  return 1
}

case "$1" in
  deps)
    shift; tiers=core
    for t in "$@"; do case $t in voice|music) tiers="$tiers $t" ;; *) echo "usage: sh setup.sh deps [voice] [music]"; exit 1 ;; esac; done
    cd "$LIB"
    command -v npm >/dev/null || { echo "✗ npm not found: install Node 20+ first"; exit 1; }
    if ! node_ok; then
      npm install --no-audit --no-fund --loglevel=error
      # npm may rewrite package-lock.json; in our own clone put it back, so the checksum stays the same
      [ "$(git config --get lemo.managed 2>/dev/null)" = true ] && git checkout -q -- package.json package-lock.json 2>/dev/null || true
      sig package.json package-lock.json > node_modules/.lemo-ok
    fi
    node node_modules/playwright-core/cli.js install chromium-headless-shell   # the renderer's browser (a no-op when present)
    # a venv whose Python is gone (after a Python upgrade) can't be repaired in place: make it again
    [ ! -e .venv ] || .venv/bin/python -c pass 2>/dev/null || { echo "! $LIB/.venv is broken; making it again"; rm -rf .venv; }
    if [ ! -x .venv/bin/python ]; then
      if command -v uv >/dev/null; then uv venv --quiet --python 3.12 .venv
      else py=$(find_py) || { echo "✗ Python 3.11+ is needed (or install uv, which fetches it)"; exit 1; }; "$py" -m venv .venv; fi
    fi
    for t in $tiers; do
      py_ok "$t" && continue
      if command -v uv >/dev/null; then uv pip install --quiet --python .venv/bin/python -r "$(req "$t")"
      else .venv/bin/python -m pip install --quiet --disable-pip-version-check -r "$(req "$t")"; fi
      pysig "$(req "$t")" > ".venv/.lemo-$t"
    done
    case " $tiers " in *" voice "*) [ -f core/tts/kokoro-v1.0.onnx ] && [ -f core/tts/voices-v1.0.bin ] || sh tools/fetch.sh voice ;; esac
    ;;
  demo)
    [ -n "$2" ] && [ -f "$LIB/styles/$2/STYLE.md" ] || { echo "usage: sh setup.sh demo <slug>  (slugs: $LIB/styles/README.md)"; exit 1; }
    if git -C "$LIB" sparse-checkout list >/dev/null 2>&1 && ! git -C "$LIB" sparse-checkout list | grep -qx "/styles/$2/demo/"; then
      git -C "$LIB" sparse-checkout add "/styles/$2/demo/" "/styles/$2/poster.jpg"
    fi
    echo "demo source: $LIB/styles/$2/demo"
    echo "demo poster: $LIB/styles/$2/poster.jpg"
    ;;
esac

# 2. Tools the pipeline needs (report only; installing them is up to the user)
miss=""
if command -v node >/dev/null; then
  [ "$(node -p 'process.versions.node.split(".")[0]')" -ge 20 ] || miss="$miss node20+(found $(node -v))"
else miss="$miss node20+"; fi
command -v ffmpeg >/dev/null || miss="$miss ffmpeg"
command -v uv >/dev/null || find_py >/dev/null || miss="$miss python3.11+(or uv)"
[ -n "$miss" ] && echo "! missing:$miss"
node_ok && py_ok core || echo "! packages not installed yet: run 'sh setup.sh deps' (a few minutes) before the first render"
echo "LIB=$LIB"
