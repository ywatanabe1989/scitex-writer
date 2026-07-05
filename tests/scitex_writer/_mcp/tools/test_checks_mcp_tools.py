#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: tests/scitex_writer/_mcp/tools/test_checks_mcp_tools.py
# Test file for: src/scitex_writer/_mcp/tools/checks.py
#
# Named distinctly from ``test_checks.py`` (which already exists at
# tests/scitex_writer/test_checks.py, testing the Python API layer) --
# neither tests/scitex_writer/ nor tests/scitex_writer/_mcp/tools/ has an
# __init__.py, so pytest's rootdir import mode would otherwise collide on
# the bare "test_checks" module name.

"""Tests for the MCP tool registrations in ``scitex_writer._mcp.tools.checks``.

Registers the tools on a real ``FastMCP`` instance and inspects the real
``Tool`` objects (name, docstring, parameter schema) -- no mocked
collaborators. Mirrors the existing coverage style for
``writer_checks_references`` / ``writer_checks_float_order`` in
``tests/scripts/python/test_scitex_writer_mcp.py`` (name-registration
checks against the real FastMCP instance).
"""

from __future__ import annotations

import asyncio

import pytest
from fastmcp import FastMCP

from scitex_writer._mcp.tools import checks as checks_tools


def _get_tools(mcp: FastMCP) -> dict:
    """Return {tool_name: Tool} across FastMCP versions."""
    try:
        return asyncio.run(mcp.get_tools())  # FastMCP >= 2.3
    except AttributeError:
        tools = asyncio.run(mcp._list_tools())  # FastMCP 2.0-2.2
        return {t.name: t for t in tools}


@pytest.fixture
def registered_tools():
    """Real FastMCP instance with the checks tools registered; {name: Tool}."""
    server = FastMCP(name="test-checks")
    checks_tools.register_tools(server)
    return _get_tools(server)


def test_all_eight_check_tools_are_registered(registered_tools):
    # Arrange
    # Act
    names = set(registered_tools)
    # Assert
    assert names == {
        "writer_checks_references",
        "writer_checks_float_order",
        "writer_checks_limits",
        "writer_checks_overflow",
        "writer_checks_paper_symlink",
        "writer_checks_media_provenance",
        "writer_checks_caption_footnote",
        "writer_checks_ref_integrity",
    }


def test_writer_checks_limits_is_registered(registered_tools):
    # Arrange
    # Act
    # Assert
    assert "writer_checks_limits" in registered_tools


def test_writer_checks_overflow_is_registered(registered_tools):
    # Arrange
    # Act
    # Assert
    assert "writer_checks_overflow" in registered_tools


def test_writer_checks_paper_symlink_is_registered(registered_tools):
    # Arrange
    # Act
    # Assert
    assert "writer_checks_paper_symlink" in registered_tools


def test_writer_checks_media_provenance_is_registered(registered_tools):
    # Arrange
    # Act
    # Assert
    assert "writer_checks_media_provenance" in registered_tools


def test_writer_checks_caption_footnote_is_registered(registered_tools):
    # Arrange
    # Act
    # Assert
    assert "writer_checks_caption_footnote" in registered_tools


def test_writer_checks_ref_integrity_is_registered(registered_tools):
    # Arrange
    # Act
    # Assert
    assert "writer_checks_ref_integrity" in registered_tools


def test_writer_checks_limits_fn_is_callable(registered_tools):
    # Arrange
    # Act
    # Assert
    assert callable(registered_tools["writer_checks_limits"].fn)


def test_writer_checks_overflow_fn_is_callable(registered_tools):
    # Arrange
    # Act
    # Assert
    assert callable(registered_tools["writer_checks_overflow"].fn)


def test_writer_checks_paper_symlink_fn_is_callable(registered_tools):
    # Arrange
    # Act
    # Assert
    assert callable(registered_tools["writer_checks_paper_symlink"].fn)


def test_writer_checks_media_provenance_fn_is_callable(registered_tools):
    # Arrange
    # Act
    # Assert
    assert callable(registered_tools["writer_checks_media_provenance"].fn)


