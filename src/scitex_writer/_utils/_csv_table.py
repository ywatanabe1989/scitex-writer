#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_utils/_csv_table.py

r"""The single CSV -> LaTeX table backend of the writer engine (pandas).

Absorbs ``scripts/python/csv_to_latex.py`` into the package and REPLACES the
shell engine's 4-way backend selection (``csv2latex`` binary / python+pandas /
python-basic / AWK fallback) with ONE pandas backend.

Why one backend (card writer-csv-latex-verbatim-all-backends): the whole-cell
verbatim passthrough -- a header/cell carrying ``$`` (math) or ``\`` (a LaTeX
command) is emitted as authored, never escaped -- lived ONLY in the Python
backend. Whenever the shell picked ``csv2latex`` (it is preferred when the
binary is installed) or fell through to AWK, ``$p<0.001$`` was silently
mangled/escaped. Collapsing to one backend makes the passthrough universal by
construction: there is no other path left to lose it.

Emitted structure (parity with the shell + the old Python script):
``\pdfbookmark[2]{Table N --- Title}{table_<base>}`` -> ``table`` float ->
``\footnotesize`` -> column-count-dependent ``\tabcolsep`` -> shrink-to-fit
``\resizebox`` -> ``booktabs`` tabular (bold header, zebra ``\rowcolor``) ->
caption (author's, or a generated default) -> ``\label{tab:<base>}`` emitted
ONLY when the caption does not already carry one.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional, Union

MAX_ROWS = 30
"""Data rows shown before the table is truncated with an omitted-rows marker."""

_TEXTBF_RE = re.compile(r"\\textbf\{([^}]*)\}")
_CAPTION_HEAD_RE = re.compile(r"\\caption\{([^.]*)\.")

_ESCAPES = (
    ("\\", r"\textbackslash{}"),  # must be first
    ("&", r"\&"),
    ("%", r"\%"),
    ("$", r"\$"),
    ("#", r"\#"),
    ("_", r"\_"),
    ("{", r"\{"),
    ("}", r"\}"),
    ("~", r"\textasciitilde{}"),
    ("^", r"\textasciicircum{}"),
    ("|", r"\textbar{}"),
    ("<", r"\textless{}"),
    (">", r"\textgreater{}"),
)


def escape_latex(text) -> str:
    """Escape LaTeX-special characters in a plain (non-verbatim) value."""
    import pandas as pd

    if pd.isna(text):
        return ""
    text = str(text)
    for old, new in _ESCAPES:
        text = text.replace(old, new)
    return text


def is_verbatim(value) -> bool:
    r"""True if a header/cell already carries explicit LaTeX or math.

    A value containing ``$`` (math) or ``\`` (a LaTeX command) is authored
    intentionally -- pass it through verbatim (no escaping, number-formatting or
    title-casing) so ``$R^2$``, ``$p<0.001$`` or ``\textit{r}`` render. Plain
    values are still escaped (safe). A rare literal ``$`` in plain data must be
    escaped by the author as ``\$``.
    """
    text = str(value)
    return "$" in text or "\\" in text


def format_number(val):
    """Format a number for LaTeX: ints bare, tiny values scientific, else 3 dp."""
    try:
        num = float(val)
    except (ValueError, TypeError):
        return val
    if num.is_integer():
        return str(int(num))
    if abs(num) < 0.01 and num != 0:
        return f"{num:.2e}"
    return f"{num:.3f}".rstrip("0").rstrip(".")


def _value_decimals(val) -> Optional[int]:
    """Decimals ``val`` shows under :func:`format_number`; None if not alignable.

    Non-numbers, NaN and scientific-notation (very small) values return None --
    they are left unaligned. Reusing format_number's own output keeps column
    precision in lockstep with the per-cell display, so alignment only PADS
    shorter values; it never uncaps precision.
    """
    try:
        num = float(val)
    except (ValueError, TypeError):
        return None
    if num != num:  # NaN
        return None
    shown = format_number(val)
    if "e" in str(shown) or "E" in str(shown):
        return None
    shown = str(shown)
    return len(shown.split(".")[1]) if "." in shown else 0


def column_precision(values) -> Optional[int]:
    """Decimal places a column pads to so its numbers align, or None.

    None for an all-integer or non-numeric column: counts like ``288`` stay
    ``288``, never ``288.000``.
    """
    decimals = [d for d in (_value_decimals(v) for v in values) if d is not None]
    if not decimals:
        return None
    target = max(decimals)
    return target if target > 0 else None


def _format_aligned(val, precision: Optional[int]) -> str:
    """Pad ``val`` to ``precision`` decimals so a column's numbers line up."""
    if precision is None or _value_decimals(val) is None:
        return str(format_number(val))
    return f"{float(val):.{precision}f}"


