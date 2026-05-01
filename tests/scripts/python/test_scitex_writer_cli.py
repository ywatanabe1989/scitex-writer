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

    def test_version_import(self):
        """Test that version can be imported."""
        from scitex_writer import __version__

        assert __version__ is not None
        assert isinstance(__version__, str)
        assert len(__version__.split(".")) >= 2

    def test_version_cli_flag(self):
        """Test --version flag."""
        from scitex_writer import __version__

        result = subprocess.run(
            [sys.executable, "-m", "scitex_writer", "--version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "scitex-writer" in result.stdout
        assert __version__ in result.stdout

    def test_version_short_flag(self):
        """Test -V flag."""
        result = subprocess.run(
            [sys.executable, "-m", "scitex_writer", "-V"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "scitex-writer" in result.stdout


class TestMainHelp:
    """Test main help functionality."""

    def test_help_flag(self):
        """Test --help flag."""
        result = subprocess.run(
            [sys.executable, "-m", "scitex_writer", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "SciTeX Writer" in result.stdout
        assert "mcp" in result.stdout

    def test_short_help_flag(self):
        """Test -h flag."""
        result = subprocess.run(
            [sys.executable, "-m", "scitex_writer", "-h"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "mcp" in result.stdout


class TestMcpCommand:
    """Test MCP subcommand."""

    def test_mcp_help(self):
        """Test mcp --help."""
        result = subprocess.run(
            [sys.executable, "-m", "scitex_writer", "mcp", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "installation" in result.stdout
        assert "start" in result.stdout


class TestMcpInstallation:
    """Test mcp installation subcommand."""

    def test_mcp_installation(self):
        """Test mcp installation output."""
        result = subprocess.run(
            [sys.executable, "-m", "scitex_writer", "mcp", "installation"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "mcpServers" in result.stdout or "Installation" in result.stdout


class TestMcpStart:
    """Test mcp start subcommand."""

    def test_mcp_start_help(self):
        """Test mcp start --help."""
        result = subprocess.run(
            [sys.executable, "-m", "scitex_writer", "mcp", "start", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "--transport" in result.stdout or "-t" in result.stdout


class TestMainFunction:
    """Test main() function directly."""

    def test_main_no_args(self):
        """Test main() with no arguments shows help."""
        from scitex_writer._cli import main

        with patch("sys.argv", ["scitex-writer"]):
            result = main()
        assert result == 0

    def test_main_mcp_no_subcommand(self):
        """Test main() with mcp but no subcommand shows help."""
        from scitex_writer._cli import main

        with patch("sys.argv", ["scitex-writer", "mcp"]):
            result = main()
        assert result == 0


# EOF
