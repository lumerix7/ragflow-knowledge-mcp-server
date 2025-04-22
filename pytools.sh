#!/usr/bin/env bash
#set -x

orig_dir=$(pwd)
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")"; pwd)
script_dirname=$(basename "$(cd "$(dirname "${BASH_SOURCE[0]}")"; pwd)")

package=$script_dirname

stop() {
  # Check if running on Windows (OSTYPE can be "msys", "cygwin", or "win32")
  if [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "cygwin"* || "$OSTYPE" == "win32"* ]]; then
    kill_bat="$script_dir"/kill.bat
    if [ -f "$kill_bat" ]; then
      # Call kill.bat using Windows command prompt
      "$kill_bat" -q
    else
      echo "kill.bat not found in the script directory => skipping kill.bat execution"
    fi
  else
    killall "$package"
  fi
}

# Function to purge temporary and build files
purge() {
  rm -rf $(find . -name build)
  rm -rf $(find . -name .venv)
  rm -rf $(find . -name uv.lock)
  rm -rf $(find . -name __pycache__)
  rm -rf $(find . -name .pytest_cache)
  rm -rf $(find . -name dist)
  rm -rf $(find . -name "*.egg-info")
  rm -rf $(find . -name _version.py)
  echo "Purge completed."
}

# Functions to run pytest
on_test_failure() {
  echo "Error: $1" 1>&2
  cd "$script_dir"
  purge
  cd "$orig_dir"
  exit 1
}

run_test() {
  cd "$script_dir" || exit 1

  echo purge
  purge

  echo "pytest --maxfail=1 -s"
  pytest --maxfail=1 -s || on_test_failure "Tests failed"

  echo purge
  purge

  echo "Tested successfully."
}

# Functions to reinstall all pyproject.toml packages
on_reinstall_failure() {
  local error="$1"

  echo "Error: $error" 1>&2

  pip uninstall "$package" --yes

  cd "$script_dir"
  purge
  cd "$orig_dir"
  exit 1
}

reinstall() {
  read -p "Reinstall $package? (y/N): " -r confirm
  if [[ "$confirm" != [yY] ]]; then
    echo "Operation cancelled."
    exit 1
  fi

  stop
  purge

  pip uninstall --yes "$package" || on_reinstall_failure "$package" "Uninstall $package failed"
  pip install --no-cache-dir --upgrade . || on_reinstall_failure "$package" "Install $package failed"

  purge

  pip show "$package"

  pytest --maxfail=1 -s || on_reinstall_failure "$package" "Tests $package failed"
  purge

  pip show -v "$package"
  echo "Reinstalled $package successfully."
}

on_upload_failure() {
  local error="$1"

  echo "Error: $error" 1>&2

  cd "$script_dir"
  purge
  cd "$orig_dir"
  exit 1
}

upload() {
  local repository="$1"

  if [ -z "$repository" ]; then
    echo "Usage: $(basename "$0") upload <repository>"
    exit 1
  fi

  cd "$script_dir" || exit 1
  purge

  echo "Building $package..."
  python -m build --sdist --wheel . || on_upload_failure "Build $package failed"

  echo "Uploading $package to $repository..."
  twine upload --repository "$repository" dist/* || on_upload_failure "Upload $package to $repository failed"
  purge

  echo "Uploaded $package to $repository successfully."
}

show_help() {
  echo "Usage: $(basename "$0") [COMMAND]"
  echo ""
  echo "Commands:"
  echo "  test                                Run pytest tests for current package"
  echo "  purge                               Remove temporary and build files"
  echo "  reinstall                           Reinstall current package"
  echo "  upload [repository]                 Package and upload current package to specified repository"
  echo "  help, -h, --help                    Show this help message"
  echo ""
}

if [ $# -eq 0 ]; then
  show_help
  exit 1
fi

case "$1" in
  test)
    run_test
    ;;
  purge)
    purge
    ;;
  reinstall)
    reinstall
    ;;
  upload)
    shift
    if [ $# -ne 1 ]; then
      echo "Usage: $(basename "$0") upload <repository>"
      show_help
      exit 1
    fi
    upload "$1"
    ;;

  help|-h|--help)
    show_help
    exit 1
    ;;
  *)
    echo "Unknown command: $1"
    show_help
    exit 1
    ;;
esac
