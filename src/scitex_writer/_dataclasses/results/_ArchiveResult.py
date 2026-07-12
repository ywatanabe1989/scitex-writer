#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_dataclasses/results/_ArchiveResult.py

"""ArchiveResult - outcome of one run of the compiled-output archive pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ArchiveResult:
    """Result of snapshotting the compiled outputs into the versions directory.

    An archive is only taken on a CLEAN working tree -- a snapshot stamped with a
    commit hash it does not actually contain would be a lie. A dirty tree is a
    ``skipped=True`` success carrying ``skip_reason``, never a silent no-op.
    """

    success: bool
    """Whether the archive run completed."""

    archive_id: Optional[str] = None
    """The snapshot identifier ``YYYYmmdd-HHMMSS_<short7>``."""

    archived: List[dict] = field(default_factory=list)
    """One ``{source, archived, current}`` entry per file actually copied."""

    versions_dir: Optional[str] = None
    """Absolute path of the directory the snapshot was written to."""

    missing: List[str] = field(default_factory=list)
    """Configured outputs that did not exist (e.g. no diff PDF was built)."""

    skipped: bool = False
    """True when nothing was archived (dirty tree, or the caller opted out)."""

    skip_reason: Optional[str] = None
    """Why the run was skipped; set iff ``skipped`` is True."""

    error: Optional[str] = None
    """Actionable error message when ``success`` is False; else None."""

    def to_dict(self) -> dict:
        """Plain dict for JSON serialization across the CLI / MCP boundary."""
        return {
            "success": self.success,
            "archive_id": self.archive_id,
            "archived": self.archived,
            "versions_dir": self.versions_dir,
            "missing": self.missing,
            "skipped": self.skipped,
            "skip_reason": self.skip_reason,
            "error": self.error,
        }

    def validate(self) -> None:
        """Raise ValueError on an internally inconsistent result (fail-loud).

        A skip must say WHY; a non-skipped success must carry the archive id it
        stamped the snapshot with; and a skipped run must not claim archived files.
        """
        if self.success and self.error:
            raise ValueError("ArchiveResult success=True but error is set")
        if not self.success and not self.error:
            raise ValueError("ArchiveResult success=False but no error message")
        if self.skipped and not self.skip_reason:
            raise ValueError("ArchiveResult skipped=True but no skip_reason given")
        if self.skipped and self.archived:
            raise ValueError(
                f"ArchiveResult skipped=True but {len(self.archived)} files "
                "were archived (the two are mutually exclusive)"
            )
        if self.success and not self.skipped and not self.archive_id:
            raise ValueError(
                "ArchiveResult success=True but no archive_id (every snapshot is "
                "stamped with its timestamp + commit hash)"
            )

    def __str__(self) -> str:
        if not self.success:
            return f"Archive FAILED: {self.error}"
        if self.skipped:
            return f"Archive: skipped ({self.skip_reason})"
        return (
            f"Archive {self.archive_id}: {len(self.archived)} files -> "
            f"{self.versions_dir}"
        )


__all__ = ["ArchiveResult"]

# EOF
