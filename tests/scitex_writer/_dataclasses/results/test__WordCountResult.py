#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: tests/scitex_writer/_dataclasses/results/test__WordCountResult.py

"""Tests for WordCountResult (the word-count engine's typed result)."""

import pytest

from scitex_writer._dataclasses.results._WordCountResult import WordCountResult


class TestWordCountResultToDict:
    def test_to_dict_serializes_every_field(self):
        # Arrange
        result = WordCountResult(
            success=True,
            doc_type="manuscript",
            counts={"abstract": 120, "imrd": 3400},
            total=3400,
            output_files=["/p/abstract_count.txt"],
        )
        # Act
        payload = result.to_dict()
        # Assert
        assert payload == {
            "success": True,
            "doc_type": "manuscript",
            "counts": {"abstract": 120, "imrd": 3400},
            "total": 3400,
            "output_files": ["/p/abstract_count.txt"],
            "error": None,
        }


class TestWordCountResultValidate:
    def test_validate_rejects_success_carrying_error(self):
        # Arrange
        result = WordCountResult(success=True, doc_type="manuscript", error="boom")
        # Act
        validate = result.validate
        # Assert
        with pytest.raises(ValueError):
            validate()

    def test_validate_rejects_failure_without_error(self):
        # Arrange
        result = WordCountResult(success=False, doc_type="manuscript", error=None)
        # Act
        validate = result.validate
        # Assert
        with pytest.raises(ValueError):
            validate()

    def test_validate_rejects_negative_count_value(self):
        # Arrange
        result = WordCountResult(
            success=True, doc_type="manuscript", counts={"abstract": -1}
        )
        # Act
        validate = result.validate
        # Assert
        with pytest.raises(ValueError):
            validate()

    def test_validate_accepts_consistent_success(self):
        # Arrange
        result = WordCountResult(
            success=True, doc_type="manuscript", counts={"abstract": 0}, total=0
        )
        # Act
        result.validate()
        # Assert
        assert result.success is True


class TestWordCountResultStr:
    def test_str_reports_total_for_success(self):
        # Arrange
        result = WordCountResult(
            success=True, doc_type="manuscript", counts={"imrd": 42}, total=42
        )
        # Act
        text = str(result)
        # Assert
        assert "total=42" in text


if __name__ == "__main__":
    import sys

    sys.exit(pytest.main([__file__, "-v"]))

# EOF
