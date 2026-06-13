#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Wave 2 cluster A batch 1 — NM+TQ003+TQ002+TQ007 cleanup.
"""Tests for scitex_writer compile.content functionality."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def scripts_dir():
    """Walk up to the directory containing `pyproject.toml`."""
    p = Path(__file__).resolve()
    for parent in [p, *p.parents]:
        if (parent / "pyproject.toml").is_file():
            return parent / "scripts"
    raise RuntimeError(f"Could not find pyproject.toml from {__file__}")


@pytest.fixture
def has_latexmk():
    """Whether the host has `latexmk` on PATH."""
    return shutil.which("latexmk") is not None


# ============================================================================
# Module-import surface
# ============================================================================


def test_compile_content_is_importable_from_compile_api():
    """`scitex_writer._compile.content.compile_content` is callable."""
    # Arrange
    from scitex_writer._compile.content import compile_content

    # Act
    is_callable = callable(compile_content)
    # Assert
    assert is_callable is True


def test_compile_content_is_importable_from_mcp_wrapper():
    """`scitex_writer._mcp.content.compile_content` is callable."""
    # Arrange
    from scitex_writer._mcp.content import compile_content

    # Act
    is_callable = callable(compile_content)
    # Assert
    assert is_callable is True


def test_compile_content_is_accessible_via_compile_module():
    """`scitex_writer.compile.content` is exposed as a callable attribute."""
    # Arrange
    from scitex_writer import compile

    # Act
    is_callable = callable(compile.content)
    # Assert
    assert is_callable is True


# ============================================================================
# tex_snippet2full.py subprocess driver
# ============================================================================


def test_tex_snippet2full_script_exists_in_scripts_dir(scripts_dir):
    """The `tex_snippet2full.py` builder script ships under `scripts/python/`."""
    # Arrange
    builder = scripts_dir / "python" / "tex_snippet2full.py"
    # Act
    exists = builder.exists()
    # Assert
    assert exists is True


def test_compile_content_shell_script_exists_in_scripts_dir(scripts_dir):
    """The `compile_content.sh` driver script ships under `scripts/shell/`."""
    # Arrange
    compiler = scripts_dir / "shell" / "compile_content.sh"
    # Act
    exists = compiler.exists()
    # Assert
    assert exists is True


def test_tex_snippet2full_light_mode_returns_zero_exit_code(scripts_dir, tmp_path):
    """`tex_snippet2full.py --color-mode light` exits with returncode 0."""
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
    # Assert
    assert result.returncode == 0


def test_tex_snippet2full_light_mode_output_has_documentclass(scripts_dir, tmp_path):
    """Light-mode output wraps the body in a complete document with \\documentclass."""
    # Arrange
    builder = scripts_dir / "python" / "tex_snippet2full.py"
    body_file = tmp_path / "body.tex"
    body_file.write_text(r"\section{Test}" + "\n\nHello World\n")
    output_file = tmp_path / "output.tex"
    subprocess.run(
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
        check=True,
    )
    # Act
    content = output_file.read_text()
    # Assert
    assert "\\documentclass" in content


def test_tex_snippet2full_light_mode_output_has_no_monaco_color(scripts_dir, tmp_path):
    """Light-mode output omits the Monaco dark-theme colours."""
    # Arrange
    builder = scripts_dir / "python" / "tex_snippet2full.py"
    body_file = tmp_path / "body.tex"
    body_file.write_text("Hello\n")
    output_file = tmp_path / "output.tex"
    subprocess.run(
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
        check=True,
    )
    # Act
    content = output_file.read_text()
    # Assert
    assert "MonacoBg" not in content


def test_tex_snippet2full_dark_mode_output_has_monaco_background(scripts_dir, tmp_path):
    """Dark-mode output injects the Monaco background colour command."""
    # Arrange
    builder = scripts_dir / "python" / "tex_snippet2full.py"
    body_file = tmp_path / "body.tex"
    body_file.write_text("Dark mode test content\n")
    output_file = tmp_path / "output.tex"
    subprocess.run(
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
        check=True,
    )
    # Act
    content = output_file.read_text()
    # Assert
    assert "MonacoBg" in content


def test_tex_snippet2full_dark_mode_pagecolor_uses_monaco_bg(scripts_dir, tmp_path):
    """Dark-mode output sets `\\pagecolor{MonacoBg}`."""
    # Arrange
    builder = scripts_dir / "python" / "tex_snippet2full.py"
    body_file = tmp_path / "body.tex"
    body_file.write_text("Dark mode test content\n")
    output_file = tmp_path / "output.tex"
    subprocess.run(
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
        check=True,
    )
    # Act
    content = output_file.read_text()
    # Assert
    assert "\\pagecolor{MonacoBg}" in content


def test_tex_snippet2full_complete_document_injects_after_begin(scripts_dir, tmp_path):
    """In `--complete-document` dark mode, colour commands appear after \\begin{document}."""
    # Arrange
    builder = scripts_dir / "python" / "tex_snippet2full.py"
    body_file = tmp_path / "body.tex"
    body_file.write_text(
        "\\documentclass{article}\n\\begin{document}\nC\n\\end{document}\n"
    )
    output_file = tmp_path / "output.tex"
    subprocess.run(
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
        check=True,
    )
    # Act
    content = output_file.read_text()
    # Assert
    assert content.find("MonacoBg") > content.find("\\begin{document}")


# ============================================================================
# compile.content end-to-end (requires latexmk)
# ============================================================================


def test_compile_content_simple_doc_returns_success_true(has_latexmk):
    """compile.content returns success=True for a minimal valid document."""
    # Arrange
    if not has_latexmk:
        pytest.skip("latexmk not available")
    from scitex_writer import compile

    src = r"\documentclass{article}\begin{document}Hello, World!\end{document}"
    # Act
    result = compile.content(src, name="test_simple")
    try:
        # Assert
        assert result["success"] is True
    finally:
        temp_dir = Path(result.get("temp_dir", ""))
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


def test_compile_content_body_only_returns_success_true(has_latexmk):
    """compile.content auto-wraps a bare body and still returns success=True."""
    # Arrange
    if not has_latexmk:
        pytest.skip("latexmk not available")
    from scitex_writer import compile

    src = r"\section{Introduction}This is the introduction."
    # Act
    result = compile.content(src, name="test_body")
    try:
        # Assert
        assert result["success"] is True
    finally:
        temp_dir = Path(result.get("temp_dir", ""))
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


def test_compile_content_dark_mode_records_color_mode(has_latexmk):
    """compile.content records `color_mode='dark'` in the result dict."""
    # Arrange
    if not has_latexmk:
        pytest.skip("latexmk not available")
    from scitex_writer import compile

    src = (
        r"\documentclass{article}\usepackage{xcolor}\usepackage{pagecolor}"
        r"\begin{document}Dark.\end{document}"
    )
    # Act
    result = compile.content(src, color_mode="dark", name="test_dark")
    try:
        # Assert
        assert result["color_mode"] == "dark"
    finally:
        temp_dir = Path(result.get("temp_dir", ""))
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


def test_compile_content_invalid_latex_returns_success_false(has_latexmk):
    """compile.content returns success=False on invalid LaTeX."""
    # Arrange
    if not has_latexmk:
        pytest.skip("latexmk not available")
    from scitex_writer import compile

    src = (
        r"\documentclass{article}\begin{document}"
        r"\invalid_command_that_does_not_exist\end{document}"
    )
    # Act
    result = compile.content(src, name="test_invalid")
    try:
        # Assert
        assert result["success"] is False
    finally:
        if "temp_dir" in result:
            temp_dir = Path(result["temp_dir"])
            if temp_dir.exists():
                shutil.rmtree(temp_dir)


def test_compile_content_timeout_returns_success_field(has_latexmk):
    """compile.content with a 1-second timeout still returns a `success` key in the result."""
    # Arrange
    if not has_latexmk:
        pytest.skip("latexmk not available")
    from scitex_writer import compile

    src = r"\documentclass{article}\begin{document}Test\end{document}"
    # Act
    result = compile.content(src, timeout=1, name="test_timeout")
    # Assert
    assert "success" in result


# ============================================================================
# MCP tool registration
# ============================================================================


def test_writer_compile_content_tool_is_registered_with_mcp():
    """The MCP tool name `writer_compile_content` is registered on the server."""
    # Arrange
    import asyncio

    from scitex_writer._mcp import mcp

    try:
        tools = asyncio.run(mcp.get_tools())
        tool_names = list(tools.keys())
    except AttributeError:
        tool_names = [t.name for t in asyncio.run(mcp._list_tools())]
    # Act
    has_tool = "writer_compile_content" in tool_names
    # Assert
    assert has_tool is True
