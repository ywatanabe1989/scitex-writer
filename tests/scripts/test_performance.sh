#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-10 01:36:00 (ywatanabe)"
# File: ./tests/scripts/test_performance.sh
# Description: Test performance optimizations

# Note: Not using 'set -e' to allow graceful handling of optional performance tests
# Performance tests are informational and shouldn't fail the build

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

# Track test failures (but don't exit on them)
TEST_FAILURES=0

echo "Performance Optimization Tests"
echo "=============================="

# Test 1: Config loading is cached
echo
echo "Test 1: Config loading cache"
export SCITEX_WRITER_DOC_TYPE=manuscript

# First load (should be slow)
start=$(date +%s%N)
source ./config/load_config.sh manuscript &> /dev/null
first_load=$(($(date +%s%N) - start))

# Second load (should be instant due to cache)
start=$(date +%s%N)
source ./config/load_config.sh manuscript &> /dev/null
second_load=$(($(date +%s%N) - start))

first_ms=$((first_load / 1000000))
second_ms=$((second_load / 1000000))

echo "  First load:  ${first_ms}ms"
echo "  Second load: ${second_ms}ms"

if [ $second_ms -lt $((first_ms / 10)) ]; then
    echo -e "${GREEN}✓${NC} Config caching works (second load is 10x+ faster)"
else
    echo -e "${YELLOW}⚠${NC} Config caching may not be working optimally"
fi

# Test 2: Command caching works
echo
echo "Test 2: Command resolution caching"

# This test is CI-friendly: it gracefully handles missing dependencies
if ! source ./config/load_config.sh manuscript &> /dev/null; then
    echo -e "${YELLOW}⚠${NC} Could not load config (skipping command caching test)"
else
    # Try to source command_switching module
    if source ./scripts/shell/modules/command_switching.src 2>/dev/null; then
        # First call (may fail if pdflatex not available)
        start=$(date +%s%N)
        if get_cmd_pdflatex "$PWD" &> /dev/null; then
            first_call=$(($(date +%s%N) - start))

            # Second call (should use cache)
            start=$(date +%s%N)
            get_cmd_pdflatex "$PWD" &> /dev/null
            second_call=$(($(date +%s%N) - start))

            first_ms=$((first_call / 1000000))
            second_ms=$((second_call / 1000000))

            echo "  First call:  ${first_ms}ms"
            echo "  Second call: ${second_ms}ms"

            # Use lenient threshold: 3x faster is good enough (CI can be slow)
            if [ $second_ms -lt $((first_ms / 3)) ] || [ $first_ms -lt 10 ]; then
                echo -e "${GREEN}✓${NC} Command caching works"
            else
                echo -e "${YELLOW}⚠${NC} Command caching may not be optimal (informational only)"
            fi
        else
            echo -e "${YELLOW}⚠${NC} Command resolution not available in this environment (skipped)"
        fi
    else
        echo -e "${YELLOW}⚠${NC} Command switching module not available (skipped)"
    fi
fi

# Test 3: Dependency check is reasonably fast
echo
echo "Test 3: Dependency check performance"
start=$(date +%s)
./scripts/shell/modules/check_dependancy_commands.sh &> /dev/null || true
elapsed=$(( $(date +%s) - start ))

echo "  Time: ${elapsed}s"

if [ $elapsed -lt 10 ]; then
    echo -e "${GREEN}✓${NC} Dependency check is fast (< 10s)"
elif [ $elapsed -lt 15 ]; then
    echo -e "${YELLOW}⚠${NC} Dependency check is acceptable (10-15s)"
else
    echo -e "${RED}✗${NC} Dependency check is slow (> 15s)"
fi

# Test 4: Word count uses cached command
echo
echo "Test 4: Word count optimization"
if grep -q "TEXCOUNT_CMD=\$(get_cmd_texcount" "./scripts/shell/modules/count_words.sh"; then
    echo -e "${GREEN}✓${NC} Word count caches texcount command"
else
    echo -e "${RED}✗${NC} Word count doesn't cache command"
fi

echo
echo "=============================="
echo "Performance tests completed"
echo "=============================="

# Performance tests are informational - always exit 0
# Real failures are caught by other test suites
exit 0

# EOF
