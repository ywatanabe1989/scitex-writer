#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: check_paper_symlink.py

import os
import subprocess
import sys
from pathlib import Path

# Add scripts/python to path for imports
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

from check_paper_symlink import compute_divergence  # noqa: E402

_SCRIPT = ROOT_DIR / "scripts" / "python" / "check_paper_symlink.py"


# ============================================================================
# helpers
# ============================================================================


def _make_canonical(tmp_path, files):
    """Create <tmp>/.scitex/writer/ with the given {relpath: content}."""
    canonical = tmp_path / ".scitex" / "writer"
    canonical.mkdir(parents=True)
    for rel, content in files.items():
        p = canonical / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    return canonical


def _run(project, *extra):
    # No env-driven config should leak into the test.
    env = dict(os.environ)
    env.pop("SCITEX_WRITER_PAPER_SYMLINK", None)
    return subprocess.run(
        [sys.executable, str(_SCRIPT), str(project), *extra],
        capture_output=True,
        text=True,
        env=env,
    )


# ============================================================================
# compute_divergence
# ============================================================================


def test_compute_divergence_identical_returns_empty(tmp_path):
    """No divergence when every paper/ file matches canonical by content."""
    # Arrange
    canonical = _make_canonical(tmp_path, {"a.tex": "hello"})
    link = tmp_path / "paper"
    link.mkdir()
    (link / "a.tex").write_text("hello")
    # Act
    diverged = compute_divergence(link, canonical)
    # Assert
    assert diverged == []


def test_compute_divergence_flags_unique_and_differing(tmp_path):
    """Files missing from or differing against canonical are reported."""
    # Arrange
    canonical = _make_canonical(tmp_path, {"a.tex": "hello"})
    link = tmp_path / "paper"
    link.mkdir()
    (link / "a.tex").write_text("CHANGED")
    (link / "new.tex").write_text("only-in-paper")
    # Act
    diverged = compute_divergence(link, canonical)
    # Assert
    assert sorted(diverged) == ["a.tex", "new.tex"]


# ============================================================================
# End-to-end script behaviour (no LaTeX toolchain needed)
# ============================================================================


def _backups(tmp_path):
    return list((tmp_path / ".scitex").glob("writer-paper-backup-*"))


def test_pass_when_paper_is_correct_symlink(tmp_path):
    """A correct paper -> .scitex/writer symlink passes (exit 0)."""
    # Arrange
    _make_canonical(tmp_path, {"a.tex": "x"})
    os.symlink(".scitex/writer", tmp_path / "paper", target_is_directory=True)
    # Act
    proc = _run(tmp_path, "--level", "error")
    # Assert
    assert proc.returncode == 0


def _run_off_with_diverged_dir(tmp_path):
    """level=off over a diverged real paper/ that would otherwise error."""
    _make_canonical(tmp_path, {"a.tex": "x"})
    link = tmp_path / "paper"
    link.mkdir()
    (link / "new.tex").write_text("only-in-paper")
    return _run(tmp_path, "--level", "off")


def test_off_level_exits_zero(tmp_path):
    """level=off disables enforcement -- exit 0 even over a diverged dir."""
    # Arrange
    # Act
    proc = _run_off_with_diverged_dir(tmp_path)
    # Assert
    assert proc.returncode == 0


def test_off_level_reports_disabled(tmp_path):
    """level=off says so explicitly rather than silently doing nothing."""
    # Arrange
    # Act
    proc = _run_off_with_diverged_dir(tmp_path)
    # Assert
    assert "disabled" in proc.stdout


def _run_repair_missing(tmp_path):
    """level=repair when paper is missing and canonical exists."""
    _make_canonical(tmp_path, {"a.tex": "x"})
    proc = _run(tmp_path, "--level", "repair")
    return proc, tmp_path / "paper"


def test_repair_missing_exits_zero(tmp_path):
    # Arrange
    # Act
    proc, _ = _run_repair_missing(tmp_path)
    # Assert
    assert proc.returncode == 0


