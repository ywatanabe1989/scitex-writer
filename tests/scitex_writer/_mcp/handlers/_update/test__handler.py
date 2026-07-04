"""Smoke test: `scitex_writer._mcp.handlers._update._handler` imports cleanly."""

import importlib

from scitex_writer._mcp.handlers._update._handler import (
    _restamp_version_tex,
    _write_vendor_stamp,
)


def test_module_exposes_collect_sync_files():
    # Arrange
    # Act
    module = importlib.import_module("scitex_writer._mcp.handlers._update._handler")
    # Assert
    assert hasattr(module, "collect_sync_files")


def test_write_vendor_stamp_first_line_is_version(tmp_path):
    # Arrange
    (tmp_path / "00_shared").mkdir()
    # Act
    _write_vendor_stamp(tmp_path, "2.24.0")
    # Assert
    stamp = tmp_path / "00_shared" / ".scitex-writer-vendored-version"
    assert stamp.read_text().splitlines()[0] == "2.24.0"


def test_restamp_version_tex_sets_colophon_version(tmp_path):
    # Arrange
    (tmp_path / "00_shared").mkdir()
    # Act
    _restamp_version_tex(tmp_path, "2.24.0")
    # Assert
    text = (tmp_path / "00_shared" / "scitex_writer_version.tex").read_text()
    assert "\\def\\ScitexWriterVersion{2.24.0}" in text


def test_restamp_version_tex_noop_without_00shared(tmp_path):
    # Arrange
    target = tmp_path / "00_shared" / "scitex_writer_version.tex"
    # Act
    _restamp_version_tex(tmp_path, "2.24.0")
    # Assert
    assert not target.exists()
