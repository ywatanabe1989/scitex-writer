#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-11 23:18:00 (ywatanabe)"
# File: ./scripts/shell/modules/compilation_compiled_tex_to_compiled_pdf.sh
# Main compilation orchestrator - delegates to engine-specific modules

ORIG_DIR="$(pwd)"
THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
ENGINES_DIR="${THIS_DIR}/engines"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
echo > "$LOG_PATH"

GIT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"

GRAY='\033[0;90m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo_info() { echo -e "${GRAY}INFO: $1${NC}"; }
log_info() {
    if [ "${SCITEX_LOG_LEVEL:-1}" -ge 2 ]; then
        echo -e "  \033[0;90m→ $1\033[0m"
    fi
}
echo_success() { echo -e "${GREEN}SUCC: $1${NC}"; }
echo_warning() { echo -e "${YELLOW}WARN: $1${NC}"; }
echo_error() { echo -e "${RED}ERRO: $1${NC}"; }
echo_header() { echo_info "=== $1 ==="; }
# ---------------------------------------

# Configurations
source ./config/load_config.sh $SCITEX_WRITER_DOC_TYPE

# Source engine implementations (use absolute paths to avoid directory confusion)
source "${ENGINES_DIR}/compile_tectonic.sh"
source "${ENGINES_DIR}/compile_latexmk.sh"
source "${ENGINES_DIR}/compile_3pass.sh"

# Logging
touch "$LOG_PATH" >/dev/null 2>&1
echo
log_info "Running $0 ..."

compiled_tex_to_pdf() {
    log_info "    Converting $SCITEX_WRITER_COMPILED_TEX to PDF..."

    local tex_file="$SCITEX_WRITER_COMPILED_TEX"
    local engine="${SCITEX_WRITER_SELECTED_ENGINE:-3pass}"

    log_info "    Selected engine: $engine"

    # Dispatch to engine-specific implementation
    case "$engine" in
        tectonic)
            compile_with_tectonic "$tex_file"
            ;;
        latexmk)
            compile_with_latexmk "$tex_file"
            ;;
        3pass)
            compile_with_3pass "$tex_file"
            ;;
        *)
            echo_error "    Unknown compilation engine: $engine"
            echo_info "    Falling back to 3-pass compilation"
            compile_with_3pass "$tex_file"
            ;;
    esac

    local ret=$?

    # If compilation failed in auto mode, try next engine
    if [ $ret -eq 2 ] && [ "$SCITEX_WRITER_ENGINE" = "auto" ]; then
        echo_warning "    Engine '$engine' failed, trying fallback..."
        # Note: Fallback logic handled by compile_manuscript.sh
        # This is just a placeholder for future enhancement
    fi

    return $ret
}

cleanup() {
    # Use fallback if SCITEX_WRITER_COMPILED_PDF is not set or empty
    local pdf_file="${SCITEX_WRITER_COMPILED_PDF}"
    if [ -z "$pdf_file" ]; then
        pdf_file="./01_manuscript/manuscript.pdf"
    fi

    # PDF is generated in LOG_DIR, move to final location
    local pdf_basename=$(basename "$pdf_file")
    local pdf_in_logs="${LOG_DIR}/${pdf_basename}"

    if [ -f "$pdf_in_logs" ]; then
        # Move PDF from logs/ to final location
        mv "$pdf_in_logs" "$pdf_file"
        log_info "    Moved PDF: $pdf_in_logs -> $pdf_file"
    fi

    if [ -f "$pdf_file" ]; then
        local size=$(du -h "$pdf_file" | cut -f1)
        echo_success "    $pdf_file ready (${size})"

        # Create/update stable symlink to latest archive version (prevents corruption during compilation)
        local latest_path="${SCITEX_WRITER_ROOT_DIR}/${SCITEX_WRITER_DOC_TYPE}-latest.pdf"

        # Find the latest archived version (highest version number)
        local archive_dir="${SCITEX_WRITER_VERSIONS_DIR}"
        local latest_archive=$(ls -1 "$archive_dir"/${SCITEX_WRITER_DOC_TYPE}_v[0-9]*.pdf 2>/dev/null | grep -v "_diff.pdf" | sort -V | tail -1)

        if [ -n "$latest_archive" ]; then
            # Create relative symlink to archive
            ln -sf "archive/$(basename "$latest_archive")" "$latest_path"
            echo_success "    Symlink updated: $latest_path -> archive/$(basename "$latest_archive")"
        else
            # Fallback to current PDF if no archive exists
            ln -sf "$(basename "$pdf_file")" "$latest_path"
            echo_success "    Symlink updated: $latest_path -> $(basename "$pdf_file") (no archive yet)"
        fi
        # Note: For rsync, use -L flag to follow symlinks: rsync -avL ...

        sleep 1
    else
        echo_error "    $pdf_file was not created"

        local log_file="${pdf_file%.pdf}.log"
        if [ -f "$log_file" ]; then
            echo_error "    LaTeX errors:"
            grep "^!" "$log_file" 2>/dev/null | head -5
        fi

        return 1
    fi
}

main() {
    compiled_tex_to_pdf
    cleanup
}

main

# EOF