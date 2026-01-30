#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-20
# File: examples/03_python_api.py

"""Example: Using scitex-writer Python API.

Usage: python examples/03_python_api.py
"""

from pathlib import Path


def main():
    """Demonstrate scitex-writer Python API."""
    print("=== Example 03: Python API ===")

    # Import handlers from the internal handlers module
    from scitex_writer._mcp.handlers import (
        get_project_info,
        list_document_types,
        list_figures,
    )

    project_dir = str(Path(__file__).parent.parent)

    # 1. List document types
    print("\n1. Document types:")
    result = list_document_types()
    for doc in result["document_types"]:
        print(f"   - {doc['id']}: {doc['name']} ({doc['directory']})")

    # 2. Get project info
    print("\n2. Project info:")
    result = get_project_info(project_dir)
    if result["success"]:
        print(f"   Project: {result['project_dir']}")
        print(f"   Has compile.sh: {result.get('has_compile_script', False)}")

    # 3. List figures
    print("\n3. Figures in project:")
    result = list_figures(project_dir)
    if result["success"]:
        print(f"   Count: {result['count']}")
        for fig in result["figures"][:3]:
            print(f"   - {fig['name']}")

    print("\n=== Done ===")


if __name__ == "__main__":
    main()

# EOF
