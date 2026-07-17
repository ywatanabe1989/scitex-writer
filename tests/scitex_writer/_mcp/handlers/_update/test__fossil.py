#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The vendored tree must not carry a second, lying answer to "what version?".

THE BUG. A project is scaffolded by copying the template repo, which brings the
ENGINE's CHANGELOG.md along. It is in no sync list (_constants.py syncs only
`scripts/`, `compile.sh` and a few named engine paths), so it freezes at the
version the project was created on while everything around it keeps refreshing.

That would be harmless debris except it NAMES A VERSION, so it reads as
authoritative. Measured in a real consumer on 2026-07-17:

    .scitex/writer/00_shared/.scitex-writer-vendored-version -> 2.24.7  (honest)
    .scitex/writer/CHANGELOG.md top entry                    -> 2.9.0   (fossil)

Fifteen minor versions apart. On 2026-07-14 that fossil convinced a reader (me)
to tell the fleet the engine was "2.9.0, four months behind". Same family as the
PDF provenance stamp fixed in 2.38.0: a marker describing an INSTALL EVENT
rather than the code.

The safety property is the important one. `project_path` is normally the
vendored engine tree, but in a directly-scaffolded layout a CHANGELOG.md there
could be the AUTHOR's own — and silently overwriting an author's file would be
far worse than the fossil we are fixing. Identification is therefore by content,
and anything unrecognised is left alone.

Pure decision functions + a tmp_path for the one I/O function, so these run with
no mock and no monkeypatch (PA-306 / STX-NM002).
"""

from scitex_writer._mcp.handlers._update._fossil import (
    is_engine_changelog,
    neutralise_fossil_changelog,
    pointer_text,
)

# The real shape of the fossil, as found in a consumer's vendored tree.
ENGINE_CHANGELOG = (
    "# Changelog\n"
    "\n"
    "All notable changes to SciTeX Writer will be documented in this file.\n"
    "\n"
    "## [Unreleased]\n"
    "\n"
    "## [2.9.0] - 2026-03-14\n"
)

AUTHORS_OWN_CHANGELOG = (
    "# Changelog\n"
    "\n"
    "Revisions to our manuscript, tracked for the co-authors.\n"
    "\n"
    "## 2026-03-01 — reviewer 2 response\n"
)


class TestEngineChangelogIsRecognised:
    def test_the_engine_changelog_is_recognised(self):
        # Arrange
        text = ENGINE_CHANGELOG

        # Act
        recognised = is_engine_changelog(text)

        # Assert
        assert recognised is True


class TestAuthorContentIsNeverTouched:
    def test_an_authors_own_changelog_is_not_recognised(self):
        # Arrange: same "# Changelog" heading, different owner.
        text = AUTHORS_OWN_CHANGELOG

        # Act
        recognised = is_engine_changelog(text)

        # Assert
        assert recognised is False

    def test_an_authors_changelog_is_left_byte_identical(self, tmp_path):
        # Arrange
        (tmp_path / "CHANGELOG.md").write_text(AUTHORS_OWN_CHANGELOG)

        # Act
        neutralise_fossil_changelog(tmp_path, "2.38.0")

        # Assert
        assert (tmp_path / "CHANGELOG.md").read_text() == AUTHORS_OWN_CHANGELOG

    def test_an_authors_changelog_reports_no_neutralisation(self, tmp_path):
        # Arrange
        (tmp_path / "CHANGELOG.md").write_text(AUTHORS_OWN_CHANGELOG)

        # Act
        neutralised = neutralise_fossil_changelog(tmp_path, "2.38.0")

        # Assert
        assert neutralised is False

    def test_unrelated_prose_is_not_recognised(self):
        # Arrange
        text = "# Notes\n\nSciTeX Writer is used to build this paper.\n"

        # Act
        recognised = is_engine_changelog(text)

        # Assert
        assert recognised is False


class TestFossilIsNeutralised:
    def test_the_fossil_is_reported_as_neutralised(self, tmp_path):
        # Arrange
        (tmp_path / "CHANGELOG.md").write_text(ENGINE_CHANGELOG)

        # Act
        neutralised = neutralise_fossil_changelog(tmp_path, "2.38.0")

        # Assert
        assert neutralised is True

    def test_the_stale_version_no_longer_appears(self, tmp_path):
        # Arrange: 2.9.0 is the lie that fooled the fleet.
        (tmp_path / "CHANGELOG.md").write_text(ENGINE_CHANGELOG)

        # Act
        neutralise_fossil_changelog(tmp_path, "2.38.0")

        # Assert
        assert "2.9.0" not in (tmp_path / "CHANGELOG.md").read_text()

    def test_the_replacement_points_at_the_honest_stamp(self, tmp_path):
        # Arrange
        (tmp_path / "CHANGELOG.md").write_text(ENGINE_CHANGELOG)

        # Act
        neutralise_fossil_changelog(tmp_path, "2.38.0")

        # Assert
        assert (
            ".scitex-writer-vendored-version" in (tmp_path / "CHANGELOG.md").read_text()
        )

    def test_a_second_run_is_a_no_op(self, tmp_path):
        # Arrange: the pointer must not be mistaken for a fossil.
        (tmp_path / "CHANGELOG.md").write_text(pointer_text("2.38.0"))

        # Act
        neutralised = neutralise_fossil_changelog(tmp_path, "2.38.0")

        # Assert
        assert neutralised is False


class TestDryRunTouchesNothing:
    def test_dry_run_leaves_the_fossil_byte_identical(self, tmp_path):
        # Arrange
        (tmp_path / "CHANGELOG.md").write_text(ENGINE_CHANGELOG)

        # Act
        neutralise_fossil_changelog(tmp_path, "2.38.0", dry_run=True)

        # Assert
        assert (tmp_path / "CHANGELOG.md").read_text() == ENGINE_CHANGELOG

    def test_dry_run_still_reports_what_it_would_do(self, tmp_path):
        # Arrange
        (tmp_path / "CHANGELOG.md").write_text(ENGINE_CHANGELOG)

        # Act
        neutralised = neutralise_fossil_changelog(tmp_path, "2.38.0", dry_run=True)

        # Assert
        assert neutralised is True


class TestAbsentFileIsNotAFailure:
    def test_no_changelog_reports_nothing_neutralised(self, tmp_path):
        # Arrange: a tree with no CHANGELOG.md at all.
        project = tmp_path

        # Act
        neutralised = neutralise_fossil_changelog(project, "2.38.0")

        # Assert
        assert neutralised is False
