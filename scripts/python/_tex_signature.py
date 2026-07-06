#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ROLE: engine-vendored — DO NOT edit here. `scitex-writer update-project`
# overwrites this file on every re-vendor; fix it upstream in the
# scitex-writer package instead (local edits are lost, and update-project
# may set it read-only in the consumer workspace after vendoring).
# File: scripts/python/_tex_signature.py
# Purpose: Build the compilation signature comment block prepended to the
#          flattened TeX by compile_tex_structure.py. Extracted from that
#          module to keep it under the line limit; pure helper, no public API
#          change.

import os
from datetime import datetime
from pathlib import Path
from typing import Optional


def generate_signature(source_file: Path = None, build_id: Optional[str] = None) -> str:
    """Generate the compilation signature comment block.

    Args:
        source_file: Original source file path (optional).
        build_id: Per-compilation build id (optional).

    Returns:
        Formatted signature as a LaTeX comment block.
    """
    # Read version from pyproject.toml (single source of truth). This module
    # lives in scripts/python/, so parent.parent.parent is the repo root.
    version = "unknown"
    pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
    try:
        with open(pyproject_path, "r") as f:
            for line in f:
                if line.startswith("version"):
                    version = line.split("=")[1].strip().strip('"')
                    break
    except Exception:
        pass

    engine = (
        os.getenv("SCITEX_WRITER_SELECTED_ENGINE", "")
        or os.getenv("SCITEX_WRITER_ENGINE", "")
        or "auto"
    )

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    signature = f"""% {"=" * 78}
% SciTeX Writer {version} (https://scitex.ai)
% LaTeX compilation engine: {engine}
% Compiled: {timestamp}
"""

    if build_id:
        signature += f"% Build ID: build:{build_id}\n"

    if source_file:
        signature += f"% Source: {source_file}\n"

    signature += f"""% {"=" * 78}

"""
    return signature


__all__ = ["generate_signature"]

# EOF
