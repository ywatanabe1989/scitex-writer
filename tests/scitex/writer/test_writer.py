#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for Writer class.

Tests cover:
- Writer initialization
- Project directory validation
- Compilation interface
"""

import shutil
import tempfile
from pathlib import Path
import pytest


class TestWriterInitialization:
    """Test Writer class initialization."""

    @pytest.fixture
    def temp_project_dir(self):
        """Create temporary project directory with required structure."""
        temp_dir = tempfile.mkdtemp(prefix="scitex_writer_test_")
        project_dir = Path(temp_dir)

        # Create minimal required structure
        for dir_name in ["01_manuscript", "02_supplementary", "03_revision"]:
            (project_dir / dir_name).mkdir(parents=True, exist_ok=True)

        # Create scripts directory
        scripts_dir = project_dir / "scripts" / "shell"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        yield project_dir

        # Cleanup
        if project_dir.exists():
            shutil.rmtree(project_dir)

    def test_writer_initialization_with_valid_project(self, temp_project_dir):
        """Test Writer initializes with valid project directory."""
        from scitex.writer import Writer

        writer = Writer(temp_project_dir)

        assert writer.project_dir == temp_project_dir
        assert writer.doc_type == "manuscript"  # default

    def test_writer_initialization_with_doc_type(self, temp_project_dir):
        """Test Writer respects doc_type parameter."""
        from scitex.writer import Writer

        for doc_type in ["manuscript", "supplementary", "revision"]:
            writer = Writer(temp_project_dir, doc_type=doc_type)
            assert writer.doc_type == doc_type

    def test_writer_initialization_nonexistent_directory(self):
        """Test Writer raises error for nonexistent directory."""
        from scitex.writer import Writer

        nonexistent = Path("/tmp/nonexistent_scitex_project_12345")
        assert not nonexistent.exists()

        with pytest.raises(ValueError) as exc_info:
            Writer(nonexistent)

        assert "does not exist" in str(exc_info.value)

    def test_writer_project_dir_resolution(self, temp_project_dir):
        """Test that project_dir is resolved to absolute path."""
        from scitex.writer import Writer

        # Create Writer with relative path
        writer = Writer(temp_project_dir)

        # Should be absolute
        assert writer.project_dir.is_absolute()
        assert writer.project_dir == temp_project_dir.resolve()


class TestWriterAttributes:
    """Test Writer class attributes."""

    @pytest.fixture
    def writer(self):
        """Create Writer instance with temporary project."""
        temp_dir = tempfile.mkdtemp(prefix="scitex_writer_attr_")
        project_dir = Path(temp_dir)

        # Create structure
        for dir_name in ["01_manuscript", "02_supplementary", "03_revision"]:
            (project_dir / dir_name).mkdir(parents=True, exist_ok=True)

        scripts_dir = project_dir / "scripts" / "shell"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        from scitex.writer import Writer
        writer = Writer(project_dir)

        yield writer

        # Cleanup
        if project_dir.exists():
            shutil.rmtree(project_dir)

    def test_writer_has_project_dir(self, writer):
        """Test Writer has project_dir attribute."""
        assert hasattr(writer, 'project_dir')
        assert isinstance(writer.project_dir, Path)

    def test_writer_has_doc_type(self, writer):
        """Test Writer has doc_type attribute."""
        assert hasattr(writer, 'doc_type')
        assert writer.doc_type in ["manuscript", "supplementary", "revision"]

    def test_writer_has_scripts_dir(self, writer):
        """Test Writer has scripts_dir attribute."""
        assert hasattr(writer, 'scripts_dir')
        assert isinstance(writer.scripts_dir, Path)
        assert writer.scripts_dir.name == "shell"


class TestWriterCompileMethod:
    """Test Writer.compile() method."""

    @pytest.fixture
    def writer_with_scripts(self):
        """Create Writer with mock compilation scripts."""
        temp_dir = tempfile.mkdtemp(prefix="scitex_compile_test_")
        project_dir = Path(temp_dir)

        # Create structure
        for dir_name in ["01_manuscript", "02_supplementary", "03_revision"]:
            (project_dir / dir_name).mkdir(parents=True, exist_ok=True)

        # Create mock compile script
        scripts_dir = project_dir / "scripts" / "shell"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        compile_script = scripts_dir / "compile_manuscript.sh"
        compile_script.write_text("""#!/bin/bash
echo "Mock compilation successful"
exit 0
""")
        compile_script.chmod(0o755)

        from scitex.writer import Writer
        writer = Writer(project_dir)

        yield writer

        # Cleanup
        if project_dir.exists():
            shutil.rmtree(project_dir)

    def test_compile_method_exists(self, writer_with_scripts):
        """Test that Writer has compile method."""
        assert hasattr(writer_with_scripts, 'compile')
        assert callable(writer_with_scripts.compile)

    def test_compile_returns_compilation_result(self, writer_with_scripts):
        """Test that compile returns CompilationResult object."""
        from scitex.writer.writer import CompilationResult

        result = writer_with_scripts.compile()

        assert isinstance(result, CompilationResult)
        assert hasattr(result, 'success')
        assert hasattr(result, 'pdf_path')
        assert hasattr(result, 'error')
