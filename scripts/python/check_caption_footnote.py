#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: scripts/python/check_caption_footnote.py
# Purpose: Catch \footnote (and \footnotetext used as an in-caption workaround)
#          inside a \caption{} at LINT time, before compile.
#
#          \footnote inside \caption{} is a fatal LaTeX pattern: the caption
#          argument is reprocessed (list-of-figures + heading), which yields
#          "Argument of \caption@ydblarg has an extra }" and a runaway
#          \@xfootnote -- fatal inside figure*/table* spanning floats. The
#          blessed pattern is \caption[short]{long\protect\footnotemark} with
#          \footnotetext AFTER the float, so \footnotemark in a caption is SAFE
#          and is NOT flagged here.
#
#          Two detection modes:
#            - caption_and_media/*.tex : the WHOLE file is the caption body the
#              engine wraps in \caption{}, so any \footnote/\footnotetext in it
#              is in-caption.
#            - other source *.tex      : brace-match each \caption{...} arg and
#              flag \footnote/\footnotetext within it.
#          The generated assembled doc (e.g. 01_manuscript/manuscript.tex) is
#          NOT scanned -- it duplicates the sources above and is a build
#          artifact; scanning sources keeps this a pre-compile lint.
#
#          Severity is a user-level knob:
#            off    -- check disabled
#            warn   -- report as a warning (exit 0)
#            error  -- report as an error (exit 1)   [DEFAULT]
#          Default is error because the pattern is always a fatal compile bug;
#          a clean manuscript never triggers it.
#
#          Severity precedence (highest -> lowest):
#            1. --level {off,warn,error} CLI flag
#            2. env SCITEX_WRITER_CAPTION_FOOTNOTE
#            3. project ./config.yaml key caption_footnote.level
#            4. user-wide ~/.scitex/writer/config.yaml key caption_footnote.level
#            5. default error
#
# Usage:
#   python check_caption_footnote.py [project_dir]
#                                    [--doc-type manuscript|supplementary|revision|all]
#                                    [--level off|warn|error]
#
# Self-contained: stdlib + optional PyYAML (only to read config files).

import argparse
import os
import re
import sys
from pathlib import Path

# ANSI colors (match check_media_provenance.py / check_paper_symlink.py)
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
_DEFAULT_LEVEL = "error"

_DOC_DIRS = {
    "manuscript": "01_manuscript",
    "supplementary": "02_supplementary",
    "revision": "03_revision",
}

# \footnote and \footnotetext, but NOT \footnotemark (the blessed in-caption
# pattern). The negative lookahead rejects a following letter, so \footnotemark
# (\footnote + "mark") is excluded while \footnote{ / \footnote[ / \footnotetext
# match.
_FOOTNOTE_RE = re.compile(r"\\footnote(?:text)?(?![A-Za-z])")
_CAPTION_RE = re.compile(r"\\caption\b")

_MAX_LIST = 50


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


def _read_block(config_path):
    """Read the ``caption_footnote`` mapping from a YAML config, or ``{}``."""
    if not config_path.exists():
        return {}
    try:
        import yaml
    except ImportError:
        return {}
    try:
        data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}
    block = data.get("caption_footnote")
    return block if isinstance(block, dict) else {}


def _config_blocks(project_dir):
    proj = _read_block(Path(project_dir) / "config.yaml")
    user = _read_block(Path.home() / ".scitex" / "writer" / "config.yaml")
    return proj, user


def resolve_level(cli_level, proj_block, user_block):
    """Resolve the effective severity level via the documented precedence."""
    if cli_level:
        return cli_level.lower()
    env = os.environ.get("SCITEX_WRITER_CAPTION_FOOTNOTE", "").strip().lower()
    if env in _LEVELS:
        return env
    for block in (proj_block, user_block):
        level = block.get("level")
        if isinstance(level, str) and level.lower() in _LEVELS:
            return level.lower()
    return _DEFAULT_LEVEL


def _strip_comments(text):
    """Blank out LaTeX comments (unescaped % to EOL) while preserving newlines
    and column offsets, so line/col reporting stays accurate."""
    out = []
    for line in text.splitlines(keepends=True):
        i = 0
        cut = None
        while i < len(line):
            ch = line[i]
            if ch == "\\":
                i += 2  # escaped char (incl. \%); skip both
                continue
            if ch == "%":
                cut = i
                break
            i += 1
        if cut is None:
            out.append(line)
        else:
            nl = "\n" if line.endswith("\n") else ""
            out.append(line[:cut] + nl)
    return "".join(out)


def _line_of(text, idx):
    """1-based line number of character offset ``idx``."""
    return text.count("\n", 0, idx) + 1


