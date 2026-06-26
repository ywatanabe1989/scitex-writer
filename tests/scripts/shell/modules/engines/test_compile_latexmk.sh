#!/bin/bash
# -*- coding: utf-8 -*-
# Test file for: compile_latexmk.sh

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

REPO_ROOT="$(realpath "$THIS_DIR/../../../../..")"
MODULE="$REPO_ROOT/scripts/shell/modules/engines/compile_latexmk.sh"

# Regression: a FAILING latexmk must make compile_with_latexmk return non-zero.
# The original code read `exit_code=$?` after `latexmk ... | grep`, capturing
# grep's exit (0, since a failed build still prints output) and falsely
# reporting success -- which let cleanup keep a stale PDF (soul.sty silent
# failure). This guards the fix: real latexmk exit code must propagate.
test_failing_latexmk_propagates_nonzero() {
    ((TESTS_RUN++))
    local desc="failing latexmk -> compile_with_latexmk returns non-zero"
    local workdir
    workdir="$(mktemp -d)"
    # Stub `latexmk` that PRINTS output (like a real failed build) then exits 1.
    cat >"$workdir/latexmk" <<'STUB'
#!/bin/bash
echo "! LaTeX Error: File 'soul.sty' not found."
echo "Emergency stop."
exit 12
STUB
    chmod +x "$workdir/latexmk"

    # Minimal logging shims so the module is callable in isolation.
    echo_info() { :; }; echo_error() { :; }; echo_success() { :; }
    echo_warning() { :; }; log_info() { :; }
    export -f echo_info echo_error echo_success echo_warning log_info 2>/dev/null

    # Sourcing the engine transitively loads config (command_switching.src);
    # give it the doc-type/root it expects, mirroring a real invocation.
    export SCITEX_WRITER_DOC_TYPE="${SCITEX_WRITER_DOC_TYPE:-manuscript}"
    export PROJECT_ROOT="${PROJECT_ROOT:-$REPO_ROOT}"
    # shellcheck disable=SC1090
    source "$MODULE"
    # Force the stub as the latexmk binary, non-auto so a fatal error returns 1.
    get_cmd_latexmk() { echo "$workdir/latexmk"; }
    SCITEX_WRITER_ENGINE="latexmk"
    LOG_DIR="$workdir"

    compile_with_latexmk "$workdir/doc.tex" >/dev/null 2>&1
    local rc=$?
    rm -rf "$workdir"

    if [ "$rc" -ne 0 ]; then
        echo -e "${GREEN}✓${NC} $desc (rc=$rc)"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} $desc (rc=$rc, expected non-zero)"
        ((TESTS_FAILED++))
    fi
}

# Run tests
main() {
    echo "Testing: compile_latexmk.sh"
    echo "========================================"

    test_failing_latexmk_propagates_nonzero

    echo "========================================"
    echo "Results: $TESTS_PASSED/$TESTS_RUN passed"
    [ $TESTS_FAILED -gt 0 ] && exit 1
    exit 0
}

main "$@"

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/scitex-writer/scripts/shell/modules/engines/compile_latexmk.sh
# --------------------------------------------------------------------------------
# #!/bin/bash
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-11-11 23:14:00 (ywatanabe)"
# # File: ./scripts/shell/modules/engines/compile_latexmk.sh
# # latexmk compilation engine with BIBINPUTS fix
# 
# THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 
# # Source command switching for command detection
# source "${THIS_DIR}/../command_switching.src"
# 
# compile_with_latexmk() {
#     local tex_file="$1"
#     local pdf_file="${tex_file%.tex}.pdf"
# 
#     echo_info "    Using latexmk engine"
# 
#     # Get latexmk command
#     local latexmk_cmd=$(get_cmd_latexmk)
#     if [ -z "$latexmk_cmd" ]; then
#         echo_error "    latexmk not available"
#         return 1
#     fi
# 
#     # Setup paths (use configured LOG_DIR for clean separation)
#     local project_root=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
# 
#     # FIX: Set BIBINPUTS to find bibliography files
#     # latexmk runs bibtex from output directory, need to point to project root
#     if [ "${SCITEX_WRITER_LATEXMK_SET_BIBINPUTS:-true}" = "true" ]; then
#         export BIBINPUTS="${project_root}:"
#         echo_info "    Set BIBINPUTS=${BIBINPUTS}"
#     fi
# 
#     # Build latexmk options as array for proper quoting
#     local -a opts=(
#         -pdf
#         -bibtex
#         -interaction=nonstopmode
#         -file-line-error
#         "-output-directory=$LOG_DIR"
#         "-pdflatex=pdflatex -shell-escape %O %S"
#     )
# 
#     # Quiet mode
#     if [ "${SCITEX_WRITER_VERBOSE_LATEXMK:-false}" != "true" ]; then
#         opts+=(-quiet)
#     fi
# 
#     # Draft mode (single pass)
#     if [ "$SCITEX_WRITER_DRAFT_MODE" = "true" ]; then
#         opts+=(-dvi- -ps-)
#         echo_info "    Draft mode: single pass only"
#     fi
# 
#     # Max passes
#     if [ -n "$SCITEX_WRITER_LATEXMK_MAX_PASSES" ]; then
#         opts+=("-latexoption=-interaction=nonstopmode")
#     fi
# 
#     # Run compilation
#     local start=$(date +%s)
# 
#     echo_info "    Running: latexmk [${#opts[@]} options] $(basename $tex_file)"
# 
#     # Run latexmk with properly quoted array expansion
#     local output=$($latexmk_cmd "${opts[@]}" "$tex_file" 2>&1 | grep -v "gocryptfs not found")
#     local exit_code=$?
# 
#     local end=$(date +%s)
# 
#     # Check for critical errors
#     if echo "$output" | grep -q "Missing bbl file\|failed to resolve\|gave return code"; then
#         echo_warning "    Compilation completed with warnings (check citations/references)"
#     fi
# 
#     # Check result
#     if [ $exit_code -eq 0 ]; then
#         echo_success "    latexmk compilation: $(($end - $start))s"
#         return 0
#     else
#         echo_error "    latexmk compilation failed (exit code: $exit_code)"
# 
#         # Show output if verbose or on failure
#         if [ "$SCITEX_WRITER_VERBOSE_LATEXMK" = "true" ] || [ $exit_code -ne 0 ]; then
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
# export -f compile_with_latexmk
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/scitex-writer/scripts/shell/modules/engines/compile_latexmk.sh
# --------------------------------------------------------------------------------
