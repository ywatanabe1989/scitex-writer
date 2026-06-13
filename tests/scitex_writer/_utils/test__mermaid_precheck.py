#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: tests/scitex_writer/_utils/test__mermaid_precheck.py

"""Tests for scitex_writer._utils._mermaid_precheck.check_mmdc_or_raise.

These tests use tmp_path PATH manipulation (not unittest.mock) to
exercise the precheck without requiring a real mmdc install on the
CI runner.
"""

import os
import stat
from pathlib import Path

import pytest

from scitex_writer._utils._mermaid_precheck import (
    MermaidDependencyError,
    check_mmdc_or_raise,
)


# ---------------------------------------------------------------------------
# Helpers (testing infrastructure — write a fake mmdc into tmp_path)
# ---------------------------------------------------------------------------


def _install_fake_mmdc(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    body: str,
) -> Path:
    """Drop a fake mmdc shell-script into tmp_path and put it on PATH.

    Returns the path to the fake mmdc binary.
    """
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "mmdc"
    fake.write_text(body)
    fake.chmod(fake.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    monkeypatch.setenv("PATH", str(bin_dir), prepend=os.pathsep)
    return fake


# ---------------------------------------------------------------------------
# mmdc not on PATH
# ---------------------------------------------------------------------------


class TestMmdcMissing:
    """mmdc binary is not present anywhere on PATH."""

    def test_raises_mermaid_dependency_error_when_mmdc_missing(
        self, tmp_path, monkeypatch
    ):
        # Arrange
        monkeypatch.setenv("PATH", str(tmp_path / "empty"))
        # Act / Assert
        with pytest.raises(MermaidDependencyError):
            check_mmdc_or_raise()

    def test_error_message_mentions_install_hint_when_missing(
        self, tmp_path, monkeypatch
    ):
        # Arrange
        monkeypatch.setenv("PATH", str(tmp_path / "empty"))
        # Act
        with pytest.raises(MermaidDependencyError) as exc_info:
            check_mmdc_or_raise()
        # Assert
        assert "mermaid-cli" in str(exc_info.value)


# ---------------------------------------------------------------------------
# mmdc present but libnspr4 missing (most common Linux gap)
# ---------------------------------------------------------------------------


class TestMmdcLibnspr4Missing:
    """mmdc is on PATH but its chromium dep is missing libnspr4."""

    def test_raises_mermaid_dependency_error_when_libnspr4_missing(
        self, tmp_path, monkeypatch
    ):
        # Arrange
        _install_fake_mmdc(
            tmp_path,
            monkeypatch,
            body=(
                "#!/bin/sh\n"
                "echo 'error while loading shared libraries: libnspr4.so:"
                " cannot open shared object file' >&2\n"
                "exit 127\n"
            ),
        )
        # Act / Assert
        with pytest.raises(MermaidDependencyError):
            check_mmdc_or_raise()

    def test_error_message_mentions_libnspr4_install_hint(
        self, tmp_path, monkeypatch
    ):
        # Arrange
        _install_fake_mmdc(
            tmp_path,
            monkeypatch,
            body=(
                "#!/bin/sh\n"
                "echo 'error while loading shared libraries: libnspr4.so:"
                " cannot open shared object file' >&2\n"
                "exit 127\n"
            ),
        )
        # Act
        with pytest.raises(MermaidDependencyError) as exc_info:
            check_mmdc_or_raise()
        # Assert
        assert "libnspr4" in str(exc_info.value)


# ---------------------------------------------------------------------------
# mmdc present but chromium SIGSEGVs (apptainer / singularity gap)
# ---------------------------------------------------------------------------


class TestMmdcApptainerSegfault:
    """mmdc on PATH, but headless chromium SIGSEGVs (typical apptainer)."""

    def test_raises_mermaid_dependency_error_on_sigsegv(
        self, tmp_path, monkeypatch
    ):
        # Arrange
        _install_fake_mmdc(
            tmp_path,
            monkeypatch,
            body=(
                "#!/bin/sh\n"
                "echo 'Aborted (core dumped) SIGSEGV in chromium' >&2\n"
                "exit 139\n"
            ),
        )
        # Act / Assert
        with pytest.raises(MermaidDependencyError):
            check_mmdc_or_raise()

    def test_error_message_mentions_sandbox_hint_on_sigsegv(
        self, tmp_path, monkeypatch
    ):
        # Arrange
        _install_fake_mmdc(
            tmp_path,
            monkeypatch,
            body=(
                "#!/bin/sh\n"
                "echo 'Aborted (core dumped) SIGSEGV in chromium' >&2\n"
                "exit 139\n"
            ),
        )
        # Act
        with pytest.raises(MermaidDependencyError) as exc_info:
            check_mmdc_or_raise()
        # Assert
        assert "sandbox" in str(exc_info.value).lower()


# ---------------------------------------------------------------------------
# mmdc present and working
# ---------------------------------------------------------------------------


class TestMmdcWorking:
    """mmdc is on PATH and runs --version successfully."""

    def test_returns_resolved_mmdc_path_when_working(
        self, tmp_path, monkeypatch
    ):
        # Arrange
        fake = _install_fake_mmdc(
            tmp_path,
            monkeypatch,
            body="#!/bin/sh\necho '10.0.0'\nexit 0\n",
        )
        # Act
        resolved = check_mmdc_or_raise()
        # Assert
        assert resolved == str(fake)


# ---------------------------------------------------------------------------
# Explicit override path
# ---------------------------------------------------------------------------


class TestMmdcExplicitOverride:
    """Caller passes mmdc_path explicitly (bypassing shutil.which)."""

    def test_raises_when_explicit_path_does_not_exist(self, tmp_path):
        # Arrange
        bogus = str(tmp_path / "does-not-exist" / "mmdc")
        # Act / Assert
        with pytest.raises(MermaidDependencyError):
            check_mmdc_or_raise(mmdc_path=bogus)


if __name__ == "__main__":
    import os as _os

    pytest.main([_os.path.abspath(__file__)])

# EOF
