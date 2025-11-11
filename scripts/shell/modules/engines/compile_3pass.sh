#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-11 23:16:00 (ywatanabe)"
# File: ./scripts/shell/modules/engines/compile_3pass.sh
# 3-pass compilation engine (most compatible)

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source command switching for command detection
source "${THIS_DIR}/../command_switching.src"

compile_with_3pass() {
    local tex_file="$1"
    local pdf_file="${tex_file%.tex}.pdf"

    echo_info "    Using 3-pass engine"

    # Get commands
    local pdf_cmd=$(get_cmd_pdflatex)
    local bib_cmd=$(get_cmd_bibtex)

    if [ -z "$pdf_cmd" ] || [ -z "$bib_cmd" ]; then
        echo_error "    No LaTeX installation found (native, module, or container)"
        return 1
    fi

    # Add compilation options (use configured LOG_DIR for clean separation)
    pdf_cmd="$pdf_cmd -output-directory=$LOG_DIR -shell-escape -interaction=nonstopmode -file-line-error"

    # Helper function for timed execution
    run_pass() {
        local cmd="$1"
        local verbose="$2"
        local desc="$3"

        echo_info "    $desc"
        local start=$(date +%s)

        if [ "$verbose" = "true" ]; then
            eval "$cmd" 2>&1 | grep -v "gocryptfs not found"
            local ret=${PIPESTATUS[0]}
        else
            eval "$cmd" >/dev/null 2>&1
            local ret=$?
        fi

        local end=$(date +%s)
        echo_info "      ($(($end - $start))s)"

        return $ret
    }

    # Main compilation sequence
    local total_start=$(date +%s)
    local tex_basename=$(basename "${tex_file%.tex}")
    local aux_file="${LOG_DIR}/${tex_basename}.aux"
    local bib_base="${LOG_DIR}/${tex_basename}"

    # Check draft mode
    if [ "$SCITEX_WRITER_DRAFT_MODE" = "true" ]; then
        # Draft: single pass only
        run_pass "$pdf_cmd $tex_file" "$SCITEX_WRITER_VERBOSE_PDFLATEX" "Single pass (draft mode)"
    else
        # Full: 3-pass compilation
        run_pass "$pdf_cmd $tex_file" "${SCITEX_WRITER_VERBOSE_PDFLATEX:-false}" "Pass 1/3: Initial"

        # Process bibliography if needed
        if [ -f "$aux_file" ]; then
            if grep -q "\\citation\|\\bibdata\|\\bibstyle" "$aux_file" 2>/dev/null; then
                run_pass "$bib_cmd $bib_base" "${SCITEX_WRITER_VERBOSE_BIBTEX:-false}" "Processing bibliography"
            fi
        fi

        run_pass "$pdf_cmd $tex_file" "${SCITEX_WRITER_VERBOSE_PDFLATEX:-false}" "Pass 2/3: Bibliography"
        run_pass "$pdf_cmd $tex_file" "${SCITEX_WRITER_VERBOSE_PDFLATEX:-false}" "Pass 3/3: Final"
    fi

    local total_end=$(date +%s)
    echo_success "    3-pass compilation: $(($total_end - $total_start))s"

    return 0
}

# Export function
export -f compile_with_3pass

# EOF
