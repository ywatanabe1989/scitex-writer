#!/bin/bash
# -*- coding: utf-8 -*-
# ROLE: engine-vendored — DO NOT edit here. `scitex-writer update-project`
# overwrites this file on every re-vendor; fix it upstream in the
# scitex-writer package instead (local edits are lost, and update-project
# may set it read-only in the consumer workspace after vendoring).
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
        -synctex=1
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

    # Force a full, deterministic build (latex -> bibtex -> latex x2), unless in
    # draft mode. latexmk's "smart incremental" logic can run bibtex against a
    # STALE/EMPTY .aux under -output-directory when its .fdb_latexmk fingerprint
    # or the .aux/.bbl desync from the real state (e.g. a manual `rm *.aux`, or a
    # partially-cleared prior run). bibtex then reports "I found no \citation /
    # \bibdata / \bibstyle command --- while reading manuscript.aux" -> no .bbl
    # -> EVERY \cite undefined (?? / [?]) while a PDF is still emitted. -gg cleans
    # generated files and rebuilds ignoring prior state, so bibtex always reads a
    # freshly-written aux. The compile re-flattens manuscript.tex each run
    # (source always changes), so -gg adds little cost over the normal rebuild.
    # Escape hatch: SCITEX_WRITER_LATEXMK_FORCE_CLEAN=false for incremental.
    if [ "${SCITEX_WRITER_DRAFT_MODE:-false}" != "true" ] &&
        [ "${SCITEX_WRITER_LATEXMK_FORCE_CLEAN:-true}" = "true" ]; then
        opts+=(-gg)
        echo_info "    Forcing clean full build (-gg) for deterministic bibtex/refs"
    fi

    # Run compilation
    local start=$(date +%s)

    echo_info "    Running: latexmk [${#opts[@]} options] $(basename $tex_file)"

    # Optional timeout (set by diff compilation to prevent infinite loops)
    local timeout_prefix=""
    if [ -n "${SCITEX_WRITER_COMPILE_TIMEOUT:-}" ]; then
        timeout_prefix="timeout ${SCITEX_WRITER_COMPILE_TIMEOUT}"
        echo_info "    Timeout: ${SCITEX_WRITER_COMPILE_TIMEOUT}s"
    fi

    # Run latexmk with properly quoted array expansion.
    # Capture latexmk's REAL exit code, then filter the output for display in a
    # SEPARATE step. Piping latexmk straight into `grep` and reading `$?` would
    # capture grep's exit, not latexmk's: a failed build still prints output, so
    # grep exits 0 and the engine falsely reports success -- masking the failure
    # and letting cleanup keep a stale PDF (the soul.sty silent-failure bug).
    local output
    output=$($timeout_prefix $latexmk_cmd "${opts[@]}" "$tex_file" 2>&1)
    local exit_code=$?
    output=$(printf '%s\n' "$output" | grep -v "gocryptfs not found")

    # Check for timeout (exit code 124)
    if [ $exit_code -eq 124 ]; then
        echo_warning "    Compilation timed out after ${SCITEX_WRITER_COMPILE_TIMEOUT}s"
        return 1
    fi

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
            return 2 # Special code: try next engine
        else
            return 1 # Fatal error
        fi
    fi
}

# Export function
export -f compile_with_latexmk

# EOF
