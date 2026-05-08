#!/usr/bin/env python3
"""Compile-only smoke test for examples/01_compile_manuscript.sh (shell)."""

from pathlib import Path

EXAMPLE = Path(__file__).resolve().parents[2] / "examples" / "01_compile_manuscript.sh"


def test_example_exists():
    assert EXAMPLE.is_file(), f"missing example: {EXAMPLE}"
    assert EXAMPLE.read_text().lstrip().startswith("#"), (
        "expected shell shebang/comment"
    )


if __name__ == "__main__":
    test_example_exists()
