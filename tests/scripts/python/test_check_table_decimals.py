#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: check_table_decimals.py
#
# The decimal-consistency safety-net lint (card writer-table-decimal-alignment
# SECONDARY). Pure stdlib -- it parses the COMPILED table .tex, so no pandas /
# LaTeX toolchain is needed and every test runs in the agent container.

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

from check_table_decimals import (  # noqa: E402
    _cell_decimals,
    _inconsistent_columns,
    resolve_level,
)

_SCRIPT = ROOT_DIR / "scripts" / "python" / "check_table_decimals.py"

_COMPILED = "01_manuscript/contents/tables/compiled"


# ============================================================================
# helpers / fixtures
# ============================================================================


def _write(tmp_path, rel, content):
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


def _tabular(header, rows, spec="rr"):
    """Wrap header + data rows in a minimal compiled tabular block."""
    body = [f"\\begin{{tabular}}{{{spec}}}", "\\toprule", header + " \\\\", "\\midrule"]
    body += [r + " \\\\" for r in rows]
    body += ["\\bottomrule", "\\end{tabular}"]
    return "\n".join(body) + "\n"


def _write_table(tmp_path, name, tabular):
    return _write(tmp_path, f"{_COMPILED}/{name}", tabular)


def _run(project, *extra):
    env = dict(os.environ)
    env.pop("SCITEX_WRITER_TABLE_DECIMALS", None)
    return subprocess.run(
        [sys.executable, str(_SCRIPT), str(project), *extra],
        capture_output=True,
        text=True,
        env=env,
    )


@pytest.fixture
def clean_env():
    saved = {k: os.environ.get(k) for k in ("SCITEX_WRITER_TABLE_DECIMALS", "HOME")}
    os.environ.pop("SCITEX_WRITER_TABLE_DECIMALS", None)
    with tempfile.TemporaryDirectory() as home:
        os.environ["HOME"] = home
        yield home
    for key, val in saved.items():
        if val is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = val


# ============================================================================
# unit: _cell_decimals
# ============================================================================


def test_cell_decimals_counts_fraction():
    """A clean decimal cell returns its decimal-place count."""
    # Arrange
    cell = "0.350"
    # Act
    got = _cell_decimals(cell)
    # Assert
    assert got == 3


def test_cell_decimals_integer_is_zero():
    """A clean integer cell has zero decimal places."""
    # Arrange
    cell = "288"
    # Act
    got = _cell_decimals(cell)
    # Assert
    assert got == 0


def test_cell_decimals_unwraps_textbf():
    """A \\textbf-wrapped numeric cell is still read as a number."""
    # Arrange
    cell = "\\textbf{0.35}"
    # Act
    got = _cell_decimals(cell)
    # Assert
    assert got == 2


def test_cell_decimals_strips_rowcolor_prefix():
    """A leading \\rowcolor directive on the first cell is ignored."""
    # Arrange
    cell = "\\rowcolor{lightgray} 0.5"
    # Act
    got = _cell_decimals(cell)
    # Assert
    assert got == 1


def test_cell_decimals_math_is_none():
    """A math/verbatim cell is not a plain number (returns None)."""
    # Arrange
    cell = "$p<0.001$"
    # Act
    got = _cell_decimals(cell)
    # Assert
    assert got is None


def test_cell_decimals_missing_marker_is_none():
    """The missing-value marker is not numeric (returns None)."""
    # Arrange
    cell = "--"
    # Act
    got = _cell_decimals(cell)
    # Assert
    assert got is None


# ============================================================================
# unit: _inconsistent_columns
# ============================================================================


def _body(header, rows, spec="rr"):
    """The tabular body (between \\begin/\\end) for the column-analysis unit tests."""
    tab = _tabular(header, rows, spec=spec)
    return tab.split(f"\\begin{{tabular}}{{{spec}}}\n", 1)[1]


def test_inconsistent_column_detected():
    """A column mixing 0.333 and 0.35 is flagged as inconsistent."""
    # Arrange
    body = _body("\\textbf{P} & \\textbf{AUC}", ["P05 & 0.333", "P12 & 0.35"])
    # Act
    reports = _inconsistent_columns(body)
    # Assert
    assert reports == [(1, [2, 3])]


def test_aligned_column_not_flagged():
    """A column already padded uniform (0.333 / 0.350) is not flagged."""
    # Arrange
    body = _body("\\textbf{P} & \\textbf{AUC}", ["P05 & 0.333", "P12 & 0.350"])
    # Act
    reports = _inconsistent_columns(body)
    # Assert
    assert reports == []


def test_all_integer_column_not_flagged():
    """An all-integer count column (5 / 288) stays bare -- never flagged."""
    # Arrange
    body = _body("\\textbf{P} & \\textbf{N}", ["P05 & 5", "P12 & 288"])
    # Act
    reports = _inconsistent_columns(body)
    # Assert
    assert reports == []


