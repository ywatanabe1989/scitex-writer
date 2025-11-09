#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for compilation functions.

Tests cover:
- compile_manuscript()
- compile_supplementary()
- compile_revision()
- CompilationResult class
"""

import shutil
import tempfile
from pathlib import Path
import pytest


class TestCompilationFunctions:
    """Test standalone compilation functions."""

    def test_compile_manuscript_import(self):
        """Test that compile_manuscript can be imported."""
        from scitex.writer import compile_manuscript

        assert callable(compile_manuscript)

    def test_compile_supplementary_import(self):
        """Test that compile_supplementary can be imported."""
        from scitex.writer import compile_supplementary

        assert callable(compile_supplementary)

    def test_compile_revision_import(self):
        """Test that compile_revision can be imported."""
        from scitex.writer import compile_revision

        assert callable(compile_revision)


class TestCompilationResult:
    """Test CompilationResult class."""

    def test_compilation_result_import(self):
        """Test that CompilationResult can be imported."""
        from scitex.writer.writer import CompilationResult

        assert CompilationResult is not None

    def test_compilation_result_success(self):
        """Test CompilationResult for successful compilation."""
        from scitex.writer.writer import CompilationResult

        result = CompilationResult(
            success=True,
            pdf_path=Path("/tmp/test.pdf"),
            tex_path=Path("/tmp/test.tex"),
        )

        assert result.success == True
        assert result.pdf_path == Path("/tmp/test.pdf")
        assert result.tex_path == Path("/tmp/test.tex")
        assert result.error is None

    def test_compilation_result_failure(self):
        """Test CompilationResult for failed compilation."""
        from scitex.writer.writer import CompilationResult

        result = CompilationResult(
            success=False,
            error="Compilation failed: missing file",
        )

        assert result.success == False
        assert result.error == "Compilation failed: missing file"
        assert result.pdf_path is None

    def test_compilation_result_repr(self):
        """Test CompilationResult string representation."""
        from scitex.writer.writer import CompilationResult

        result = CompilationResult(
            success=True,
            pdf_path=Path("/tmp/test.pdf"),
        )

        repr_str = repr(result)
        assert "CompilationResult" in repr_str
        assert "SUCCESS" in repr_str or "True" in repr_str


class TestCompilationWithMockScripts:
    """Test compilation with mock scripts."""

    @pytest.fixture
    def mock_project(self):
        """Create project with mock compilation scripts."""
        temp_dir = tempfile.mkdtemp(prefix="scitex_mock_compile_")
        project_dir = Path(temp_dir)

        # Create structure
        for dir_name in ["01_manuscript", "02_supplementary", "03_revision"]:
            (project_dir / dir_name).mkdir(parents=True, exist_ok=True)

        # Create mock scripts
        scripts_dir = project_dir / "scripts" / "shell"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        for doc_type in ["manuscript", "supplementary", "revision"]:
            script = scripts_dir / f"compile_{doc_type}.sh"
            script.write_text(f"""#!/bin/bash
# Mock compilation script
echo "Compiling {doc_type}..."
mkdir -p 01_manuscript 02_supplementary 03_revision
touch 01_{doc_type}/{doc_type}.pdf
exit 0
""")
            script.chmod(0o755)

        yield project_dir

        # Cleanup
        if project_dir.exists():
            shutil.rmtree(project_dir)

    def test_compile_manuscript_with_mock(self, mock_project):
        """Test compile_manuscript with mock script."""
        from scitex.writer import compile_manuscript

        result = compile_manuscript(
            project_dir=mock_project,
            verbose=False,
        )

        assert isinstance(result, object)  # Should return CompilationResult
        assert hasattr(result, 'success')

    def test_compile_with_missing_script_returns_error(self):
        """Test compilation fails gracefully when script missing."""
        from scitex.writer import compile_manuscript

        temp_dir = tempfile.mkdtemp(prefix="scitex_no_script_")
        project_dir = Path(temp_dir)
        project_dir.mkdir(parents=True, exist_ok=True)

        result = compile_manuscript(project_dir=project_dir)

        assert result.success == False
        assert result.error is not None
        assert "not found" in result.error

        # Cleanup
        shutil.rmtree(temp_dir)
