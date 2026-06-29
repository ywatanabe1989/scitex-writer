#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2024-09-28 18:20:00 (ywatanabe)"
# File: csv_to_latex.py

"""
Robust CSV to LaTeX table converter with proper escaping and formatting.

Dependencies:
    - pandas
    - numpy

Usage:
    python csv_to_latex.py input.csv output.tex [--caption "caption text"]
"""

import argparse
import re
import sys
from pathlib import Path

import pandas as pd


def escape_latex(text):
    """Properly escape special LaTeX characters."""
    if pd.isna(text):
        return ""

    # Convert to string if not already
    text = str(text)

    # Order matters - backslash must be first
    replacements = [
        ("\\", r"\textbackslash{}"),
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
    ]

    for old, new in replacements:
        text = text.replace(old, new)

    return text


def _is_verbatim(value) -> bool:
    """True if a header/cell already carries explicit LaTeX or math.

    A value containing ``$`` (math) or ``\\`` (a LaTeX command) is authored
    intentionally — pass it through verbatim (no escaping, number-formatting,
    or title-casing) so e.g. ``$R^2$``, ``$p$``, ``$N_{\\mathrm{perm}}$`` or
    ``\\textit{r}`` render. Plain values are still escaped (safe). Rare literal
    ``$`` in plain data must be escaped by the author as ``\\$``.
    """
    return "$" in str(value) or "\\" in str(value)


def format_number(val):
    """Format numbers appropriately for LaTeX."""
    try:
        # Try to convert to float
        num = float(val)

        # Check if it's actually an integer
        if num.is_integer():
            return str(int(num))
        else:
            # Format with appropriate decimal places
            if abs(num) < 0.01 and num != 0:
                # Scientific notation for very small numbers
                return f"{num:.2e}"
            else:
                # Regular decimal notation
                return f"{num:.3f}".rstrip("0").rstrip(".")
    except (ValueError, TypeError):
        # Not a number, return as is
        return val


def _value_decimals(val):
    """Decimal places a numeric value needs to display, or None if not numeric.

    Integer-valued numbers (incl. ``5.0``) need 0. The ``.6f`` cap strips
    float-repr noise (e.g. ``0.1+0.2``) before counting.
    """
    try:
        num = float(val)
    except (ValueError, TypeError):
        return None
    if num != num:  # NaN
        return None
    if num.is_integer():
        return 0
    trimmed = f"{num:.6f}".rstrip("0")
    return len(trimmed.split(".")[1]) if "." in trimmed else 0


def column_precision(values):
    """Target decimal precision for a column so its numbers align.

    The max decimal places among the column's numeric cells, but only when the
    column actually has a fractional value. Returns ``None`` for an all-integer
    or non-numeric column (leave those untouched: counts like ``288`` stay
    ``288``, never ``288.000``).
    """
    decimals = [d for d in (_value_decimals(v) for v in values) if d is not None]
    if not decimals:
        return None
    target = max(decimals)
    return target if target > 0 else None


def _format_aligned(val, precision):
    """Format ``val`` to a fixed ``precision`` (padding trailing zeros) so a
    column's numbers line up; fall back to ``format_number`` when ``precision``
    is None or ``val`` is not a plain number (``--`` / ``...`` / text)."""
    if precision is None:
        return format_number(val)
    try:
        return f"{float(val):.{precision}f}"
    except (ValueError, TypeError):
        return format_number(val)


