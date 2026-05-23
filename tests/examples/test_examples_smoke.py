"""Smoke tests: every example *.py script must run to completion.

Bash examples (*.sh) are excluded — they invoke external tools (latex
toolchain, mcp servers) that aren't part of the unit-test contract.
"""

import subprocess
import sys
from pathlib import Path

import pytest

EXAMPLES = sorted(Path(__file__).parent.parent.joinpath("examples").glob("*.py"))


def test_example_scripts_are_discovered():
    # Arrange
    # Act
    # Assert
    assert EXAMPLES


@pytest.mark.parametrize("example", EXAMPLES, ids=lambda p: p.name)
def test_example_script_runs_to_completion(example, tmp_path):
    # Arrange
    # Act
    result = subprocess.run(
        [sys.executable, str(example)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=120,
    )
    # Assert
    assert result.returncode == 0, f"{example.name} failed: {result.stderr}"
