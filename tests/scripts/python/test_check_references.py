#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: check_references.py
# Wave 2 cluster A batch 1 — NM+TQ003+TQ002+TQ007 cleanup.

import os
import sys
from pathlib import Path

import pytest

# Add scripts/python to path for imports
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

from check_references import (  # noqa: E402
    collect_tex_files,
    extract_bib_keys,
    extract_citations,
    extract_labels,
    extract_refs,
    infer_auto_labels,
)

# ============================================================================
# extract_refs
# ============================================================================


def test_extract_refs_basic_finds_figure_ref(tmp_path):
    """A figure reference is captured by extract_refs."""
    # Arrange
    tex_file = tmp_path / "test.tex"
    tex_file.write_text(r"See Figure~\ref{fig:01_example} for details.")
    # Act
    refs = extract_refs([tex_file])
    # Assert
    assert "fig:01_example" in refs


def test_extract_refs_basic_finds_table_ref(tmp_path):
    """A table reference is captured by extract_refs."""
    # Arrange
    tex_file = tmp_path / "test.tex"
    tex_file.write_text(r"Results are shown in \ref{tab:01_data}.")
    # Act
    refs = extract_refs([tex_file])
    # Assert
    assert "tab:01_data" in refs


def test_extract_refs_full_line_comment_is_skipped(tmp_path):
    """A whole-line comment beginning with % is ignored."""
    # Arrange
    tex_file = tmp_path / "test.tex"
    tex_file.write_text(
        r"\ref{fig:real_ref}" + "\n" + r"% comment \ref{fig:commented_ref}" + "\n"
    )
    # Act
    refs = extract_refs([tex_file])
    # Assert
    assert "fig:commented_ref" not in refs


def test_extract_refs_macro_argument_placeholder_is_skipped(tmp_path):
    """Macro argument `#1` is not recorded as a referenced key."""
    # Arrange
    tex_file = tmp_path / "test.tex"
    tex_file.write_text(
        r"\newcommand{\figref}[1]{\ref{#1}}" + "\n" + r"\ref{fig:actual_ref}"
    )
    # Act
    refs = extract_refs([tex_file])
    # Assert
    assert "#1" not in refs


# ============================================================================
# extract_labels
# ============================================================================


def test_extract_labels_basic_finds_figure_label(tmp_path):
    """A `\\label{fig:...}` definition is captured by extract_labels."""
    # Arrange
    tex_file = tmp_path / "test.tex"
    tex_file.write_text(r"\begin{figure}\label{fig:01_example}\end{figure}")
    # Act
    labels = extract_labels([tex_file])
    # Assert
    assert "fig:01_example" in labels


def test_extract_labels_full_line_comment_is_skipped(tmp_path):
    """A label defined inside a `% comment` line is ignored."""
    # Arrange
    tex_file = tmp_path / "test.tex"
    tex_file.write_text(
        r"\label{sec:real_label}" + "\n" + r"% \label{sec:commented_label}"
    )
    # Act
    labels = extract_labels([tex_file])
    # Assert
    assert "sec:commented_label" not in labels


def test_extract_labels_duplicate_definition_is_tracked_twice(tmp_path):
    """A label defined in two files is recorded with two source-locations."""
    # Arrange
    tex1 = tmp_path / "file1.tex"
    tex2 = tmp_path / "file2.tex"
    tex1.write_text(r"\label{fig:duplicate}")
    tex2.write_text(r"\label{fig:duplicate}")
    # Act
    labels = extract_labels([tex1, tex2])
    # Assert
    assert len(labels["fig:duplicate"]) == 2


# ============================================================================
# extract_citations
# ============================================================================


def test_extract_citations_single_key_is_captured(tmp_path):
    """A single \\cite call yields the cited key."""
    # Arrange
    tex_file = tmp_path / "test.tex"
    tex_file.write_text(r"Previous work \cite{author2020} showed that...")
    # Act
    cites = extract_citations([tex_file])
    # Assert
    assert "author2020" in cites


def test_extract_citations_multi_key_command_yields_three_keys(tmp_path):
    """A \\citep with three comma-separated keys yields all three."""
    # Arrange
    tex_file = tmp_path / "test.tex"
    tex_file.write_text(r"\citep{Smith2018, Jones2019, Brown2020}")
    # Act
    cites = extract_citations([tex_file])
    # Assert
    assert {"Smith2018", "Jones2019", "Brown2020"}.issubset(cites)


