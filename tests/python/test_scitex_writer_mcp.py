#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-19 05:15:00
# File: tests/python/test_scitex_writer_mcp.py

"""Tests for scitex_writer MCP module."""


class TestMcpModule:
    """Test MCP module functionality."""

    def test_mcp_import(self):
        """Test that MCP module can be imported."""
        from scitex_writer._mcp import mcp

        assert mcp is not None
        assert mcp.name == "scitex-writer"

    def test_instructions_defined(self):
        """Test that INSTRUCTIONS is defined."""
        from scitex_writer._mcp import INSTRUCTIONS

        assert INSTRUCTIONS is not None
        assert isinstance(INSTRUCTIONS, str)
        assert "scitex-writer" in INSTRUCTIONS
        assert "manuscript" in INSTRUCTIONS

    def test_run_server_function_exists(self):
        """Test that run_server function exists."""
        from scitex_writer._mcp import run_server

        assert callable(run_server)


class TestScitexWriterTool:
    """Test scitex_writer tool functionality."""

    def test_scitex_writer_tool_registered(self):
        """Test that scitex_writer tool is registered with MCP."""
        from scitex_writer._mcp import mcp

        tool_names = [t.name for t in mcp._tool_manager._tools.values()]
        assert "scitex_writer" in tool_names

    def test_scitex_writer_tool_has_fn(self):
        """Test that scitex_writer tool has underlying function."""
        from scitex_writer._mcp import mcp

        tool = mcp._tool_manager._tools.get("scitex_writer")
        assert tool is not None
        assert hasattr(tool, "fn")
        assert callable(tool.fn)

    def test_scitex_writer_usage_command(self):
        """Test scitex_writer with usage command."""
        from scitex_writer._mcp import INSTRUCTIONS, mcp

        tool = mcp._tool_manager._tools.get("scitex_writer")
        result = tool.fn(command="usage")
        assert result == INSTRUCTIONS

    def test_scitex_writer_manuscript_doc_type(self):
        """Test scitex_writer with manuscript doc_type."""
        from scitex_writer._mcp import INSTRUCTIONS, mcp

        tool = mcp._tool_manager._tools.get("scitex_writer")
        result = tool.fn(command="usage", doc_type="manuscript")
        assert result == INSTRUCTIONS

    def test_scitex_writer_supplementary_doc_type(self):
        """Test scitex_writer with supplementary doc_type."""
        from scitex_writer._mcp import INSTRUCTIONS, mcp

        tool = mcp._tool_manager._tools.get("scitex_writer")
        result = tool.fn(command="usage", doc_type="supplementary")
        assert result == INSTRUCTIONS

    def test_scitex_writer_revision_doc_type(self):
        """Test scitex_writer with revision doc_type."""
        from scitex_writer._mcp import INSTRUCTIONS, mcp

        tool = mcp._tool_manager._tools.get("scitex_writer")
        result = tool.fn(command="usage", doc_type="revision")
        assert result == INSTRUCTIONS

    def test_scitex_writer_project_dir(self):
        """Test scitex_writer with project_dir parameter."""
        from scitex_writer._mcp import INSTRUCTIONS, mcp

        tool = mcp._tool_manager._tools.get("scitex_writer")
        result = tool.fn(command="usage", project_dir="/tmp/test")
        assert result == INSTRUCTIONS


class TestInstructionsContent:
    """Test INSTRUCTIONS content."""

    def test_instructions_has_setup(self):
        """Test that INSTRUCTIONS contains setup/clone info."""
        from scitex_writer._mcp import INSTRUCTIONS

        assert "git clone" in INSTRUCTIONS
        assert "scitex-writer" in INSTRUCTIONS

    def test_instructions_has_structure(self):
        """Test that INSTRUCTIONS contains project structure info."""
        from scitex_writer._mcp import INSTRUCTIONS

        assert "00_shared/" in INSTRUCTIONS
        assert "01_manuscript/" in INSTRUCTIONS
        assert "02_supplementary/" in INSTRUCTIONS
        assert "03_revision/" in INSTRUCTIONS

    def test_instructions_has_quick_start(self):
        """Test that INSTRUCTIONS contains quick start commands."""
        from scitex_writer._mcp import INSTRUCTIONS

        assert "./compile.sh manuscript" in INSTRUCTIONS
        assert "./compile.sh supplementary" in INSTRUCTIONS
        assert "./compile.sh revision" in INSTRUCTIONS

    def test_instructions_has_editable_files(self):
        """Test that INSTRUCTIONS lists editable files."""
        from scitex_writer._mcp import INSTRUCTIONS

        assert "abstract.tex" in INSTRUCTIONS
        assert "introduction.tex" in INSTRUCTIONS
        assert "methods.tex" in INSTRUCTIONS
        assert "results.tex" in INSTRUCTIONS
        assert "discussion.tex" in INSTRUCTIONS

    def test_instructions_has_compile_options(self):
        """Test that INSTRUCTIONS lists compile options."""
        from scitex_writer._mcp import INSTRUCTIONS

        assert "--draft" in INSTRUCTIONS
        assert "--no_figs" in INSTRUCTIONS
        assert "--no_tables" in INSTRUCTIONS
        assert "--no_diff" in INSTRUCTIONS

    def test_instructions_has_output_info(self):
        """Test that INSTRUCTIONS lists output files."""
        from scitex_writer._mcp import INSTRUCTIONS

        assert "manuscript.pdf" in INSTRUCTIONS
        assert "supplementary.pdf" in INSTRUCTIONS
        assert "revision.pdf" in INSTRUCTIONS


# EOF
