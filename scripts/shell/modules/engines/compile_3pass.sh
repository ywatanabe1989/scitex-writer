#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-11 23:16:00 (ywatanabe)"
# File: ./scripts/shell/modules/engines/compile_3pass.sh
# 3-pass compilation engine (most compatible)

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source command switching for command detection
source "${THIS_DIR}/../command_switching.src"

# Portable file mtime (epoch seconds); prints 0 if absent/unsupported.
_file_mtime() {
    stat -c %Y "$1" 2>/dev/null || stat -f %m "$1" 2>/dev/null || echo 0
}

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
    pdf_cmd="$pdf_cmd -output-directory=$LOG_DIR -shell-escape -interaction=nonstopmode -file-line-error -synctex=1"

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

    # Optional timeout prefix (set by diff compilation to prevent infinite loops)
    local timeout_prefix=""
    if [ -n "${SCITEX_WRITER_COMPILE_TIMEOUT:-}" ]; then
        timeout_prefix="timeout ${SCITEX_WRITER_COMPILE_TIMEOUT}"
        echo_info "    Timeout: ${SCITEX_WRITER_COMPILE_TIMEOUT}s"
        pdf_cmd="$timeout_prefix $pdf_cmd"
    fi

    # Main compilation sequence
    local total_start=$(date +%s)
    local tex_basename=$(basename "${tex_file%.tex}")
    local aux_file="${LOG_DIR}/${tex_basename}.aux"
    local bib_base="${LOG_DIR}/${tex_basename}"
    local out_pdf="${LOG_DIR}/${tex_basename}.pdf"

    # Record the output PDF's mtime BEFORE compiling so we can prove a fresh
    # build afterwards. Without this, a pre-existing (stale) PDF makes a no-op
    # run look successful even when pdflatex never executed (e.g. the container
    # failed to mount). We FAIL LOUD below instead of trusting a stale PDF.
    local before_mtime=0
    [ -f "$out_pdf" ] && before_mtime=$(_file_mtime "$out_pdf")

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

    # HONESTY GATE: report success only if a NEWER PDF was actually produced.
    # A newer mtime proves pdflatex ran and wrote output this run; its absence
    # means the engine did not run (e.g. container mount failure) -- never pass
    # off a stale PDF as a successful compile.
    local after_mtime=0
    [ -f "$out_pdf" ] && after_mtime=$(_file_mtime "$out_pdf")

    if [ ! -f "$out_pdf" ] || [ "$after_mtime" -le "$before_mtime" ]; then
        echo_error "    3-pass compilation did NOT produce a fresh PDF."
        echo_error "      No newer $out_pdf than before the run -- pdflatex did not actually run"
        echo_error "      (e.g. the container failed to mount: squashfuse 'fuse: device not found')."
        echo_error "      Refusing to report a stale PDF as success."
        echo_error "      Fix: 'scitex-writer containers install texlive -y' or install native TeX Live."
        return 1
    fi

    echo_success "    3-pass compilation: $(($total_end - $total_start))s"

    return 0
}

# Export function
export -f compile_with_3pass

# EOF
