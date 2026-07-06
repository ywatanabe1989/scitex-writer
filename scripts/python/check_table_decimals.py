#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ROLE: engine-vendored — DO NOT edit here. `scitex-writer update-project`
# overwrites this file on every re-vendor; fix it upstream in the
# scitex-writer package instead (local edits are lost, and update-project
# may set it read-only in the consumer workspace after vendoring).
# File: scripts/python/check_table_decimals.py
# Purpose: SAFETY-NET lint (writer card writer-table-decimal-alignment SECONDARY)
#          for per-column decimal-place CONSISTENCY in the COMPILED table .tex.
#
#          The PRIMARY fix (PR #185) makes csv_to_latex.py per-column decimal-pad
#          (0.35 -> 0.350 so a column aligns). But that auto-pad ONLY runs on the
#          pandas backend of the CSV->LaTeX pipeline. The pipeline
#          (process_tables_modules/03_csv2tex.src) picks a backend by priority:
#            1. csv2latex (external Debian binary) -- NO decimal padding, and it
#               is chosen BEFORE pandas, so it silently preempts the #185 auto-pad
#               even on a host that HAS pandas.
#            2. python + pandas -> csv_to_latex.py (the #185 auto-pad). Normalized.
#            3. python without pandas / AWK fallback (csv2tex_single_fallback) --
#               prints cells verbatim, NO number formatting.
#          Hand-authored .tex tables are never touched by any converter either.
#          So a real table can still reach the PDF with mismatched per-column
#          decimals that the auto-pad did not normalize. This lint catches that.
#
#          It reads the COMPILED output (not the source CSV) on purpose: on the
#          pandas path the compiled cells are ALREADY padded uniform, so the lint
#          sees a consistent column and does NOT fire -- it never re-flags what
#          the auto-pad already fixed. It fires exactly on the un-normalized
#          backends (csv2latex / AWK) and hand-authored tables.
#
#          Severity off|warn|error (default warn -- a safety net, never blocks by
#          default; the auto-pad is the systemic prevention):
#            off   -- skip the lint (prints a loud "disabled (level=off)" note)
#            warn  -- report inconsistent columns, exit 0 (does NOT block)
#            error -- report, exit 1 (blocks the compile)
#          Precedence (highest -> lowest), via the shared _severity resolver:
#          --level, env SCITEX_WRITER_TABLE_DECIMALS, project ./config.yaml
#          table_decimals.level, user ~/.scitex/writer/config.yaml, default warn.
#
# Usage:
#   python check_table_decimals.py [project_dir]
#                                  [--doc-type manuscript|supplementary|revision|all]
#                                  [--level off|warn|error]
#
# Self-contained: stdlib + optional PyYAML (config only) + sibling _severity.py.

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _severity import resolve_level  # noqa: E402

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

# SSoT for the per-check env knob (mirrors check_ref_integrity's provisional
# knob-naming pattern -- a later rename per the scitex-dev standard is one line).
_TABLE_DECIMALS_ENV = "SCITEX_WRITER_TABLE_DECIMALS"

_DOC_DIRS = {
    "manuscript": "01_manuscript",
    "supplementary": "02_supplementary",
    "revision": "03_revision",
}

# Compiled per-table .tex live here (process_tables writes them; FINAL.tex just
# \input{}s them, so they persist after a compile). Relative to each doc dir.
_COMPILED_SUBDIR = Path("contents") / "tables" / "compiled"

# A "clean numeric" cell: an optional sign, digits, optional single decimal
# part. Anything else (math $...$, LaTeX commands, ranges, %, thousands commas,
# "--", "...") is NOT clean-numeric and makes its column ineligible, so the lint
# stays conservative and never false-positives on a non-numeric / mixed column.
_CLEAN_NUMERIC = re.compile(r"^[+-]?\d+(?:\.(\d+))?$")

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


def _strip_cell(cell):
    """Reduce a raw LaTeX cell to its bare textual value for numeric testing.

    Drops the wrappers the converters add around a value -- ``\\textbf{...}``,
    a leading ``\\rowcolor{...}`` (only ever on the first cell), and surrounding
    whitespace/braces -- WITHOUT interpreting math. A cell that still carries a
    backslash or ``$`` after this is treated as non-clean (its column is skipped),
    so verbatim / math cells never trip the lint.
    """
    text = cell.strip()
    # A \rowcolor{...} prefix rides on the first cell of a striped row.
    text = re.sub(r"^\\rowcolor\{[^}]*\}\s*", "", text)
    # Unwrap a single \textbf{...} (headers; never numeric data, but be safe).
    m = re.match(r"^\\textbf\{(.*)\}$", text)
    if m:
        text = m.group(1).strip()
    return text


def _cell_decimals(cell):
    """Decimal-place count of a clean-numeric ``cell``, or None if not clean.

    None means "not a plain number" (blank, ``--``, math, a range, a percent,
    a LaTeX command, ...). A clean integer returns 0; ``0.350`` returns 3.
    """
    text = _strip_cell(cell)
    if not text:
        return None
    if "\\" in text or "$" in text:
        return None
    m = _CLEAN_NUMERIC.match(text)
    if not m:
        return None
    frac = m.group(1)
    return len(frac) if frac else 0