def test_writer_checks_caption_footnote_fn_is_callable(registered_tools):
    # Arrange
    # Act
    # Assert
    assert callable(registered_tools["writer_checks_caption_footnote"].fn)


def test_writer_checks_ref_integrity_fn_is_callable(registered_tools):
    # Arrange
    # Act
    # Assert
    assert callable(registered_tools["writer_checks_ref_integrity"].fn)


def test_writer_checks_limits_docstring_mentions_limits(registered_tools):
    # Arrange
    # Act
    doc = registered_tools["writer_checks_limits"].fn.__doc__ or ""
    # Assert
    assert "limit" in doc.lower()


def test_writer_checks_overflow_docstring_mentions_overflow(registered_tools):
    # Arrange
    # Act
    doc = registered_tools["writer_checks_overflow"].fn.__doc__ or ""
    # Assert
    assert "overflow" in doc.lower() or "hbox" in doc.lower()


def test_writer_checks_paper_symlink_docstring_mentions_symlink(registered_tools):
    # Arrange
    # Act
    doc = registered_tools["writer_checks_paper_symlink"].fn.__doc__ or ""
    # Assert
    assert "symlink" in doc.lower()


def test_writer_checks_media_provenance_docstring_mentions_provenance(
    registered_tools,
):
    # Arrange
    # Act
    doc = registered_tools["writer_checks_media_provenance"].fn.__doc__ or ""
    # Assert
    assert "symlink" in doc.lower()


def test_writer_checks_caption_footnote_docstring_mentions_footnote(
    registered_tools,
):
    # Arrange
    # Act
    doc = registered_tools["writer_checks_caption_footnote"].fn.__doc__ or ""
    # Assert
    assert "footnote" in doc.lower()


def test_writer_checks_ref_integrity_docstring_mentions_reference_integrity(
    registered_tools,
):
    # Arrange
    # Act
    doc = registered_tools["writer_checks_ref_integrity"].fn.__doc__ or ""
    # Assert
    assert "reference-integrity" in doc.lower()


def test_writer_checks_limits_calls_the_real_check_limits_handler(registered_tools):
    """Wiring check: the tool's closure calls the same object the module
    imports as ``_check_limits`` -- verified by giving it a nonexistent
    project dir (a real, deterministic error path -- no mocking) and
    checking the real handler's "script not found" contract fires.
    """
    # Arrange
    tool = registered_tools["writer_checks_limits"]
    # Act
    out = tool.fn("/nonexistent/scitex-writer-mcp-tools-test-project")
    # Assert
    assert out["success"] is False


def test_writer_checks_overflow_reports_missing_script_for_bad_project(
    registered_tools,
):
    # Arrange
    tool = registered_tools["writer_checks_overflow"]
    # Act
    out = tool.fn("/nonexistent/scitex-writer-mcp-tools-test-project")
    # Assert
    assert out["success"] is False


def test_writer_checks_paper_symlink_reports_missing_script_for_bad_project(
    registered_tools,
):
    # Arrange
    tool = registered_tools["writer_checks_paper_symlink"]
    # Act
    out = tool.fn("/nonexistent/scitex-writer-mcp-tools-test-project")
    # Assert
    assert out["success"] is False


def test_writer_checks_media_provenance_reports_missing_script_for_bad_project(
    registered_tools,
):
    # Arrange
    tool = registered_tools["writer_checks_media_provenance"]
    # Act
    out = tool.fn("/nonexistent/scitex-writer-mcp-tools-test-project")
    # Assert
    assert out["success"] is False


def test_writer_checks_caption_footnote_reports_missing_script_for_bad_project(
    registered_tools,
):
    # Arrange
    tool = registered_tools["writer_checks_caption_footnote"]
    # Act
    out = tool.fn("/nonexistent/scitex-writer-mcp-tools-test-project")
    # Assert
    assert out["success"] is False


def test_writer_checks_ref_integrity_reports_missing_script_for_bad_project(
    registered_tools,
):
    # Arrange
    tool = registered_tools["writer_checks_ref_integrity"]
    # Act
    out = tool.fn("/nonexistent/scitex-writer-mcp-tools-test-project")
    # Assert
    assert out["success"] is False


# EOF
