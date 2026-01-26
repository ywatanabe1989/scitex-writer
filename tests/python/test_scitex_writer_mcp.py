#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-20
# File: tests/python/test_scitex_writer_mcp.py

"""Tests for scitex_writer MCP module.

The MCP server exposes comprehensive tools for manuscript operations.
"""

from pathlib import Path


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


class TestToolRegistration:
    """Test that the usage tool is registered."""

    def test_usage_tool_registered(self):
        """Test that usage tool is registered with MCP."""
        from scitex_writer._mcp import mcp

        tool_names = [t.name for t in mcp._tool_manager._tools.values()]
        assert "usage" in tool_names

    def test_tool_count(self):
        """Test that expected number of tools are registered."""
        from scitex_writer._mcp import mcp

        tool_count = len(mcp._tool_manager._tools)
        # 28 tools: usage, project (4), compile (3), tables (5), figures (5),
        # bib (6), guidelines (3), prompts (1)
        assert tool_count >= 20  # At least 20 tools expected


class TestUsageTool:
    """Test usage tool functionality."""

    def test_usage_returns_instructions(self):
        """Test usage tool returns INSTRUCTIONS."""
        from scitex_writer._mcp import INSTRUCTIONS, mcp

        tool = mcp._tool_manager._tools.get("usage")
        assert tool is not None
        result = tool.fn()
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

    def test_instructions_has_scitex_writer_root(self):
        """Test that INSTRUCTIONS explains SCITEX_WRITER_ROOT."""
        from scitex_writer._mcp import INSTRUCTIONS

        assert "SCITEX_WRITER_ROOT" in INSTRUCTIONS
        assert "compile.sh" in INSTRUCTIONS

    def test_instructions_has_revision_info(self):
        """Test that INSTRUCTIONS mentions revision directory."""
        from scitex_writer._mcp import INSTRUCTIONS

        assert "03_revision" in INSTRUCTIONS

    def test_instructions_has_bib_merge(self):
        """Test that INSTRUCTIONS explains bib auto-merge."""
        from scitex_writer._mcp import INSTRUCTIONS

        assert "bib_files/" in INSTRUCTIONS
        assert "auto-merge" in INSTRUCTIONS.lower() or "merge" in INSTRUCTIONS.lower()


class TestHandlersModule:
    """Test handlers module can be imported."""

    def test_handlers_import(self):
        """Test that handlers module can be imported."""
        from scitex_writer._mcp import handlers

        assert handlers is not None

    def test_handlers_functions_exist(self):
        """Test that all handler functions exist (not registered, but available)."""
        from scitex_writer._mcp import handlers

        assert callable(handlers.clone_project)
        assert callable(handlers.compile_manuscript)
        assert callable(handlers.compile_supplementary)
        assert callable(handlers.compile_revision)
        assert callable(handlers.get_project_info)
        assert callable(handlers.get_pdf)
        assert callable(handlers.list_document_types)
        assert callable(handlers.csv_to_latex)
        assert callable(handlers.latex_to_csv)
        assert callable(handlers.pdf_to_images)
        assert callable(handlers.list_figures)
        assert callable(handlers.convert_figure)


class TestUtilsModule:
    """Test utils module."""

    def test_utils_import(self):
        """Test that utils module can be imported."""
        from scitex_writer._mcp.utils import resolve_project_path, run_compile_script

        assert callable(resolve_project_path)
        assert callable(run_compile_script)

    def test_resolve_project_path_relative(self):
        """Test resolve_project_path with relative path."""
        from scitex_writer._mcp.utils import resolve_project_path

        result = resolve_project_path(".")
        assert result.is_absolute()

    def test_resolve_project_path_absolute(self):
        """Test resolve_project_path with absolute path."""
        from scitex_writer._mcp.utils import resolve_project_path

        result = resolve_project_path("/tmp")
        assert result == Path("/tmp")


# EOF
