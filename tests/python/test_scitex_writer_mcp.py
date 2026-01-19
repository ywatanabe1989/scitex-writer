#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-20
# File: tests/python/test_scitex_writer_mcp.py

"""Tests for scitex_writer MCP module."""

import tempfile
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
    """Test that all 13 tools are registered."""

    def test_all_tools_registered(self):
        """Test that all expected tools are registered with MCP."""
        from scitex_writer._mcp import mcp

        tool_names = [t.name for t in mcp._tool_manager._tools.values()]

        expected_tools = [
            "clone_project",
            "compile_manuscript",
            "compile_supplementary",
            "compile_revision",
            "get_project_info",
            "get_pdf",
            "list_document_types",
            "csv_to_latex",
            "latex_to_csv",
            "pdf_to_images",
            "list_figures",
            "convert_figure",
            "scitex_writer",
        ]

        for tool in expected_tools:
            assert tool in tool_names, f"Tool {tool} not registered"

    def test_tool_count(self):
        """Test that exactly 13 tools are registered."""
        from scitex_writer._mcp import mcp

        tool_count = len(mcp._tool_manager._tools)
        assert tool_count == 13


class TestScitexWriterTool:
    """Test scitex_writer tool functionality."""

    def test_scitex_writer_usage_command(self):
        """Test scitex_writer with usage command."""
        from scitex_writer._mcp import INSTRUCTIONS, mcp

        tool = mcp._tool_manager._tools.get("scitex_writer")
        result = tool.fn(command="usage")
        assert result == INSTRUCTIONS


class TestListDocumentTypes:
    """Test list_document_types tool."""

    def test_list_document_types_returns_dict(self):
        """Test that list_document_types returns a dict."""
        from scitex_writer._mcp import mcp

        tool = mcp._tool_manager._tools.get("list_document_types")
        result = tool.fn()
        assert isinstance(result, dict)
        assert result["success"] is True

    def test_list_document_types_has_types(self):
        """Test that list_document_types includes all doc types."""
        from scitex_writer._mcp import mcp

        tool = mcp._tool_manager._tools.get("list_document_types")
        result = tool.fn()
        doc_types = [d["id"] for d in result["document_types"]]
        assert "manuscript" in doc_types
        assert "supplementary" in doc_types
        assert "revision" in doc_types


class TestGetProjectInfo:
    """Test get_project_info tool."""

    def test_get_project_info_nonexistent(self):
        """Test get_project_info with non-existent directory."""
        from scitex_writer._mcp import mcp

        tool = mcp._tool_manager._tools.get("get_project_info")
        result = tool.fn(project_dir="/nonexistent/path")
        assert result["success"] is False
        assert "error" in result

    def test_get_project_info_current_dir(self):
        """Test get_project_info with current project directory."""
        from scitex_writer._mcp import mcp

        tool = mcp._tool_manager._tools.get("get_project_info")
        result = tool.fn(project_dir=".")
        assert result["success"] is True
        assert "project_dir" in result


class TestGetPdf:
    """Test get_pdf tool."""

    def test_get_pdf_manuscript(self):
        """Test get_pdf with manuscript doc_type."""
        from scitex_writer._mcp import mcp

        tool = mcp._tool_manager._tools.get("get_pdf")
        result = tool.fn(project_dir=".", doc_type="manuscript")
        assert result["success"] is True
        assert result["doc_type"] == "manuscript"


class TestCsvToLatex:
    """Test csv_to_latex tool."""

    def test_csv_to_latex_nonexistent(self):
        """Test csv_to_latex with non-existent file."""
        from scitex_writer._mcp import mcp

        tool = mcp._tool_manager._tools.get("csv_to_latex")
        result = tool.fn(csv_path="/nonexistent/file.csv")
        assert result["success"] is False

    def test_csv_to_latex_valid(self):
        """Test csv_to_latex with valid CSV."""
        from scitex_writer._mcp import mcp

        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("Name,Value\nA,1\nB,2\n")
            csv_path = f.name

        try:
            tool = mcp._tool_manager._tools.get("csv_to_latex")
            result = tool.fn(csv_path=csv_path)
            assert result["success"] is True
            assert "latex_content" in result
            assert "\\begin{table}" in result["latex_content"]
        finally:
            Path(csv_path).unlink()


class TestListFigures:
    """Test list_figures tool."""

    def test_list_figures_current_project(self):
        """Test list_figures on current project."""
        from scitex_writer._mcp import mcp

        tool = mcp._tool_manager._tools.get("list_figures")
        result = tool.fn(project_dir=".")
        assert result["success"] is True
        assert "figures" in result
        assert "count" in result


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
        assert "supplementary.pdf" in INSTRUCTIONS
        assert "revision.pdf" in INSTRUCTIONS


class TestHandlersModule:
    """Test handlers module can be imported."""

    def test_handlers_import(self):
        """Test that handlers module can be imported."""
        from scitex_writer._mcp import handlers

        assert handlers is not None

    def test_handlers_functions_exist(self):
        """Test that all handler functions exist."""
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