def test_mixed_text_number_column_not_flagged():
    """A column with a non-numeric cell is ineligible (no false positive)."""
    # Arrange
    body = _body("\\textbf{P} & \\textbf{AUC}", ["P05 & 0.333", "P12 & n/a"])
    # Act
    reports = _inconsistent_columns(body)
    # Assert
    assert reports == []


# ============================================================================
# resolve_level
# ============================================================================


def test_resolve_level_default_warn(tmp_path, clean_env):
    """The lint defaults to warn (a safety net; it never blocks by default)."""
    # Arrange
    # Act
    level = resolve_level(
        "table_decimals",
        None,
        str(tmp_path),
        default="warn",
        env_var="SCITEX_WRITER_TABLE_DECIMALS",
    )
    # Assert
    assert level == "warn"


def test_env_knob_escalates_to_error(tmp_path, clean_env):
    """The SCITEX_WRITER_TABLE_DECIMALS env knob overrides the default to error."""
    # Arrange
    os.environ["SCITEX_WRITER_TABLE_DECIMALS"] = "error"
    try:
        # Act
        level = resolve_level(
            "table_decimals",
            None,
            str(tmp_path),
            default="warn",
            env_var="SCITEX_WRITER_TABLE_DECIMALS",
        )
    finally:
        os.environ.pop("SCITEX_WRITER_TABLE_DECIMALS", None)
    # Assert
    assert level == "error"


# ============================================================================
# End-to-end (no LaTeX toolchain / pandas needed)
# ============================================================================


def test_inconsistent_table_warns_but_does_not_block(tmp_path, clean_env):
    """Default (warn): an inconsistent column reports but exits 0."""
    # Arrange
    _write_table(
        tmp_path,
        "01_auc.tex",
        _tabular("\\textbf{P} & \\textbf{AUC}", ["P05 & 0.333", "P12 & 0.35"]),
    )
    # Act
    proc = _run(tmp_path)
    # Assert
    assert proc.returncode == 0


def test_inconsistent_table_emits_warning(tmp_path, clean_env):
    """The inconsistent column is reported loudly (one warning)."""
    # Arrange
    _write_table(
        tmp_path,
        "01_auc.tex",
        _tabular("\\textbf{P} & \\textbf{AUC}", ["P05 & 0.333", "P12 & 0.35"]),
    )
    # Act
    proc = _run(tmp_path)
    # Assert
    assert "1 warnings" in proc.stdout


def test_inconsistent_table_blocks_at_error(tmp_path, clean_env):
    """At --level error an inconsistent column blocks (exit 1)."""
    # Arrange
    _write_table(
        tmp_path,
        "01_auc.tex",
        _tabular("\\textbf{P} & \\textbf{AUC}", ["P05 & 0.333", "P12 & 0.35"]),
    )
    # Act
    proc = _run(tmp_path, "--level", "error")
    # Assert
    assert proc.returncode == 1


def test_aligned_table_passes(tmp_path, clean_env):
    """A compiled table already padded uniform passes (exit 0)."""
    # Arrange
    _write_table(
        tmp_path,
        "01_auc.tex",
        _tabular("\\textbf{P} & \\textbf{AUC}", ["P05 & 0.333", "P12 & 0.350"]),
    )
    # Act
    proc = _run(tmp_path, "--level", "error")
    # Assert
    assert proc.returncode == 0


def test_header_fallback_file_ignored(tmp_path, clean_env):
    """The 00_Tables_Header.tex fallback (no tabular) is not scanned."""
    # Arrange
    _write(tmp_path, f"{_COMPILED}/00_Tables_Header.tex", "%% No tables present.\n")
    # Act
    proc = _run(tmp_path)
    # Assert
    assert "no compiled table .tex found to check" in proc.stdout


def test_off_level_skips(tmp_path, clean_env):
    """--level off disables the lint even with an inconsistent column (exit 0)."""
    # Arrange
    _write_table(
        tmp_path,
        "01_auc.tex",
        _tabular("\\textbf{P} & \\textbf{AUC}", ["P05 & 0.333", "P12 & 0.35"]),
    )
    # Act
    proc = _run(tmp_path, "--level", "off")
    # Assert
    assert proc.returncode == 0


def test_off_level_prints_loud_disabled_note(tmp_path, clean_env):
    """--level off is not silent: it prints a loud DISABLED (level=off) note."""
    # Arrange
    _write_table(
        tmp_path,
        "01_auc.tex",
        _tabular("\\textbf{P} & \\textbf{AUC}", ["P05 & 0.333", "P12 & 0.35"]),
    )
    # Act
    proc = _run(tmp_path, "--level", "off")
    # Assert
    assert "DISABLED (level=off)" in proc.stdout


def test_no_tables_passes(tmp_path, clean_env):
    """A project with no compiled tables passes cleanly (exit 0)."""
    # Arrange
    _write(tmp_path, "01_manuscript/contents/results.tex", "Body.\n")
    # Act
    proc = _run(tmp_path)
    # Assert
    assert proc.returncode == 0
