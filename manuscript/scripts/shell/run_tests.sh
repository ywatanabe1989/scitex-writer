#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-06 12:58:23 (ywatanabe)"
# File: ./manuscript/scripts/shell/run_tests.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1


# Run tests for SciTex

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
ROOT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
PY_DIR="$ROOT_DIR/scripts/python"

# Change to the scripts/python directory
cd "$PY_DIR" || {
  echo "Error: Could not change to directory $PY_DIR"
  exit 1
}

# Check if Python environment is set up
if [ -d "$ROOT_DIR/.env" ]; then
  # Activate the Python environment
  if [ -f "$ROOT_DIR/.env/bin/activate" ]; then
    source "$ROOT_DIR/.env/bin/activate"
    echo "Activated Python environment"
  fi
fi

# Parse arguments
VERBOSITY=1
FAILFAST=0
PATTERN="test_*.py"

show_usage() {
  echo "Usage: $(basename "$0") [options]"
  echo "Run tests for SciTex"
  echo ""
  echo "Options:"
  echo "  -h, --help            Show this help message and exit"
  echo "  -v, --verbose         Increase verbosity (can be used multiple times)"
  echo "  -f, --failfast        Stop on first failure"
  echo "  -p, --pattern PATTERN Pattern to match test files (default: test_*.py)"
  echo "  -l, --list            List available tests"
  echo ""
  echo "Examples:"
  echo "  $(basename "$0") -v"
  echo "  $(basename "$0") -v -f -p test_file_utils.py"
  echo "  $(basename "$0") --list"
}

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      show_usage
      exit 0
      ;;
    -v|--verbose)
      VERBOSITY=$((VERBOSITY + 1))
      shift
      ;;
    -f|--failfast)
      FAILFAST=1
      shift
      ;;
    -p|--pattern)
      PATTERN="$2"
      shift 2
      ;;
    -l|--list)
      python run_tests.py --list
      exit $?
      ;;
    *)
      echo "Error: Unknown option: $1"
      show_usage
      exit 1
      ;;
  esac
done

# Run tests
ARGS=("--verbosity" "$VERBOSITY" "--pattern" "$PATTERN")
if [ "$FAILFAST" -eq 1 ]; then
  ARGS+=("--failfast")
fi

echo "Running tests with arguments: ${ARGS[*]}"
python run_tests.py "${ARGS[@]}"
EXIT_CODE=$?

# Deactivate Python environment if it was activated
if [ -n "$VIRTUAL_ENV" ]; then
  deactivate
  echo "Deactivated Python environment"
fi

exit $EXIT_CODE

# EOF