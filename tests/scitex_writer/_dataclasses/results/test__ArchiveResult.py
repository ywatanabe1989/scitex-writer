#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: tests/scitex_writer/_dataclasses/results/test__ArchiveResult.py

"""Tests for ArchiveResult's fail-loud validate().

A skip must say WHY (the shell's silent "skipping archive" warning is what this
replaces), and a snapshot must always carry the id it was stamped with.
"""

import pytest

from scitex_writer._dataclasses import ArchiveResult


def _complete(**overrides):
    fields = dict(
        success=True,
        archive_id="20260712-093000_abc1234",
        archived=[
            {"source": "/p/m.pdf", "archived": "/a/m_x.pdf", "current": "/a/m.pdf"}
        ],
        versions_dir="/a",
    )
    fields.update(overrides)
    return ArchiveResult(**fields)


class TestValidate:
    def test_complete_success_validates_cleanly(self):
        # Arrange
        result = _complete()
        # Act
        result.validate()
        # Assert
        assert result.success is True

    def test_skip_with_reason_validates_cleanly(self):
        # Arrange
        result = ArchiveResult(success=True, skipped=True, skip_reason="dirty tree")
        # Act
        result.validate()
        # Assert
        assert result.skipped is True

    def test_skip_without_reason_is_rejected(self):
        # Arrange
        result = ArchiveResult(success=True, skipped=True)
        # Act
        # Assert
        with pytest.raises(ValueError, match="no skip_reason"):
            result.validate()

    def test_skip_that_archived_files_is_rejected(self):
        # Arrange
        result = _complete(skipped=True, skip_reason="dirty tree")
        # Act
        # Assert
        with pytest.raises(ValueError, match="mutually exclusive"):
            result.validate()

    def test_success_without_archive_id_is_rejected(self):
        # Arrange
        result = _complete(archive_id=None)
        # Act
        # Assert
        with pytest.raises(ValueError, match="no archive_id"):
            result.validate()

    def test_success_with_error_is_rejected(self):
        # Arrange
        result = _complete(error="boom")
        # Act
        # Assert
        with pytest.raises(ValueError, match="error is set"):
            result.validate()

    def test_failure_without_error_is_rejected(self):
        # Arrange
        result = ArchiveResult(success=False)
        # Act
        # Assert
        with pytest.raises(ValueError, match="no error message"):
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
            "archive_id",
            "archived",
            "versions_dir",
            "missing",
            "skipped",
            "skip_reason",
            "error",
        }

    def test_str_of_skip_names_the_reason(self):
        # Arrange
        result = ArchiveResult(success=True, skipped=True, skip_reason="dirty tree")
        # Act
        text = str(result)
        # Assert
        assert "dirty tree" in text
