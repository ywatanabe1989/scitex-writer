#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration tests for scitex-writer.

Tests full workflows with real file operations.
"""

import shutil
import tempfile
from pathlib import Path
import subprocess
import pytest


class TestEndToEndWorkflow:
    """Test complete workflow from project creation to compilation."""

    @pytest.fixture
    def clean_temp_dir(self):
        """Create clean temporary directory."""
        temp_dir = tempfile.mkdtemp(prefix="scitex_e2e_")
        yield Path(temp_dir)

        # Cleanup
        if Path(temp_dir).exists():
            shutil.rmtree(temp_dir)

    def test_import_all_main_interfaces(self):
        """Test that all main interfaces can be imported."""
        try:
            from scitex.writer import Writer
            from scitex.writer import __version__
            from scitex.writer import clone_writer_project
            from scitex.writer import compile_manuscript
            from scitex.writer import compile_supplementary
            from scitex.writer import compile_revision

            assert Writer is not None
            assert __version__ is not None
            assert clone_writer_project is not None
            assert compile_manuscript is not None
            assert compile_supplementary is not None
            assert compile_revision is not None

        except ImportError as e:
            pytest.fail(f"Failed to import main interfaces: {e}")

    def test_writer_class_instantiation(self):
        """Test Writer class can be instantiated."""
        temp_dir = tempfile.mkdtemp(prefix="scitex_instantiate_")
        project_dir = Path(temp_dir)

        try:
            # Create minimal structure
            for dir_name in ["01_manuscript", "02_supplementary", "03_revision"]:
                (project_dir / dir_name).mkdir(parents=True, exist_ok=True)

            scripts_dir = project_dir / "scripts" / "shell"
            scripts_dir.mkdir(parents=True, exist_ok=True)

            from scitex.writer import Writer

            writer = Writer(project_dir)
            assert writer is not None
            assert writer.project_dir == project_dir

        finally:
            if project_dir.exists():
                shutil.rmtree(temp_dir)


class TestVersionConsistency:
    """Test version consistency across interfaces."""

    def test_python_shell_version_match(self):
        """Test Python and shell versions are identical."""
        from scitex.writer import __version__

        project_root = Path(__file__).parent.parent.parent.parent

        # Get shell version
        result = subprocess.run(
            ["bash", "-c",
             "source config/load_config.sh manuscript 2>&1; echo $SCITEX_WRITER_VERSION"],
            capture_output=True,
            text=True,
            cwd=project_root,
        )

        shell_version = result.stdout.strip().split('\n')[-1]

        assert __version__ == shell_version, \
            f"Version mismatch: Python={__version__}, Shell={shell_version}"

    def test_makefile_version_matches(self):
        """Test Makefile version extraction matches Python."""
        from scitex.writer import __version__

        project_root = Path(__file__).parent.parent.parent.parent

        result = subprocess.run(
            ["make", "version"],
            capture_output=True,
            text=True,
            cwd=project_root,
        )

        # Extract version from output like "SciTeX Writer 2.0.0a0"
        version_line = result.stdout.strip()
        if "SciTeX Writer" in version_line:
            makefile_version = version_line.split()[-1]
            assert __version__ == makefile_version, \
                f"Makefile version mismatch: Python={__version__}, Make={makefile_version}"


class TestProjectStructureValidation:
    """Test project structure validation."""

    def test_required_directories_exist_in_repo(self):
        """Test that repository has required directory structure."""
        project_root = Path(__file__).parent.parent.parent.parent

        required_dirs = [
            "01_manuscript",
            "02_supplementary",
            "03_revision",
            "00_shared",
            "config",
            "scripts/shell",
            "src/scitex/writer",
        ]

        for dir_path in required_dirs:
            full_path = project_root / dir_path
            assert full_path.exists(), f"Required directory missing: {dir_path}"
            assert full_path.is_dir(), f"Not a directory: {dir_path}"

    def test_required_files_exist_in_repo(self):
        """Test that repository has required files."""
        project_root = Path(__file__).parent.parent.parent.parent

        required_files = [
            "pyproject.toml",
            "Makefile",
            "README.md",
            "compile.sh",
            "config/load_config.sh",
            "scripts/update.sh",
        ]

        for file_path in required_files:
            full_path = project_root / file_path
            assert full_path.exists(), f"Required file missing: {file_path}"
            assert full_path.is_file(), f"Not a file: {file_path}"
