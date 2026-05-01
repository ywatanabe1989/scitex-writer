#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: check_references.py

import os
import sys
from pathlib import Path

# Add scripts/python to path for imports
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
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
# Test extract_refs
# ============================================================================


def test_extract_refs_basic(tmp_path):
    """Test basic \\ref extraction from .tex files."""
    tex_file = tmp_path / "test.tex"
    tex_file.write_text(
        r"""
See Figure~\ref{fig:01_example} for details.
Results are shown in \ref{tab:01_data}.
"""
    )
    refs = extract_refs([tex_file])
    assert "fig:01_example" in refs
    assert "tab:01_data" in refs
    assert len(refs) == 2
    assert refs["fig:01_example"][0][1] == 2  # Line number


def test_extract_refs_skips_comments(tmp_path):
    """Test that \\ref in comments is ignored."""
    tex_file = tmp_path / "test.tex"
    tex_file.write_text(
        r"""
\ref{fig:real_ref}
% This is a comment with \ref{fig:commented_ref}
Some text % inline \ref{fig:inline_comment}
"""
    )
    refs = extract_refs([tex_file])
    assert "fig:real_ref" in refs
    assert "fig:commented_ref" not in refs
    assert "fig:inline_comment" not in refs


def test_extract_refs_skips_macro_args(tmp_path):
    """Test that \\ref{#1} (macro arguments) are skipped."""
    tex_file = tmp_path / "test.tex"
    tex_file.write_text(
        r"\newcommand{\figref}[1]{\ref{#1}}" "\n" r"\ref{fig:actual_ref}"
    )
    refs = extract_refs([tex_file])
    assert "fig:actual_ref" in refs
    assert "#1" not in refs


# ============================================================================
# Test extract_labels
# ============================================================================


def test_extract_labels_basic(tmp_path):
    """Test basic \\label extraction from .tex files."""
    tex_file = tmp_path / "test.tex"
    tex_file.write_text(
        r"""
\begin{figure}
  \label{fig:01_example}
\end{figure}
\begin{table}
  \label{tab:01_data}
\end{table}
"""
    )
    labels = extract_labels([tex_file])
    assert "fig:01_example" in labels
    assert "tab:01_data" in labels
    assert len(labels) == 2


def test_extract_labels_skips_comments(tmp_path):
    """Test that \\label in comments is ignored."""
    tex_file = tmp_path / "test.tex"
    tex_file.write_text(
        r"""
\label{sec:real_label}
% \label{sec:commented_label}
"""
    )
    labels = extract_labels([tex_file])
    assert "sec:real_label" in labels
    assert "sec:commented_label" not in labels


def test_extract_labels_multiple_definitions(tmp_path):
    """Test that multiply-defined labels are tracked."""
    tex1 = tmp_path / "file1.tex"
    tex2 = tmp_path / "file2.tex"
    tex1.write_text(r"\label{fig:duplicate}")
    tex2.write_text(r"\label{fig:duplicate}")
    labels = extract_labels([tex1, tex2])
    assert len(labels["fig:duplicate"]) == 2


# ============================================================================
# Test extract_citations
# ============================================================================


def test_extract_citations_single(tmp_path):
    """Test extraction of single citation keys."""
    tex_file = tmp_path / "test.tex"
    tex_file.write_text(r"Previous work \cite{author2020} showed that...")
    cites = extract_citations([tex_file])
    assert "author2020" in cites
    assert len(cites) == 1


def test_extract_citations_multi_key(tmp_path):
    """Test extraction of multiple keys in one cite command."""
    tex_file = tmp_path / "test.tex"
    tex_file.write_text(r"\citep{Smith2018, Jones2019, Brown2020}")
    cites = extract_citations([tex_file])
    assert all(k in cites for k in ["Smith2018", "Jones2019", "Brown2020"])
    assert len(cites) == 3


def test_extract_citations_variants(tmp_path):
    """Test that various citation commands are recognized."""
    tex_file = tmp_path / "test.tex"
    tex_file.write_text(
        r"""
\cite{ref1}
\citep{ref2}
\citet{ref3}
\citealt{ref4}
\citeauthor{ref5}
\citeyear{ref6}
"""
    )
    cites = extract_citations([tex_file])
    assert all(f"ref{i}" in cites for i in range(1, 7))
    assert len(cites) == 6


def test_extract_citations_skips_comments(tmp_path):
    """Test that citations in comments are ignored."""
    tex_file = tmp_path / "test.tex"
    tex_file.write_text(r"\cite{real_ref}" "\n" r"% \cite{commented_ref}")
    cites = extract_citations([tex_file])
    assert "real_ref" in cites
    assert "commented_ref" not in cites


