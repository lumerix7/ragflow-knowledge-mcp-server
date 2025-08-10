#!/usr/bin/env bash
# set -x

orig_dir=$(pwd)
script_dir="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
script_dirname="$(basename "$script_dir")"
package="$script_dirname"                   # Package name defaults to directory name
PYTHON_BIN="${PYTHON_BIN:-python3}"         # Can be overridden via environment variable
VENV_DIR="${VENV_DIR:-$script_dir/.venv}"   # Project-local venv directory

log() { printf '[%s] %s\n' "$(date +'%F %T')" "$*"; }
err() { printf '[%s] ERROR: %s\n' "$(date +'%F %T')" "$*" 1>&2; }
die() { err "$*"; exit 1; }

have_cmd() { command -v "$1" >/dev/null 2>&1; }

ensure_py() {
  if ! have_cmd "$PYTHON_BIN"; then
    die "Python not found: $PYTHON_BIN"
  fi
}

# Usage: run_or_die "desc" cmd arg...
run_or_die() {
  local desc="$1"; shift
  log "$desc"
  "$@"
  local rc=$?
  if [ $rc -ne 0 ]; then
    die "Failed: ${desc} (exit=$rc)"
  fi
}

stop() {
  # Windows (Git Bash / MSYS / Cygwin)
  if [[ "${OSTYPE:-}" == msys* || "${OSTYPE:-}" == cygwin* || "${OSTYPE:-}" == win32* ]]; then
    local killall_bat="$script_dir/killall.bat"
    if [[ -f "$killall_bat" ]]; then
      "$killall_bat" "$package.exe" || log "killall.bat returned non-zero (ignored)."
    else
      log "killall.bat not found; skipping Windows process kill."
    fi
  else
    if have_cmd killall; then
      killall "$package" 2>/dev/null || true
    else
      pkill -x "$package" 2>/dev/null || pkill -f "$package" 2>/dev/null || true
    fi
  fi
}

# Purge build/venv/temp
purge() {
  cd "$script_dir" || die "cd $script_dir failed"
  log "Purging temp/build files..."

  # Directories
  for d in \
    ".venv" "build" "dist" \
    "__pycache__" ".pytest_cache" ".mypy_cache" ".ruff_cache" ".tox" \
    "htmlcov" ".benchmarks" ".ipynb_checkpoints"
  do
    find . -name "$d" -type d -print0 2>/dev/null | xargs -0r rm -rf -- || err "rm $d failed (ignored)"
  done

  # Files
  find . -name "uv.lock"     -print0 2>/dev/null | xargs -0r rm -f -- || err "rm uv.lock failed (ignored)"
  find . -name "_version.py" -print0 2>/dev/null | xargs -0r rm -f -- || err "rm _version.py failed (ignored)"
  find . -name "*.egg-info"  -type d -print0 2>/dev/null | xargs -0r rm -rf -- || err "rm *.egg-info failed (ignored)"
  find . -name "*.py[co]"    -print0 2>/dev/null | xargs -0r rm -f -- || err "rm *.py[co] failed (ignored)"
  find . -name ".coverage"   -print0 2>/dev/null | xargs -0r rm -f -- || err "rm .coverage failed (ignored)"
  find . -name "coverage.xml" -print0 2>/dev/null | xargs -0r rm -f -- || err "rm coverage.xml failed (ignored)"

  log "Purge completed."
  cd "$orig_dir" || die "cd back failed"
}

ensure_venv() {
  ensure_py
  if [[ ! -x "$VENV_DIR/bin/python" ]]; then
    log "Creating venv at: $VENV_DIR"
    "$PYTHON_BIN" -m venv "$VENV_DIR"
    local rc=$?
    [ $rc -eq 0 ] || die "python -m venv failed (exit=$rc)"
  fi
}

ensure_pytest_in() {
  local pybin="$1"
  if "$pybin" -m pytest --version >/dev/null 2>&1; then
    return 0
  fi
  log "pytest not found in $pybin; installing into venv..."
  "$pybin" -m pip install -U pip >/dev/null 2>&1 || err "upgrade pip failed (ignored)"
  "$pybin" -m pip install -U pytest
  local rc=$?
  [ $rc -eq 0 ] || die "install pytest failed (exit=$rc)"
}

run_pytest_with() {
  local pybin="$1"
  "$pybin" -m pytest --maxfail=1 -s
  return $?
}

