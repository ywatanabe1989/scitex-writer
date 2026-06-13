#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: tests/scitex_writer/_utils/test__mermaid_precheck.py

"""Tests for scitex_writer._utils._mermaid_precheck.check_mmdc_or_raise.

These tests use ``tmp_path`` plus the explicit ``mmdc_path`` override
on ``check_mmdc_or_raise`` so we never touch ``shutil.which`` / PATH
and never need the ``monkeypatch`` fixture (PA-306 no-mocks doctrine).
A fake ``mmdc`` is written into ``tmp_path`` as a tiny shell script
with controlled exit code / stderr to simulate each failure mode.
"""

from pathlib import Path

import pytest

from scitex_writer._utils._mermaid_precheck import (
    MermaidDependencyError,
    check_mmdc_or_raise,
)

# ---------------------------------------------------------------------------
# Helpers (testing infrastructure — drop a fake mmdc shim into tmp_path)
# ---------------------------------------------------------------------------


def _write_fake_mmdc(tmp_path: Path, body: str) -> Path:
    """Write an executable shim at ``tmp_path/mmdc`` and return its path."""
    fake = tmp_path / "mmdc"
    fake.write_text(body)
    # chmod +rwx for owner / group / world (0o755)
    fake.chmod(0o755)
    return fake


# ---------------------------------------------------------------------------
# mmdc not on PATH (caller passes an explicit nonexistent path)
# ---------------------------------------------------------------------------


class TestMmdcMissing:
    """No mmdc binary exists at the given path."""

    def test_raises_mermaid_dependency_error_when_mmdc_missing(self, tmp_path):
        # Arrange
        bogus = str(tmp_path / "does-not-exist" / "mmdc")
        # Act
        # Assert
        with pytest.raises(MermaidDependencyError, match="mermaid-cli"):
            check_mmdc_or_raise(mmdc_path=bogus)


# ---------------------------------------------------------------------------
# mmdc present but libnspr4 missing (most common Linux gap)
# ---------------------------------------------------------------------------


class TestMmdcLibnspr4Missing:
    """mmdc binary exists but its chromium dep is missing libnspr4."""

    def test_raises_with_libnspr4_install_hint(self, tmp_path):
        # Arrange
        fake = _write_fake_mmdc(
            tmp_path,
            body=(
                "#!/bin/sh\n"
                "echo 'error while loading shared libraries: libnspr4.so:"
                " cannot open shared object file' >&2\n"
                "exit 127\n"
            ),
        )
        # Act
        # Assert
        with pytest.raises(MermaidDependencyError, match="libnspr4"):
            check_mmdc_or_raise(mmdc_path=str(fake))


# ---------------------------------------------------------------------------
# mmdc present but chromium SIGSEGVs (apptainer / singularity gap)
# ---------------------------------------------------------------------------


class TestMmdcApptainerSegfault:
    """mmdc binary exists, but its headless chromium SIGSEGVs."""

    def test_raises_with_sandbox_hint_on_sigsegv(self, tmp_path):
        # Arrange
        fake = _write_fake_mmdc(
            tmp_path,
            body=(
                "#!/bin/sh\n"
                "echo 'Aborted (core dumped) SIGSEGV in chromium' >&2\n"
                "exit 139\n"
            ),
        )
        # Act
        # Assert
        with pytest.raises(MermaidDependencyError, match="sandbox"):
            check_mmdc_or_raise(mmdc_path=str(fake))


# ---------------------------------------------------------------------------
# mmdc present and working
# ---------------------------------------------------------------------------


class TestMmdcWorking:
    """mmdc binary exists and ``mmdc --version`` succeeds."""

    def test_returns_resolved_mmdc_path_when_working(self, tmp_path):
        # Arrange
        fake = _write_fake_mmdc(
            tmp_path,
            body="#!/bin/sh\necho '10.0.0'\nexit 0\n",
        )
        # Act
        resolved = check_mmdc_or_raise(mmdc_path=str(fake))
        # Assert
        assert resolved == str(fake)


# ---------------------------------------------------------------------------
# mmdc present but a generic non-zero exit (not libnspr4 / not SIGSEGV)
# ---------------------------------------------------------------------------


class TestMmdcGenericFailure:
    """mmdc exits non-zero with stderr that matches neither known needle."""

    def test_raises_with_install_hint_on_generic_failure(self, tmp_path):
        # Arrange
        fake = _write_fake_mmdc(
            tmp_path,
            body=("#!/bin/sh\necho 'some unrelated error message' >&2\nexit 2\n"),
        )
        # Act
        # Assert
        with pytest.raises(MermaidDependencyError, match="exited with code 2"):
            check_mmdc_or_raise(mmdc_path=str(fake))


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__)])

# EOF
