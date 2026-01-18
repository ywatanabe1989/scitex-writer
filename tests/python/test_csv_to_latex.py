#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: csv_to_latex.py

import os
import sys
from pathlib import Path

# Add scripts/python to path for imports
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))


# Add your tests here
def test_placeholder():
    """TODO: Add tests for csv_to_latex.py"""
    pass


if __name__ == "__main__":
    import pytest

    pytest.main([os.path.abspath(__file__), "-v"])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/scitex-writer/scripts/python/csv_to_latex.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2024-09-28 18:20:00 (ywatanabe)"
# # File: csv_to_latex.py
#
# """
# Robust CSV to LaTeX table converter with proper escaping and formatting.
#
# Dependencies:
#     - pandas
#     - numpy
#
# Usage:
#     python csv_to_latex.py input.csv output.tex [--caption "caption text"]
# """
#
# import argparse
# import sys
# import pandas as pd
# import numpy as np
# from pathlib import Path
# import re
#
#
# def escape_latex(text):
#     """Properly escape special LaTeX characters."""
#     if pd.isna(text):
#         return ""
#
#     # Convert to string if not already
#     text = str(text)
#
#     # Order matters - backslash must be first
#     replacements = [
#         ('\\', r'\textbackslash{}'),
#         ('&', r'\&'),
#         ('%', r'\%'),
#         ('$', r'\$'),
#         ('#', r'\#'),
#         ('_', r'\_'),
#         ('{', r'\{'),
#         ('}', r'\}'),
#         ('~', r'\textasciitilde{}'),
#         ('^', r'\textasciicircum{}'),
#         ('|', r'\textbar{}'),
#         ('<', r'\textless{}'),
#         ('>', r'\textgreater{}'),
#     ]
#
#     for old, new in replacements:
#         text = text.replace(old, new)
#
#     return text
#
#
# def format_number(val):
#     """Format numbers appropriately for LaTeX."""
#     try:
#         # Try to convert to float
#         num = float(val)
#
#         # Check if it's actually an integer
#         if num.is_integer():
#             return str(int(num))
#         else:
#             # Format with appropriate decimal places
#             if abs(num) < 0.01 and num != 0:
#                 # Scientific notation for very small numbers
#                 return f"{num:.2e}"
#             else:
#                 # Regular decimal notation
#                 return f"{num:.3f}".rstrip('0').rstrip('.')
#     except (ValueError, TypeError):
#         # Not a number, return as is
#         return val
#
#
# def csv_to_latex(csv_file, output_file, caption=None, label=None, max_rows=30):
#     """Convert CSV to LaTeX table with proper formatting.
#
#     Args:
#         csv_file: Input CSV file path
#         output_file: Output LaTeX file path
#         caption: Optional table caption
#         label: Optional table label for references
#         max_rows: Maximum number of data rows to display (default: 30)
#     """
#
#     # Read CSV with pandas for robust parsing
#     try:
#         df = pd.read_csv(csv_file)
#     except Exception as e:
#         print(f"Error reading CSV: {e}", file=sys.stderr)
#         return False
#
#     # Store original row count for truncation message
#     original_rows = len(df)
#     truncated = False
#
#     # Truncate if necessary
#     if len(df) > max_rows:
#         truncated = True
#         # Keep first N-3 rows and last 2 rows with separator
#         if max_rows > 5:
#             df_top = df.head(max_rows - 2)
#             df_bottom = df.tail(2)
#             # Create separator row with "..." in each column
#             separator = pd.DataFrame([['...' for _ in df.columns]], columns=df.columns)
#             df = pd.concat([df_top, separator, df_bottom], ignore_index=True)
#         else:
#             df = df.head(max_rows)
#
#     # Extract metadata from filename
#     csv_path = Path(csv_file)
#     base_name = csv_path.stem
#
#     # Extract table number if present
#     table_number = ""
#     table_name = base_name
#     match = re.match(r'^(\d+)_(.*)$', base_name)
#     if match:
#         table_number = match.group(1).lstrip('0')
#         table_name = match.group(2).replace('_', ' ')
#
#     # Determine column alignment
#     alignments = []
#     for col in df.columns:
#         # Check if column is numeric
#         try:
#             pd.to_numeric(df[col], errors='raise')
#             alignments.append('r')  # Right align for numbers
#         except:
#             alignments.append('l')  # Left align for text
#
#     # Start building LaTeX
#     lines = []
#
#     # Table environment
#     lines.append(f"\\pdfbookmark[2]{{Table {table_number}}}{{table_{base_name}}}")
#     lines.append("\\begin{table}[htbp]")
#     lines.append("\\centering")
#
#     # Use standard font size for tables
#     # Standard academic paper convention: \footnotesize (8pt) for tables
#     lines.append("\\footnotesize")
#
#     # Adjust tabcolsep based on number of columns to fit width
#     num_columns = len(df.columns)
#     if num_columns > 8:
#         lines.append("\\setlength{\\tabcolsep}{2pt}")  # Very tight for many columns
#     elif num_columns > 6:
#         lines.append("\\setlength{\\tabcolsep}{3pt}")  # Tight spacing
#     elif num_columns > 4:
#         lines.append("\\setlength{\\tabcolsep}{4pt}")  # Medium spacing
#     else:
#         lines.append("\\setlength{\\tabcolsep}{6pt}")  # Normal spacing
#
#     # Use resizebox to ensure table fits within text width
#     lines.append("\\resizebox{\\textwidth}{!}{%")
#
#     # Begin tabular
#     tabular_spec = ''.join(alignments)
#     lines.append(f"\\begin{{tabular}}{{{tabular_spec}}}")
#     lines.append("\\toprule")
#
#     # Header row
#     headers = []
#     for col in df.columns:
#         # Format header
#         header = escape_latex(col)
#         # Remove underscores and capitalize
#         header = header.replace('\\_', ' ').title()
#         headers.append(f"\\textbf{{{header}}}")
#     lines.append(" & ".join(headers) + " \\\\")
#     lines.append("\\midrule")
#
#     # Data rows
#     for idx, row in df.iterrows():
#         values = []
#         is_separator = False
#
#         for col in df.columns:
#             val = row[col]
#
#             # Check if this is the separator row
#             if str(val) == '...':
#                 is_separator = True
#
#             # Format the value
#             if pd.notna(val):
#                 if not is_separator:
#                     val = format_number(val)
#                     val = escape_latex(val)
#             else:
#                 val = "--"  # Display for missing values
#
#             values.append(val)
#
#         # Don't add row coloring for separator
#         if is_separator:
#             lines.append("\\midrule")
#             lines.append("\\multicolumn{" + str(len(df.columns)) + "}{c}{\\textit{... " +
#                         f"{original_rows - max_rows + 1} rows omitted ..." + "}} \\\\")
#             lines.append("\\midrule")
#         else:
#             # Add row coloring for readability (skip separator in count)
#             if idx % 2 == 1:
#                 lines.append("\\rowcolor{gray!10}")
#             lines.append(" & ".join(values) + " \\\\")
#
#     lines.append("\\bottomrule")
#     lines.append("\\end{tabular}")
#     lines.append("}")  # Close resizebox
#
#     # Caption
#     lines.append("\\captionsetup{width=\\textwidth}")
#     if caption:
#         # Add truncation note to existing caption if needed
#         if truncated:
#             caption = caption.rstrip('}')
#             caption += f" \\textit{{Note: Table truncated to {max_rows} rows from {original_rows} total rows for display purposes.}}"
#             caption += "}"
#         lines.append(caption)
#     else:
#         # Generate default caption
#         if table_number:
#             lines.append(f"\\caption{{\\textbf{{Table {table_number}: {table_name.title()}}}")
#         else:
#             lines.append(f"\\caption{{\\textbf{{{table_name.title()}}}")
#         lines.append("\\\\")
#         if truncated:
#             lines.append(f"\\textit{{Note: Table truncated to {max_rows} rows from {original_rows} total rows for display purposes.}}")
#         else:
#             lines.append("Data table generated from CSV file.")
#         lines.append("}")
#
#     # Label
#     if label:
#         lines.append(f"\\label{{{label}}}")
#     else:
#         lines.append(f"\\label{{tab:{base_name}}}")
#
#     lines.append("\\end{table}")
#     lines.append("")
#     lines.append("\\restoregeometry")
#
#     # Write to file
#     try:
#         with open(output_file, 'w', encoding='utf-8') as f:
#             f.write('\n'.join(lines))
#         return True
#     except Exception as e:
#         print(f"Error writing output: {e}", file=sys.stderr)
#         return False
#
#
# def main():
#     parser = argparse.ArgumentParser(description='Convert CSV to LaTeX table')
#     parser.add_argument('input_csv', help='Input CSV file')
#     parser.add_argument('output_tex', help='Output LaTeX file')
#     parser.add_argument('--caption', help='Custom caption text')
#     parser.add_argument('--caption-file', help='File containing caption text')
#     parser.add_argument('--label', help='Custom label for referencing')
#
#     args = parser.parse_args()
#
#     # Read caption from file if provided
#     caption = args.caption
#     if args.caption_file and Path(args.caption_file).exists():
#         with open(args.caption_file, 'r', encoding='utf-8') as f:
#             caption = f.read().strip()
#
#     success = csv_to_latex(
#         args.input_csv,
#         args.output_tex,
#         caption=caption,
#         label=args.label
#     )
#
#     sys.exit(0 if success else 1)
#
#
# if __name__ == '__main__':
#     main()
# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/scitex-writer/scripts/python/csv_to_latex.py
# --------------------------------------------------------------------------------
