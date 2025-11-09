#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pytest configuration and shared fixtures for scitex-writer tests.

Provides:
- Common fixtures for project directories
- Test utilities
- Shared test data
"""

import shutil
import tempfile
from pathlib import Path
import pytest


@pytest.fixture
def project_root():
    """Get project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def temp_project_dir():
    """
    Create temporary project directory with minimal structure.

    Yields clean directory, cleans up after test.
    """
    temp_dir = tempfile.mkdtemp(prefix="scitex_test_")
    project_dir = Path(temp_dir)

    # Create minimal required structure
    for dir_name in ["01_manuscript", "02_supplementary", "03_revision"]:
        (project_dir / dir_name).mkdir(parents=True, exist_ok=True)

    scripts_dir = project_dir / "scripts" / "shell"
    scripts_dir.mkdir(parents=True, exist_ok=True)

    yield project_dir

    # Cleanup
    if project_dir.exists():
        shutil.rmtree(project_dir)


@pytest.fixture
def mock_compilation_scripts(temp_project_dir):
    """
    Create mock compilation scripts that succeed.

    Returns project directory with working mock scripts.
    """
    scripts_dir = temp_project_dir / "scripts" / "shell"

    for doc_type in ["manuscript", "supplementary", "revision"]:
        script = scripts_dir / f"compile_{doc_type}.sh"
        doc_num = {"manuscript": "01", "supplementary": "02", "revision": "03"}[doc_type]

        script.write_text(f"""#!/bin/bash
# Mock compilation script for {doc_type}
mkdir -p {doc_num}_{doc_type}
touch {doc_num}_{doc_type}/{doc_type}.pdf
touch {doc_num}_{doc_type}/{doc_type}_compiled.tex
echo "Mock compilation successful"
exit 0
""")
        script.chmod(0o755)

    return temp_project_dir


@pytest.fixture
def project_with_pyproject(temp_project_dir):
    """Create project with pyproject.toml."""
    pyproject = temp_project_dir / "pyproject.toml"
    pyproject.write_text("""[project]
name = "test-project"
version = "0.1.0"
""")

    return temp_project_dir


# Markers for test categorization
def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, isolated)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (slower, use real files)"
    )
    config.addinivalue_line(
        "markers", "slow: Slow tests (can be skipped for quick runs)"
    )
    config.addinivalue_line(
        "markers", "requires_latex: Tests requiring LaTeX installation"
    )
    config.addinivalue_line(
        "markers", "requires_containers: Tests requiring Apptainer/Singularity"
    )
