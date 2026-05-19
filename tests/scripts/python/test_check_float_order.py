#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: check_float_order.py

import os
import sys
from pathlib import Path

# Add scripts/python to path for imports
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

from check_float_order import (  # noqa: E402
    check_order,
    extract_number_and_name,
    find_labels,
    find_references,
)

# ====================================================================
# Tests for extract_number_and_name
# ====================================================================


def test_extract_number_and_name_basic():
    """Test basic numbered key extraction."""
    # Arrange
    # Act
    num, name = extract_number_and_name("04_modules")
    # Assert
    assert (num == 4) and (name == 'modules')


def test_extract_number_and_name_no_prefix():
    """Test key without numeric prefix."""
    # Arrange
    # Act
    num, name = extract_number_and_name("no_number")
    # Assert
    assert (num is None) and (name == 'no_number')


def test_extract_number_and_name_number_only():
    """Test key with only a number."""
    # Arrange
    # Act
    num, name = extract_number_and_name("05")
    # Assert
    assert (num == 5) and (name == '')


def test_extract_number_and_name_two_digit():
    """Test two-digit numbered key."""
    # Arrange
    # Act
    num, name = extract_number_and_name("12_results")
    # Assert
    assert (num == 12) and (name == 'results')


def test_extract_number_and_name_leading_zero():
    """Test key with leading zero."""
    # Arrange
    # Act
    num, name = extract_number_and_name("01_intro")
    # Assert
    assert (num == 1) and (name == 'intro')


# ====================================================================
# Tests for find_references
# ====================================================================


def test_find_references_in_order(tmp_path):
    """Test finding references that are in correct order."""
    # Arrange
    content_dir = tmp_path / "contents"
    content_dir.mkdir()

    # Create introduction.tex with refs to 01, 02
    intro_file = content_dir / "introduction.tex"
    intro_file.write_text(
        r"""
\section{Introduction}
See \ref{fig:01_first} for details.
Also see \ref{fig:02_second}.
"""
    )

    # Create results.tex with ref to 03
    results_file = content_dir / "results.tex"
    results_file.write_text(
        r"""
\section{Results}
The results in \ref{fig:03_third} show this.
"""
    )

    # Act
    refs = find_references(content_dir, "fig")

    # Assert
    assert (len(refs) == 3) and (refs[0][0] == '01_first') and (refs[1][0] == '02_second') and (refs[2][0] == '03_third')


def test_find_references_out_of_order(tmp_path):
    """Test finding references that are out of order."""
    # Arrange
    content_dir = tmp_path / "contents"
    content_dir.mkdir()

    # Create introduction.tex with refs in wrong order
    intro_file = content_dir / "introduction.tex"
    intro_file.write_text(
        r"""
\section{Introduction}
See \ref{fig:03_third} first.
Then \ref{fig:01_first}.
Finally \ref{fig:02_second}.
"""
    )

    # Act
    refs = find_references(content_dir, "fig")

    # Assert
    assert (len(refs) == 3) and (refs[0][0] == '03_third') and (refs[1][0] == '01_first') and (refs[2][0] == '02_second')


def test_find_references_empty(tmp_path):
    """Test finding references when no refs exist."""
    # Arrange
    content_dir = tmp_path / "contents"
    content_dir.mkdir()

    # Create file without any refs
    intro_file = content_dir / "introduction.tex"
    intro_file.write_text(
        r"""
\section{Introduction}
This section has no figure references.
"""
    )

    # Act
    refs = find_references(content_dir, "fig")
    # Assert
    assert len(refs) == 0


def test_find_references_multiple_types(tmp_path):
    """Test finding references for different float types (fig vs tab)."""
    # Arrange
    content_dir = tmp_path / "contents"
    content_dir.mkdir()

    intro_file = content_dir / "introduction.tex"
    intro_file.write_text(
        r"""
\section{Introduction}
See \ref{fig:01_figure} and \ref{tab:01_table}.
Also \ref{fig:02_another} and \ref{tab:02_more}.
"""
    )

    fig_refs = find_references(content_dir, "fig")
    # Act
    tab_refs = find_references(content_dir, "tab")

    # Assert
    assert (len(fig_refs) == 2) and (len(tab_refs) == 2) and (fig_refs[0][0] == '01_figure') and (tab_refs[0][0] == '01_table')


