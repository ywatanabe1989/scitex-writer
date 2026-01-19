#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-20
# File: examples/00_run_all.sh

# Run all examples
# Usage: ./examples/00_run_all.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== SciTeX Writer Examples ==="
echo ""

# Run each example
for script in "$SCRIPT_DIR"/[0-9][0-9]_*.sh; do
    if [[ "$script" != *"00_run_all.sh" ]] && [[ -x "$script" ]]; then
        echo "Running: $(basename "$script")"
        bash "$script"
        echo ""
    fi
done

echo "=== All examples completed ==="

# EOF
