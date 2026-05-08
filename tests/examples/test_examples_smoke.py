"""Smoke tests: every example *.py script must run to completion.

Bash examples (*.sh) are excluded — they invoke external tools (latex
toolchain, mcp servers) that aren't part of the unit-test contract.
"""

import subprocess
import sys
from pathlib import Path

EXAMPLES = sorted(Path(__file__).parent.parent.joinpath("examples").glob("*.py"))


def test_examples_smoke(tmp_path):
    assert EXAMPLES, "no example scripts found"
    for ex in EXAMPLES:
        r = subprocess.run(
            [sys.executable, str(ex)],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert r.returncode == 0, f"{ex.name} failed: {r.stderr}"
