#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-27
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
        # Server name uses branding
        from scitex_writer._branding import get_mcp_server_name

        assert mcp.name == get_mcp_server_name()

    def test_instructions_via_branding(self):
        """Test that instructions are available via branding module."""
        from scitex_writer._branding import get_mcp_instructions

        instructions = get_mcp_instructions()
        assert instructions is not None
        assert isinstance(instructions, str)
        assert "manuscript" in instructions

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
        """Test usage tool returns instructions."""
        from scitex_writer._branding import get_mcp_instructions
        from scitex_writer._mcp import mcp

        tool = mcp._tool_manager._tools.get("usage")
        assert tool is not None
        result = tool.fn()
        assert result == get_mcp_instructions()


class TestInstructionsContent:
    """Test instructions content."""

    def test_instructions_has_setup(self):
        """Test that instructions contains setup/clone info."""
        from scitex_writer._branding import get_mcp_instructions

        instructions = get_mcp_instructions()
        assert "git clone" in instructions
        assert "scitex-writer" in instructions

    def test_instructions_has_structure(self):
        """Test that instructions contains project structure info."""
        from scitex_writer._branding import get_mcp_instructions

        instructions = get_mcp_instructions()
        assert "00_shared/" in instructions
        assert "01_manuscript/" in instructions
        assert "02_supplementary/" in instructions
        assert "03_revision/" in instructions

    def test_instructions_has_editable_files(self):
        """Test that instructions lists editable files."""
        from scitex_writer._branding import get_mcp_instructions

        instructions = get_mcp_instructions()
        assert "abstract.tex" in instructions
        assert "introduction.tex" in instructions
        assert "methods.tex" in instructions
        assert "results.tex" in instructions
        assert "discussion.tex" in instructions

    def test_instructions_has_compile_options(self):
        """Test that instructions lists compile options."""
        from scitex_writer._branding import get_mcp_instructions

        instructions = get_mcp_instructions()
        assert "--draft" in instructions
        assert "--no_figs" in instructions
        assert "--no_tables" in instructions
        assert "--no_diff" in instructions

    def test_instructions_has_output_info(self):
        """Test that instructions lists output files."""
        from scitex_writer._branding import get_mcp_instructions

        instructions = get_mcp_instructions()
        assert "manuscript.pdf" in instructions

    def test_instructions_has_scitex_writer_root(self):
        """Test that instructions explains SCITEX_WRITER_ROOT."""
        from scitex_writer._branding import get_mcp_instructions

        instructions = get_mcp_instructions()
        assert "SCITEX_WRITER_ROOT" in instructions
        assert "compile.sh" in instructions

    def test_instructions_has_revision_info(self):
        """Test that instructions mentions revision directory."""
        from scitex_writer._branding import get_mcp_instructions

        instructions = get_mcp_instructions()
        assert "03_revision" in instructions

    def test_instructions_has_bib_merge(self):
        """Test that instructions explains bib auto-merge."""
        from scitex_writer._branding import get_mcp_instructions

        instructions = get_mcp_instructions()
        assert "bib_files/" in instructions
        assert "auto-merge" in instructions.lower() or "merge" in instructions.lower()


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


class TestBranding:
    """Test branding module functionality."""

    def test_default_brand_values(self):
        """Test default branding values."""
        from scitex_writer._branding import BRAND_ALIAS, BRAND_NAME

        # Default values when env vars not set
        assert BRAND_NAME == "scitex-writer"
        assert BRAND_ALIAS == "sw"

    def test_get_mcp_server_name(self):
        """Test MCP server name generation."""
        from scitex_writer._branding import get_mcp_server_name

        # Should replace dots with hyphens
        name = get_mcp_server_name()
        assert "." not in name

    def test_rebrand_text_noop(self):
        """Test rebrand_text returns original when no branding change."""
        from scitex_writer._branding import rebrand_text

        text = "import scitex_writer as sw"
        result = rebrand_text(text)
        assert result == text

    def test_rebrand_text_none(self):
        """Test rebrand_text handles None."""
        from scitex_writer._branding import rebrand_text

        result = rebrand_text(None)
        assert result is None


# EOF
