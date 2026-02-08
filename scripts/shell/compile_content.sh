#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: 2026-02-08
# File: scripts/shell/compile_content.sh

################################################################################
# Content/preview LaTeX compilation
# Compiles a .tex file to PDF using latexmk (no bibliography processing)
################################################################################

set -e
set -o pipefail

# Defaults
TEX_FILE=""
OUTPUT_DIR=""
JOB_NAME="content"
COLOR_MODE="light"
PREVIEW_DIR=""
TIMEOUT=60
KEEP_AUX=false
QUIET=false

# Colors
GRAY='\033[0;90m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { [ "$QUIET" = true ] || echo -e "${GRAY}INFO: $1${NC}"; }
log_success() { echo -e "${GREEN}SUCC: $1${NC}"; }
log_error() { echo -e "${RED}ERRO: $1${NC}" >&2; }

show_usage() {
    cat <<EOF
Usage: compile_content.sh --tex-file PATH --output-dir PATH [OPTIONS]

Compile a LaTeX .tex file to PDF (content/preview mode, no bibliography).

REQUIRED:
    --tex-file PATH       Input .tex file to compile
    --output-dir PATH     Directory for output PDF

OPTIONS:
    --job-name NAME       latexmk job name (default: content)
    --color-mode MODE     light|dark (default: light)
    --preview-dir PATH    Copy PDF to this directory after compilation
    --timeout SECS        Compilation timeout (default: 60)
    --keep-aux            Keep auxiliary files (.aux, .log, etc.)
    -q, --quiet           Suppress output
    -h, --help            Show this help

EXAMPLES:
    compile_content.sh --tex-file /tmp/preview.tex --output-dir /tmp/out
    compile_content.sh --tex-file /tmp/preview.tex --output-dir /tmp/out --color-mode dark
    compile_content.sh --tex-file /tmp/preview.tex --output-dir /tmp/out --preview-dir ./project/.preview
EOF
}

# Parse arguments
while [ $# -gt 0 ]; do
    case $1 in
    --tex-file | --tex_file)
        TEX_FILE="$2"
        shift 2
        ;;
    --tex-file=* | --tex_file=*)
        TEX_FILE="${1#*=}"
        shift
        ;;
    --output-dir | --output_dir)
        OUTPUT_DIR="$2"
        shift 2
        ;;
    --output-dir=* | --output_dir=*)
        OUTPUT_DIR="${1#*=}"
        shift
        ;;
    --job-name | --job_name)
        JOB_NAME="$2"
        shift 2
        ;;
    --job-name=* | --job_name=*)
        JOB_NAME="${1#*=}"
        shift
        ;;
    --color-mode | --color_mode)
        COLOR_MODE="$2"
        shift 2
        ;;
    --color-mode=* | --color_mode=*)
        COLOR_MODE="${1#*=}"
        shift
        ;;
    --preview-dir | --preview_dir)
        PREVIEW_DIR="$2"
        shift 2
        ;;
    --preview-dir=* | --preview_dir=*)
        PREVIEW_DIR="${1#*=}"
        shift
        ;;
    --timeout)
        TIMEOUT="$2"
        shift 2
        ;;
    --timeout=*)
        TIMEOUT="${1#*=}"
        shift
        ;;
    --keep-aux | --keep_aux)
        KEEP_AUX=true
        shift
        ;;
    -q | --quiet)
        QUIET=true
        shift
        ;;
    -h | --help)
        show_usage
        exit 0
        ;;
    *)
        log_error "Unknown argument: $1"
        show_usage
        exit 1
        ;;
    esac
done

# Validate required arguments
if [ -z "$TEX_FILE" ]; then
    log_error "Missing required argument: --tex-file"
    exit 1
fi

if [ -z "$OUTPUT_DIR" ]; then
    log_error "Missing required argument: --output-dir"
    exit 1
fi

if [ ! -f "$TEX_FILE" ]; then
    log_error "TeX file not found: $TEX_FILE"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

log_info "Compiling content: $JOB_NAME (color_mode=$COLOR_MODE)"

# Run latexmk (no bibliography processing for content/preview)
timeout "$TIMEOUT" latexmk \
    -pdf \
    -interaction=nonstopmode \
    -halt-on-error \
    -bibtex- \
    -jobname="$JOB_NAME" \
    -output-directory="$OUTPUT_DIR" \
    "$TEX_FILE"

COMPILE_EXIT=$?

if [ $COMPILE_EXIT -ne 0 ]; then
    log_error "latexmk failed with exit code $COMPILE_EXIT"
    exit $COMPILE_EXIT
fi

PDF_FILE="$OUTPUT_DIR/$JOB_NAME.pdf"

if [ ! -f "$PDF_FILE" ]; then
    log_error "PDF not generated: $PDF_FILE"
    exit 1
fi

log_success "PDF generated: $PDF_FILE"

# Copy to preview directory if specified
if [ -n "$PREVIEW_DIR" ]; then
    mkdir -p "$PREVIEW_DIR"
    cp "$PDF_FILE" "$PREVIEW_DIR/"
    log_info "Copied to preview: $PREVIEW_DIR/$JOB_NAME.pdf"
fi

# Cleanup auxiliary files
if [ "$KEEP_AUX" = false ]; then
    for ext in aux log fls fdb_latexmk synctex.gz out bbl blg toc lof lot; do
        rm -f "$OUTPUT_DIR/$JOB_NAME.$ext"
    done
    log_info "Cleaned auxiliary files"
fi

exit 0

# EOF
