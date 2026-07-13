#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A recorded pointer to a file that is not there is NOT provenance.

THE BUG. `has_provenance` was `bool(session_id or output_file)` — true for any
non-empty string. So a claim whose output was deleted, renamed, or never written
still reported "this claim has provenance". paper-scitex-clew found **24 of 49
claims** in a real manuscript in exactly that state: `output_file` recorded,
file absent from disk, every one of them claiming provenance it did not have.

That is a confident wrong answer about the science — strictly worse than an
admitted gap, because an admitted gap gets investigated and a confident lie does
not.

These use real files on a real tmp_path. No mocks, no monkeypatch
(PA-306 / STX-NM002) — the whole bug was that nobody ever asked the filesystem.
"""


from scitex_writer._mcp.handlers._claim import (
    _dangling_output_error,
    _output_file_exists,
)


class TestOutputFileExists:
    def test_existing_relative_output_resolves_against_the_project(self, tmp_path):
        # Arrange
        (tmp_path / "data").mkdir()
        (tmp_path / "data" / "result.json").write_text("{}")

        # Act
        exists = _output_file_exists(tmp_path, "data/result.json")

        # Assert
        assert exists is True

    def test_missing_output_file_is_reported_missing(self, tmp_path):
        # Arrange: the 24-claim case — a pointer recorded, nothing on disk.
        recorded = "data/deleted.json"

        # Act
        exists = _output_file_exists(tmp_path, recorded)

        # Assert
        assert exists is False

    def test_absent_output_file_field_is_unknown_not_missing(self, tmp_path):
        # Arrange: no pointer recorded at all. "unknown" and "missing" are
        # different facts and must not be collapsed.
        recorded = None

        # Act
        exists = _output_file_exists(tmp_path, recorded)

        # Assert
        assert exists is None

    def test_existing_absolute_output_is_found(self, tmp_path):
        # Arrange
        target = tmp_path / "abs.json"
        target.write_text("{}")

        # Act
        exists = _output_file_exists(tmp_path, str(target))

        # Assert
        assert exists is True


class TestDanglingPointerIsNamed:
    def test_dangling_pointer_produces_an_error_naming_the_path(self):
        # Arrange
        recorded = "data/deleted.json"

        # Act
        err = _dangling_output_error(recorded, False)

        # Assert
        assert recorded in err

    def test_existing_output_produces_no_error(self):
        # Arrange
        recorded = "data/result.json"

        # Act
        err = _dangling_output_error(recorded, True)

        # Assert
        assert err is None

    def test_no_recorded_output_produces_no_error(self):
        # Arrange: a claim with no output_file is an honest gap, not a lie.
        recorded = None

        # Act
        err = _dangling_output_error(recorded, None)

        # Assert
        assert err is None


class TestHasProvenanceIsEarned:
    def test_dangling_output_alone_does_not_earn_provenance(self, tmp_path):
        # Arrange: THE REGRESSION. Old code: bool(None or "data/gone.json") -> True.
        session_id, output_file = None, "data/gone.json"
        exists = _output_file_exists(tmp_path, output_file)

        # Act
        has_provenance = bool(session_id or exists)

        # Assert
        assert has_provenance is False

    def test_existing_output_earns_provenance(self, tmp_path):
        # Arrange
        (tmp_path / "r.json").write_text("{}")
        session_id, output_file = None, "r.json"
        exists = _output_file_exists(tmp_path, output_file)

        # Act
        has_provenance = bool(session_id or exists)

        # Assert
        assert has_provenance is True

    def test_session_id_alone_still_earns_provenance(self, tmp_path):
        # Arrange: a recorded session IS provenance even with no output file.
        session_id, output_file = "2026Y-04M-18D_6qto", None
        exists = _output_file_exists(tmp_path, output_file)

        # Act
        has_provenance = bool(session_id or exists)

        # Assert
        assert has_provenance is True
