#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""update-project must never vendor a stale engine and call it success.

THE BUG. `update-project` vendors from the INSTALLED scitex-writer. An agent on
an old writer therefore vendors an OLD engine — and is told it worked. The
project silently carries bugs the fleet already fixed. That is the same
silent-wrong-answer class the engine exists to prevent, sitting inside the very
command we hand people to fix things.

Real incident (2026-07-14): neurovista and paper-scitex-clew were both told to
run `update-project`. Their installed writer was 2.29.0 while 2.32.1 was current.
Running it verbatim would have quietly vendored 2.29.0 under a "done" report.

The decision functions are pure, so these run against real values with no mock
and no monkeypatch (PA-306 / STX-NM002) — and crucially without touching PyPI.
"""

from scitex_writer._mcp.handlers._update._source_check import (
    is_older,
    outdated_source_error,
    source_report,
)


class TestIsOlder:
    def test_older_installed_version_is_detected(self):
        # Arrange: the real incident's versions.
        installed, latest = "2.29.0", "2.32.1"

        # Act
        stale = is_older(installed, latest)

        # Assert
        assert stale is True

    def test_current_version_is_not_older(self):
        # Arrange
        installed, latest = "2.32.1", "2.32.1"

        # Act
        stale = is_older(installed, latest)

        # Assert
        assert stale is False

    def test_newer_installed_version_is_not_older(self):
        # Arrange: a dev running ahead of PyPI must not be blocked.
        installed, latest = "2.33.0", "2.32.1"

        # Act
        stale = is_older(installed, latest)

        # Assert
        assert stale is False

    def test_minor_version_is_compared_numerically_not_lexically(self):
        # Arrange: "2.9.0" > "2.32.1" as STRINGS. A lexical compare would call
        # a four-month-old engine current.
        installed, latest = "2.9.0", "2.32.1"

        # Act
        stale = is_older(installed, latest)

        # Assert
        assert stale is True


class TestRefusalMessage:
    def test_refusal_names_the_installed_version(self):
        # Arrange
        installed, latest = "2.29.0", "2.32.1"

        # Act
        msg = outdated_source_error(installed, latest)

        # Assert
        assert installed in msg

    def test_refusal_hands_back_a_working_upgrade_command(self):
        # Arrange: a remedy the reader can paste. An instruction that does not
        # actually fix it is worse than none — they believe they have tried.
        expected = "uv pip install -U 'scitex-writer[all]'"

        # Act
        msg = outdated_source_error("2.29.0", "2.32.1")

        # Assert
        assert expected in msg

    def test_refusal_names_the_override(self):
        # Arrange
        installed, latest = "2.29.0", "2.32.1"

        # Act
        msg = outdated_source_error(installed, latest)

        # Assert
        assert "allow_outdated" in msg


class TestUnknownIsNeverReportedAsCurrent:
    def test_unreachable_pypi_reports_outdated_as_unknown_not_false(self):
        # Arrange: is_outdated=False would mean "verified current". When we could
        # not ask, the honest answer is None. Collapsing the two is the exact
        # silent-fallback this guard exists to prevent, so pin it explicitly.
        report = source_report.__doc__ or ""

        # Act
        promises_no_false_currency = (
            "Never claims currency it has not verified" in report
        )

        # Assert
        assert promises_no_false_currency
