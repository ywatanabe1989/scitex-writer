#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-11 23:10:00 (ywatanabe)"
# File: ./scripts/shell/modules/select_compilation_engine.sh
# Select and verify compilation engine

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source command switching module for engine detection
source "${THIS_DIR}/command_switching.src"

# Auto-detect best available engine
auto_detect_engine() {
    # Default priority: latexmk (fastest for development) → tectonic (fallback) → 3pass (guaranteed)
    local auto_order="${SCITEX_WRITER_AUTO_ORDER:-latexmk tectonic 3pass}"

    for engine in $auto_order; do
        if verify_engine "$engine" >/dev/null 2>&1; then
            echo "$engine"
            return 0
        fi
    done

    # Fallback to 3pass (always works if pdflatex exists)
    echo "3pass"
}

# Verify engine is available
verify_engine() {
    local engine="$1"

    case "$engine" in
        tectonic)
            get_cmd_tectonic >/dev/null 2>&1
            return $?
            ;;
        latexmk)
            # Need both latexmk and pdflatex
            get_cmd_latexmk >/dev/null 2>&1 && \
            get_cmd_pdflatex >/dev/null 2>&1
            return $?
            ;;
        3pass)
            # Need pdflatex and bibtex
            get_cmd_pdflatex >/dev/null 2>&1 && \
            get_cmd_bibtex >/dev/null 2>&1
            return $?
            ;;
        *)
            echo_error "Unknown engine: $engine"
            return 1
            ;;
    esac
}

# Get human-readable engine info
get_engine_info() {
    local engine="$1"

    case "$engine" in
        tectonic)
            echo "🔄 Tectonic (Reproducible, 4-5s per compile)"
            ;;
        latexmk)
            echo "⚡ latexmk (Smart incremental, 3s)"
            ;;
        3pass)
            echo "🔒 3-pass (Guaranteed correctness, 6-7s)"
            ;;
    esac
}

# Get engine version
get_engine_version() {
    local engine="$1"

    case "$engine" in
        tectonic)
            local cmd=$(get_cmd_tectonic)
            if [ -n "$cmd" ]; then
                $cmd --version 2>&1 | head -1 | grep -oP '\d+\.\d+\.\d+'
            fi
            ;;
        latexmk)
            local cmd=$(get_cmd_latexmk)
            if [ -n "$cmd" ]; then
                $cmd -version 2>&1 | head -1 | grep -oP '\d+\.\d+'
            fi
            ;;
        3pass)
            echo "native"
            ;;
    esac
}

# List all available engines
list_available_engines() {
    echo "Available compilation engines:"
    echo ""

    for engine in tectonic latexmk 3pass; do
        if verify_engine "$engine" >/dev/null 2>&1; then
            local version=$(get_engine_version "$engine")
            local info=$(get_engine_info "$engine")
            printf "  ✓ %-10s (%-10s) %s\n" "$engine" "$version" "$info"
        else
            printf "  ✗ %-10s (not available)\n" "$engine"
        fi
    done
}

# Export functions
export -f auto_detect_engine
export -f verify_engine
export -f get_engine_info
export -f get_engine_version
export -f list_available_engines

# EOF
