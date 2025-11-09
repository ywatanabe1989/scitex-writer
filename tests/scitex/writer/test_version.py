#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for version management.

Tests that version is correctly read from pyproject.toml
and accessible from both Python and shell scripts.
"""

import subprocess
from pathlib import Path
import pytest


class TestVersionManagement:
    """Test version tracking and display."""

    @pytest.fixture
    def project_root(self):
        """Get project root directory."""
        return Path(__file__).parent.parent.parent.parent

    def test_version_exists_in_pyproject(self, project_root):
        """Test that version is defined in pyproject.toml."""
        pyproject_file = project_root / "pyproject.toml"
        assert pyproject_file.exists(), "pyproject.toml not found"

        content = pyproject_file.read_text()
        assert 'version = ' in content, "version not defined in pyproject.toml"

    def test_python_version_import(self):
        """Test that __version__ can be imported."""
        from scitex.writer import __version__

        assert __version__ is not None
        assert __version__ != "unknown"
        assert isinstance(__version__, str)

    def test_python_version_format(self):
        """Test that version follows semantic versioning."""
        from scitex.writer import __version__

        # Should be in format: X.Y.Z or X.Y.Z-alpha/beta
        assert len(__version__) > 0
        # Contains numbers and dots
        assert any(c.isdigit() for c in __version__)

    def test_shell_version_loading(self, project_root):
        """Test that shell can load version from pyproject.toml."""
        config_script = project_root / "config" / "load_config.sh"
        assert config_script.exists(), "load_config.sh not found"

        # Test loading version in shell
        result = subprocess.run(
            ["bash", "-c",
             f'source {config_script} manuscript 2>&1; echo $SCITEX_WRITER_VERSION'],
            capture_output=True,
            text=True,
            cwd=project_root,
        )

        version_output = result.stdout.strip().split('\n')[-1]
        assert version_output != "unknown"
        assert len(version_output) > 0

    def test_makefile_version_command(self, project_root):
        """Test make version command works."""
        result = subprocess.run(
            ["make", "version"],
            capture_output=True,
            text=True,
            cwd=project_root,
        )

        assert result.returncode == 0
        assert "SciTeX Writer" in result.stdout
        assert len(result.stdout.strip()) > 0

    def test_version_consistency(self, project_root):
        """Test that Python and shell versions match."""
        from scitex.writer import __version__ as python_version

        # Get shell version
        result = subprocess.run(
            ["bash", "-c",
             f'source config/load_config.sh manuscript 2>&1; echo $SCITEX_WRITER_VERSION'],
            capture_output=True,
            text=True,
            cwd=project_root,
        )

        shell_version = result.stdout.strip().split('\n')[-1]

        # Should match
        assert python_version == shell_version, \
            f"Version mismatch: Python={python_version}, Shell={shell_version}"