def test_extract_citations_whitespace_handling(tmp_path):
    """Test citation extraction handles whitespace in keys."""
    tex_file = tmp_path / "test.tex"
    tex_file.write_text(r"\cite{Key1,  Key2,   Key3}")
    cites = extract_citations([tex_file])
    assert all(k in cites for k in ["Key1", "Key2", "Key3"])


# ============================================================================
# Test extract_bib_keys
# ============================================================================


def test_extract_bib_keys(tmp_path):
    """Test extraction of citation keys from .bib files."""
    bib_file = tmp_path / "refs.bib"
    bib_file.write_text(
        """
@article{Smith2020, author={John Smith}}
@book{Jones2019, title={A Book}}
@inproceedings{Brown2018, booktitle={Proceedings}}
"""
    )
    keys = extract_bib_keys(tmp_path)
    assert all(k in keys for k in ["Smith2020", "Jones2019", "Brown2018"])
    assert keys["Smith2020"] == bib_file


def test_extract_bib_keys_multiple_files(tmp_path):
    """Test extraction from multiple .bib files."""
    (tmp_path / "refs1.bib").write_text("@article{Key1, title={Test}}")
    (tmp_path / "refs2.bib").write_text("@book{Key2, title={Test}}")
    keys = extract_bib_keys(tmp_path)
    assert "Key1" in keys and "Key2" in keys


def test_extract_bib_keys_no_directory(tmp_path):
    """Test that missing directory returns empty dict."""
    assert extract_bib_keys(tmp_path / "nonexistent") == {}


def test_extract_bib_keys_various_formats(tmp_path):
    """Test extraction with various BibTeX entry formats."""
    bib_file = tmp_path / "refs.bib"
    bib_file.write_text(
        "@article{NoSpaces,author={Test}}\n"
        "@book{WithComma, title={Test}}\n"
        "@misc{TrailingComma,}"
    )
    keys = extract_bib_keys(tmp_path)
    assert all(k in keys for k in ["NoSpaces", "WithComma", "TrailingComma"])


# ============================================================================
# Test infer_auto_labels
# ============================================================================


def test_infer_auto_labels(tmp_path):
    """Test inference of auto-generated labels from caption files."""
    doc_dir = tmp_path / "01_manuscript"
    fig_dir = doc_dir / "contents" / "figures" / "caption_and_media"
    tab_dir = doc_dir / "contents" / "tables" / "caption_and_media"
    fig_dir.mkdir(parents=True)
    tab_dir.mkdir(parents=True)

    (fig_dir / "01_example.tex").write_text("Figure caption")
    (fig_dir / "02_results.tex").write_text("Results figure")
    (tab_dir / "01_data.tex").write_text("Data table")

    labels = infer_auto_labels(doc_dir)
    assert all(k in labels for k in ["fig:01_example", "fig:02_results", "tab:01_data"])
    assert len(labels) == 3


def test_infer_auto_labels_skips_panels(tmp_path):
    """Test that panel files (01a_name) are skipped."""
    doc_dir = tmp_path / "01_manuscript"
    fig_dir = doc_dir / "contents" / "figures" / "caption_and_media"
    fig_dir.mkdir(parents=True)

    (fig_dir / "01_main.tex").write_text("Main")
    (fig_dir / "01a_panel.tex").write_text("Panel A")
    (fig_dir / "01b_panel.tex").write_text("Panel B")
    (fig_dir / "02_other.tex").write_text("Other")

    labels = infer_auto_labels(doc_dir)
    assert "fig:01_main" in labels and "fig:02_other" in labels
    assert "fig:01a_panel" not in labels and "fig:01b_panel" not in labels


def test_infer_auto_labels_no_contents_dir(tmp_path):
    """Test behavior when contents directory doesn't exist."""
    doc_dir = tmp_path / "01_manuscript"
    doc_dir.mkdir()
    assert infer_auto_labels(doc_dir) == {}


def test_infer_auto_labels_line_zero(tmp_path):
    """Test that inferred labels have line number 0 (auto-generated marker)."""
    doc_dir = tmp_path / "01_manuscript"
    fig_dir = doc_dir / "contents" / "figures" / "caption_and_media"
    fig_dir.mkdir(parents=True)
    (fig_dir / "01_test.tex").write_text("Test")
    labels = infer_auto_labels(doc_dir)
    assert labels["fig:01_test"][0][1] == 0  # Line number should be 0


# ============================================================================
# Test collect_tex_files
# ============================================================================