def test_find_references_duplicate_refs(tmp_path):
    """Test that duplicate references are only counted once."""
    # Arrange
    content_dir = tmp_path / "contents"
    content_dir.mkdir()

    intro_file = content_dir / "introduction.tex"
    intro_file.write_text(
        r"""
\section{Introduction}
See \ref{fig:01_first}.
Again, see \ref{fig:01_first}.
And \ref{fig:02_second}.
"""
    )

    # Act
    refs = find_references(content_dir, "fig")

    # Should only count first appearance
    # Assert
    assert (len(refs) == 2) and (refs[0][0] == '01_first') and (refs[1][0] == '02_second')


# ====================================================================
# Tests for find_labels
# ====================================================================


def test_find_labels_in_caption_files(tmp_path):
    """Test finding labels in caption files."""
    # Arrange
    content_dir = tmp_path / "contents"
    figures_dir = content_dir / "figures" / "caption_and_media"
    figures_dir.mkdir(parents=True)

    # Create caption files with labels
    caption1 = figures_dir / "01_first.tex"
    caption1.write_text(r"\caption{First figure}\label{fig:01_first}")

    caption2 = figures_dir / "02_second.tex"
    caption2.write_text(r"\caption{Second figure}\label{fig:02_second}")

    # Act
    labels = find_labels(content_dir, "fig")

    # Assert
    assert (len(labels) == 2) and ('01_first' in labels) and ('02_second' in labels) and (labels['01_first']['source'] == 'caption_file') and (labels['02_second']['source'] == 'caption_file')


def test_find_labels_inline(tmp_path):
    """Test finding labels inline in content tex files."""
    # Arrange
    content_dir = tmp_path / "contents"
    content_dir.mkdir()

    intro_file = content_dir / "introduction.tex"
    intro_file.write_text(
        r"""
\section{Introduction}
\begin{figure}
\includegraphics{image.png}
\caption{An inline figure}
\label{fig:01_inline}
\end{figure}
"""
    )

    # Act
    labels = find_labels(content_dir, "fig")

    # Assert
    assert (len(labels) == 1) and ('01_inline' in labels) and (labels['01_inline']['source'] == 'inline')


def test_find_labels_tables(tmp_path):
    """Test finding table labels."""
    # Arrange
    content_dir = tmp_path / "contents"
    tables_dir = content_dir / "tables" / "caption_and_media"
    tables_dir.mkdir(parents=True)

    caption1 = tables_dir / "01_results.tex"
    caption1.write_text(r"\caption{Results table}\label{tab:01_results}")

    # Act
    labels = find_labels(content_dir, "tab")

    # Assert
    assert (len(labels) == 1) and ('01_results' in labels) and (labels['01_results']['source'] == 'caption_file')


# ====================================================================
# Tests for check_order
# ====================================================================


def test_check_order_passing(tmp_path, capsys):
    """Test check_order with sequential references."""
    # Arrange
    content_dir = tmp_path / "contents"
    figures_dir = content_dir / "figures" / "caption_and_media"
    figures_dir.mkdir(parents=True)

    # Create content with refs in order
    intro_file = content_dir / "introduction.tex"
    intro_file.write_text(
        r"""
\section{Introduction}
See \ref{fig:01_first} and \ref{fig:02_second}.
"""
    )

    # Create corresponding caption files
    (figures_dir / "01_first.tex").write_text(r"\label{fig:01_first}")
    (figures_dir / "02_second.tex").write_text(r"\label{fig:02_second}")

    # Act
    is_ok, refs, mapping = check_order(content_dir, "fig", "Figure Test")

    # Assert
    assert (is_ok is True) and (len(refs) == 2) and (len(mapping) == 0)


