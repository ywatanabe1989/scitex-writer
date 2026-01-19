#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-20
# File: examples/02_mcp_tools.sh

# Example: Using MCP tools via CLI
# Usage: ./examples/02_mcp_tools.sh

set -e

echo "=== Example 02: MCP Tools ==="

# Show available tools
echo "1. List MCP tools:"
scitex-writer mcp info

# Check MCP setup
echo "2. Doctor check:"
scitex-writer mcp doctor

# Show Claude Desktop config
echo "3. Claude Desktop config:"
scitex-writer mcp config

echo "=== Done ==="

# EOF
