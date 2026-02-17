#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: 2026-02-18
# File: examples/02_mcp_tools.sh

# Example: Using MCP tools via CLI
# Usage: ./examples/02_mcp_tools.sh

set -e

echo "=== Example 02: MCP Tools ==="

# Show available tools
echo "1. List MCP tools:"
scitex-writer mcp list-tools

# Check MCP setup
echo "2. Doctor check:"
scitex-writer mcp doctor

# Show Claude Desktop config
echo "3. Claude Desktop installation guide:"
scitex-writer mcp installation

echo "=== Done ==="

# EOF
