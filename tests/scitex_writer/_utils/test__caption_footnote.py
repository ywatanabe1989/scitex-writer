#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: tests/scitex_writer/_utils/test__caption_footnote.py

r"""Tests for the \captionfootnote splitter (port of caption_footnote_split.py).

Pure string transforms on real caption bodies -- no mocks, no temp files.
"""

import pytest

from scitex_writer._utils._caption_footnote import split_caption_footnote


class TestNoMarker:
    def test_caption_without_marker_is_unchanged(self):
        # Arrange
        caption = "\\caption{\\textbf{Title}\\\\ Legend text.}"
        # Act
        body, footnote = split_caption_footnote(caption)
        # Assert
        assert body == caption and footnote is None

    def test_unbalanced_marker_leaves_caption_intact(self):
        # Arrange: a missing closing brace must not corrupt the caption body.
        caption = "\\caption{Legend.\\captionfootnote{unterminated"
        # Act
        body, footnote = split_caption_footnote(caption)
        # Assert
        assert body == caption and footnote is None

    def test_marker_without_brace_is_ignored(self):
        # Arrange
        caption = "\\caption{Legend.\\captionfootnote no braces}"
        # Act
        body, footnote = split_caption_footnote(caption)
        # Assert
        assert body == caption and footnote is None


class TestMarkerSplit:
    def test_marker_becomes_protected_footnotemark(self):
        # Arrange
        caption = "\\caption{Legend.\\captionfootnote{Funding disclosure.}}"
        # Act
        body, _ = split_caption_footnote(caption)
        # Assert
        assert body == "\\caption{Legend.\\protect\\footnotemark}"

    def test_disclosure_text_is_reported(self):
        # Arrange
        caption = "\\caption{Legend.\\captionfootnote{  Funding disclosure.  }}"
        # Act
        _, footnote = split_caption_footnote(caption)
        # Assert
        assert footnote == "Funding disclosure."

    def test_nested_braces_survive_extraction(self):
        # Arrange
        caption = "\\caption{L.\\captionfootnote{See \\textbf{Table 1} for detail.}}"
        # Act
        _, footnote = split_caption_footnote(caption)
        # Assert
        assert footnote == "See \\textbf{Table 1} for detail."

    def test_whitespace_before_brace_is_tolerated(self):
        # Arrange
        caption = "\\caption{L.\\captionfootnote {Disclosure.}}"
        # Act
        _, footnote = split_caption_footnote(caption)
        # Assert
        assert footnote == "Disclosure."

    def test_only_first_marker_is_split(self):
        # Arrange
        caption = "\\caption{A\\captionfootnote{one}B\\captionfootnote{two}}"
        # Act
        body, footnote = split_caption_footnote(caption)
        # Assert
        assert footnote == "one" and "\\captionfootnote{two}" in body


if __name__ == "__main__":
    import sys

    sys.exit(pytest.main([__file__, "-v"]))

# EOF
