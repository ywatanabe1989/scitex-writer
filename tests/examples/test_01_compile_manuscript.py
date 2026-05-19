#!/usr/bin/env python3
"""Compile-only smoke test for examples/01_compile_manuscript.sh (shell)."""

from pathlib import Path

EXAMPLE = Path(__file__).resolve().parents[2] / "examples" / "01_compile_manuscript.sh"


def test_example_exists_example_is_file():
    # Arrange
    # Act
    # Assert
    # Arrange
    # Act
    # Assert
    assert EXAMPLE.is_file(), f"missing example: {EXAMPLE}"


def test_example_exists_example_read_text_lstrip_startswith():
    # Arrange
    # Act
    # Assert
    # Arrange
    # Act
    # Assert
    assert EXAMPLE.read_text().lstrip().startswith("#"), (
        "expected shell shebang/comment"
    )




if __name__ == "__main__":
    test_example_exists()
