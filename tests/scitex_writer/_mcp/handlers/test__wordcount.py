#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: tests/scitex_writer/_mcp/handlers/test__wordcount.py

"""Tests for the word-count handler (pure-Python count_words engine)."""

from pathlib import Path

from scitex_writer._mcp.handlers import _wordcount


class TestCountWordsErrors:
    def test_invalid_doc_type_returns_actionable_error(self):
        # Arrange
        bad_doc_type = "poster"
        # Act
        result = _wordcount.count_words(".", bad_doc_type)
        # Assert
        assert result["success"] is False and "poster" in result["error"]

    def test_missing_config_returns_error_with_hint(self, tmp_path):
        # Arrange
        (tmp_path / "01_manuscript").mkdir()
        # Act
        result = _wordcount.count_words(str(tmp_path), "manuscript")
        # Assert
        assert result["success"] is False and "Config not found" in result["error"]


class TestResolveHelper:
    def test_resolve_strips_leading_dot_slash(self, tmp_path):
        # Arrange
        rel = "./01_manuscript/contents/wordcounts"
        # Act
        resolved = _wordcount._resolve(tmp_path, rel)
        # Assert
        assert resolved == (tmp_path / "01_manuscript/contents/wordcounts").resolve()

    def test_resolve_returns_none_for_empty(self, tmp_path):
        # Arrange
        rel = None
        # Act
        resolved = _wordcount._resolve(tmp_path, rel)
        # Assert
        assert resolved is None


class TestCountElementsHelper:
    def test_count_elements_excludes_headers_and_final(self, tmp_path):
        # Arrange
        for name in ["01_a.tex", "02_b.tex", "00_Figures_Header.tex", "FINAL.tex"]:
            (tmp_path / name).write_text("x")
        # Act
        n = _wordcount._count_elements(tmp_path)
        # Assert
        assert n == 2

    def test_count_elements_missing_dir_returns_zero(self, tmp_path):
        # Arrange
        missing = tmp_path / "nope"
        # Act
        n = _wordcount._count_elements(missing)
        # Assert
        assert n == 0


class TestCountWordsTexcountHelper:
    def test_missing_section_file_counts_zero(self, tmp_path):
        # Arrange
        absent = tmp_path / "abstract.tex"
        # Act
        n = _wordcount._count_words_texcount("texcount", absent)
        # Assert
        assert n == 0


if __name__ == "__main__":
    import sys

    import pytest

    sys.exit(pytest.main([__file__, "-v"]))

# EOF
