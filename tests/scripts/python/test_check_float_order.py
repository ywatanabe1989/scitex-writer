#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: check_float_order.py
# Wave 2 cluster A batch 1 — NM+TQ003+TQ002+TQ007 cleanup.

import os
import sys
from pathlib import Path

import pytest

# Add scripts/python to path for imports
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

from check_float_order import (  # noqa: E402
    check_order,
    extract_number_and_name,
    find_labels,
    find_references,
)

# ============================================================================
# extract_number_and_name
# ============================================================================


def test_extract_number_and_name_basic_numbered_key_returns_int_number():
    """Numbered prefix is returned as an int."""
    # Arrange
    key = "04_modules"
    # Act
    num, _ = extract_number_and_name(key)
    # Assert
    assert num == 4


def test_extract_number_and_name_basic_numbered_key_returns_name_part():
    """Suffix after the underscore is returned as the name."""
    # Arrange
    key = "04_modules"
    # Act
    _, name = extract_number_and_name(key)
    # Assert
    assert name == "modules"


def test_extract_number_and_name_no_prefix_returns_none_number():
    """Key without numeric prefix yields None for the number."""
    # Arrange
    key = "no_number"
    # Act
    num, _ = extract_number_and_name(key)
    # Assert
    assert num is None


def test_extract_number_and_name_no_prefix_preserves_full_name():
    """Key without numeric prefix returns the whole key as the name."""
    # Arrange
    key = "no_number"
    # Act
    _, name = extract_number_and_name(key)
    # Assert
    assert name == "no_number"


def test_extract_number_and_name_number_only_key_returns_empty_name():
    """All-digit key returns the empty name part."""
    # Arrange
    key = "05"
    # Act
    _, name = extract_number_and_name(key)
    # Assert
    assert name == ""


def test_extract_number_and_name_two_digit_prefix_returns_int_twelve():
    """Two-digit prefix `12_results` returns 12 as the number."""
    # Arrange
    key = "12_results"
    # Act
    num, _ = extract_number_and_name(key)
    # Assert
    assert num == 12


def test_extract_number_and_name_leading_zero_returns_int_one():
    """Leading-zero prefix `01_intro` returns 1 as the number."""
    # Arrange
    key = "01_intro"
    # Act
    num, _ = extract_number_and_name(key)
    # Assert
    assert num == 1


# ============================================================================
# find_references
# ============================================================================


def test_find_references_returns_all_three_in_appearance_order(tmp_path):
    """find_references returns three refs across two files in IMRAD order."""
    # Arrange
    content_dir = tmp_path / "contents"
    content_dir.mkdir()
    (content_dir / "introduction.tex").write_text(
        r"\section{Introduction}"
        + "\n"
        + r"See \ref{fig:01_first} for details."
        + "\n"
        + r"Also see \ref{fig:02_second}."
        + "\n"
    )
    (content_dir / "results.tex").write_text(
        r"\section{Results}"
        + "\n"
        + r"The results in \ref{fig:03_third} show this."
        + "\n"
    )
    # Act
    refs = find_references(content_dir, "fig")
    # Assert
    assert [r[0] for r in refs] == ["01_first", "02_second", "03_third"]


def test_find_references_preserves_out_of_order_appearance(tmp_path):
    """find_references preserves first-appearance order even when not numerically sorted."""
    # Arrange
    content_dir = tmp_path / "contents"
    content_dir.mkdir()
    (content_dir / "introduction.tex").write_text(
        r"See \ref{fig:03_third} first. Then \ref{fig:01_first}. Finally \ref{fig:02_second}."
    )
    # Act
    refs = find_references(content_dir, "fig")
    # Assert
    assert [r[0] for r in refs] == ["03_third", "01_first", "02_second"]


def test_find_references_empty_content_returns_empty_list(tmp_path):
    """A document with no \\ref calls returns the empty list."""
    # Arrange
    content_dir = tmp_path / "contents"
    content_dir.mkdir()
    (content_dir / "introduction.tex").write_text(
        r"\section{Introduction}" + "\n" + "This section has no figure references."
    )
    # Act
    refs = find_references(content_dir, "fig")
    # Assert
    assert refs == []


