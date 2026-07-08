#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: tests/scitex_writer/_dataclasses/results/test__CleanupResult.py

"""Tests for CleanupResult (the cleanup engine's typed result)."""

import pytest

from scitex_writer._dataclasses.results._CleanupResult import CleanupResult


class TestCleanupResultToDict:
    def test_to_dict_serializes_every_field(self):
        # Arrange
        result = CleanupResult(
            success=True,
            bak_removed=2,
            emacs_removed=1,
            aux_moved=3,
            progress_removed=1,
            versioned_removed=4,
            log_dir="/p/logs",
        )
        # Act
        payload = result.to_dict()
        # Assert
        assert payload == {
            "success": True,
            "bak_removed": 2,
            "emacs_removed": 1,
            "aux_moved": 3,
            "progress_removed": 1,
            "versioned_removed": 4,
            "log_dir": "/p/logs",
            "dry_run": False,
            "error": None,
        }


class TestCleanupResultValidate:
    def test_validate_rejects_success_carrying_error(self):
        # Arrange
        result = CleanupResult(success=True, error="boom")
        # Act
        validate = result.validate
        # Assert
        with pytest.raises(ValueError):
            validate()

    def test_validate_rejects_failure_without_error(self):
        # Arrange
        result = CleanupResult(success=False, error=None)
        # Act
        validate = result.validate
        # Assert
        with pytest.raises(ValueError):
            validate()

    def test_validate_rejects_negative_count_value(self):
        # Arrange
        result = CleanupResult(success=True, bak_removed=-1)
        # Act
        validate = result.validate
        # Assert
        with pytest.raises(ValueError):
            validate()

    def test_validate_accepts_consistent_success(self):
        # Arrange
        result = CleanupResult(success=True, bak_removed=0, log_dir="/p/logs")
        # Act
        result.validate()
        # Assert
        assert result.success is True


class TestCleanupResultStr:
    def test_str_reports_counts_for_success(self):
        # Arrange
        result = CleanupResult(success=True, bak_removed=5)
        # Act
        text = str(result)
        # Assert
        assert "bak=5" in text


if __name__ == "__main__":
    import sys

    sys.exit(pytest.main([__file__, "-v"]))

# EOF
