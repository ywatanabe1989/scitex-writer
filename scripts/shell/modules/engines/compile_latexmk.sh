#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-11 23:14:00 (ywatanabe)"
# File: ./scripts/shell/modules/engines/compile_latexmk.sh
# latexmk compilation engine with BIBINPUTS fix

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source command switching for command detection
source "${THIS_DIR}/../command_switching.src"

compile_with_latexmk() {
    local tex_file="$1"
    local pdf_file="${tex_file%.tex}.pdf"

    echo_info "    Using latexmk engine"

    # Get latexmk command
    local latexmk_cmd=$(get_cmd_latexmk)
    if [ -z "$latexmk_cmd" ]; then
        echo_error "    latexmk not available"
        return 1
    fi

    # Setup paths (use configured LOG_DIR for clean separation)
    local project_root=$(git rev-parse --show-toplevel 2>/dev/null || pwd)

    # FIX: Set BIBINPUTS to find bibliography files
    # latexmk runs bibtex from output directory, need to point to project root
    if [ "${SCITEX_WRITER_LATEXMK_SET_BIBINPUTS:-true}" = "true" ]; then
        export BIBINPUTS="${project_root}:"
        echo_info "    Set BIBINPUTS=${BIBINPUTS}"
    fi

    # Build latexmk options as array for proper quoting
    local -a opts=(
        -pdf
        -bibtex
        -interaction=nonstopmode
        -file-line-error
        "-output-directory=$LOG_DIR"
        "-pdflatex=pdflatex -shell-escape %O %S"
    )

    # Quiet mode
    if [ "${SCITEX_WRITER_VERBOSE_LATEXMK:-false}" != "true" ]; then
        opts+=(-quiet)
    fi

    # Draft mode (single pass)
    if [ "$SCITEX_WRITER_DRAFT_MODE" = "true" ]; then
        opts+=(-dvi- -ps-)
        echo_info "    Draft mode: single pass only"
    fi

    # Max passes
    if [ -n "$SCITEX_WRITER_LATEXMK_MAX_PASSES" ]; then
        opts+=("-latexoption=-interaction=nonstopmode")
    fi

    # Run compilation
    local start=$(date +%s)

    echo_info "    Running: latexmk [${#opts[@]} options] $(basename $tex_file)"

    # Run latexmk with properly quoted array expansion
    local output=$($latexmk_cmd "${opts[@]}" "$tex_file" 2>&1 | grep -v "gocryptfs not found")
    local exit_code=$?

    local end=$(date +%s)

    # Check for critical errors
    if echo "$output" | grep -q "Missing bbl file\|failed to resolve\|gave return code"; then
        echo_warning "    Compilation completed with warnings (check citations/references)"
    fi

    # Check result
    if [ $exit_code -eq 0 ]; then
        echo_success "    latexmk compilation: $(($end - $start))s"
        return 0
    else
        echo_error "    latexmk compilation failed (exit code: $exit_code)"

        # Show output if verbose or on failure
        if [ "$SCITEX_WRITER_VERBOSE_LATEXMK" = "true" ] || [ $exit_code -ne 0 ]; then
            echo "$output" | grep -i "error\|warning" | head -10
        fi

        # If in auto mode, signal to try fallback
        if [ "$SCITEX_WRITER_ENGINE" = "auto" ]; then
            return 2  # Special code: try next engine
        else
            return 1  # Fatal error
        fi
    fi
}

# Export function
export -f compile_with_latexmk

# EOF
