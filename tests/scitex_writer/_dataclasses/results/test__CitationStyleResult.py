#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: tests/scitex_writer/_dataclasses/results/test__CitationStyleResult.py

"""Tests for CitationStyleResult."""

import pytest

from scitex_writer._dataclasses.results._CitationStyleResult import (
    CitationStyleResult,
)


class TestCitationStyleResultToDict:
    def test_to_dict_serializes_every_field(self):
        # Arrange
        result = CitationStyleResult(
            success=True,
            changed=True,
            current_style="unsrt",
            new_style="nature",
            backup_path="/p/bibliography.tex.bak",
            message="ok",
        )
        # Act
        payload = result.to_dict()
        # Assert
        assert payload["new_style"] == "nature" and payload["changed"] is True


class TestCitationStyleResultValidate:
    def test_validate_rejects_success_carrying_error(self):
        # Arrange
        result = CitationStyleResult(success=True, error="boom")
        # Act
        validate = result.validate
        # Assert
        with pytest.raises(ValueError):
            validate()

    def test_validate_rejects_failure_without_error(self):
        # Arrange
        result = CitationStyleResult(success=False, error=None)
        # Act
        validate = result.validate
        # Assert
        with pytest.raises(ValueError):
            validate()

    def test_validate_rejects_changed_without_new_style(self):
        # Arrange
        result = CitationStyleResult(success=True, changed=True, new_style=None)
        # Act
        validate = result.validate
        # Assert
        with pytest.raises(ValueError):
            validate()

    def test_validate_accepts_consistent_noop(self):
        # Arrange
        result = CitationStyleResult(success=True, changed=False, new_style="nature")
        # Act
        result.validate()
        # Assert
        assert result.success is True


if __name__ == "__main__":
    import sys

    sys.exit(pytest.main([__file__, "-v"]))

# EOF