def test_check_order_failing(tmp_path, capsys):
    """Test check_order with out-of-order references."""
    # Arrange
    content_dir = tmp_path / "contents"
    figures_dir = content_dir / "figures" / "caption_and_media"
    figures_dir.mkdir(parents=True)

    # Create content with refs out of order
    intro_file = content_dir / "introduction.tex"
    intro_file.write_text(
        r"""
\section{Introduction}
See \ref{fig:03_third} first, then \ref{fig:01_first}, then \ref{fig:02_second}.
"""
    )

    # Create corresponding caption files
    (figures_dir / "01_first.tex").write_text(r"\label{fig:01_first}")
    (figures_dir / "02_second.tex").write_text(r"\label{fig:02_second}")
    (figures_dir / "03_third.tex").write_text(r"\label{fig:03_third}")

    # Act
    is_ok, refs, mapping = check_order(content_dir, "fig", "Figure Test")

    # Assert
    assert (is_ok is False) and (len(refs) == 3) and ('03_third' in mapping) and ('01_first' in mapping) and ('02_second' in mapping) and (mapping['03_third'] == '01_third') and (mapping['01_first'] == '02_first') and (mapping['02_second'] == '03_second')


def test_check_order_no_references(tmp_path, capsys):
    """Test check_order when no references exist."""
    # Arrange
    content_dir = tmp_path / "contents"
    content_dir.mkdir()

    intro_file = content_dir / "introduction.tex"
    intro_file.write_text(
        r"""
\section{Introduction}
No figures here.
"""
    )

    # Act
    is_ok, refs, mapping = check_order(content_dir, "fig", "Figure Test")

    # Assert
    assert (is_ok is True) and (len(refs) == 0) and (len(mapping) == 0)


def test_check_order_non_numbered_refs(tmp_path, capsys):
    """Test check_order with non-numbered reference keys."""
    # Arrange
    content_dir = tmp_path / "contents"
    content_dir.mkdir()

    intro_file = content_dir / "introduction.tex"
    intro_file.write_text(
        r"""
\section{Introduction}
See \ref{fig:schematic} and \ref{fig:workflow}.
"""
    )

    # Act
    is_ok, refs, mapping = check_order(content_dir, "fig", "Figure Test")

    # Assert
    assert (is_ok is True) and (len(refs) == 2) and (len(mapping) == 0)


def test_check_order_mixed_numbered_unnumbered(tmp_path, capsys):
    """Test check_order with mix of numbered and unnumbered refs."""
    # Arrange
    content_dir = tmp_path / "contents"
    content_dir.mkdir()

    intro_file = content_dir / "introduction.tex"
    intro_file.write_text(
        r"""
\section{Introduction}
See \ref{fig:01_intro}, \ref{fig:schematic}, and \ref{fig:02_results}.
"""
    )

    # Act
    is_ok, refs, mapping = check_order(content_dir, "fig", "Figure Test")

    # Assert
    assert (is_ok is True) and (len(refs) == 3)


if __name__ == "__main__":
    import pytest

    pytest.main([os.path.abspath(__file__), "-v"])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/scitex-writer/scripts/python/check_float_order.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # File: scripts/python/check_float_order.py
# # Purpose: Validate and auto-renumber figure/table reference ordering in LaTeX manuscripts
# # Usage:
# #   python check_float_order.py [project_dir] [--fix] [--doc-type manuscript|supplementary]
# #
# # Checks that figures and tables are referenced in numerical order in the text.
# # With --fix, renumbers files and updates all \ref{} and \label{} to match appearance order.
#
# import argparse
# import os
# import re
# import shutil
# import sys
# from collections import OrderedDict
# from pathlib import Path
#
# # ANSI colors
# GREEN = "\033[0;32m"
# YELLOW = "\033[1;33m"
# RED = "\033[0;31m"
# DIM = "\033[0;90m"
# BOLD = "\033[1m"
# NC = "\033[0m"
#
# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/scitex-writer/scripts/python/check_float_order.py
# --------------------------------------------------------------------------------
