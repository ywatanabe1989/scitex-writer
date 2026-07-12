#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_dataclasses/results/_FiguresResult.py

"""FiguresResult - outcome of one run of the image -> LaTeX figure pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class FiguresResult:
    """Result of processing every figure of one document type.

    Counts are what ACTUALLY happened during this run, never a request total, and
    are never negative. ``figures`` carries one entry per compiled figure
    (``{name, number, image, tex, placeholder, caption_generated}``).
    ``fallback_header`` is True when NO real figure existed and the comment-only
    ``00_Figures_Header.tex`` was emitted instead (it renders no figure float).
    ``warnings`` carries non-fatal findings the shell echoed to the terminal and
    then lost -- chiefly an orphan user-placed JPG in ``jpg_for_compilation``
    with no ``caption_and_media`` source to regenerate it from.
    """

    success: bool
    """Whether the pipeline completed."""

    figures_compiled: int = 0
    """Number of figures rendered into the compiled directory."""

    captions_created: int = 0
    """Number of default caption files written for figures lacking one."""

    panel_captions_removed: int = 0
    """Number of stray panel caption files deleted (panels must not have one)."""

    renamed_panels: int = 0
    """Number of uppercase panel ids lowercased (``01A_`` -> ``01a_``)."""

    converted: int = 0
    """Number of format conversions performed (TIF->PNG, MMD->PNG, PNG->JPG)."""

    composed: int = 0
    """Number of multi-panel figures tiled into a single composite image."""

    placeholders_created: int = 0
    """Number of missing figures filled with a placeholder JPG."""

    cropped: int = 0
    """Number of compilation JPGs whose uniform border was trimmed."""

    figures: List[dict] = field(default_factory=list)
    """Per-figure outcomes, ordered by figure number."""

    compiled_file: Optional[str] = None
    """Absolute path of the gathered FINAL.tex (the file the manuscript inputs)."""

    figures_enabled: bool = False
    """True when the ``.figures_enabled`` marker was written (at least one JPG)."""

    fallback_header: bool = False
    """True when no real figure existed: a comment-only header was emitted."""

    skipped: bool = False
    """True when image processing was skipped (the shell's ``--no_figs``)."""

    warnings: List[str] = field(default_factory=list)
    """Non-fatal findings surfaced to the caller instead of echoed and lost."""

    error: Optional[str] = None
    """Actionable error message when ``success`` is False; else None."""

    _COUNTS = (
        "figures_compiled",
        "captions_created",
        "panel_captions_removed",
        "renamed_panels",
        "converted",
        "composed",
        "placeholders_created",
        "cropped",
    )

    def to_dict(self) -> dict:
        """Plain dict for JSON serialization across the CLI / MCP boundary."""
        return {
            "success": self.success,
            "figures_compiled": self.figures_compiled,
            "captions_created": self.captions_created,
            "panel_captions_removed": self.panel_captions_removed,
            "renamed_panels": self.renamed_panels,
            "converted": self.converted,
            "composed": self.composed,
            "placeholders_created": self.placeholders_created,
            "cropped": self.cropped,
            "figures": self.figures,
            "compiled_file": self.compiled_file,
            "figures_enabled": self.figures_enabled,
            "fallback_header": self.fallback_header,
            "skipped": self.skipped,
            "warnings": self.warnings,
            "error": self.error,
        }

    def validate(self) -> None:
        """Raise ValueError on an internally inconsistent result (fail-loud).

        A success carries no error and only non-negative counts; a failure must
        carry an error message; and a fallback header is only legitimate when no
        figure was compiled (the two are mutually exclusive by construction).
        """
        if self.success and self.error:
            raise ValueError("FiguresResult success=True but error is set")
        if not self.success and not self.error:
            raise ValueError("FiguresResult success=False but no error message")
        for name in self._COUNTS:
            value = getattr(self, name)
            if not isinstance(value, int) or value < 0:
                raise ValueError(
                    f"FiguresResult {name} must be a non-negative int, got {value!r}"
                )
        if self.fallback_header and self.figures_compiled:
            raise ValueError(
                "FiguresResult fallback_header=True but figures_compiled="
                f"{self.figures_compiled} (the fallback is the NO-figures branch)"
            )

    def __str__(self) -> str:
        if not self.success:
            return f"Figures FAILED: {self.error}"
        if self.skipped:
            return "Figures: skipped (--no-figs)"
        if self.fallback_header:
            return "Figures: none found -- comment-only fallback header emitted"
        return (
            f"Figures: compiled={self.figures_compiled}, "
            f"captions_created={self.captions_created}, "
            f"converted={self.converted}, composed={self.composed}, "
            f"placeholders={self.placeholders_created}"
        )


__all__ = ["FiguresResult"]

# EOF
