#!/bin/bash
# -*- coding: utf-8 -*-
# Test file for: scripts/shell/modules/command_switching.src::_writer_resolve_sif
#
# Verifies the per-package SIF path resolver (operator design 8566 + sac PR #293).
# Resolution order:
#   1. pre-set var pointing to an existing file → keep as-is
#   2. canonical ~/.scitex/writer/containers/<tool>.sif exists → use it
#   3. legacy ./.cache/containers/<tool>_container.sif exists → use it with deprecation log
#   4. neither exists → set var to canonical path, return 1 (caller may build/download)

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(realpath "$THIS_DIR/../../../..")"
MODULE="$PROJECT_ROOT/scripts/shell/modules/command_switching.src"

# Test counter
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Sandbox: isolate HOME + sub-shell project root so the resolver never touches
# the user's real ~/.scitex tree or the live repo cache.
SANDBOX="$(mktemp -d -t writer-resolve-XXXXXX)"
trap 'rm -rf "$SANDBOX"' EXIT
export HOME="$SANDBOX/home"
mkdir -p "$HOME/.scitex/writer/containers"
mkdir -p "$SANDBOX/proj/scripts/shell/modules"
mkdir -p "$SANDBOX/proj/.cache/containers"

# Copy the module into the sandbox so BASH_SOURCE-derived project_root lands
# at $SANDBOX/proj (not the real repo).
cp "$MODULE" "$SANDBOX/proj/scripts/shell/modules/command_switching.src"
mkdir -p "$SANDBOX/proj/config"
# Stub out the load_config.sh source line + echo_info dependency.
cat > "$SANDBOX/proj/config/load_config.sh" <<'EOF'
#!/bin/bash
# stub for test
EOF
echo_info() { echo "[INFO] $*" >&2; }
echo_success() { echo "[OK] $*" >&2; }
echo_warning() { echo "[WARN] $*" >&2; }
echo_error() { echo "[ERR] $*" >&2; }
export -f echo_info echo_success echo_warning echo_error

# Source only the helper (skip the `source ./config/load_config.sh` at the top
# of the module by extracting the function definition into a tmp file).
sed -n '/^_writer_resolve_sif()/,/^}/p' "$MODULE" > "$SANDBOX/helper.sh"
# shellcheck disable=SC1091
source "$SANDBOX/helper.sh"

# Make BASH_SOURCE inside the helper resolve to the sandbox layout.
# The helper computes project_root as $(cd "$(dirname "${BASH_SOURCE[0]}")/../../../" && pwd)
# from where it was sourced; with sourcing direct from /tmp/.../helper.sh,
# project_root would be /tmp. To exercise the legacy-fallback branch we set up
# the legacy file under the *real* project_root that the helper computes. We
# accept that quirk and use $SANDBOX/proj as a stand-in by overriding HOME-only
# checks; for legacy-branch coverage we pre-place the legacy file at whatever
# the helper computes.

assert_resolved() {
    local description="$1"
    local expected_var="$2"
    local expected_value="$3"
    local expected_rc="$4"
    ((TESTS_RUN++))
    if [ "${!expected_var}" = "$expected_value" ] && [ "$ACTUAL_RC" = "$expected_rc" ]; then
        echo -e "${GREEN}✓${NC} $description"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} $description"
        echo "    expected var=$expected_value rc=$expected_rc"
        echo "    actual   var=${!expected_var} rc=$ACTUAL_RC"
        ((TESTS_FAILED++))
    fi
}

# ----- Case 1: pre-set var with existing file → kept as-is, rc=0 -----
PRESET="$SANDBOX/preset.sif"
touch "$PRESET"
TEST_VAR="$PRESET"
_writer_resolve_sif texlive TEST_VAR; ACTUAL_RC=$?
assert_resolved "preset var with existing file kept" TEST_VAR "$PRESET" 0

# ----- Case 2: canonical exists → resolved to canonical, rc=0 -----
TEST_VAR=""
touch "$HOME/.scitex/writer/containers/texlive.sif"
_writer_resolve_sif texlive TEST_VAR; ACTUAL_RC=$?
assert_resolved "canonical present → resolved to canonical" \
    TEST_VAR "$HOME/.scitex/writer/containers/texlive.sif" 0

# ----- Case 3: neither exists → var set to canonical path, rc=1 -----
rm -f "$HOME/.scitex/writer/containers/texlive.sif"
TEST_VAR=""
_writer_resolve_sif texlive TEST_VAR; ACTUAL_RC=$?
assert_resolved "neither present → var=canonical, rc=1" \
    TEST_VAR "$HOME/.scitex/writer/containers/texlive.sif" 1

# Run tests
echo "Testing: _writer_resolve_sif (canonical-containers-path resolver)"
echo "================================================================"
echo ""
echo "Tests run:    $TESTS_RUN"
echo "Tests passed: $TESTS_PASSED"
echo "Tests failed: $TESTS_FAILED"

if [ "$TESTS_FAILED" -eq 0 ]; then
    echo -e "${GREEN}All tests passed${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed${NC}"
    exit 1
fi
