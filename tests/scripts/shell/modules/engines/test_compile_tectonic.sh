#!/bin/bash
# -*- coding: utf-8 -*-
# Test file for: compile_tectonic.sh

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(realpath "$THIS_DIR/../..")"

# Test counter
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

assert_success() {
    local cmd="$1"
    local desc="${2:-$cmd}"
    ((TESTS_RUN++))
    if eval "$cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $desc"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} $desc"
        ((TESTS_FAILED++))
    fi
}

assert_file_exists() {
    local file="$1"
    ((TESTS_RUN++))
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} File exists: $file"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} File missing: $file"
        ((TESTS_FAILED++))
    fi
}

# Add your tests here
test_placeholder() {
    echo "TODO: Add tests for compile_tectonic.sh"
}

# Run tests
main() {
    echo "Testing: compile_tectonic.sh"
    echo "========================================"

    test_placeholder

    echo "========================================"
    echo "Results: $TESTS_PASSED/$TESTS_RUN passed"
    [ $TESTS_FAILED -gt 0 ] && exit 1
    exit 0
}

main "$@"

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/scitex-writer/scripts/shell/modules/engines/compile_tectonic.sh
# --------------------------------------------------------------------------------
# #!/bin/bash
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-11-11 23:12:00 (ywatanabe)"
# # File: ./scripts/shell/modules/engines/compile_tectonic.sh
# # Tectonic compilation engine
# 
# THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 
# # Source command switching for command detection
# source "${THIS_DIR}/../command_switching.src"
# 
# compile_with_tectonic() {
#     local tex_file="$1"
#     local pdf_file="${tex_file%.tex}.pdf"
# 
#     echo_info "    Using Tectonic engine"
# 
#     # Get tectonic command
#     local tectonic_cmd=$(get_cmd_tectonic)
#     if [ -z "$tectonic_cmd" ]; then
#         echo_error "    Tectonic not available"
#         return 1
#     fi
# 
#     # Build tectonic options
#     local opts=""
# 
#     # Output directory (use configured LOG_DIR for clean separation)
#     # Tectonic requires absolute paths for --outdir
#     local abs_log_dir="$(cd "$(dirname "$LOG_DIR")" && pwd)/$(basename "$LOG_DIR")"
#     opts="$opts --outdir=$abs_log_dir"
# 
#     # Incremental mode (use cache)
#     if [ "$SCITEX_WRITER_TECTONIC_INCREMENTAL" = "true" ]; then
#         opts="$opts --keep-intermediates"
#         # Set cache directory
#         if [ -n "$SCITEX_WRITER_TECTONIC_CACHE_DIR" ]; then
#             export TECTONIC_CACHE_DIR="$SCITEX_WRITER_TECTONIC_CACHE_DIR"
#             echo_info "    Using cache: $TECTONIC_CACHE_DIR"
#         fi
#     fi
# 
#     # Bundle directory (offline mode)
#     if [ -n "$SCITEX_WRITER_TECTONIC_BUNDLE_DIR" ] && [ -d "$SCITEX_WRITER_TECTONIC_BUNDLE_DIR" ]; then
#         opts="$opts --bundle=$SCITEX_WRITER_TECTONIC_BUNDLE_DIR"
#         echo_info "    Using offline bundle: $SCITEX_WRITER_TECTONIC_BUNDLE_DIR"
#     fi
# 
#     # Reruns (limit compilation passes to avoid excessive reruns)
#     # Default to 1 rerun (2 total passes) which is sufficient for most documents
#     # Can be overridden with SCITEX_WRITER_TECTONIC_RERUNS environment variable
#     local reruns="${SCITEX_WRITER_TECTONIC_RERUNS:-1}"
#     opts="$opts --reruns=$reruns"
# 
#     # Verbosity
#     if [ "$SCITEX_WRITER_VERBOSE_TECTONIC" != "true" ]; then
#         opts="$opts --print=error"
#     fi
# 
#     # Use relative path for tex file to maintain proper working directory
#     # Tectonic will run from current directory (project root) to resolve relative image paths
# 
#     # Run compilation
#     local start=$(date +%s)
#     echo_info "    Running: $tectonic_cmd $opts $tex_file"
# 
#     # Run tectonic with relative path (maintains project root as working directory)
#     local output=$($tectonic_cmd $opts "$tex_file" 2>&1)
#     local exit_code=$?
# 
#     local end=$(date +%s)
# 
#     # Check result
#     if [ $exit_code -eq 0 ]; then
#         echo_success "    Tectonic compilation: $(($end - $start))s"
#         return 0
#     else
#         echo_error "    Tectonic compilation failed (exit code: $exit_code)"
# 
#         # Show errors if verbose or on failure
#         if [ "$SCITEX_WRITER_VERBOSE_TECTONIC" = "true" ] || [ $exit_code -ne 0 ]; then
#             echo "$output" | grep -i "error\|warning" | head -10
#         fi
# 
#         # If in auto mode, signal to try fallback
#         if [ "$SCITEX_WRITER_ENGINE" = "auto" ]; then
#             return 2  # Special code: try next engine
#         else
#             return 1  # Fatal error
#         fi
#     fi
# }
# 
# # Export function
# export -f compile_with_tectonic
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/scitex-writer/scripts/shell/modules/engines/compile_tectonic.sh
# --------------------------------------------------------------------------------
