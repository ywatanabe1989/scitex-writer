#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-10 01:36:00 (ywatanabe)"
# File: ./tests/scripts/test_performance.sh
# Description: Test performance optimizations

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

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
export SCITEX_WRITER_DOC_TYPE=manuscript
source ./config/load_config.sh manuscript &> /dev/null
source ./scripts/shell/modules/command_switching.src

# First call
start=$(date +%s%N)
get_cmd_pdflatex "$PWD" &> /dev/null
first_call=$(($(date +%s%N) - start))

# Second call (should use cache)
start=$(date +%s%N)
get_cmd_pdflatex "$PWD" &> /dev/null
second_call=$(($(date +%s%N) - start))

first_ms=$((first_call / 1000000))
second_ms=$((second_call / 1000000))

echo "  First call:  ${first_ms}ms"
echo "  Second call: ${second_ms}ms"

if [ $second_ms -lt $((first_ms / 2)) ]; then
    echo -e "${GREEN}✓${NC} Command caching works"
else
    echo -e "${YELLOW}⚠${NC} Command caching may not be optimal"
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

# EOF