def test_collect_tex_files_basic(tmp_path):
    """Test collection of source .tex files."""
    doc_dir = tmp_path / "01_manuscript"
    content_dir = doc_dir / "contents"
    content_dir.mkdir(parents=True)

    (content_dir / "intro.tex").write_text("Intro")
    (content_dir / "methods.tex").write_text("Methods")
    (doc_dir / "base.tex").write_text("Base")

    files = collect_tex_files(doc_dir)
    file_names = {f.name for f in files}
    assert all(name in file_names for name in ["intro.tex", "methods.tex", "base.tex"])


def test_collect_tex_files_skips_generated(tmp_path):
    """Test that generated files are skipped."""
    doc_dir = tmp_path / "01_manuscript"
    doc_dir.mkdir()

    (doc_dir / "manuscript.tex").write_text("Generated")
    (doc_dir / "manuscript_diff.tex").write_text("Generated diff")
    (doc_dir / "base.tex").write_text("Source")

    files = collect_tex_files(doc_dir)
    assert len(files) == 1 and files[0].name == "base.tex"


def test_collect_tex_files_skips_versioned(tmp_path):
    """Test that versioned files (_v01.tex) are skipped."""
    doc_dir = tmp_path / "01_manuscript"
    content_dir = doc_dir / "contents"
    content_dir.mkdir(parents=True)

    (content_dir / "intro.tex").write_text("Current")
    (content_dir / "intro_v01.tex").write_text("Version 1")
    (content_dir / "intro_v02.tex").write_text("Version 2")

    files = collect_tex_files(doc_dir)
    assert len(files) == 1 and files[0].name == "intro.tex"


def test_collect_tex_files_includes_captions(tmp_path):
    """Test that caption files are included."""
    doc_dir = tmp_path / "01_manuscript"
    fig_dir = doc_dir / "contents" / "figures" / "caption_and_media"
    tab_dir = doc_dir / "contents" / "tables" / "caption_and_media"
    fig_dir.mkdir(parents=True)
    tab_dir.mkdir(parents=True)

    (fig_dir / "01_fig.tex").write_text("Fig")
    (tab_dir / "01_tab.tex").write_text("Tab")

    files = collect_tex_files(doc_dir)
    file_names = {f.name for f in files}
    assert "01_fig.tex" in file_names and "01_tab.tex" in file_names


def test_collect_tex_files_nonexistent_dir(tmp_path):
    """Test behavior with nonexistent directories."""
    assert collect_tex_files(tmp_path / "nonexistent") == []


# ============================================================================
# Test integration scenarios
# ============================================================================


def test_refs_and_labels_match(tmp_path):
    """Integration test: refs should find matching labels."""
    tex_file = tmp_path / "test.tex"
    tex_file.write_text(
        r"\section{Intro}\label{sec:intro}" "\n" r"See \ref{sec:intro}."
    )
    refs = extract_refs([tex_file])
    labels = extract_labels([tex_file])
    for ref_key in refs:
        assert ref_key in labels


def test_citations_and_bib_match(tmp_path):
    """Integration test: citations should find matching bib entries."""
    tex_file = tmp_path / "test.tex"
    bib_dir = tmp_path / "bib"
    bib_dir.mkdir()

    tex_file.write_text(r"\cite{Smith2020}")
    (bib_dir / "refs.bib").write_text("@article{Smith2020, title={Test}}")

    cites = extract_citations([tex_file])
    bib_keys = extract_bib_keys(bib_dir)
    for cite_key in cites:
        assert cite_key in bib_keys


def test_auto_labels_vs_explicit(tmp_path):
    """Test that auto-inferred labels work like explicit ones."""
    doc_dir = tmp_path / "01_manuscript"
    content_dir = doc_dir / "contents"
    fig_dir = content_dir / "figures" / "caption_and_media"
    fig_dir.mkdir(parents=True)

    (fig_dir / "01_auto.tex").write_text("Auto")
    tex_file = content_dir / "text.tex"
    tex_file.write_text(
        r"\ref{fig:01_auto}" "\n" r"\ref{fig:explicit}" "\n" r"\label{fig:explicit}"
    )

    refs = extract_refs([tex_file])
    labels = extract_labels([tex_file])
    auto_labels = infer_auto_labels(doc_dir)
    all_labels = {**labels, **auto_labels}

    assert all(k in refs for k in ["fig:01_auto", "fig:explicit"])
    assert all(k in all_labels for k in ["fig:01_auto", "fig:explicit"])


if __name__ == "__main__":
    import pytest

    pytest.main([os.path.abspath(__file__), "-v"])
