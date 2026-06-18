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
DASHBOARD_URL="http://localhost:3000/d/raginator-3000/raginator-3000"

cd "$ROOT_DIR"

log() { echo -e "$@"; }

# Prefer `docker compose`, fall back to `podman compose` -- the
# docker-compose.yml is plain Compose v2 syntax, both providers consume it
# the same way.
compose() {
  if command -v docker &>/dev/null; then
    docker compose "$@"
  elif command -v podman &>/dev/null; then
    podman compose "$@"
  else
    log "❌ Neither docker nor podman found -- install one to run ./go observe."
    return 1
  fi
}

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
=== 5. 📈 OBSERVABILITY          ===
=== 6. 🌉 BRIDGE                 ===

Enter a number to see details:
HEREDOC

read -rn 1 option
echo ""; echo ""

case ${option} in
  0)
    echo "=== 🛠 PREREQUISITES ==="
    echo "⚙️  install_tools     -- Create .venv and upgrade pip"
    echo "📦  install           -- Editable-install raginator[dev] (every stage + pytest/ruff/mypy)"
    echo "📦  install <stage>   -- Editable-install just raginator[<stage>], e.g. ./go install chunk"
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
    echo "🛠  build_native [--cuda]   -- CMake build raginator_native (CPU by default)"
    ;;

  4)
    echo "=== 🧹 CLEANUP ==="
    echo "🧹  clean             -- Remove .venv, native/build, __pycache__, egg-info, caches"
    ;;

  5)
    echo "=== 📈 OBSERVABILITY ==="
    echo "📈  metrics_server    -- Run the toy pipeline on a loop, exposing :8000/metrics"
    echo "📊  observe           -- docker/podman compose up Prometheus+Grafana, open the dashboard"
    ;;

  6)
    echo "=== 🌉 BRIDGE ==="
    echo "🌉  api               -- Run the FastAPI bridge (uvicorn) on :8001 for the frontend"
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
    log "📦 Installing raginator[$stage]..."
    "$PIP" install -e ".[$stage]"
    return
  fi

  log "📦 Installing raginator[dev] (every stage + pytest/ruff/mypy)..."
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
  # "raginator" -- same as the import namespace -- which then shadows the
  # editable-install finder for raginator.<stage>.
  local stage="${1:-}"
  if [ "$stage" == "api" ]; then
    log "🧪 Testing api..."
    "$PYTEST" "api/tests"
    return
  fi
  if [ -n "$stage" ]; then
    log "🧪 Testing raginator.$stage..."
    "$PYTEST" "raginator/$stage/tests"
    return
  fi
  log "🧪 Testing everything..."
  "$PYTEST"
}

function lint() {
  log "🔎 Linting..."
  "$RUFF" check raginator api
}

function typecheck() {
  # Run per stage, not "mypy raginator": every stage's source dir is named
  # plain "src" (flattened, no nested raginator/<stage>/ folder), and mypy
  # infers module names from nested __init__.py directories on disk -- so
  # checking them all together hits "Duplicate module named src".
  log "🔎 Type-checking (per stage)..."
  for s in core ingest chunk embed store retrieve rerank generate evaluate observe pipeline; do
    (cd "raginator/$s" && "$MYPY" src)
  done
  # api/ is flat (no nested src/, no __init__.py -- a plain namespace-style
  # dir, not part of the raginator.* dotted package). --no-namespace-packages
  # stops mypy from also treating raginator/<stage>/ (no __init__.py, only a
  # nested src/) as a content-less namespace package that shadows the real,
  # properly-installed raginator.<stage> -- the same family of bug as the
  # python -m / pytest cwd-collision gotchas, just mypy's own variant of it.
  "$MYPY" --no-namespace-packages api/main.py api/preflight.py api/providers.py api/pipeline_runner.py api/schemas.py
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
  # venv's site-packages so raginator.store can actually import it.
  local site_packages
  site_packages="$("$PY" -c 'import sysconfig; print(sysconfig.get_path("purelib"))')"
  cp native/build/raginator_native*.so "$site_packages/"
  log "✅ Installed raginator_native into $site_packages"
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

# ---------------------------------------------------------------------------------------
#  5)                === 📈 OBSERVABILITY ===
# ---------------------------------------------------------------------------------------
function metrics_server() {
  log "📈 Serving live pipeline metrics on :8000/metrics (Ctrl-C to stop)..."
  "$PY" scripts/metrics_server.py
}

function observe() {
  compose up -d || return 1

  if ! curl -s -o /dev/null "http://localhost:8000/metrics"; then
    log "ℹ️  Nothing is serving :8000/metrics yet -- run './go metrics_server' in another shell for live data."
  fi

  log "⏳ Waiting for Grafana..."
  for _ in $(seq 1 30); do
    if curl -s -o /dev/null -w "%{http_code}" "http://localhost:3000/api/health" | grep -q 200; then
      log "🌐 Opening $DASHBOARD_URL"
      open "$DASHBOARD_URL"
      return 0
    fi
    sleep 1
  done

  log "❌ Grafana never became ready -- check 'compose logs grafana'."
  return 1
}

# ---------------------------------------------------------------------------------------
#  6)                === 🌉 BRIDGE ===
# ---------------------------------------------------------------------------------------
function api() {
  # :8001, not :8000 -- that port's already spoken for by metrics_server's
  # Prometheus exposition endpoint. Goes through scripts/serve_api.py rather
  # than `uvicorn api.main:app` directly -- uvicorn's app-string loader
  # inserts cwd onto sys.path, the same collision class as `python -m`/`-c`,
  # and the wrapper pre-imports raginator before that happens.
  log "🌉 Starting the FastAPI bridge on :8001 (Ctrl-C to stop)..."
  "$PY" scripts/serve_api.py
}

# -----------------------------
# Dispatch
# -----------------------------
if [ $# -eq 0 ]; then
  help
else
  "$@"
fi
