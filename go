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
PYTEST="$VENV_DIR/bin/pytest"
RUFF="$VENV_DIR/bin/ruff"
MYPY="$VENV_DIR/bin/mypy"

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
    echo "📦  install           -- Editable-install ragfactory[dev] (every stage + pytest/ruff/mypy)"
    echo "📦  install <stage>   -- Editable-install just ragfactory[<stage>], e.g. ./go install chunk"
    ;;

  1)
    echo "=== 💻 LOCAL DEVELOPMENT    ==="
    echo "▶️  dev               -- install + run the toy pipeline end to end"
    echo "🏃  demo              -- Run the toy pipeline against sample text (no install)"
    ;;

  2)
    echo "=== 🔎 TESTING AND ANALYSIS ==="
    echo "🧪  test              -- Run pytest across the whole codebase"
    echo "🧪  test <stage>      -- Run pytest for one stage, e.g. ./go test embed"
    echo "🔎  lint              -- Run ruff check"
    echo "🔎  typecheck         -- Run mypy"
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
    log "📦 Installing ragfactory[$stage]..."
    "$PIP" install -e ".[$stage]"
    return
  fi

  log "📦 Installing ragfactory[dev] (every stage + pytest/ruff/mypy)..."
  "$PIP" install -e ".[dev]"
}

# ---------------------------------------------------------------------------------------
#  1)                === 💻 LOCAL DEVELOPMENT ===
# ---------------------------------------------------------------------------------------
function demo() {
  log "🏃 Running the toy pipeline end to end..."
  "$PY" scripts/demo.py
}

function dev() {
  demo
}

# ---------------------------------------------------------------------------------------
#  2)                === 🔎 TESTING AND ANALYSIS ===
# ---------------------------------------------------------------------------------------
function test() {
  # Use the pytest console script, not `python -m pytest`: `-m` always
  # prepends the cwd to sys.path, and our top-level dir is literally named
  # "ragfactory" -- same as the import namespace -- which then shadows the
  # editable-install finder for ragfactory.<stage>.
  local stage="${1:-}"
  if [ -n "$stage" ]; then
    log "🧪 Testing ragfactory.$stage..."
    "$PYTEST" "ragfactory/$stage/tests"
    return
  fi
  log "🧪 Testing everything..."
  "$PYTEST"
}

function lint() {
  log "🔎 Linting..."
  "$RUFF" check ragfactory
}

function typecheck() {
  # Run per stage, not "mypy ragfactory": every stage's source dir is named
  # plain "src" (flattened, no nested ragfactory/<stage>/ folder), and mypy
  # infers module names from nested __init__.py directories on disk -- so
  # checking them all together hits "Duplicate module named src".
  log "🔎 Type-checking (per stage)..."
  for s in core ingest chunk embed store retrieve rerank generate evaluate observe pipeline; do
    (cd "ragfactory/$s" && "$MYPY" src)
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

  # find_package(pybind11 CONFIG) doesn't know where pip put it -- point
  # CMake at pybind11's own packaged cmake config directory explicitly.
  local pybind11_dir
  pybind11_dir="$("$PY" -c 'import pybind11; print(pybind11.get_cmake_dir())')"
  "$VENV_DIR/bin/cmake" -S native -B native/build -DUSE_CUDA="$cuda_flag" -Dpybind11_DIR="$pybind11_dir"
  "$VENV_DIR/bin/cmake" --build native/build

  # native/build isn't on sys.path -- drop the built extension into the
  # venv's site-packages so ragfactory.store can actually import it.
  local site_packages
  site_packages="$("$PY" -c 'import sysconfig; print(sysconfig.get_path("purelib"))')"
  cp native/build/ragfactory_native*.so "$site_packages/"
  log "✅ Installed ragfactory_native into $site_packages"
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