def test_extract_citations_natbib_variants_are_all_recognised(tmp_path):
    """All natbib variants (\\cite/\\citep/\\citet/\\citealt/\\citeauthor/\\citeyear) are captured."""
    # Arrange
    tex_file = tmp_path / "test.tex"
    tex_file.write_text(
        r"\cite{ref1}"
        + "\n"
        + r"\citep{ref2}"
        + "\n"
        + r"\citet{ref3}"
        + "\n"
        + r"\citealt{ref4}"
        + "\n"
        + r"\citeauthor{ref5}"
        + "\n"
        + r"\citeyear{ref6}"
    )
    # Act
    cites = extract_citations([tex_file])
    # Assert
    assert all(f"ref{i}" in cites for i in range(1, 7))


def test_extract_citations_commented_citation_is_skipped(tmp_path):
    """A `% \\cite{commented_ref}` line is ignored."""
    # Arrange
    tex_file = tmp_path / "test.tex"
    tex_file.write_text(r"\cite{real_ref}" + "\n" + r"% \cite{commented_ref}")
    # Act
    cites = extract_citations([tex_file])
    # Assert
    assert "commented_ref" not in cites


def test_extract_citations_whitespace_padded_keys_are_stripped(tmp_path):
    """Keys with leading/trailing whitespace inside `\\cite{}` are stripped."""
    # Arrange
    tex_file = tmp_path / "test.tex"
    tex_file.write_text(r"\cite{Key1,  Key2,   Key3}")
    # Act
    cites = extract_citations([tex_file])
    # Assert
    assert {"Key1", "Key2", "Key3"}.issubset(cites)


# ============================================================================
# extract_bib_keys
# ============================================================================


def test_extract_bib_keys_three_entry_types_yields_all_keys(tmp_path):
    """@article/@book/@inproceedings entries each contribute one key."""
    # Arrange
    bib_file = tmp_path / "refs.bib"
    bib_file.write_text(
        "@article{Smith2020, author={John Smith}}\n"
        "@book{Jones2019, title={A Book}}\n"
        "@inproceedings{Brown2018, booktitle={Proceedings}}\n"
    )
    # Act
    keys = extract_bib_keys(tmp_path)
    # Assert
    assert {"Smith2020", "Jones2019", "Brown2018"}.issubset(set(keys))


def test_extract_bib_keys_multiple_files_are_merged(tmp_path):
    """Keys from separate .bib files are merged into one dict."""
    # Arrange
    (tmp_path / "refs1.bib").write_text("@article{Key1, title={T}}")
    (tmp_path / "refs2.bib").write_text("@book{Key2, title={T}}")
    # Act
    keys = extract_bib_keys(tmp_path)
    # Assert
    assert "Key1" in keys and "Key2" in keys


def test_extract_bib_keys_missing_directory_returns_empty_dict(tmp_path):
    """A non-existent directory yields the empty dict."""
    # Arrange
    nonexistent = tmp_path / "nonexistent"
    # Act
    keys = extract_bib_keys(nonexistent)
    # Assert
    assert keys == {}


def test_extract_bib_keys_trailing_comma_entry_is_recognised(tmp_path):
    """`@misc{TrailingComma,}` still yields the key `TrailingComma`."""
    # Arrange
    bib_file = tmp_path / "refs.bib"
    bib_file.write_text("@misc{TrailingComma,}")
    # Act
    keys = extract_bib_keys(tmp_path)
    # Assert
    assert "TrailingComma" in keys


# ============================================================================
# infer_auto_labels
# ============================================================================


def test_infer_auto_labels_caption_files_yield_three_labels(tmp_path):
    """Three caption files (fig+tab) yield three inferred labels."""
    # Arrange
    doc_dir = tmp_path / "01_manuscript"
    fig_dir = doc_dir / "contents" / "figures" / "caption_and_media"
    tab_dir = doc_dir / "contents" / "tables" / "caption_and_media"
    fig_dir.mkdir(parents=True)
    tab_dir.mkdir(parents=True)
    (fig_dir / "01_example.tex").write_text("F")
    (fig_dir / "02_results.tex").write_text("F")
    (tab_dir / "01_data.tex").write_text("T")
    # Act
    labels = infer_auto_labels(doc_dir)
    # Assert
    assert len(labels) == 3


def test_infer_auto_labels_skips_panel_files(tmp_path):
    """Panel-suffixed filenames like `01a_panel.tex` are not inferred."""
    # Arrange
    doc_dir = tmp_path / "01_manuscript"
    fig_dir = doc_dir / "contents" / "figures" / "caption_and_media"
    fig_dir.mkdir(parents=True)
    (fig_dir / "01_main.tex").write_text("M")
    (fig_dir / "01a_panel.tex").write_text("P")
    # Act
    labels = infer_auto_labels(doc_dir)
    # Assert
    assert "fig:01a_panel" not in labels


