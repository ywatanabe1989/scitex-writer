#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ROLE: engine-vendored — DO NOT edit here. `scitex-writer update-project`
# overwrites this file on every re-vendor; fix it upstream in the
# scitex-writer package instead (local edits are lost, and update-project
# may set it read-only in the consumer workspace after vendoring).
# File: scripts/python/check_figure_media.py
# Purpose: Pre-compile FIGURE-MEDIA gate. A manuscript declares a figure by
#          dropping a caption `.tex` file under
#            <doc>/contents/figures/caption_and_media/NN_Name.tex
#          The compile pipeline resolves each declared figure to a rendered
#          media asset (jpg/png/pdf/tif/svg/pptx/mmd/... same numeric prefix,
#          incl. multi-panel figures composed from NN{a,b,...} panels). When a
#          figure is DECLARED but NO media asset exists, the figure pipeline
#          historically substituted a silent "Missing Figure" placeholder JPG
#          (process_figures_modules/04_compilation.src:check_and_create_placeholders)
#          and the compile SUCCEEDED -- a silent degradation the operator wants
#          eliminated.
#
#          This gate scans every declared figure up front, reports ALL figures
#          that have no media (name + expected media path), then exits non-zero
#          so the caller (run_provenance_checks.sh -> compile_*.sh) BLOCKS the
#          compile before the placeholder is ever created. It runs BEFORE
#          process_figures.sh, so at error-level the placeholder code path is
#          never reached; at warn/off the placeholder still fills in (the
#          explicit draft opt-in).
#
#          DEFAULT depends on project type (mirrors check_citations /
#          check_clew_verify): a *research* project (marked by
#          .scitex/dev/config.yaml `project-type: research`) defaults to error
#          -- a research manuscript must never ship a placeholder figure -- and
#          a non-research project (the public template, whose example figures
#          ship without media by design) defaults to warn.
#
#          Severity precedence (highest -> lowest), via the shared _severity
#          resolver:
#            1. --level {off,warn,error} CLI flag
#            2. env SCITEX_WRITER_FIGURE_MEDIA
#            3. project ./config.yaml key figure_media.level
#            4. user ~/.scitex/writer/config.yaml key figure_media.level
#            5. default: error for research projects, else warn
#          Levels:
#            off   -- skip the gate
#            warn  -- report missing figures, exit 0 (does NOT block; the
#                     downstream placeholder fills in for a draft compile)
#            error -- report missing figures, exit 1 (caller blocks the compile)
#
# Usage:
#   python check_figure_media.py [project_dir]
#                                [--doc-type manuscript|supplementary|revision|all]
#                                [--level off|warn|error]
#
# Self-contained: stdlib + optional PyYAML (config files only).

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _severity import resolve_level  # noqa: E402

# ANSI colors (match the sibling check_*.py standalones)
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
DIM = "\033[0;90m"
BOLD = "\033[1m"
NC = "\033[0m"

PASS_COUNT = 0
WARN_COUNT = 0
FAIL_COUNT = 0

_LEVELS = ("off", "warn", "error")

_DOC_DIRS = {
    "manuscript": "01_manuscript",
    "supplementary": "02_supplementary",
    "revision": "03_revision",
}

# Media assets a declared figure can resolve to. The figure pipeline converts
# any of these (pptx/mmd/pdf/tif -> png -> jpg; panels -> composed jpg).
_MEDIA_EXTS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".pdf",
    ".tif",
    ".tiff",
    ".svg",
    ".eps",
    ".gif",
    ".pptx",
    ".mmd",
}

# A declared MAIN figure caption stem: leading digits, optionally `_Name`.
# A PANEL caption/media stem: leading digits + a single lowercase letter (NNa_).
_MAIN_STEM_RE = re.compile(r"^\d+(?:_.*)?$")
_PANEL_STEM_RE = re.compile(r"^\d+[a-z](?:_.*|$)")

_MAX_LIST = 100


def log_pass(msg):
    global PASS_COUNT
    print(f"  {GREEN}[PASS]{NC} {msg}")
    PASS_COUNT += 1


def log_warn(msg):
    global WARN_COUNT
    print(f"  {YELLOW}[WARN]{NC} {msg}")
    WARN_COUNT += 1


def log_fail(msg):
    global FAIL_COUNT
    print(f"  {RED}[FAIL]{NC} {msg}")
    FAIL_COUNT += 1


def log_detail(msg):
    print(f"    {DIM}{msg}{NC}")


def _is_research_project(project_dir):
    """True iff .scitex/dev/config.yaml marks this a ``project-type: research``.

    Mirrors check_citations / check_clew_verify so every gate shares one
    research-mode signal. PyYAML optional; falls back to a textual marker scan.
    """
    cfg = Path(project_dir) / ".scitex" / "dev" / "config.yaml"
    if not cfg.is_file():
        return False
    try:
        text = cfg.read_text(encoding="utf-8")
    except OSError:
        return False
    try:
        import yaml

        data = yaml.safe_load(text) or {}
        if isinstance(data, dict):
            return str(data.get("project-type", "")).strip().lower() == "research"
    except Exception:
        pass
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("project-type:"):
            return stripped.split(":", 1)[1].strip().strip("\"'").lower() == "research"
    return False


