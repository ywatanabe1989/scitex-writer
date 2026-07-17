#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The compile must never stamp a version it cannot establish.

THE BUG. `_inject_version_stamp` wrote `scitex_writer.__version__` into the
manuscript's PDF provenance metadata (\\ScitexWriterVersion + pdfcreator), and
`__version__` comes from `importlib.metadata.version()`. When an environment
holds more than one scitex-writer distribution, that call resolves one by
directory scan order and returns it with no sign the question was ambiguous.
The whole thing was wrapped in `except Exception: pass`, so a stamp that never
got written looked exactly like a clean compile.

Real incident (2026-07-17): this container carried both a 2.26.1 and a 2.37.0
dist-info. `version()` answered 2.26.1 while 2.37.0 code was actually running --
verified by probing for a 2.33.0+ symbol. Every PDF compiled here would have
asserted it was built by v2.26.1. Unlike a bad log line, that falsehood is
durable: it survives in the published file after the environment is repaired,
and no later reader can detect it from the PDF alone.

Two silent failures stacked: one wrote the wrong version, the other hid writing
nothing.

The decision functions are pure -- they take the facts as arguments -- so these
run against real values with no mock and no monkeypatch (PA-306 / STX-NM002).
"""

import functools

import pytest

from scitex_writer._version_truth import (
    describe_ambiguous_metadata,
    resolve_stamp_version,
    version_stamp_tex,
)

# The exact state measured in the container that surfaced this bug.
AMBIGUOUS = ["2.26.1", "2.37.0"]


def _refusal_message(installed, declared) -> str:
    """Return the refusal message, or "" when the call is allowed through."""
    try:
        resolve_stamp_version(installed, declared)
    except RuntimeError as exc:
        return str(exc)
    return ""


class TestAmbiguousMetadataIsRefused:
    def test_two_distinct_versions_are_refused(self):
        # Arrange
        installed = AMBIGUOUS

        # Act
        message = _refusal_message(installed, "2.26.1")

        # Assert
        assert message != ""

    def test_refusal_raises_rather_than_returning_a_guess(self):
        # Arrange
        installed = AMBIGUOUS

        # Act
        act = functools.partial(resolve_stamp_version, installed, "2.26.1")

        # Assert
        with pytest.raises(RuntimeError):
            act()


class TestRefusalMessage:
    def test_message_names_the_stale_candidate(self):
        # Arrange
        installed = AMBIGUOUS

        # Act
        message = _refusal_message(installed, "2.26.1")

        # Assert
        assert "2.26.1" in message

    def test_message_names_the_current_candidate(self):
        # Arrange
        installed = AMBIGUOUS

        # Act
        message = _refusal_message(installed, "2.26.1")

        # Assert
        assert "2.37.0" in message

    def test_message_hands_back_a_working_repair_command(self):
        # Arrange
        installed = AMBIGUOUS

        # Act
        message = _refusal_message(installed, "2.26.1")

        # Assert
        assert "pip uninstall -y scitex-writer" in message

    def test_message_explains_the_provenance_stake(self):
        # Arrange: the message must say WHY, or a reader will force past it.
        versions = AMBIGUOUS

        # Act
        message = describe_ambiguous_metadata(versions)

        # Assert
        assert "provenance" in message


class TestUnambiguousMetadataIsStamped:
    def test_single_installed_version_is_returned(self):
        # Arrange
        installed = ["2.37.0"]

        # Act
        version = resolve_stamp_version(installed, "2.37.0")

        # Assert
        assert version == "2.37.0"

    def test_same_version_declared_twice_is_not_ambiguous(self):
        # Arrange: duplicate dist-info that AGREE answer the question, so they
        # must not block a compile.
        installed = ["2.37.0", "2.37.0"]

        # Act
        version = resolve_stamp_version(installed, "2.37.0")

        # Assert
        assert version == "2.37.0"

    def test_nothing_installed_defers_to_the_declared_version(self):
        # Arrange: a source tree with nothing installed is legitimate;
        # __version__ falls back to pyproject.toml there.
        installed = []

        # Act
        version = resolve_stamp_version(installed, "0.0.0+local")

        # Assert
        assert version == "0.0.0+local"


class TestStampRendersTheVersion:
    def test_stamp_defines_the_latex_version_macro(self):
        # Arrange
        version = "2.37.0"

        # Act
        tex = version_stamp_tex(version)

        # Assert
        assert "\\def\\ScitexWriterVersion{2.37.0}" in tex

    def test_stamp_sets_the_pdf_creator_metadata(self):
        # Arrange
        version = "2.37.0"

        # Act
        tex = version_stamp_tex(version)

        # Assert
        assert "pdfcreator={Compiled by SciTeX Writer v2.37.0}" in tex