def test_infer_auto_labels_no_contents_dir_returns_empty_dict(tmp_path):
    """A manuscript without a `contents/` subdir yields the empty dict."""
    # Arrange
    doc_dir = tmp_path / "01_manuscript"
    doc_dir.mkdir()
    # Act
    labels = infer_auto_labels(doc_dir)
    # Assert
    assert labels == {}


def test_infer_auto_labels_line_number_is_zero(tmp_path):
    """Auto-inferred labels are tagged with line-number 0 as a synthetic marker."""
    # Arrange
    doc_dir = tmp_path / "01_manuscript"
    fig_dir = doc_dir / "contents" / "figures" / "caption_and_media"
    fig_dir.mkdir(parents=True)
    (fig_dir / "01_test.tex").write_text("T")
    # Act
    labels = infer_auto_labels(doc_dir)
    # Assert
    assert labels["fig:01_test"][0][1] == 0


# ============================================================================
# collect_tex_files
# ============================================================================


def test_collect_tex_files_includes_source_tex_files(tmp_path):
    """Three plain .tex source files under the manuscript dir are collected."""
    # Arrange
    doc_dir = tmp_path / "01_manuscript"
    content_dir = doc_dir / "contents"
    content_dir.mkdir(parents=True)
    (content_dir / "intro.tex").write_text("I")
    (content_dir / "methods.tex").write_text("M")
    (doc_dir / "base.tex").write_text("B")
    # Act
    files = collect_tex_files(doc_dir)
    # Assert
    assert {f.name for f in files} >= {"intro.tex", "methods.tex", "base.tex"}


def test_collect_tex_files_excludes_generated_manuscript_tex(tmp_path):
    """The generated `manuscript.tex` aggregate is excluded from the source list."""
    # Arrange
    doc_dir = tmp_path / "01_manuscript"
    doc_dir.mkdir()
    (doc_dir / "manuscript.tex").write_text("G")
    (doc_dir / "base.tex").write_text("S")
    # Act
    files = collect_tex_files(doc_dir)
    # Assert
    assert "manuscript.tex" not in {f.name for f in files}


def test_collect_tex_files_excludes_versioned_backups(tmp_path):
    """Versioned backups like `intro_v01.tex` are skipped."""
    # Arrange
    doc_dir = tmp_path / "01_manuscript"
    content_dir = doc_dir / "contents"
    content_dir.mkdir(parents=True)
    (content_dir / "intro.tex").write_text("C")
    (content_dir / "intro_v01.tex").write_text("V")
    # Act
    files = collect_tex_files(doc_dir)
    # Assert
    assert "intro_v01.tex" not in {f.name for f in files}


def test_collect_tex_files_includes_figure_caption_files(tmp_path):
    """Figure caption files under `contents/figures/caption_and_media` are included."""
    # Arrange
    doc_dir = tmp_path / "01_manuscript"
    fig_dir = doc_dir / "contents" / "figures" / "caption_and_media"
    fig_dir.mkdir(parents=True)
    (fig_dir / "01_fig.tex").write_text("F")
    # Act
    files = collect_tex_files(doc_dir)
    # Assert
    assert "01_fig.tex" in {f.name for f in files}


def test_collect_tex_files_missing_directory_returns_empty_list(tmp_path):
    """A nonexistent manuscript directory yields the empty list."""
    # Arrange
    nonexistent = tmp_path / "nonexistent"
    # Act
    files = collect_tex_files(nonexistent)
    # Assert
    assert files == []


# ============================================================================
# Integration smoke
# ============================================================================


def test_refs_and_labels_intersection_smoke(tmp_path):
    """When refs and labels are defined for the same key, the ref maps to a label."""
    # Arrange
    tex_file = tmp_path / "test.tex"
    tex_file.write_text(
        r"\section{Intro}\label{sec:intro}" + "\n" + r"See \ref{sec:intro}."
    )
    # Act
    refs = extract_refs([tex_file])
    labels = extract_labels([tex_file])
    # Assert
    assert all(ref_key in labels for ref_key in refs)


def test_citations_intersect_bib_keys_smoke(tmp_path):
    """A cited key Smith2020 appears in the bib-key dict for the same project."""
    # Arrange
    tex_file = tmp_path / "test.tex"
    bib_dir = tmp_path / "bib"
    bib_dir.mkdir()
    tex_file.write_text(r"\cite{Smith2020}")
    (bib_dir / "refs.bib").write_text("@article{Smith2020, title={T}}")
    # Act
    cites = extract_citations([tex_file])
    bib_keys = extract_bib_keys(bib_dir)
    # Assert
    assert all(cite_key in bib_keys for cite_key in cites)


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v"])
