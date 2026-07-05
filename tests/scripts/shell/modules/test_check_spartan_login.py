"""check_spartan_login.sh refuses TeX on a Spartan login node but is a no-op elsewhere."""

import subprocess
from pathlib import Path

_MODULE = (
    Path(__file__).resolve().parents[4]
    / "scripts/shell/modules/check_spartan_login.sh"
)


def _predicate_rc(host, job):
    # Source the module and run the pure predicate with controlled args.
    return subprocess.run(
        ["bash", "-c", f"source '{_MODULE}'; _scitex_on_spartan_login_no_job '{host}' '{job}'"],
    ).returncode


def test_detects_login_node_without_job():
    # Arrange
    host, job = "spartan-login1.hpc.unimelb.edu.au", ""
    # Act
    rc = _predicate_rc(host, job)
    # Assert
    assert rc == 0


def test_allows_login_node_inside_job():
    # Arrange
    host, job = "spartan-login1.hpc.unimelb.edu.au", "123456"
    # Act
    rc = _predicate_rc(host, job)
    # Assert
    assert rc == 1


def test_allows_non_spartan_host():
    # Arrange
    host, job = "my-laptop", ""
    # Act
    rc = _predicate_rc(host, job)
    # Assert
    assert rc == 1


def test_standalone_guard_is_noop_off_spartan():
    # Arrange
    # The CI/test host is not a spartan-login node, so the standalone guard exits 0.
    cmd = ["bash", str(_MODULE)]
    # Act
    result = subprocess.run(cmd)
    # Assert
    assert result.returncode == 0
