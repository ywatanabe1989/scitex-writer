#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: tests/scitex_writer/_dataclasses/results/test__DiffResult.py

"""Tests for DiffResult's fail-loud validate().

The point of validate() is that a DiffResult cannot claim success while
describing an empty or unattributed diff -- the exact shape the shell used to
emit when it silently diffed the manuscript against itself.
"""

import pytest

from scitex_writer._dataclasses import DiffResult


def _complete(**overrides):
    fields = dict(
        success=True,
        from_hash="aaaaaaa",
        to_hash="bbbbbbb",
        diff_tex="/p/m_diff.tex",
        diff_pdf="/p/m_diff.pdf",
        pdf_bytes=4096,
    )
    fields.update(overrides)
    return DiffResult(**fields)


class TestValidate:
    def test_complete_success_validates_cleanly(self):
        # Arrange
        result = _complete()
        # Act
        result.validate()
        # Assert
        assert result.success is True

    def test_skipped_run_needs_no_versions(self):
        # Arrange
        result = DiffResult(success=True, skipped=True)
        # Act
        result.validate()
        # Assert
        assert result.skipped is True

    def test_success_with_error_is_rejected(self):
        # Arrange
        result = _complete(error="boom")
        # Act
        # Assert
        with pytest.raises(ValueError, match="error is set"):
            result.validate()

    def test_failure_without_error_is_rejected(self):
        # Arrange
        result = DiffResult(success=False)
        # Act
        # Assert
        with pytest.raises(ValueError, match="no error message"):
            result.validate()

    def test_success_without_versions_is_rejected(self):
        # Arrange
        result = _complete(from_hash=None)
        # Act
        # Assert
        with pytest.raises(ValueError, match="from_hash/to_hash is unset"):
            result.validate()

    def test_success_with_empty_pdf_is_rejected(self):
        # Arrange
        result = _complete(pdf_bytes=0)
        # Act
        # Assert
        with pytest.raises(ValueError, match="no non-empty diff_pdf"):
            result.validate()

    def test_negative_pdf_size_is_rejected(self):
        # Arrange
        result = _complete(pdf_bytes=-1)
        # Act
        # Assert
        with pytest.raises(ValueError, match="non-negative int"):
            result.validate()


class TestSerialization:
    def test_to_dict_exposes_every_field(self):
        # Arrange
        result = _complete()
        # Act
        payload = result.to_dict()
        # Assert
        assert set(payload) == {
            "success",
            "from_hash",
            "to_hash",
            "diff_tex",
            "diff_pdf",
            "pdf_bytes",
            "skipped",
            "error",
        }

    def test_str_of_failure_names_the_error(self):
        # Arrange
        result = DiffResult(success=False, error="latexdiff not found")
        # Act
        text = str(result)
        # Assert
        assert "latexdiff not found" in text
