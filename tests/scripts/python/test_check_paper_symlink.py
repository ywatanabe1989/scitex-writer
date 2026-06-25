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


def test_pass_when_paper_is_correct_symlink(tmp_path):
    """A correct paper -> .scitex/writer symlink passes (exit 0)."""
    # Arrange
    _make_canonical(tmp_path, {"a.tex": "x"})
    os.symlink(".scitex/writer", tmp_path / "paper", target_is_directory=True)
    # Act
    proc = _run(tmp_path, "--level", "error")
    # Assert
    assert proc.returncode == 0


def test_off_level_is_noop(tmp_path):
    """level=off disables the check entirely (exit 0, no enforcement)."""
    # Arrange: a diverged real dir that would otherwise be an error.
    canonical = _make_canonical(tmp_path, {"a.tex": "x"})  # noqa: F841
    link = tmp_path / "paper"
    link.mkdir()
    (link / "new.tex").write_text("only-in-paper")
    # Act
    proc = _run(tmp_path, "--level", "off")
    # Assert
    assert proc.returncode == 0
    assert "disabled" in proc.stdout


def test_repair_creates_symlink_when_missing(tmp_path):
    """level=repair creates the symlink when paper is missing & canonical exists."""
    # Arrange
    _make_canonical(tmp_path, {"a.tex": "x"})
    # Act
    proc = _run(tmp_path, "--level", "repair")
    # Assert
    link = tmp_path / "paper"
    assert proc.returncode == 0
    assert link.is_symlink()
    assert os.readlink(link) == ".scitex/writer"


def test_repair_converts_nondiverged_real_dir_with_backup(tmp_path):
    """A real, non-diverged paper/ is backed up then replaced by a symlink."""
    # Arrange
    _make_canonical(tmp_path, {"a.tex": "same"})
    link = tmp_path / "paper"
    link.mkdir()
    (link / "a.tex").write_text("same")
    # Act
    proc = _run(tmp_path, "--level", "repair")
    # Assert
    assert proc.returncode == 0
    assert link.is_symlink()
    backups = list((tmp_path / ".scitex").glob("writer-paper-backup-*"))
    assert len(backups) == 1
    assert (backups[0] / "a.tex").read_text() == "same"


def test_diverged_repair_without_force_refuses(tmp_path):
    """Diverged real paper/ under repair (no force) refuses: no symlink, dir intact."""
    # Arrange
    _make_canonical(tmp_path, {"a.tex": "canonical"})
    link = tmp_path / "paper"
    link.mkdir()
    (link / "a.tex").write_text("DIVERGED")
    (link / "unique.tex").write_text("only-in-paper")
    # Act
    proc = _run(tmp_path, "--level", "repair")
    # Assert
    assert proc.returncode == 1
    assert link.is_dir() and not link.is_symlink()
    assert (link / "unique.tex").read_text() == "only-in-paper"
    assert not list((tmp_path / ".scitex").glob("writer-paper-backup-*"))


def test_diverged_force_after_backup_preserves_and_links(tmp_path):
    """Diverged paper/ with --force-after-backup is moved to backup, then symlinked."""
    # Arrange
    _make_canonical(tmp_path, {"a.tex": "canonical"})
    link = tmp_path / "paper"
    link.mkdir()
    (link / "unique.tex").write_text("only-in-paper")
    # Act
    proc = _run(tmp_path, "--level", "repair", "--force-after-backup")
    # Assert
    assert proc.returncode == 0
    assert link.is_symlink()
    backups = list((tmp_path / ".scitex").glob("writer-paper-backup-*"))
    assert len(backups) == 1
    # Diverged content preserved -- nothing lost.
    assert (backups[0] / "unique.tex").read_text() == "only-in-paper"
