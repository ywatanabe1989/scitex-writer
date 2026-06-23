#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: check_overflow.py

import subprocess
import sys
from pathlib import Path

# Add scripts/python to path for imports
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

from check_overflow import (  # noqa: E402
    load_overflow_config,
    parse_overflows,
)

_SCRIPT = ROOT_DIR / "scripts" / "python" / "check_overflow.py"

_TABLE_LOG = "Overfull \\hbox (31.07352pt too wide) in alignment at lines 120--145\n"
_PAGE_LOG = "Overfull \\vbox (40.0pt too high) has occurred while \\output is active\n"


# ============================================================================
# parse_overflows
# ============================================================================


def test_parse_overflows_table_box_context_is_alignment():
    """A wide tabular is reported with the alignment (table) context."""
    # Arrange
    log = _TABLE_LOG
    # Act
    boxes = parse_overflows(log, 5.0)
    # Assert
    assert boxes[0]["context"] == "alignment"


def test_parse_overflows_table_box_keeps_line_range():
    """The source line range of a wide tabular is preserved."""
    # Arrange
    log = _TABLE_LOG
    # Act
    boxes = parse_overflows(log, 5.0)
    # Assert
    assert boxes[0]["lines"] == "120--145"


def test_parse_overflows_table_box_extracts_points():
    """The overflow magnitude in points is parsed as a float."""
    # Arrange
    log = _TABLE_LOG
    # Act
    boxes = parse_overflows(log, 5.0)
    # Assert
    assert abs(boxes[0]["pts"] - 31.07352) < 0.001


def test_parse_overflows_skips_cosmetic_below_threshold():
    """A box overflowing by less than min_pt is ignored as cosmetic."""
    # Arrange
    log = "Overfull \\hbox (2.05426pt too wide) in paragraph at lines 5--6\n"
    # Act
    boxes = parse_overflows(log, 5.0)
    # Assert
    assert boxes == []


def test_parse_overflows_dedupes_repeated_boxes():
    """A box repeated across compile passes is reported once."""
    # Arrange
    log = _TABLE_LOG * 3
    # Act
    boxes = parse_overflows(log, 5.0)
    # Assert
    assert len(boxes) == 1


def test_parse_overflows_vbox_kind_is_v():
    """An over-tall box is parsed as a vbox."""
    # Arrange
    log = _PAGE_LOG
    # Act
    boxes = parse_overflows(log, 5.0)
    # Assert
    assert boxes[0]["kind"] == "v"


def test_parse_overflows_vbox_classified_as_page():
    """A vbox with no line range is classified as a page overflow."""
    # Arrange
    log = _PAGE_LOG
    # Act
    boxes = parse_overflows(log, 5.0)
    # Assert
    assert boxes[0]["context"] == "page"


# ============================================================================
# load_overflow_config
# ============================================================================


def test_load_overflow_config_reads_strict(tmp_path):
    """load_overflow_config reads the strict flag from the block."""
    # Arrange
    cfg = tmp_path / "config_manuscript.yaml"
    cfg.write_text("overflow:\n  strict: true\n  max_pt: 3.0\n")
    # Act
    out = load_overflow_config(cfg)
    # Assert
    assert out["strict"] is True


def test_load_overflow_config_reads_max_pt(tmp_path):
    """load_overflow_config reads the max_pt threshold from the block."""
    # Arrange
    cfg = tmp_path / "config_manuscript.yaml"
    cfg.write_text("overflow:\n  strict: true\n  max_pt: 3.0\n")
    # Act
    out = load_overflow_config(cfg)
    # Assert
    assert out["max_pt"] == 3.0


def test_load_overflow_config_no_block_returns_empty(tmp_path):
    """load_overflow_config returns {} when there is no overflow: block."""
    # Arrange
    cfg = tmp_path / "config_manuscript.yaml"
    cfg.write_text("limits:\n  strict: false\n")
    # Act
    out = load_overflow_config(cfg)
    # Assert
    assert out == {}


def test_load_overflow_config_bad_shape_returns_none(tmp_path):
    """load_overflow_config fails loud (None) when overflow: is not a mapping."""
    # Arrange
    cfg = tmp_path / "config_manuscript.yaml"
    cfg.write_text("overflow:\n  - 1\n  - 2\n")
    # Act
    out = load_overflow_config(cfg)
    # Assert
    assert out is None


# ============================================================================
# End-to-end script behaviour (reads a .log; no LaTeX toolchain needed)
# ============================================================================


def _make_project_with_log(tmp_path, strict, overfull_pt):
    config = tmp_path / "config"
    config.mkdir()
    logs = tmp_path / "01_manuscript" / "logs"
    logs.mkdir(parents=True)
    (logs / "manuscript.log").write_text(
        f"Overfull \\hbox ({overfull_pt}pt too wide) in alignment at lines 10--20\n"
    )
    (config / "config_manuscript.yaml").write_text(
        f"overflow:\n  strict: {str(strict).lower()}\n  max_pt: 5.0\n"
    )
    return tmp_path


def _run(project):
    return subprocess.run(
        [sys.executable, str(_SCRIPT), str(project)],
        capture_output=True,
        text=True,
    )


def test_check_overflow_strict_exits_nonzero_when_overflowing(tmp_path):
    """Strict mode returns a non-zero exit when a box overflows past max_pt."""
    # Arrange
    project = _make_project_with_log(tmp_path, strict=True, overfull_pt="40.0")
    # Act
    proc = _run(project)
    # Assert
    assert proc.returncode == 1


def test_check_overflow_nonstrict_exits_zero(tmp_path):
    """Non-strict mode still exits zero on an overflow (warning only)."""
    # Arrange
    project = _make_project_with_log(tmp_path, strict=False, overfull_pt="40.0")
    # Act
    proc = _run(project)
    # Assert
    assert proc.returncode == 0


def test_check_overflow_nonstrict_reports_too_wide(tmp_path):
    """Non-strict mode names the overflow in its output."""
    # Arrange
    project = _make_project_with_log(tmp_path, strict=False, overfull_pt="40.0")
    # Act
    proc = _run(project)
    # Assert
    assert "too wide" in proc.stdout