cmd_test() {
  cd "$script_dir" || die "cd $script_dir failed"
  ensure_venv
  local vpy="$VENV_DIR/bin/python"
  #ensure_pytest_in "$vpy"
  #uv sync --no-install-project
  if command -v uv >/dev/null 2>&1; then
    uv sync --no-install-project --extra test || die "uv sync failed"
  else
    die "uv not found; install uv or use the 'extras' fallback"
  fi
  run_pytest_with "$vpy"
  local rc=$?
  cd "$orig_dir" || true
  [ $rc -eq 0 ] || die "Tests failed"
  log "Tests passed."
}

cmd_reinstall_system() {
  ensure_py
  cd "$script_dir" || die "cd $script_dir failed"
  stop
  log "Reinstalling $package into SYSTEM environment..."
  "$PYTHON_BIN" -m pip uninstall -y "$package" >/dev/null 2>&1 || log "uninstall returned non-zero (ignored)."
  log "pip install --upgrade . $*"
  "$PYTHON_BIN" -m pip install --upgrade . "$@"
  local rc=$?
  cd "$orig_dir" || true
  [ $rc -eq 0 ] || die "pip install (system) failed"
  log "Reinstalled (system) successfully."
}

cmd_reinstall_venv() {
  cd "$script_dir" || die "cd $script_dir failed"
  stop
  ensure_venv
  local vpy="$VENV_DIR/bin/python"
  "$vpy" -m pip install -U pip
  [ $? -eq 0 ] || die "upgrade pip failed"
  "$vpy" -m pip uninstall -y "$package" >/dev/null 2>&1 || log "uninstall returned non-zero (ignored)."
  log "$vpy -m pip install --upgrade . $*"
  "$vpy" -m pip install --upgrade . "$@"
  local rc=$?
  cd "$orig_dir" || true
  [ $rc -eq 0 ] || die "pip install (venv) failed"
  log "Reinstalled (venv) successfully."
}

cmd_upload() {
  local repository="${1:-}"
  if [ -z "$repository" ]; then
    die "Usage: $(basename "$0") upload <repository>"
  fi
  ensure_py
  cd "$script_dir" || die "cd $script_dir failed"
  log "Preparing build tooling..."
  "$PYTHON_BIN" -m pip install -U build twine >/dev/null 2>&1
  [ $? -eq 0 ] || die "install build/twine failed"
  run_or_die "Building $package..." "$PYTHON_BIN" -m build --sdist --wheel .
  run_or_die "Uploading to repository: $repository" "$PYTHON_BIN" -m twine upload --repository "$repository" dist/*
  cd "$orig_dir" || die "cd back failed"
  log "Uploaded $package to $repository successfully."
}

show_help() {
  cat <<EOF
Usage: $(basename "$0") <command> [args...]

Commands:
  test                              Always run pytest in project .venv (auto-create). If pytest missing, auto-install.
  purge                             Remove temp/build files (.venv, build, dist, caches, *.egg-info, _version.py)
  reinstall-system [pip-args...]    Reinstall into SYSTEM Python. Pass extra args to 'pip install'. No purge.
                                    Examples:
                                      $(basename "$0") reinstall-system --break-system-packages
                                      $(basename "$0") reinstall-system --no-build-isolation ".[dev]"
  reinstall-venv [pip-args...]      Reinstall into project .venv (auto-create). Pass extra args to 'pip install'. No purge.
                                    Examples:
                                      $(basename "$0") reinstall-venv
                                      $(basename "$0") reinstall-venv --no-build-isolation ".[dev]"
  upload <repository>               Build (sdist+wheel) and upload via twine to the named repository (e.g. pypi, testpypi).

Env vars:
  PYTHON_BIN   Python command to use (default: python3)
  VENV_DIR     Virtualenv path (default: \$script_dir/.venv)
EOF
}

cmd="${1:-}"
if [ -z "$cmd" ]; then
  show_help
  exit 1
fi
shift || true

case "$cmd" in
  test)               cmd_test "$@" ;;
  purge)              purge ;;
  reinstall-system)   cmd_reinstall_system "$@" ;;
  reinstall-venv)     cmd_reinstall_venv "$@" ;;
  upload)             cmd_upload "$@" ;;
  help|-h|--help)     show_help ;;
  *)                  err "Unknown command: $cmd"; show_help; exit 1 ;;
esac