def _numeric_prefix(stem):
    """The leading-digit run of a figure stem (e.g. '01_Foo' -> '01')."""
    m = re.match(r"^(\d+)", stem)
    return m.group(1) if m else ""


def _declared_main_figures(media_dir):
    """Return {stem: caption_path} for each DECLARED main figure caption.

    A main figure caption is a ``.tex`` whose stem is leading digits optionally
    followed by ``_Name`` (e.g. ``01.tex`` / ``01_Overview.tex``). Panel
    captions (``01a_...tex``) are NOT independently declared figures -- they are
    media sources for their parent figure -- so they are skipped.
    """
    figures = {}
    for tex in sorted(media_dir.glob("*.tex")):
        stem = tex.stem
        if _PANEL_STEM_RE.match(stem):
            continue
        if not _MAIN_STEM_RE.match(stem):
            continue
        figures[stem] = tex
    return figures


def _has_media(media_dir, stem):
    """True iff some rendered media asset exists for the figure ``stem``.

    Matches (a) a same-stem asset (``01_Foo.png``), (b) a bare numeric-prefix
    asset (``01.jpg``), and (c) any panel asset (``01a_left.png``) that composes
    into the figure -- every asset whose stem begins with the figure's numeric
    prefix followed by a ``_`` / lowercase-letter / end boundary. A broken
    symlink counts as MISSING (``exists()`` follows the link), because the
    pipeline could not render it either.
    """
    prefix = _numeric_prefix(stem)
    if not prefix:
        return False
    # `01` must not match `010...`; require a non-digit boundary after prefix.
    boundary = re.compile(rf"^{re.escape(prefix)}(?:[a-z]|_|$)")
    for asset in media_dir.iterdir():
        if asset.suffix.lower() not in _MEDIA_EXTS:
            continue
        if boundary.match(asset.stem) and asset.exists():
            return True
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Pre-compile figure-media gate: FAIL when a figure is "
        "declared (caption .tex) but has no rendered media asset -- catches the "
        "silent 'Missing Figure' placeholder BEFORE it degrades the PDF. "
        "Defaults to error for research projects, warn otherwise."
    )
    parser.add_argument("project_dir", nargs="?", default=".")
    parser.add_argument(
        "--doc-type",
        choices=[*_DOC_DIRS, "all"],
        default="all",
        help="Which document(s) to scan (default: all present).",
    )
    parser.add_argument(
        "--level",
        choices=list(_LEVELS),
        default=None,
        help="Severity: off, warn, or error. Overrides env and config.",
    )
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    research = _is_research_project(project_dir)
    default = "error" if research else "warn"
    level = resolve_level(
        "figure_media",
        args.level,
        project_dir,
        default=default,
        env_var="SCITEX_WRITER_FIGURE_MEDIA",
    )
    kind = "research" if research else "non-research"
    print(f"\n{BOLD}=== Figure Media Gate (level={level}, {kind}) ==={NC}\n")

    if level == "off":
        print(
            f"  {DIM}[INFO]{NC} figure-media gate is disabled (level=off). "
            f"Set figure_media.level or --level to enable."
        )
        print(
            f"\n{BOLD}Summary:{NC} {GREEN}0 passed{NC}, "
            f"{YELLOW}0 warnings{NC}, {RED}0 errors{NC}"
        )
        return 0

    report = log_fail if level == "error" else log_warn
    doc_types = list(_DOC_DIRS) if args.doc_type == "all" else [args.doc_type]

    any_dir = False
    total = 0
    missing = []
    for doc_type in doc_types:
        media_dir = (
            project_dir
            / _DOC_DIRS[doc_type]
            / "contents"
            / "figures"
            / "caption_and_media"
        )
        if not media_dir.is_dir():
            continue
        any_dir = True
        for stem, caption in sorted(_declared_main_figures(media_dir).items()):
            total += 1
            if not _has_media(media_dir, stem):
                rel = caption.relative_to(project_dir)
                expected = (
                    media_dir.relative_to(project_dir)
                    / f"{stem}.<jpg|png|pdf|tif|svg|pptx|mmd>"
                )
                missing.append((doc_type, str(rel), str(expected)))

    if not any_dir:
        log_pass("no figure caption_and_media directories found to check")
    elif total == 0:
        log_pass("no declared figures found to check")
    elif not missing:
        log_pass(f"all {total} declared figure(s) have rendered media")
    else:
        for doc_type, rel, expected in missing[:_MAX_LIST]:
            report(
                f"{doc_type}: {rel}: figure declared but NO media asset "
                f"(expected {expected})"
            )
        if len(missing) > _MAX_LIST:
            log_detail(f"... and {len(missing) - _MAX_LIST} more")
        log_detail(
            "fix: add the figure's rendered media (jpg/png/pdf/tif/svg/pptx/mmd, "
            "or NN{a,b,...} panels) next to its caption .tex, or remove the "
            "caption if the figure is not used."
        )

    print()
    print(
        f"{BOLD}Summary:{NC} {GREEN}{PASS_COUNT} passed{NC}, "
        f"{YELLOW}{WARN_COUNT} warnings{NC}, {RED}{FAIL_COUNT} errors{NC}"
    )
    return 1 if FAIL_COUNT > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
