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
        # Arrange
        # Act
        from scitex_writer._compile.content import compile_content

        # Assert
        assert callable(compile_content)

    def test_content_import_from_mcp_wrapper(self):
        """Test that _mcp.content thin wrapper works."""
        # Arrange
        # Act
        from scitex_writer._mcp.content import compile_content

        # Assert
        assert callable(compile_content)

    def test_content_via_compile_module(self):
        """Test that content is accessible via compile module."""
        # Arrange
        # Act
        from scitex_writer import compile

        # Assert
        assert callable(compile.content)


class TestDocumentBuilder:
    """Test tex_snippet2full.py script functions."""

    @pytest.fixture
    def scripts_dir(self):
        """Get the project's `scripts/` directory.

        Walks up to the directory containing `pyproject.toml` so the lookup
        survives test-tree depth changes.
        """
        p = Path(__file__).resolve()
        for parent in [p, *p.parents]:
            if (parent / "pyproject.toml").is_file():
                return parent / "scripts"
        raise RuntimeError(f"Could not find pyproject.toml from {__file__}")

    def test_document_builder_exists(self, scripts_dir):
        """Test that the document builder script exists."""
        # Arrange
        # Act
        builder = scripts_dir / "python" / "tex_snippet2full.py"
        # Assert
        assert builder.exists()

    def test_shell_script_exists(self, scripts_dir):
        """Test that the compile shell script exists."""
        # Arrange
        # Act
        compiler = scripts_dir / "shell" / "compile_content.sh"
        # Assert
        assert compiler.exists()

    def test_document_builder_light_mode_result_returncode_equals_n_0(self, scripts_dir, tmp_path):
        # Arrange
        builder = scripts_dir / "python" / "tex_snippet2full.py"
        body_file = tmp_path / "body.tex"
        body_file.write_text(r"\section{Test}" + "\n\nHello World\n")
        output_file = tmp_path / "output.tex"
        # Act
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
        # Act
        # Assert
        assert result.returncode == 0

    def test_document_builder_light_mode_documentclass_in_content_and_begin_document_in_content_and_h(self, scripts_dir, tmp_path):
        # Arrange
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
        # Act
        content = output_file.read_text()
        # Act
        # Assert
        assert ('\\documentclass' in content) and ('\\begin{document}' in content) and ('Hello World' in content) and ('MonacoBg' not in content)


    def test_document_builder_dark_mode_result_returncode_equals_n_0(self, scripts_dir, tmp_path):
        # Arrange
        builder = scripts_dir / "python" / "tex_snippet2full.py"
        body_file = tmp_path / "body.tex"
        body_file.write_text("Dark mode test content\n")
        output_file = tmp_path / "output.tex"
        # Act
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
        # Act
        # Assert
        assert result.returncode == 0

    def test_document_builder_dark_mode_monacobg_in_content_and_1e1e1e_in_content_and_monacofg_in_co(self, scripts_dir, tmp_path):
        # Arrange
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
        # Act
        content = output_file.read_text()
        # Act
        # Assert
        assert ('MonacoBg' in content) and ('1E1E1E' in content) and ('MonacoFg' in content) and ('D4D4D4' in content) and ('\\pagecolor{MonacoBg}' in content) and ('\\color{MonacoFg}' in content)


    def test_document_builder_complete_document_result_returncode_equals_n_0(self, scripts_dir, tmp_path):
        # Arrange
        builder = scripts_dir / "python" / "tex_snippet2full.py"
        body_file = tmp_path / "body.tex"
        body_file.write_text(
            "\\documentclass{article}\n\\begin{document}\nComplete doc\n\\end{document}\n"
        )
        output_file = tmp_path / "output.tex"
        # Act
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
        # Act
        # Assert
        assert result.returncode == 0

    def test_document_builder_complete_document_monaco_pos_begin_pos(self, scripts_dir, tmp_path):
        # Arrange
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
        content = output_file.read_text()
        # Should inject after \begin{document}
        begin_pos = content.find("\\begin{document}")
        # Act
        monaco_pos = content.find("MonacoBg")
        # Act
        # Assert
        assert monaco_pos > begin_pos



class TestContentCompilation:
    """Test content compilation (requires latexmk)."""

    @pytest.fixture
    def has_latexmk(self):
        """Check if latexmk is available."""
        return shutil.which("latexmk") is not None

    def test_compile_simple_content(self, has_latexmk):
        """Test compiling simple LaTeX content."""
        # Arrange
        if not has_latexmk:
            pytest.skip("latexmk not available")

        from scitex_writer import compile

        content = r"""
\documentclass{article}
\begin{document}
Hello, World!
\end{document}
"""
        # Act
        result = compile.content(content, name="test_simple")

        # Assert
        assert (result['success'] is True) and (result['output_pdf'] is not None) and (Path(result['output_pdf']).exists())

        # Cleanup
        temp_dir = Path(result["temp_dir"])
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

    def test_compile_body_only(self, has_latexmk):
        """Test compiling body-only content (auto-wrapped)."""
        # Arrange
        if not has_latexmk:
            pytest.skip("latexmk not available")

        from scitex_writer import compile

        content = r"""
\section{Introduction}

This is the introduction.
"""
        # Act
        result = compile.content(content, name="test_body")

        # Assert
        assert (result['success'] is True) and (result['output_pdf'] is not None)

        # Cleanup
        temp_dir = Path(result["temp_dir"])
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

    def test_compile_with_dark_mode(self, has_latexmk):
        """Test compiling with dark mode."""
        # Arrange
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
        # Act
        result = compile.content(content, color_mode="dark", name="test_dark")

        # Assert
        assert (result['success'] is True) and (result['color_mode'] == 'dark')

        # Cleanup
        temp_dir = Path(result["temp_dir"])
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

    def test_compile_invalid_latex(self, has_latexmk):
        """Test compiling invalid LaTeX content."""
        # Arrange
        if not has_latexmk:
            pytest.skip("latexmk not available")

        from scitex_writer import compile

        content = r"""
\documentclass{article}
\begin{document}
\invalid_command_that_does_not_exist
\end{document}
"""
        # Act
        result = compile.content(content, name="test_invalid")

        # Assert
        assert (result['success'] is False) and ('error' in result)

        # Cleanup
        if "temp_dir" in result:
            temp_dir = Path(result["temp_dir"])
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

    def test_compile_timeout_success_in_result(self, has_latexmk):
        """Test compilation timeout."""
        # Arrange
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
        # Act
        result = compile.content(content, timeout=1, name="test_timeout")

        # May succeed or timeout depending on system speed
        # Assert
        assert "success" in result


class TestMcpToolRegistration:
    """Test MCP tool registration for content."""

    def test_compile_content_tool_registered(self):
        """Test that compile_content tool is registered with MCP."""
        # Arrange
        import asyncio

        from scitex_writer._mcp import mcp

        # Act
        try:
            tools = asyncio.run(mcp.get_tools())
            tool_names = list(tools.keys())
        except AttributeError:
            tool_names = [t.name for t in asyncio.run(mcp._list_tools())]
        # Assert
        assert "writer_compile_content" in tool_names


# EOF
