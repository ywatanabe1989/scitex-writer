#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: scripts/python/_tectonic_compat.py
# Purpose: Tectonic-engine compatibility transforms for the flattened TeX.
#          Extracted verbatim from compile_tex_structure.py to keep that module
#          under the line limit (same pattern as _tex_signature.py /
#          _build_id.py); pure helper, no behavior change.

import re
from pathlib import Path


def apply_tectonic_compat(expanded_content: str, base_tex: Path) -> str:
    r"""Rewrite the flattened TeX for tectonic compatibility.

    Disables packages/commands that tectonic chokes on (lineno, bashful,
    \linenumbers) and inlines \readwordcount{file} with the file's contents
    (tectonic has no shell-escape). Returns the transformed content.
    """
    # Comment out incompatible packages
    expanded_content = re.sub(
        r"(\\usepackage\{[^}]*lineno[^}]*\})",
        r"% \1  % Disabled for tectonic",
        expanded_content,
    )
    expanded_content = re.sub(
        r"(\\usepackage\{[^}]*bashful[^}]*\})",
        r"% \1  % Disabled for tectonic",
        expanded_content,
    )
    # Comment out \linenumbers command
    expanded_content = re.sub(
        r"(^\\linenumbers)",
        r"% \1  % Disabled for tectonic",
        expanded_content,
        flags=re.MULTILINE,
    )

    # Replace \readwordcount{file} with actual file contents
    def replace_wordcount(match):
        file_path = match.group(1)
        try:
            # Resolve file path (could be relative or absolute)
            if not file_path.startswith("/"):
                # Paths starting with ./ are relative to project root, not base_tex
                if file_path.startswith("./"):
                    # Use current working directory as base (should be project root)
                    full_path = Path(file_path)
                else:
                    # Relative to base_tex directory
                    full_path = base_tex.parent / file_path
            else:
                full_path = Path(file_path)

            # Read the count value
            with open(full_path, "r") as f:
                count_value = f.read().strip()

            # Match the \readwordcount macro's thousands separator (e.g.
            # 1,259) so tectonic mode (which inlines the raw number) renders
            # the same as the latexmk/pdflatex path.
            if count_value.isdigit():
                count_value = f"{int(count_value):,}"
            return count_value
        except Exception as e:
            # If file can't be read, return a placeholder with debug info
            return f"??({e})"

    expanded_content = re.sub(
        r"\\readwordcount\{([^}]+)\}", replace_wordcount, expanded_content
    )
    return expanded_content


__all__ = ["apply_tectonic_compat"]

# EOF