def test_find_references_table_type_filters_only_table_refs(tmp_path):
    """Requesting `tab` ignores `fig` references in the same file."""
    # Arrange
    content_dir = tmp_path / "contents"
    content_dir.mkdir()
    (content_dir / "introduction.tex").write_text(
        r"See \ref{fig:01_figure} and \ref{tab:01_table}. "
        r"Also \ref{fig:02_another} and \ref{tab:02_more}."
    )
    # Act
    tab_refs = find_references(content_dir, "tab")
    # Assert
    assert [r[0] for r in tab_refs] == ["01_table", "02_more"]


def test_find_references_duplicate_reference_is_deduplicated(tmp_path):
    """A reference cited twice is recorded only on its first appearance."""
    # Arrange
    content_dir = tmp_path / "contents"
    content_dir.mkdir()
    (content_dir / "introduction.tex").write_text(
        r"See \ref{fig:01_first}. Again \ref{fig:01_first}. And \ref{fig:02_second}."
    )
    # Act
    refs = find_references(content_dir, "fig")
    # Assert
    assert [r[0] for r in refs] == ["01_first", "02_second"]


# ============================================================================
# find_labels
# ============================================================================


def test_find_labels_caption_file_label_is_recorded(tmp_path):
    """A label inside a caption-file `01_first.tex` is recorded under key `01_first`."""
    # Arrange
    content_dir = tmp_path / "contents"
    figures_dir = content_dir / "figures" / "caption_and_media"
    figures_dir.mkdir(parents=True)
    (figures_dir / "01_first.tex").write_text(r"\caption{First}\label{fig:01_first}")
    # Act
    labels = find_labels(content_dir, "fig")
    # Assert
    assert "01_first" in labels


def test_find_labels_caption_file_source_marker_is_caption_file(tmp_path):
    """A caption-file label is annotated with source == 'caption_file'."""
    # Arrange
    content_dir = tmp_path / "contents"
    figures_dir = content_dir / "figures" / "caption_and_media"
    figures_dir.mkdir(parents=True)
    (figures_dir / "01_first.tex").write_text(r"\caption{First}\label{fig:01_first}")
    # Act
    labels = find_labels(content_dir, "fig")
    # Assert
    assert labels["01_first"]["source"] == "caption_file"


def test_find_labels_inline_label_source_marker_is_inline(tmp_path):
    """A label defined inline inside a content `.tex` is annotated source == 'inline'."""
    # Arrange
    content_dir = tmp_path / "contents"
    content_dir.mkdir()
    (content_dir / "introduction.tex").write_text(
        r"\begin{figure}\includegraphics{img.png}\caption{X}\label{fig:01_inline}\end{figure}"
    )
    # Act
    labels = find_labels(content_dir, "fig")
    # Assert
    assert labels["01_inline"]["source"] == "inline"


def test_find_labels_table_type_recognises_tab_caption_file(tmp_path):
    """Table caption files under `tables/caption_and_media` are recognised for `tab` prefix."""
    # Arrange
    content_dir = tmp_path / "contents"
    tables_dir = content_dir / "tables" / "caption_and_media"
    tables_dir.mkdir(parents=True)
    (tables_dir / "01_results.tex").write_text(r"\caption{R}\label{tab:01_results}")
    # Act
    labels = find_labels(content_dir, "tab")
    # Assert
    assert "01_results" in labels


# ============================================================================
# check_order
# ============================================================================


def test_check_order_sequential_references_returns_ok_true(tmp_path):
    """Two refs in numerical order yield is_ok == True."""
    # Arrange
    content_dir = tmp_path / "contents"
    figures_dir = content_dir / "figures" / "caption_and_media"
    figures_dir.mkdir(parents=True)
    (content_dir / "introduction.tex").write_text(
        r"See \ref{fig:01_first} and \ref{fig:02_second}."
    )
    (figures_dir / "01_first.tex").write_text(r"\label{fig:01_first}")
    (figures_dir / "02_second.tex").write_text(r"\label{fig:02_second}")
    # Act
    is_ok, _, _ = check_order(content_dir, "fig", "Figure Test")
    # Assert
    assert is_ok is True