def _render_cell(val, precision: Optional[int]) -> str:
    """One data cell: verbatim if authored LaTeX/math, else aligned + escaped."""
    import pandas as pd

    if not pd.notna(val):
        return "--"
    if is_verbatim(val):
        return str(val)
    return escape_latex(_format_aligned(val, precision))


def _render_header(col) -> str:
    r"""One header cell: verbatim if authored LaTeX/math, else escaped.

    Underscores become spaces (``mean_iou`` -> ``mean iou``). NOT title-cased:
    acronyms must survive as authored (``ROC-AUC`` stays ``ROC-AUC``).
    """
    header = str(col) if is_verbatim(col) else escape_latex(col).replace("\\_", " ")
    return f"\\textbf{{{header}}}"


def split_table_name(base_name: str):
    """Split ``01_seizure_count`` into ``("1", "seizure count")``.

    Falls back to ``(base_name, base_name)`` when the stem carries no leading
    ``NN_`` number -- exactly the shell's behaviour.
    """
    match = re.match(r"^(\d+)_(.*)$", base_name)
    if not match:
        return base_name, base_name
    number = match.group(1).lstrip("0") or "0"
    return number, match.group(2).replace("_", " ")


def caption_title(caption: Optional[str]) -> str:
    r"""The table title carried by a caption, for the PDF bookmark.

    Prefers the ``\textbf{...}`` title (the template's shape), else the caption
    text up to its first period. Trailing periods are stripped. Empty when the
    caption carries neither -- the caller then emits a bare ``Table N``
    bookmark. Mirrors the sed pair in ``process_tables_modules/03_csv2tex.src``.
    """
    if not caption:
        return ""
    match = _TEXTBF_RE.search(caption)
    if not match:
        match = _CAPTION_HEAD_RE.search(caption)
    if not match:
        return ""
    return match.group(1).strip().rstrip(".").strip()


def _tabcolsep(num_columns: int) -> str:
    """Column separation that keeps a wide table inside the text width."""
    if num_columns > 8:
        return "2pt"
    if num_columns > 6:
        return "3pt"
    if num_columns > 4:
        return "4pt"
    return "6pt"