def _caption_arg_spans(text):
    """Yield (start, end) char offsets of each \\caption{...} argument body.

    Skips an optional ``*`` and an optional ``[...]`` short-caption arg, then
    brace-matches the mandatory ``{...}`` (honoring escaped braces). ``start``
    is just after the opening brace, ``end`` is the matching close brace index.
    """
    for m in _CAPTION_RE.finditer(text):
        i = m.end()
        n = len(text)
        if i < n and text[i] == "*":
            i += 1
        while i < n and text[i] in " \t\r\n":
            i += 1
        # Optional [short] arg (brace/bracket-escaped chars skipped).
        if i < n and text[i] == "[":
            depth = 1
            i += 1
            while i < n and depth:
                if text[i] == "\\":
                    i += 2
                    continue
                if text[i] == "[":
                    depth += 1
                elif text[i] == "]":
                    depth -= 1
                i += 1
            while i < n and text[i] in " \t\r\n":
                i += 1
        if i >= n or text[i] != "{":
            continue
        start = i + 1
        depth = 1
        j = start
        while j < n and depth:
            if text[j] == "\\":
                j += 2
                continue
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        if depth == 0:
            yield start, j


def _iter_source_tex(project_dir, doc_types):
    """Yield (path, is_caption_media) for each source .tex under the docs.

    Walks ``<doc>/contents/`` (NOT the generated assembled ``<doc>.tex``).
    ``is_caption_media`` is True for files under a ``caption_and_media/`` dir --
    those whole files are caption bodies.
    """
    for doc_type in doc_types:
        contents = project_dir / _DOC_DIRS[doc_type] / "contents"
        if not contents.is_dir():
            continue
        for root, _dirs, files in os.walk(contents):
            in_caption_media = (os.sep + "caption_and_media") in (
                os.sep + os.path.relpath(root, contents)
            ) or root.endswith("caption_and_media")
            for name in files:
                if name.endswith(".tex"):
                    yield Path(root) / name, in_caption_media


def _offenses_in(path, is_caption_media):
    """Return [(line, snippet), ...] for footnote-in-caption hits in ``path``."""
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    text = _strip_comments(raw)
    hits = []
    if is_caption_media:
        # The whole file becomes the \caption{} body.
        for m in _FOOTNOTE_RE.finditer(text):
            hits.append((_line_of(text, m.start()), m.group(0)))
    else:
        for start, end in _caption_arg_spans(text):
            for m in _FOOTNOTE_RE.finditer(text, start, end):
                hits.append((_line_of(text, m.start()), m.group(0)))
    return hits


def main():
    parser = argparse.ArgumentParser(
        description="Lint: ERROR when \\footnote/\\footnotetext appears inside a "
        "\\caption{} (a fatal LaTeX pattern). \\footnotemark is allowed."
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
        help="Severity: off, warn, or error (default). Overrides env and config.",
    )
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    proj_block, user_block = _config_blocks(project_dir)
    level = resolve_level(args.level, proj_block, user_block)

    print(f"\n{BOLD}=== Caption Footnote Check (level={level}) ==={NC}\n")

    if level == "off":
        print(
            f"  {DIM}[INFO]{NC} caption-footnote check is disabled (level=off)."
        )
        print(
            f"\n{BOLD}Summary:{NC} {GREEN}0 passed{NC}, "
            f"{YELLOW}0 warnings{NC}, {RED}0 errors{NC}"
        )
        return 0

    doc_types = list(_DOC_DIRS) if args.doc_type == "all" else [args.doc_type]
    report = log_fail if level == "error" else log_warn

    offenders = []
    scanned = 0
    for path, is_caption_media in _iter_source_tex(project_dir, doc_types):
        scanned += 1
        for line, snippet in _offenses_in(path, is_caption_media):
            rel = path.relative_to(project_dir)
            offenders.append((f"{rel}:{line}", snippet))

    if not offenders:
        log_pass(
            f"no \\footnote/\\footnotetext inside \\caption{{}} "
            f"({scanned} source .tex scanned)"
        )
    else:
        for loc, snippet in offenders[:_MAX_LIST]:
            report(f"{loc}: {snippet} inside a \\caption{{}}")
        if len(offenders) > _MAX_LIST:
            log_detail(f"... and {len(offenders) - _MAX_LIST} more")
        log_detail(
            "fix: move the note out of the caption. Use "
            "\\caption[short]{long\\protect\\footnotemark} and place "
            "\\footnotetext{...} AFTER the float (\\footnotemark in a caption "
            "is allowed); or inline the disclosure into the caption text."
        )

    print()
    print(
        f"{BOLD}Summary:{NC} {GREEN}{PASS_COUNT} passed{NC}, "
        f"{YELLOW}{WARN_COUNT} warnings{NC}, {RED}{FAIL_COUNT} errors{NC}"
    )
    return 1 if FAIL_COUNT > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