def _data_rows(tabular_body):
    """Yield the ``&``-split cell lists of the DATA rows in a tabular body.

    Splits on the LaTeX row terminator ``\\\\``. Skips booktabs rules
    (``\\toprule``/``\\midrule``/``\\bottomrule``), the header row (the first
    non-rule row, which carries ``\\textbf`` labels), ``\\multicolumn`` spanner
    rows (the "... N rows omitted ..." separator), and empty fragments.
    """
    # Row terminator is a literal double backslash in the source.
    raw_rows = re.split(r"\\\\", tabular_body)
    seen_header = False
    for raw in raw_rows:
        row = raw.strip()
        if not row:
            continue
        # Drop leading booktabs rules / rowcolor directives that share the line.
        row = re.sub(r"\\(top|mid|bottom)rule", "", row).strip()
        if not row:
            continue
        if "\\multicolumn" in row:
            continue
        if "&" not in row and _cell_decimals(row) is None:
            # A stray single-cell control line, not a data row.
            continue
        cells = row.split("&")
        if not seen_header:
            # The first real row is the header (\textbf labels); skip it.
            seen_header = True
            continue
        yield cells


def _inconsistent_columns(tabular_body):
    """Return ``[(col_index, sorted_decimal_set), ...]`` for columns whose
    clean-numeric cells disagree on decimal places AND have a fractional value.

    A column is REPORTED only when EVERY one of its data cells is clean-numeric
    (so a mixed text/number column is never flagged), the column contains at
    least one fractional value (all-integer count columns are left bare, matching
    the auto-pad rule), and more than one distinct decimal-place count appears.
    """
    rows = list(_data_rows(tabular_body))
    if not rows:
        return []
    ncols = max(len(r) for r in rows)
    reports = []
    for col in range(ncols):
        decimals = []
        eligible = True
        for row in rows:
            if col >= len(row):
                continue
            d = _cell_decimals(row[col])
            if d is None:
                eligible = False
                break
            decimals.append(d)
        if not eligible or not decimals:
            continue
        distinct = set(decimals)
        if len(distinct) > 1 and max(distinct) > 0:
            reports.append((col, sorted(distinct)))
    return reports


def _iter_tabulars(tex):
    """Yield each ``\\begin{tabular}...\\end{tabular}`` body in ``tex``."""
    for m in re.finditer(
        r"\\begin\{tabular\}.*?\n(.*?)\\end\{tabular\}", tex, re.DOTALL
    ):
        yield m.group(1)


def _compiled_table_files(doc_dir):
    """Compiled per-table .tex under a doc dir (numeric-prefixed, sorted).

    Excludes the ``00_Tables_Header.tex`` fallback and the ``FINAL.tex``
    assembly (which only ``\\input{}``s the per-table files).
    """
    comp = doc_dir / _COMPILED_SUBDIR
    if not comp.is_dir():
        return []
    files = sorted(
        p for p in comp.glob("[0-9]*.tex") if p.name != "00_Tables_Header.tex"
    )
    return files


def main():
    parser = argparse.ArgumentParser(
        description="Safety-net lint: warn when a compiled table column has "
        "inconsistent per-column decimal places (the auto-pad missed it)."
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
        help="Severity: off, warn, or error. Overrides env and config. "
        "Default: warn (a safety net; the auto-pad is the systemic prevention).",
    )
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    level = resolve_level(
        "table_decimals",
        args.level,
        project_dir,
        default="warn",
        env_var=_TABLE_DECIMALS_ENV,
    )

    print(f"\n{BOLD}=== Table Decimal-Consistency Lint (level={level}) ==={NC}\n")
    if level == "off":
        print(
            f"  {BOLD}{YELLOW}[INFO]{NC} table decimal-consistency lint is "
            f"DISABLED (level=off) -- compiled tables will NOT be checked for "
            f"inconsistent per-column decimals."
        )
        print(
            f"\n{BOLD}Summary:{NC} {GREEN}0 passed{NC}, "
            f"{YELLOW}0 warnings{NC}, {RED}0 errors{NC}"
        )
        return 0

    report = log_fail if level == "error" else log_warn
    doc_types = list(_DOC_DIRS) if args.doc_type == "all" else [args.doc_type]

    any_file = False
    for doc_type in doc_types:
        doc_dir = project_dir / _DOC_DIRS[doc_type]
        if not doc_dir.is_dir():
            continue
        for tex_file in _compiled_table_files(doc_dir):
            any_file = True
            try:
                tex = tex_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for tabular in _iter_tabulars(tex):
                for col, distinct in _inconsistent_columns(tabular):
                    report(
                        f"{doc_type}: {tex_file.name}: column {col + 1} has "
                        f"inconsistent decimal places {distinct} "
                        f"-- pad all cells to {max(distinct)} dp so the column aligns"
                    )
                    log_detail(
                        "fix: install pandas so csv_to_latex.py auto-pads this "
                        "column (0.35 -> 0.350); the csv2latex/AWK backends do not."
                    )

    if not any_file:
        log_pass("no compiled table .tex found to check")
    elif FAIL_COUNT == 0 and WARN_COUNT == 0:
        log_pass("all compiled table columns have consistent decimal places")

    print()
    print(
        f"{BOLD}Summary:{NC} {GREEN}{PASS_COUNT} passed{NC}, "
        f"{YELLOW}{WARN_COUNT} warnings{NC}, {RED}{FAIL_COUNT} errors{NC}"
    )
    return 1 if FAIL_COUNT > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
