#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-20
# File: examples/01_compile_manuscript.sh

# Example: Compile manuscript with various options
# Usage: ./examples/01_compile_manuscript.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=== Example 01: Compile Manuscript ==="

# Fast compilation (draft mode, no diff)
echo "1. Fast compilation (draft, no diff)..."
"$PROJECT_ROOT/compile.sh" manuscript --draft --no_diff --quiet

echo "   Output: $PROJECT_ROOT/01_manuscript/manuscript.pdf"

# Full compilation with diff
echo "2. Full compilation with diff..."
"$PROJECT_ROOT/compile.sh" manuscript --quiet

echo "   Output: $PROJECT_ROOT/01_manuscript/manuscript.pdf"
echo "   Diff:   $PROJECT_ROOT/01_manuscript/manuscript_diff.pdf"

echo "=== Done ==="

# EOF