def render_csv_table(
    csv_path: Union[str, Path],
    caption: Optional[str] = None,
    label: Optional[str] = None,
    max_rows: int = MAX_ROWS,
) -> str:
    r"""Render one CSV file as a complete LaTeX ``table`` float.

    Parameters
    ----------
    csv_path : str or Path
        The CSV to render. Its stem (``01_seizure_count``) supplies the table
        number, the default caption text and the default label.
    caption : str, optional
        The author's caption BLOCK (a full ``\caption{...}``, typically the
        sibling ``NN_name.tex``). When absent a default caption is generated.
    label : str, optional
        Overrides the default ``tab:<stem>`` label. A label is emitted ONLY when
        the caption does not already carry a ``\label{tab:`` of its own -- so an
        author-supplied label is never duplicated.
    max_rows : int
        Data rows shown before truncation (default 30). Truncated tables keep
        the first ``max_rows - 2`` and the last 2 rows around an
        "... N rows omitted ..." marker, and the note is appended to the caption.

    Returns
    -------
    str
        The LaTeX table float (no trailing newline).

    Raises
    ------
    FileNotFoundError
        If ``csv_path`` does not exist (fail-loud: never a silent empty table).
    """
    import pandas as pd

    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = pd.read_csv(csv_path)
    original_rows = len(df)
    truncated = original_rows > max_rows
    if truncated:
        if max_rows > 5:
            separator = pd.DataFrame([["..."] * len(df.columns)], columns=df.columns)
            df = pd.concat(
                [df.head(max_rows - 2), separator, df.tail(2)], ignore_index=True
            )
        else:
            df = df.head(max_rows)

    base_name = csv_path.stem
    table_number, table_clean_name = split_table_name(base_name)

    alignments = []
    for col in df.columns:
        try:
            pd.to_numeric(df[col], errors="raise")
            alignments.append("r")
        except (ValueError, TypeError):
            alignments.append("l")

    title = caption_title(caption)
    bookmark = f"Table {table_number}"
    if title:
        bookmark = f"Table {table_number} --- {title}"

    lines = [
        f"\\pdfbookmark[2]{{{bookmark}}}{{table_{base_name}}}",
        "\\begin{table}[htbp]",
        "\\centering",
        "\\footnotesize",
        f"\\setlength{{\\tabcolsep}}{{{_tabcolsep(len(df.columns))}}}",
        # Shrink-to-fit ONLY: a too-wide table scales down to \linewidth; a
        # narrow one keeps its natural width (never stretched).
        "\\resizebox{\\ifdim\\width>\\linewidth\\linewidth\\else\\width\\fi}{!}{%",
        f"\\begin{{tabular}}{{{''.join(alignments)}}}",
        "\\toprule",
        " & ".join(_render_header(col) for col in df.columns) + " \\\\",
        "\\midrule",
    ]

    col_prec = {col: column_precision(df[col]) for col in df.columns}
    for idx, row in df.iterrows():
        if any(str(row[col]) == "..." for col in df.columns):
            omitted = original_rows - max_rows + 1
            lines.append("\\midrule")
            lines.append(
                f"\\multicolumn{{{len(df.columns)}}}{{c}}"
                f"{{\\textit{{... {omitted} rows omitted ...}}}} \\\\"
            )
            lines.append("\\midrule")
            continue
        # Zebra striping via the theme color `lightgray` (redefined under
        # dark_mode.tex), so the stripe stays legible in BOTH modes.
        if idx % 2 == 1:
            lines.append("\\rowcolor{lightgray}")
        lines.append(
            " & ".join(_render_cell(row[col], col_prec[col]) for col in df.columns)
            + " \\\\"
        )

    lines += [
        "\\bottomrule",
        "\\end{tabular}",
        "}",
        "\\captionsetup{width=\\textwidth}",
    ]

    note = (
        f"\\textit{{Note: Table truncated to {max_rows} rows from "
        f"{original_rows} total rows for display purposes.}}"
    )
    if caption:
        block = caption.rstrip()
        if truncated:
            block = block.rstrip("}") + f" {note}" + "}"
        lines.append(block)
    else:
        lines.append(f"\\caption{{\\textbf{{Table {table_number}: {table_clean_name}}}")
        lines.append("\\\\")
        lines.append(note if truncated else "Data table generated from CSV file.")
        lines.append("}")

    # Label ONLY when the caption does not already carry one (no duplicates).
    if not (caption and "\\label{tab:" in caption):
        lines.append(f"\\label{{{label or 'tab:' + base_name}}}")

    lines.append("\\end{table}")
    return "\n".join(lines)


__all__ = [
    "MAX_ROWS",
    "caption_title",
    "column_precision",
    "escape_latex",
    "format_number",
    "is_verbatim",
    "render_csv_table",
    "split_table_name",
]

# EOF
