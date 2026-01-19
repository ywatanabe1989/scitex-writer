#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-20
# File: src/scitex_writer/_mcp/utils.py

"""Utility functions for SciTeX Writer MCP handlers."""

from __future__ import annotations

import subprocess
from pathlib import Path


def resolve_project_path(project_dir: str) -> Path:
    """Resolve project directory to absolute path."""
    project_path = Path(project_dir)
    if not project_path.is_absolute():
        project_path = Path.cwd() / project_path
    return project_path.resolve()


def run_compile_script(
    project_dir: Path,
    doc_type: str,
    timeout: int = 300,
    no_figs: bool = False,
    no_tables: bool = False,
    no_diff: bool = False,
    draft: bool = False,
    dark_mode: bool = False,
    quiet: bool = False,
    verbose: bool = False,
    track_changes: bool = False,
) -> dict:
    """Run compile.sh script with specified options."""
    compile_script = project_dir / "compile.sh"

    if not compile_script.exists():
        return {
            "success": False,
            "error": f"compile.sh not found at {compile_script}",
        }

    # Build command
    cmd = ["env", "-u", "BASH_ENV", "/bin/bash", str(compile_script), doc_type]

    if no_figs:
        cmd.append("--no_figs")
    if no_tables:
        cmd.append("--no_tables")
    if no_diff:
        cmd.append("--no_diff")
    if draft:
        cmd.append("--draft")
    if dark_mode:
        cmd.append("--dark_mode")
    if quiet:
        cmd.append("--quiet")
    if verbose:
        cmd.append("--verbose")
    if track_changes and doc_type == "revision":
        cmd.append("--track_changes")

    try:
        result = subprocess.run(
            cmd,
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        # Determine output PDF path
        pdf_paths = {
            "manuscript": project_dir / "01_manuscript" / "manuscript.pdf",
            "supplementary": project_dir / "02_supplementary" / "supplementary.pdf",
            "revision": project_dir / "03_revision" / "revision.pdf",
        }
        output_pdf = pdf_paths.get(doc_type)

        if result.returncode == 0:
            return {
                "success": True,
                "output_pdf": str(output_pdf)
                if output_pdf and output_pdf.exists()
                else None,
                "exit_code": result.returncode,
                "stdout": result.stdout[-2000:]
                if len(result.stdout) > 2000
                else result.stdout,
                "message": f"{doc_type.title()} compiled successfully",
            }
        else:
            return {
                "success": False,
                "exit_code": result.returncode,
                "stdout": result.stdout[-2000:]
                if len(result.stdout) > 2000
                else result.stdout,
                "stderr": result.stderr[-2000:]
                if len(result.stderr) > 2000
                else result.stderr,
                "error": f"Compilation failed with exit code {result.returncode}",
            }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Compilation timed out after {timeout} seconds",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


__all__ = ["resolve_project_path", "run_compile_script"]

# EOF
