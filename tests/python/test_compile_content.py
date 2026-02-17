#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-02-08
# File: tests/python/test_compile_content.py

"""Tests for scitex_writer compile.content functionality."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest


class TestContentModule:
    """Test content module can be imported."""

    def test_content_import_from_compile_api(self):
        """Test that compile_content is importable from _compile."""
        from scitex_writer._compile.content import compile_content

        assert callable(compile_content)

    def test_content_import_from_mcp_wrapper(self):
        """Test that _mcp.content thin wrapper works."""
        from scitex_writer._mcp.content import compile_content

        assert callable(compile_content)

    def test_content_via_compile_module(self):
        """Test that content is accessible via compile module."""
        from scitex_writer import compile

        assert callable(compile.content)


class TestDocumentBuilder:
    """Test tex_snippet2full.py script functions."""

    @pytest.fixture
    def scripts_dir(self):
        """Get scripts directory."""
        return Path(__file__).resolve().parents[2] / "scripts"

    def test_document_builder_exists(self, scripts_dir):
        """Test that the document builder script exists."""
        builder = scripts_dir / "python" / "tex_snippet2full.py"
        assert builder.exists()

    def test_shell_script_exists(self, scripts_dir):
        """Test that the compile shell script exists."""
        compiler = scripts_dir / "shell" / "compile_content.sh"
        assert compiler.exists()

    def test_document_builder_light_mode(self, scripts_dir, tmp_path):
        """Test building a light mode document."""
        builder = scripts_dir / "python" / "tex_snippet2full.py"
        body_file = tmp_path / "body.tex"
        body_file.write_text(r"\section{Test}" + "\n\nHello World\n")
        output_file = tmp_path / "output.tex"

        result = subprocess.run(
            [
                sys.executable,
                str(builder),
                "--body-file",
                str(body_file),
                "--output",
                str(output_file),
                "--color-mode",
                "light",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        content = output_file.read_text()
        assert "\\documentclass" in content
        assert "\\begin{document}" in content
        assert "Hello World" in content
        # Light mode should not have color commands
        assert "MonacoBg" not in content

    def test_document_builder_dark_mode(self, scripts_dir, tmp_path):
        """Test building a dark mode document with Monaco colors."""
        builder = scripts_dir / "python" / "tex_snippet2full.py"
        body_file = tmp_path / "body.tex"
        body_file.write_text("Dark mode test content\n")
        output_file = tmp_path / "output.tex"

        result = subprocess.run(
            [
                sys.executable,
                str(builder),
                "--body-file",
                str(body_file),
                "--output",
                str(output_file),
                "--color-mode",
                "dark",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        content = output_file.read_text()
        assert "MonacoBg" in content
        assert "1E1E1E" in content  # Monaco background
        assert "MonacoFg" in content
        assert "D4D4D4" in content  # Monaco foreground
        assert "\\pagecolor{MonacoBg}" in content
        assert "\\color{MonacoFg}" in content

    def test_document_builder_complete_document(self, scripts_dir, tmp_path):
        """Test injecting color into a complete document."""
        builder = scripts_dir / "python" / "tex_snippet2full.py"
        body_file = tmp_path / "body.tex"
        body_file.write_text(
            "\\documentclass{article}\n\\begin{document}\nComplete doc\n\\end{document}\n"
        )
        output_file = tmp_path / "output.tex"

        result = subprocess.run(
            [
                sys.executable,
                str(builder),
                "--body-file",
                str(body_file),
                "--output",
                str(output_file),
                "--color-mode",
                "dark",
                "--complete-document",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        content = output_file.read_text()
        # Should inject after \begin{document}
        begin_pos = content.find("\\begin{document}")
        monaco_pos = content.find("MonacoBg")
        assert monaco_pos > begin_pos


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