def csv_to_latex(csv_file, output_file, caption=None, label=None, max_rows=30):
    """Convert CSV to LaTeX table with proper formatting.

    Args:
        csv_file: Input CSV file path
        output_file: Output LaTeX file path
        caption: Optional table caption
        label: Optional table label for references
        max_rows: Maximum number of data rows to display (default: 30)
    """

    # Read CSV with pandas for robust parsing
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"Error reading CSV: {e}", file=sys.stderr)
        return False

    # Store original row count for truncation message
    original_rows = len(df)
    truncated = False

    # Truncate if necessary
    if len(df) > max_rows:
        truncated = True
        # Keep first N-3 rows and last 2 rows with separator
        if max_rows > 5:
            df_top = df.head(max_rows - 2)
            df_bottom = df.tail(2)
            # Create separator row with "..." in each column
            separator = pd.DataFrame([["..." for _ in df.columns]], columns=df.columns)
            df = pd.concat([df_top, separator, df_bottom], ignore_index=True)
        else:
            df = df.head(max_rows)

    # Extract metadata from filename
    csv_path = Path(csv_file)
    base_name = csv_path.stem

    # Extract table number if present
    table_number = ""
    table_name = base_name
    match = re.match(r"^(\d+)_(.*)$", base_name)
    if match:
        table_number = match.group(1).lstrip("0")
        table_name = match.group(2).replace("_", " ")

    # Determine column alignment
    alignments = []
    for col in df.columns:
        # Check if column is numeric
        try:
            pd.to_numeric(df[col], errors="raise")
            alignments.append("r")  # Right align for numbers
        except:
            alignments.append("l")  # Left align for text

    # Start building LaTeX
    lines = []

    # Table environment
    lines.append(f"\\pdfbookmark[2]{{Table {table_number}}}{{table_{base_name}}}")
    lines.append("\\begin{table}[htbp]")
    lines.append("\\centering")

    # Use standard font size for tables
    # Standard academic paper convention: \footnotesize (8pt) for tables
    lines.append("\\footnotesize")

    # Adjust tabcolsep based on number of columns to fit width
    num_columns = len(df.columns)
    if num_columns > 8:
        lines.append("\\setlength{\\tabcolsep}{2pt}")  # Very tight for many columns
    elif num_columns > 6:
        lines.append("\\setlength{\\tabcolsep}{3pt}")  # Tight spacing
    elif num_columns > 4:
        lines.append("\\setlength{\\tabcolsep}{4pt}")  # Medium spacing
    else:
        lines.append("\\setlength{\\tabcolsep}{6pt}")  # Normal spacing

    # Use resizebox to ensure table fits within text width
    lines.append("\\resizebox{\\textwidth}{!}{%")

    # Begin tabular
    tabular_spec = "".join(alignments)
    lines.append(f"\\begin{{tabular}}{{{tabular_spec}}}")
    lines.append("\\toprule")

    # Header row
    headers = []
    for col in df.columns:
        # Format header. Verbatim if it carries explicit LaTeX/math (e.g.
        # "$R^2$"); otherwise escape + underscores->spaces. NOT title-cased —
        # render as authored so acronyms survive ("ROC-AUC" stays "ROC-AUC").
        if _is_verbatim(col):
            header = str(col)
        else:
            header = escape_latex(col).replace("\\_", " ")
        headers.append(f"\\textbf{{{header}}}")
    lines.append(" & ".join(headers) + " \\\\")
    lines.append("\\midrule")

    # Data rows. Pre-compute each column's decimal precision so its numbers
    # align (e.g. 0.333 / 0.35 -> 0.333 / 0.350); all-integer columns stay bare.
    col_prec = {col: column_precision(df[col]) for col in df.columns}
    for idx, row in df.iterrows():
        values = []
        is_separator = False

        for col in df.columns:
            val = row[col]

            # Check if this is the separator row
            if str(val) == "...":
                is_separator = True

            # Format the value. Pass through verbatim if it carries explicit
            # LaTeX/math ("$p<0.001$"); otherwise number-format + escape.
            if pd.notna(val):
                if not is_separator:
                    if _is_verbatim(val):
                        val = str(val)
                    else:
                        val = _format_aligned(val, col_prec[col])
                        val = escape_latex(val)
            else:
                val = "--"  # Display for missing values

            values.append(val)

        # Don't add row coloring for separator
        if is_separator:
            lines.append("\\midrule")
            lines.append(
                "\\multicolumn{"
                + str(len(df.columns))
                + "}{c}{\\textit{... "
                + f"{original_rows - max_rows + 1} rows omitted ..."
                + "}} \\\\"
            )
            lines.append("\\midrule")
        else:
            # Add row coloring for readability (skip separator in count).
            # Use the theme color `lightgray` (gray 0.95 light mode; redefined to
            # gray 0.2 in dark_mode.tex) so the zebra stripe stays legible in
            # BOTH modes. A literal gray!10 stayed light under dark mode, hiding
            # the light text on the striped rows.
            if idx % 2 == 1:
                lines.append("\\rowcolor{lightgray}")
            lines.append(" & ".join(values) + " \\\\")

    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    lines.append("}")  # Close resizebox

    # Caption
    lines.append("\\captionsetup{width=\\textwidth}")
    if caption:
        # Add truncation note to existing caption if needed
        if truncated:
            caption = caption.rstrip("}")
            caption += f" \\textit{{Note: Table truncated to {max_rows} rows from {original_rows} total rows for display purposes.}}"
            caption += "}"
        lines.append(caption)
    else:
        # Generate default caption. Do NOT .title() the name — preserve the
        # CSV-derived casing so acronyms survive (ROC-AUC, PR-AUC), matching the
        # header handling.
        if table_number:
            lines.append(
                f"\\caption{{\\textbf{{Table {table_number}: {table_name}}}"
            )
        else:
            lines.append(f"\\caption{{\\textbf{{{table_name}}}")
        lines.append("\\\\")
        if truncated:
            lines.append(
                f"\\textit{{Note: Table truncated to {max_rows} rows from {original_rows} total rows for display purposes.}}"
            )
        else:
            lines.append("Data table generated from CSV file.")
        lines.append("}")

    # Label
    if label:
        lines.append(f"\\label{{{label}}}")
    else:
        lines.append(f"\\label{{tab:{base_name}}}")

    lines.append("\\end{table}")
    lines.append("")
    lines.append("\\restoregeometry")

    # Write to file
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return True
    except Exception as e:
        print(f"Error writing output: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Convert CSV to LaTeX table")
    parser.add_argument("input_csv", help="Input CSV file")
    parser.add_argument("output_tex", help="Output LaTeX file")
    parser.add_argument("--caption", help="Custom caption text")
    parser.add_argument("--caption-file", help="File containing caption text")
    parser.add_argument("--label", help="Custom label for referencing")

    args = parser.parse_args()

    # Read caption from file if provided
    caption = args.caption
    if args.caption_file and Path(args.caption_file).exists():
        with open(args.caption_file, "r", encoding="utf-8") as f:
            caption = f.read().strip()

    success = csv_to_latex(
        args.input_csv, args.output_tex, caption=caption, label=args.label
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
