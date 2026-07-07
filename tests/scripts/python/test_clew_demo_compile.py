#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: the clew tooltip smoke -- compile demo/clew_demo.tex under
# pdflatex and assert the produced PDF carries pdfcomment \pdftooltip
# annotations (the static-PDF provenance tooltips).
#
# Style: no mocks (STX-NM002) -- a REAL pdflatex compile of the REAL demo;
# one behavioral assert per test (STX-TQ007); explicit AAA markers (STX-TQ002).
#
# pdfcomment's \pdftooltip emits a form-field WIDGET annotation whose /TU
# ("user name") carries the tooltip text -- the standard mechanism for
# static-PDF tooltips that Adobe Reader / pdf.js surface on hover. It is
# tectonic-safe by construction (no shell-escape, hyperref-only); this smoke
# uses pdflatex because tectonic is not present in every environment.

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
DEMO_TEX = ROOT_DIR / "demo" / "clew_demo.tex"

pytestmark = pytest.mark.skipif(
    shutil.which("pdflatex") is None, reason="pdflatex not available"
)


def _decode_tu(raw):
    """Return the decoded /TU tooltip strings from a decompressed PDF byte
    stream (literal ``(...)`` or UTF-16BE hex ``<...>`` PDF-string forms)."""
    out = []
    for m in re.findall(rb"/TU\s*(<[0-9A-Fa-f]+>|\([^)]*\))", raw):
        if m.startswith(b"<"):
            out.append(
                bytes.fromhex(m[1:-1].decode())
                .decode("utf-16-be", "replace")
                .replace("﻿", "")
            )
        else:
            out.append(m[1:-1].decode("latin1"))
    return out


@pytest.fixture
def compiled_demo(tmp_path):
    """Compile demo/clew_demo.tex twice (hyperref) into a tmp dir; yield the
    return code plus the decompressed PDF bytes so the annotation checks can
    inspect the tooltip widgets without depending on stream compression.

    Function-scoped and yield-based on purpose: it mutates state (runs
    pdflatex, writes files) and acquires an external resource (subprocess),
    so a session/module fixture returning the artifact would violate
    STX-TQ004/TQ005. tmp_path auto-cleans after each test."""
    out_dir = tmp_path
    cmd = [
        "pdflatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-output-directory={out_dir}",
        str(DEMO_TEX),
    ]
    proc = None
    for _ in range(2):
        proc = subprocess.run(cmd, cwd=ROOT_DIR, capture_output=True, text=True)
    pdf = out_dir / "clew_demo.pdf"
    raw = b""
    if pdf.exists():
        fitz = pytest.importorskip("fitz")
        doc = fitz.open(str(pdf))
        expanded = out_dir / "expanded.pdf"
        doc.save(str(expanded), expand=255, deflate=False)
        raw = expanded.read_bytes()
    yield {"returncode": proc.returncode, "pdf": pdf, "raw": raw}


class TestClewDemoTooltips:
    def test_pdflatex_exits_clean(self, compiled_demo):
        # Arrange
        rc = compiled_demo["returncode"]
        # Act
        clean = rc == 0
        # Assert
        assert clean

    def test_pdf_is_produced(self, compiled_demo):
        # Arrange
        pdf = compiled_demo["pdf"]
        # Act
        exists = pdf.exists()
        # Assert
        assert exists

    def test_pdf_contains_tooltip_widget_annotations(self, compiled_demo):
        # Arrange: pdfcomment \pdftooltip -> /Subtype/Widget annotations.
        raw = compiled_demo["raw"]
        # Act
        match = re.search(rb"/Subtype\s*/Widget", raw)
        # Assert
        assert match is not None

    def test_tooltip_text_carries_the_source_pointer(self, compiled_demo):
        # Arrange
        tooltips = _decode_tu(compiled_demo["raw"])
        # Act: at least one tooltip shows "... source: <path>".
        has_source = any("source:" in t for t in tooltips)
        # Assert
        assert has_source

    def test_linkless_claim_tooltip_degrades_to_status_only(self, compiled_demo):
        # Arrange: the exception claim has no link -> status-only tooltip.
        tooltips = _decode_tu(compiled_demo["raw"])
        # Act
        status_only = "exception" in tooltips
        # Assert
        assert status_only


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))

# EOF
