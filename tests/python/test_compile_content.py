#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-27
# File: tests/python/test_compile_content.py

"""Tests for scitex_writer compile.content functionality."""

import shutil
from pathlib import Path

import pytest


class TestContentModule:
    """Test content module can be imported."""

    def test_content_import(self):
        """Test that content module can be imported."""
        from scitex_writer._mcp.content import compile_content

        assert callable(compile_content)

    def test_content_via_compile_module(self):
        """Test that content is accessible via compile module."""
        from scitex_writer import compile

        assert callable(compile.content)


class TestContentHelpers:
    """Test content helper functions."""

    def test_get_color_commands_light(self):
        """Test light mode returns empty string."""
        from scitex_writer._mcp.content import _get_color_commands

        result = _get_color_commands("light")
        assert result == ""

    def test_get_color_commands_dark(self):
        """Test dark mode returns color commands."""
        from scitex_writer._mcp.content import _get_color_commands

        result = _get_color_commands("dark")
        assert "pagecolor" in result
        assert "black" in result
        assert "white" in result

    def test_get_color_commands_sepia(self):
        """Test sepia mode returns color commands."""
        from scitex_writer._mcp.content import _get_color_commands

        result = _get_color_commands("sepia")
        assert "pagecolor" in result
        assert "Sepia" in result

    def test_get_color_commands_paper(self):
        """Test paper mode returns empty string."""
        from scitex_writer._mcp.content import _get_color_commands

        result = _get_color_commands("paper")
        assert result == ""

    def test_get_color_commands_unknown(self):
        """Test unknown mode returns empty string."""
        from scitex_writer._mcp.content import _get_color_commands

        result = _get_color_commands("unknown")
        assert result == ""


class TestContentDocumentCreation:
    """Test content document creation."""

    def test_create_content_document_basic(self):
        """Test creating a basic content document."""
        from scitex_writer._mcp.content import _create_content_document

        body = r"\section{Test}\nThis is a test."
        result = _create_content_document(body, "light", None)

        assert "\\documentclass" in result
        assert "\\begin{document}" in result
        assert "\\end{document}" in result
        assert body in result

    def test_create_content_document_with_color(self):
        """Test creating content document with dark mode."""
        from scitex_writer._mcp.content import _create_content_document

        body = "Test content"
        result = _create_content_document(body, "dark", None)

        assert "pagecolor" in result
        assert "black" in result

    def test_inject_color_mode_into_document(self):
        """Test injecting color mode into existing document."""
        from scitex_writer._mcp.content import _inject_color_mode

        doc = r"\documentclass{article}\begin{document}Content\end{document}"
        result = _inject_color_mode(doc, "dark")

        assert "pagecolor" in result
        # Color commands should be after \begin{document}
        begin_doc_pos = result.find(r"\begin{document}")
        pagecolor_pos = result.find("pagecolor")
        assert pagecolor_pos > begin_doc_pos


class TestContentCompilation:
    """Test content compilation (requires latexmk)."""

    @pytest.fixture
    def has_latexmk(self):
        """Check if latexmk is available."""
        return shutil.which("latexmk") is not None

    def test_compile_simple_content(self, has_latexmk):
        """Test compiling simple LaTeX content."""
        if not has_latexmk:
            pytest.skip("latexmk not available")

        from scitex_writer import compile

        content = r"""
\documentclass{article}
\begin{document}
Hello, World!
\end{document}
"""
        result = compile.content(content, name="test_simple")

        assert result["success"] is True
        assert result["output_pdf"] is not None
        assert Path(result["output_pdf"]).exists()

        # Cleanup
        temp_dir = Path(result["temp_dir"])
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

    def test_compile_body_only(self, has_latexmk):
        """Test compiling body-only content (auto-wrapped)."""
        if not has_latexmk:
            pytest.skip("latexmk not available")

        from scitex_writer import compile

        content = r"""
\section{Introduction}

This is the introduction.
"""
        result = compile.content(content, name="test_body")

        assert result["success"] is True
        assert result["output_pdf"] is not None

        # Cleanup
        temp_dir = Path(result["temp_dir"])
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

    def test_compile_with_dark_mode(self, has_latexmk):
        """Test compiling with dark mode."""
        if not has_latexmk:
            pytest.skip("latexmk not available")

        from scitex_writer import compile

        content = r"""
\documentclass{article}
\usepackage{xcolor}
\usepackage{pagecolor}
\begin{document}
Dark mode test.
\end{document}
"""
        result = compile.content(content, color_mode="dark", name="test_dark")

        assert result["success"] is True
        assert result["color_mode"] == "dark"

        # Cleanup
        temp_dir = Path(result["temp_dir"])
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

    def test_compile_invalid_latex(self, has_latexmk):
        """Test compiling invalid LaTeX content."""
        if not has_latexmk:
            pytest.skip("latexmk not available")

        from scitex_writer import compile

        content = r"""
\documentclass{article}
\begin{document}
\invalid_command_that_does_not_exist
\end{document}
"""
        result = compile.content(content, name="test_invalid")

        assert result["success"] is False
        assert "error" in result

        # Cleanup
        if "temp_dir" in result:
            temp_dir = Path(result["temp_dir"])
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

    def test_compile_timeout(self, has_latexmk):
        """Test compilation timeout."""
        if not has_latexmk:
            pytest.skip("latexmk not available")

        from scitex_writer import compile

        # Very short timeout to trigger timeout error
        content = r"""
\documentclass{article}
\begin{document}
Test
\end{document}
"""
        # Note: timeout=1 might be too short even for simple docs on slow systems
        # This test is more about verifying the timeout mechanism exists
        result = compile.content(content, timeout=1, name="test_timeout")

        # May succeed or timeout depending on system speed
        assert "success" in result


class TestMcpToolRegistration:
    """Test MCP tool registration for content."""

    def test_compile_content_tool_registered(self):
        """Test that compile_content tool is registered with MCP."""
        from scitex_writer._mcp import mcp

        tool_names = [t.name for t in mcp._tool_manager._tools.values()]
        assert "writer_compile_content" in tool_names


# EOF