def test_check_order_sequential_references_produces_empty_mapping(tmp_path):
    """When refs are in order, the renumber-mapping is empty."""
    # Arrange
    content_dir = tmp_path / "contents"
    figures_dir = content_dir / "figures" / "caption_and_media"
    figures_dir.mkdir(parents=True)
    (content_dir / "introduction.tex").write_text(
        r"See \ref{fig:01_first} and \ref{fig:02_second}."
    )
    (figures_dir / "01_first.tex").write_text(r"\label{fig:01_first}")
    (figures_dir / "02_second.tex").write_text(r"\label{fig:02_second}")
    # Act
    _, _, mapping = check_order(content_dir, "fig", "Figure Test")
    # Assert
    assert mapping == {}


def test_check_order_out_of_order_returns_ok_false(tmp_path):
    """Refs in wrong order yield is_ok == False."""
    # Arrange
    content_dir = tmp_path / "contents"
    figures_dir = content_dir / "figures" / "caption_and_media"
    figures_dir.mkdir(parents=True)
    (content_dir / "introduction.tex").write_text(
        r"See \ref{fig:03_third} first, then \ref{fig:01_first}, then \ref{fig:02_second}."
    )
    (figures_dir / "01_first.tex").write_text(r"\label{fig:01_first}")
    (figures_dir / "02_second.tex").write_text(r"\label{fig:02_second}")
    (figures_dir / "03_third.tex").write_text(r"\label{fig:03_third}")
    # Act
    is_ok, _, _ = check_order(content_dir, "fig", "Figure Test")
    # Assert
    assert is_ok is False


def test_check_order_out_of_order_maps_first_seen_to_position_one(tmp_path):
    """First-seen `03_third` ref maps to renumbered `01_third`."""
    # Arrange
    content_dir = tmp_path / "contents"
    figures_dir = content_dir / "figures" / "caption_and_media"
    figures_dir.mkdir(parents=True)
    (content_dir / "introduction.tex").write_text(
        r"See \ref{fig:03_third} first, then \ref{fig:01_first}, then \ref{fig:02_second}."
    )
    (figures_dir / "01_first.tex").write_text(r"\label{fig:01_first}")
    (figures_dir / "02_second.tex").write_text(r"\label{fig:02_second}")
    (figures_dir / "03_third.tex").write_text(r"\label{fig:03_third}")
    # Act
    _, _, mapping = check_order(content_dir, "fig", "Figure Test")
    # Assert
    assert mapping["03_third"] == "01_third"


def test_check_order_no_references_returns_ok_true(tmp_path):
    """An empty manuscript with no \\ref calls trivially passes the order check."""
    # Arrange
    content_dir = tmp_path / "contents"
    content_dir.mkdir()
    (content_dir / "introduction.tex").write_text(
        r"\section{Introduction}" + "\n" + "No figures here."
    )
    # Act
    is_ok, _, _ = check_order(content_dir, "fig", "Figure Test")
    # Assert
    assert is_ok is True


def test_check_order_non_numbered_keys_pass_order_check(tmp_path):
    """Refs whose keys have no numeric prefix pass the order check trivially."""
    # Arrange
    content_dir = tmp_path / "contents"
    content_dir.mkdir()
    (content_dir / "introduction.tex").write_text(
        r"See \ref{fig:schematic} and \ref{fig:workflow}."
    )
    # Act
    is_ok, _, _ = check_order(content_dir, "fig", "Figure Test")
    # Assert
    assert is_ok is True


def test_check_order_mixed_numbered_and_unnumbered_keys_pass(tmp_path):
    """A mix of numbered (01,02) and unnumbered refs passes the order check."""
    # Arrange
    content_dir = tmp_path / "contents"
    content_dir.mkdir()
    (content_dir / "introduction.tex").write_text(
        r"See \ref{fig:01_intro}, \ref{fig:schematic}, and \ref{fig:02_results}."
    )
    # Act
    is_ok, _, _ = check_order(content_dir, "fig", "Figure Test")
    # Assert
    assert is_ok is True


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v"])
