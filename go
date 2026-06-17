#!/usr/bin/env bash
# set -e
# set -o pipefail

# -----------------------------
# Config
# -----------------------------
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$ROOT_DIR/.venv"
PY="$VENV_DIR/bin/python"
PIP="$VENV_DIR/bin/pip"
STAGES=(ingest chunk embed store retrieve rerank generate evaluate observe)

cd "$ROOT_DIR"

log() { echo -e "$@"; }

# -----------------------------
# HELP / HINT (Interactive)
# -----------------------------
help() {
cat <<HEREDOC
Usage: ./go <command> [options]

Commands:
=== 0. 🛠 PREREQUISITES          ===
=== 1. 💻 LOCAL DEVELOPMENT      ===
=== 2. 🧪 TESTING AND ANALYSIS   ===
=== 3. ⚡ NATIVE ACCELERATION    ===
=== 4. 🧹 CLEANUP                ===

Enter a number to see details:
HEREDOC

read -rn 1 option
echo ""; echo ""

case ${option} in
  0)
    echo "=== 🛠 PREREQUISITES ==="
    echo "⚙️  install_tools     -- Create .venv and upgrade pip"
    echo "📦  install           -- Editable-install every package (core -> stages -> pipeline)"
    echo "📦  install <stage>   -- Editable-install one package, e.g. ./go install chunk"
    ;;

  1)
    echo "=== 💻 LOCAL DEVELOPMENT    ==="
    echo "▶️  dev               -- install + run the toy pipeline end to end"
    echo "🏃  demo              -- Run the toy pipeline against sample text (no install)"
    ;;

  2)
    echo "=== 🔎 TESTING AND ANALYSIS ==="
    echo "🧪  test              -- Run pytest across every package"
    echo "🧪  test <stage>      -- Run pytest for one package, e.g. ./go test embed"
    echo "🔎  lint              -- Run ruff check across every package"
    echo "🔎  typecheck         -- Run mypy across every package"
    echo "✅  check             -- lint + typecheck + test"
    ;;

  3)
    echo "=== ⚡ NATIVE ACCELERATION ==="
    echo "🛠  build_native [--cuda]   -- CMake build ragfactory_native (CPU by default)"
    ;;

  4)
    echo "=== 🧹 CLEANUP ==="
    echo "🧹  clean             -- Remove .venv, native/build, __pycache__, egg-info, caches"
    ;;
  *)
    echo "Section $option does not exist"
    ;;
esac
}

# ---------------------------------------------------------------------------------------
# 0)                  === 🛠 PREREQUISITES ===
# ---------------------------------------------------------------------------------------
function install_tools() {
  log "🛠 Setting up the virtualenv..."
  if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
  fi
  "$PIP" install -q --upgrade pip
  log "✨ Python: $("$PY" --version)"
}

function install() {
  install_tools

  local stage="${1:-}"
  if [ -n "$stage" ]; then
    log "📦 Installing ragfactory-core (dependency of every stage)..."
    "$PIP" install -e packages/core
    if [ "$stage" != "core" ]; then
      log "📦 Installing ragfactory-$stage..."
      "$PIP" install -e "packages/$stage"
    fi
    return
  fi

  log "📦 Installing every package in dependency order..."
  "$PIP" install -e packages/core
  for s in "${STAGES[@]}"; do
    "$PIP" install -e "packages/$s"
  done
  "$PIP" install -e "packages/pipeline[dev]"
}

# ---------------------------------------------------------------------------------------
#  1)                === 💻 LOCAL DEVELOPMENT ===
# ---------------------------------------------------------------------------------------
function demo() {
  log "🏃 Running the toy pipeline end to end..."
  "$PY" scripts/demo.py
}

function dev() {
  install
  demo
}

# ---------------------------------------------------------------------------------------
#  2)                === 🔎 TESTING AND ANALYSIS ===
# ---------------------------------------------------------------------------------------
function test() {
  local stage="${1:-}"
  if [ -n "$stage" ]; then
    log "🧪 Testing ragfactory-$stage..."
    (cd "packages/$stage" && "$PY" -m pytest)
    return
  fi
  log "🧪 Testing every package..."
  "$PY" -m pytest
}

function lint() {
  log "🔎 Linting every package..."
  "$PY" -m ruff check packages
}

function typecheck() {
  log "🔎 Type-checking every package..."
  for s in core "${STAGES[@]}" pipeline; do
    (cd "packages/$s" && "$PY" -m mypy src)
  done
}

function check() {
  lint
  typecheck
  test
}

# ---------------------------------------------------------------------------------------
#  3)                === ⚡ NATIVE ACCELERATION ===
# ---------------------------------------------------------------------------------------
function build_native() {
  local cuda_flag="OFF"
  if [ "${1:-}" == "--cuda" ]; then
    cuda_flag="ON"
  fi
  log "⚡ Building native extension (USE_CUDA=$cuda_flag)..."
  "$PIP" install -q pybind11 cmake
  "$VENV_DIR/bin/cmake" -S native -B native/build -DUSE_CUDA="$cuda_flag"
  "$VENV_DIR/bin/cmake" --build native/build
}

# ---------------------------------------------------------------------------------------
#  4)                === 🧹 CLEANUP ===
# ---------------------------------------------------------------------------------------
function clean() {
  log "🧹 Cleaning build artifacts..."
  rm -rf "$VENV_DIR" native/build
  find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null
  find . -name "*.egg-info" -exec rm -rf {} + 2>/dev/null
  find . -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null
  find . -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null
  find . -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null
}

# -----------------------------
# Dispatch
# -----------------------------
if [ $# -eq 0 ]; then
  help
else
  "$@"
fi
