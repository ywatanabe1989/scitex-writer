#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-29 12:59:32 (ywatanabe)"
# File: ./compile.sh

ORIG_DIR="$(pwd)"
export ORIG_DIR
THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_PATH="$THIS_DIR/.$(basename "$0").log"
echo >"$LOG_PATH"

# Resolve project root - handles working directory independence (Issue #13)
GIT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [ -z "$GIT_ROOT" ]; then
    # Fallback: resolve from script location
    GIT_ROOT="$(cd "$THIS_DIR" && pwd)"
fi
export PROJECT_ROOT="$GIT_ROOT"

# Change to project root to ensure all relative paths work (Issue #13)
cd "$PROJECT_ROOT" || exit 1

# Auto-initialize project if preprocessing artifacts are missing (Issue #12)
if [ ! -f "01_manuscript/contents/wordcounts/figure_count.txt" ]; then
    if [ -x "scripts/installation/init_project.sh" ]; then
        echo "Initializing project (missing preprocessing artifacts)..."
        ./scripts/installation/init_project.sh >/dev/null 2>&1 || true
    fi
fi

GRAY='\033[0;90m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo_info() { echo -e "${GRAY}INFO: $1${NC}"; }
echo_success() { echo -e "${GREEN}SUCC: $1${NC}"; }
echo_warning() { echo -e "${YELLOW}WARN: $1${NC}"; }
echo_error() { echo -e "${RED}ERRO: $1${NC}"; }
echo_header() { echo_info "=== $1 ==="; }
# ---------------------------------------
# Time-stamp: "2025-09-27 15:00:00 (ywatanabe)"

################################################################################
# Unified compilation interface
# Delegates to specific compilation scripts based on document type
################################################################################

# Default values
DOC_TYPE=""
WATCH_MODE=false

# Function to display usage
show_usage() {
    cat <<EOF
Usage: ./compile.sh [TYPE] [OPTIONS]

Unified compilation interface for scientific documents.

DOCUMENT TYPES:
    manuscript, -m        Compile manuscript (default if no type specified)
    supplementary, -s     Compile supplementary materials
    revision, -r          Compile revision responses

GLOBAL OPTIONS:
    -h, --help           Show this help message
    -w, --watch          Enable watch mode for hot-recompiling
                         (Only works with manuscript type)

COMMON SPEED OPTIONS (available for all document types):
    -nf, --no_figs       Skip figure processing (~4s faster)
    -nt, --no_tables     Skip table processing (~4s faster)
    -nd, --no_diff       Skip diff generation (~17s faster)
                         (revision skips diff by default)
    -d,  --draft         Single-pass PDF compilation (~5s faster)
    -dm, --dark_mode     Dark mode: black background, white text
                         (figures keep original colors)
    -q,  --quiet         Minimal logs
    -v,  --verbose       Detailed logs

    Note: All options accept both hyphens and underscores
          (e.g., --no-figs or --no_figs, --dark-mode or --dark_mode)

EXAMPLES:
    Basic compilation:
    ./compile.sh                           # Compile manuscript (default)
    ./compile.sh manuscript                # Explicitly compile manuscript
    ./compile.sh supplementary             # Compile supplementary materials
    ./compile.sh revision                  # Compile revision responses

    Short forms:
    ./compile.sh -m                        # Compile manuscript
    ./compile.sh -s                        # Compile supplementary
    ./compile.sh -r                        # Compile revision

    Speed options:
    ./compile.sh -m --no-figs --no-diff    # Fast manuscript (~12s)
    ./compile.sh -s --no_figs --no_tables --draft  # Ultra-fast supplementary
    ./compile.sh -r --no-figs --draft      # Fast revision

    Ultra-fast mode (all speed flags):
    ./compile.sh -m --no-figs --no-tables --no-diff --draft  # ~8s

    Dark mode:
    ./compile.sh -m --dark-mode            # Black background, white text
    ./compile.sh -s --dark_mode            # Works with all doc types

    Watch mode:
    ./compile.sh -m -w                     # Watch and recompile manuscript
    ./compile.sh -m --watch --no-figs      # Watch mode with speed options

DELEGATION:
    This script delegates to:
    - ./scripts/shell/compile_manuscript.sh for manuscripts
    - ./scripts/shell/compile_supplementary.sh for supplementary materials
    - ./scripts/shell/compile_revision.sh for revision responses

    For type-specific options, use: ./compile.sh [TYPE] --help

EOF
}

# Parse arguments
REMAINING_ARGS=""

while [ $# -gt 0 ]; do
    case $1 in
    manuscript | -m)
        DOC_TYPE="manuscript"
        shift
        ;;
    supplementary | -s)
        DOC_TYPE="supplementary"
        shift
        ;;
    revision | -r)
        DOC_TYPE="revision"
        shift
        ;;
    -w | --watch)
        WATCH_MODE=true
        shift
        ;;
    -h | --help)
        # If document type already specified, pass --help to that script
        # Otherwise, show wrapper's help
        if [ -z "$DOC_TYPE" ]; then
            show_usage
            exit 0
        else
            REMAINING_ARGS="$REMAINING_ARGS $1"
            shift
        fi
        ;;
    *)
        # Collect remaining arguments
        if [ -z "$DOC_TYPE" ]; then
            echo "ERROR: Unknown document type '$1'"
            echo "Valid types: manuscript, supplementary, revision"
            echo "Use './compile --help' for usage information"
            exit 1
        else
            REMAINING_ARGS="$REMAINING_ARGS $1"
            shift
        fi
        ;;
    esac
done

# Default to manuscript if no type specified
if [ -z "$DOC_TYPE" ]; then
    DOC_TYPE="manuscript"
fi

# Check if watch mode is supported for this document type
if [ "$WATCH_MODE" = true ] && [ "$DOC_TYPE" != "manuscript" ]; then
    echo "ERROR: Watch mode is only supported for manuscript compilation"
    echo "Use: ./compile -m -w"
    exit 1
fi

# Display what we're doing (compact format)
echo ""
echo -e "\033[1;36m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m"
echo -e "\033[1;36m  SciTeX Writer Compilation\033[0m"
echo -e "\033[0;36m  Type: $DOC_TYPE\033[0m"
if [ "$WATCH_MODE" = true ]; then
    echo -e "\033[0;36m  Mode: WATCH\033[0m"
fi
if [ -n "$REMAINING_ARGS" ]; then
    echo -e "\033[0;90m  Options:$REMAINING_ARGS\033[0m"
fi
echo -e "\033[1;36m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m"
echo ""

# Handle watch mode
if [ "$WATCH_MODE" = true ]; then
    # Run watch script for manuscript
    ./scripts/shell/watch_compile.sh "$REMAINING_ARGS"
    exit $?
fi

# Delegate to the appropriate compilation script
# Note: Use ${VAR:+$VAR} to only pass args when non-empty (avoid passing "" as an argument)
case $DOC_TYPE in
manuscript)
    ./scripts/shell/compile_manuscript.sh ${REMAINING_ARGS:+$REMAINING_ARGS}
    ;;
supplementary)
    ./scripts/shell/compile_supplementary.sh ${REMAINING_ARGS:+$REMAINING_ARGS}
    ;;
revision)
    ./scripts/shell/compile_revision.sh ${REMAINING_ARGS:+$REMAINING_ARGS}
    ;;
*)
    echo "Error: Unknown document type: $DOC_TYPE"
    exit 1
    ;;
esac

# Exit with the same status as the delegated script
exit $?

# EOF
