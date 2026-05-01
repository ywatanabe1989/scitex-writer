#!/usr/bin/env python3
"""Compile-only smoke test for examples/03_python_api.py."""

import py_compile
from pathlib import Path

EXAMPLE = Path(__file__).resolve().parents[2] / "examples" / "03_python_api.py"


def test_example_compiles():
    assert EXAMPLE.is_file(), f"missing example: {EXAMPLE}"
    py_compile.compile(str(EXAMPLE), doraise=True)


if __name__ == "__main__":
    test_example_compiles()