def test_repair_missing_creates_symlink(tmp_path):
    # Arrange
    # Act
    _, link = _run_repair_missing(tmp_path)
    # Assert
    assert link.is_symlink()


def test_repair_missing_symlink_is_relative(tmp_path):
    # Arrange
    # Act
    _, link = _run_repair_missing(tmp_path)
    # Assert
    assert os.readlink(link) == ".scitex/writer"


def _run_repair_nondiverged(tmp_path):
    """level=repair over a real, non-diverged paper/ dir."""
    _make_canonical(tmp_path, {"a.tex": "same"})
    link = tmp_path / "paper"
    link.mkdir()
    (link / "a.tex").write_text("same")
    return _run(tmp_path, "--level", "repair"), link


def test_repair_nondiverged_exits_zero(tmp_path):
    # Arrange
    # Act
    proc, _ = _run_repair_nondiverged(tmp_path)
    # Assert
    assert proc.returncode == 0


def test_repair_nondiverged_becomes_symlink(tmp_path):
    # Arrange
    # Act
    _, link = _run_repair_nondiverged(tmp_path)
    # Assert
    assert link.is_symlink()


def test_repair_nondiverged_makes_one_backup(tmp_path):
    # Arrange
    # Act
    _run_repair_nondiverged(tmp_path)
    # Assert
    assert len(_backups(tmp_path)) == 1


def test_repair_nondiverged_backup_preserves_content(tmp_path):
    # Arrange
    # Act
    _run_repair_nondiverged(tmp_path)
    # Assert
    assert (_backups(tmp_path)[0] / "a.tex").read_text() == "same"


def _run_diverged_no_force(tmp_path):
    """level=repair (no force) over a DIVERGED real paper/ dir."""
    _make_canonical(tmp_path, {"a.tex": "canonical"})
    link = tmp_path / "paper"
    link.mkdir()
    (link / "a.tex").write_text("DIVERGED")
    (link / "unique.tex").write_text("only-in-paper")
    return _run(tmp_path, "--level", "repair"), link


def test_diverged_no_force_exits_one(tmp_path):
    # Arrange
    # Act
    proc, _ = _run_diverged_no_force(tmp_path)
    # Assert
    assert proc.returncode == 1


def test_diverged_no_force_leaves_real_dir(tmp_path):
    # Arrange
    # Act
    _, link = _run_diverged_no_force(tmp_path)
    # Assert
    assert link.is_dir() and not link.is_symlink()


def test_diverged_no_force_preserves_unique_content(tmp_path):
    # Arrange
    # Act
    _, link = _run_diverged_no_force(tmp_path)
    # Assert
    assert (link / "unique.tex").read_text() == "only-in-paper"


def test_diverged_no_force_makes_no_backup(tmp_path):
    # Arrange
    # Act
    _run_diverged_no_force(tmp_path)
    # Assert
    assert not _backups(tmp_path)


def _run_diverged_force(tmp_path):
    """level=repair --force-after-backup over a DIVERGED real paper/ dir."""
    _make_canonical(tmp_path, {"a.tex": "canonical"})
    link = tmp_path / "paper"
    link.mkdir()
    (link / "unique.tex").write_text("only-in-paper")
    return _run(tmp_path, "--level", "repair", "--force-after-backup"), link


def test_diverged_force_exits_zero(tmp_path):
    # Arrange
    # Act
    proc, _ = _run_diverged_force(tmp_path)
    # Assert
    assert proc.returncode == 0


def test_diverged_force_becomes_symlink(tmp_path):
    # Arrange
    # Act
    _, link = _run_diverged_force(tmp_path)
    # Assert
    assert link.is_symlink()


def test_diverged_force_makes_one_backup(tmp_path):
    # Arrange
    # Act
    _run_diverged_force(tmp_path)
    # Assert
    assert len(_backups(tmp_path)) == 1


def test_diverged_force_preserves_unique_content(tmp_path):
    # Arrange
    # Act
    _run_diverged_force(tmp_path)
    # Assert
    assert (_backups(tmp_path)[0] / "unique.tex").read_text() == "only-in-paper"
