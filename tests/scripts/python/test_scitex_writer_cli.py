#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-20
# File: tests/python/test_scitex_writer_cli.py

"""Tests for scitex_writer CLI module."""

import subprocess
import sys
from unittest.mock import patch


class TestVersion:
    """Test version-related functionality."""

    def test_version_import_version_is_not_none_and_isinstance_version_str_and(self):
        """Test that version can be imported."""
        # Arrange
        # Act
        from scitex_writer import __version__

        # Assert
        assert (__version__ is not None) and (isinstance(__version__, str)) and (len(__version__.split('.')) >= 2)

    def test_version_cli_flag(self):
        """Test --version flag."""
        # Arrange
        from scitex_writer import __version__

        # Act
        result = subprocess.run(
            [sys.executable, "-m", "scitex_writer", "--version"],
            capture_output=True,
            text=True,
        )
        # Assert
        assert (result.returncode == 0) and ('scitex-writer' in result.stdout) and (__version__ in result.stdout)

    def test_version_short_flag(self):
        """Test -V flag."""
        # Arrange
        # Act
        result = subprocess.run(
            [sys.executable, "-m", "scitex_writer", "-V"],
            capture_output=True,
            text=True,
        )
        # Assert
        assert (result.returncode == 0) and ('scitex-writer' in result.stdout)


class TestMainHelp:
    """Test main help functionality."""

    def test_help_flag_result_returncode_equals_n_0_and_scitex_write(self):
        """Test --help flag."""
        # Arrange
        # Act
        result = subprocess.run(
            [sys.executable, "-m", "scitex_writer", "--help"],
            capture_output=True,
            text=True,
        )
        # Assert
        assert (result.returncode == 0) and ('scitex-writer' in result.stdout.lower()) and ('mcp' in result.stdout)

    def test_short_help_flag(self):
        """Test -h flag."""
        # Arrange
        # Act
        result = subprocess.run(
            [sys.executable, "-m", "scitex_writer", "-h"],
            capture_output=True,
            text=True,
        )
        # Assert
        assert (result.returncode == 0) and ('mcp' in result.stdout)


class TestMcpCommand:
    """Test MCP subcommand."""

    def test_mcp_help_result_returncode_equals_n_0_and_installation(self):
        """Test mcp --help."""
        # Arrange
        # Act
        result = subprocess.run(
            [sys.executable, "-m", "scitex_writer", "mcp", "--help"],
            capture_output=True,
            text=True,
        )
        # Assert
        assert (result.returncode == 0) and ('installation' in result.stdout) and ('start' in result.stdout)


class TestMcpInstallation:
    """Test mcp installation subcommand."""

    def test_mcp_installation_result_returncode_equals_n_0_and_mcpservers_i(self):
        """Test mcp installation output."""
        # Arrange
        # Act
        result = subprocess.run(
            [sys.executable, "-m", "scitex_writer", "mcp", "installation"],
            capture_output=True,
            text=True,
        )
        # Assert
        assert (result.returncode == 0) and ('mcpServers' in result.stdout or 'Installation' in result.stdout)


class TestMcpStart:
    """Test mcp start subcommand."""

    def test_mcp_start_help(self):
        """Test mcp start --help."""
        # Arrange
        # Act
        result = subprocess.run(
            [sys.executable, "-m", "scitex_writer", "mcp", "start", "--help"],
            capture_output=True,
            text=True,
        )
        # Assert
        assert (result.returncode == 0) and ('--transport' in result.stdout or '-t' in result.stdout)


class TestMainFunction:
    """Test main() function directly."""

    def test_main_no_args(self):
        """Test main() with no arguments shows help."""
        # Arrange
        from scitex_writer._cli import main

        # Act
        with patch("sys.argv", ["scitex-writer"]):
            result = main()
        # Assert
        assert result == 0

    def test_main_mcp_no_subcommand(self):
        """Test main() with mcp but no subcommand shows help."""
        # Arrange
        from scitex_writer._cli import main

        # Act
        with patch("sys.argv", ["scitex-writer", "mcp"]):
            result = main()
        # Assert
        assert result == 0


# EOF
