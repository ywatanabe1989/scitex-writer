#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/handlers/_tables.py

"""Table conversion handlers: CSV to LaTeX, LaTeX to CSV."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional


def csv_to_latex(
    csv_path: str,
    output_path: Optional[str] = None,
    caption: Optional[str] = None,
    label: Optional[str] = None,
    longtable: bool = False,
) -> dict:
    """Convert CSV file to LaTeX table."""
    try:
        import pandas as pd

        csv_file = Path(csv_path)
        if not csv_file.exists():
            return {"success": False, "error": f"CSV file not found: {csv_path}"}

        df = pd.read_csv(csv_file)
        base_name = csv_file.stem

        alignments = []
        for col in df.columns:
            try:
                pd.to_numeric(df[col], errors="raise")
                alignments.append("r")
            except Exception:
                alignments.append("l")

        lines = []
        if longtable:
            lines.append("\\begin{longtable}{" + "".join(alignments) + "}")
        else:
            lines.extend(
                [
                    "\\begin{table}[htbp]",
                    "\\centering",
                    "\\begin{tabular}{" + "".join(alignments) + "}",
                ]
            )

        lines.append("\\toprule")
        lines.append(" & ".join([f"\\textbf{{{col}}}" for col in df.columns]) + " \\\\")
        lines.append("\\midrule")

        for _, row in df.iterrows():
            values = [str(v) if pd.notna(v) else "--" for v in row]
            lines.append(" & ".join(values) + " \\\\")

        lines.append("\\bottomrule")

        if longtable:
            if caption:
                lines.append(f"\\caption{{{caption}}}")
            if label:
                lines.append(f"\\label{{{label}}}")
            lines.append("\\end{longtable}")
        else:
            lines.append("\\end{tabular}")
            if caption:
                lines.append(f"\\caption{{{caption}}}")
            lines.append(f"\\label{{{label or 'tab:' + base_name}}}")
            lines.append("\\end{table}")

        latex_content = "\n".join(lines)
        if output_path:
            Path(output_path).write_text(latex_content, encoding="utf-8")

        return {
            "success": True,
            "latex_content": latex_content,
            "output_path": output_path,
            "rows": len(df),
            "columns": len(df.columns),
        }
    except ImportError:
        return {"success": False, "error": "pandas required: pip install pandas"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def latex_to_csv(
    latex_path: str,
    output_path: Optional[str] = None,
    table_index: int = 0,
) -> dict:
    """Convert LaTeX table to CSV."""
    try:
        import pandas as pd

        latex_file = Path(latex_path)
        if not latex_file.exists():
            return {"success": False, "error": f"LaTeX file not found: {latex_path}"}

        content = latex_file.read_text(encoding="utf-8")
        pattern = r"\\begin\{tabular\}.*?\\end\{tabular\}"
        matches = list(re.finditer(pattern, content, re.DOTALL))

        if not matches:
            return {"success": False, "error": "No tabular environment found"}
        if table_index >= len(matches):
            return {
                "success": False,
                "error": f"Table index {table_index} out of range",
            }

        table_content = matches[table_index].group()
        rows = []
        for line in table_content.split("\\\\"):
            if any(
                x in line
                for x in ["\\begin", "\\end", "\\toprule", "\\midrule", "\\bottomrule"]
            ):
                continue
            cells = [
                re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", c.strip())
                for c in line.split("&")
            ]
            if any(cells):
                rows.append(cells)

        if not rows:
            return {"success": False, "error": "Could not parse table"}

        df = pd.DataFrame(rows[1:], columns=rows[0] if rows else None)
        if output_path:
            df.to_csv(output_path, index=False)

        return {
            "success": True,
            "rows": len(df),
            "columns": list(df.columns),
            "preview": df.head(5).to_dict(),
            "output_path": output_path,
        }
    except ImportError:
        return {"success": False, "error": "pandas required: pip install pandas"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# EOF
