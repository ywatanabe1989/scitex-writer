#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: tests/scitex_writer/_mcp/handlers/test__citation_style.py

"""Tests for the citation-style handler (pure-Python apply_citation_style)."""

import os

import pytest

from scitex_writer._mcp.handlers import _citation_style

_BIB = (
    "%% BIBLIOGRAPHY STYLE\n"
    "%% OPTION 1\n"
    "\\bibliographystyle{unsrtnat}\n"
    "%% OPTION 2\n"
    "% \\bibliographystyle{apalike}\n"
)


def _make_bib(tmp_path):
    d = tmp_path / "00_shared" / "latex_styles"
    d.mkdir(parents=True)
    bib = d / "bibliography.tex"
    bib.write_text(_BIB, encoding="utf-8")
    return bib


@pytest.fixture
def _clear_style_env():
    old = os.environ.pop("SCITEX_WRITER_CITATION_STYLE", None)
    yield
    if old is not None:
        os.environ["SCITEX_WRITER_CITATION_STYLE"] = old


class TestApplyCitationStyleGuards:
    def test_invalid_doc_type_returns_error(self):
        # Arrange
        bad = "poster"
        # Act
        result = _citation_style.apply(".", bad, "nature")
        # Assert
        assert result["success"] is False and "poster" in result["error"]

    def test_missing_bib_file_returns_error(self, tmp_path):
        # Arrange
        project = tmp_path
        # Act
        result = _citation_style.apply(str(project), "manuscript", "nature")
        # Assert
        assert result["success"] is False and "not found" in result["error"]

    def test_no_style_configured_is_noop(self, tmp_path, _clear_style_env):
        # Arrange
        _make_bib(tmp_path)
        # Act
        result = _citation_style.apply(str(tmp_path), "manuscript", None)
        # Assert
        assert result["success"] is True and result["changed"] is False


class TestApplyCitationStyleChanges:
    def test_already_active_style_is_noop(self, tmp_path):
        # Arrange
        _make_bib(tmp_path)
        # Act
        result = _citation_style.apply(str(tmp_path), "manuscript", "unsrtnat")
        # Assert
        assert result["changed"] is False and result["current_style"] == "unsrtnat"

    def test_commented_target_is_uncommented(self, tmp_path):
        # Arrange
        bib = _make_bib(tmp_path)
        # Act
        result = _citation_style.apply(str(tmp_path), "manuscript", "apalike")
        # Assert
        assert (
            result["changed"] is True
            and "\n\\bibliographystyle{apalike}\n" in bib.read_text()
        )

    def test_old_active_style_is_commented_out(self, tmp_path):
        # Arrange
        bib = _make_bib(tmp_path)
        # Act
        _citation_style.apply(str(tmp_path), "manuscript", "apalike")
        # Assert
        assert "% \\bibliographystyle{unsrtnat}" in bib.read_text()

    def test_absent_target_is_inserted(self, tmp_path):
        # Arrange
        bib = _make_bib(tmp_path)
        # Act
        result = _citation_style.apply(str(tmp_path), "manuscript", "ieeetr")
        # Assert
        assert (
            result["changed"] is True
            and "\\bibliographystyle{ieeetr}" in bib.read_text()
        )

    def test_change_writes_a_backup(self, tmp_path):
        # Arrange
        _make_bib(tmp_path)
        # Act
        result = _citation_style.apply(str(tmp_path), "manuscript", "apalike")
        # Assert
        assert result["backup_path"] and os.path.isfile(result["backup_path"])

    def test_config_citation_style_is_read_when_no_arg(
        self, tmp_path, _clear_style_env
    ):
        # Arrange
        _make_bib(tmp_path)
        cfg = tmp_path / "config"
        cfg.mkdir()
        (cfg / "config_manuscript.yaml").write_text("citation:\n  style: apalike\n")
        # Act
        result = _citation_style.apply(str(tmp_path), "manuscript", None)
        # Assert
        assert result["changed"] is True and result["new_style"] == "apalike"


if __name__ == "__main__":
    import sys

    sys.exit(pytest.main([__file__, "-v"]))

# EOF
