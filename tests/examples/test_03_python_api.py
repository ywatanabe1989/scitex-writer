#!/usr/bin/env python3
"""Compile-only smoke test for examples/03_python_api.py."""

import py_compile
from pathlib import Path

EXAMPLE = Path(__file__).resolve().parents[2] / "examples" / "03_python_api.py"


def test_example_file_exists():
    # Arrange
    # Act
    # Assert
    assert EXAMPLE.is_file(), f"missing example: {EXAMPLE}"


def test_example_compiles_without_syntax_error():
    # Arrange
    # Act
    compiled = py_compile.compile(str(EXAMPLE), doraise=True)
    # Assert
    assert compiled is not None


if __name__ == "__main__":
    import os
    import sys

    import pytest

    sys.exit(pytest.main([os.path.abspath(__file__)]))
