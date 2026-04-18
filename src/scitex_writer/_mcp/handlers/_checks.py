#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/handlers/_checks.py
# Purpose: Expose scripts/python/check_references.py and check_float_order.py
#          over MCP. Keeps the existing scripts as the single source of truth;
#          this module is a thin subprocess wrapper that normalises their
#          exit codes and text output into a dict the MCP layer can ship.
#
# See writer issues #44 (float order) and #45 (cross-ref + citation check).

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from ..utils import resolve_project_path

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


def _run_script(
    script_path: Path,
    project_dir: Path,
    extra_args: list[str],
    timeout: int,
) -> dict:
    if not script_path.exists():
        return {
            "success": False,
            "error": f"Script not found: {script_path}",
        }
    cmd = ["python3", str(script_path), str(project_dir), *extra_args]
    try:
        result = subprocess.run(
            cmd,
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Check timed out after {timeout}s",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

    stdout = _strip_ansi(result.stdout)
    stderr = _strip_ansi(result.stderr)
    return {
        "success": result.returncode == 0,
        "exit_code": result.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "summary": _extract_summary(stdout),
    }


def _extract_summary(stdout: str) -> dict:
    """Pull the PASS/WARN/FAIL counts out of the script's summary line."""
    m = re.search(
        r"Summary:\s+(\d+)\s+passed,\s+(\d+)\s+warnings,\s+(\d+)\s+errors",
        stdout,
    )
    if not m:
        return {}
    return {
        "passed": int(m.group(1)),
        "warnings": int(m.group(2)),
        "errors": int(m.group(3)),
    }


def _script_path(project_path: Path, name: str) -> Path:
    return project_path / "scripts" / "python" / name


def check_references(
    project_dir: str,
    doc_type: str = "all",
    parse_log: bool = False,
    timeout: int = 60,
) -> dict:
    """Run cross-reference, citation, and label validation (issue #45).

    Args:
        project_dir: Project root containing ``01_manuscript/``,
            ``02_supplementary/``, and ``00_shared/bib_files/``.
        doc_type: One of ``manuscript``, ``supplementary``, ``all``.
        parse_log: Also parse ``*.log`` files for LaTeX cross-ref warnings.
        timeout: Subprocess timeout in seconds.
    """
    project_path = resolve_project_path(project_dir)
    script = _script_path(project_path, "check_references.py")
    args = ["--doc-type", doc_type]
    if parse_log:
        args.append("--log")
    return _run_script(script, project_path, args, timeout)


def check_float_order(
    project_dir: str,
    doc_type: str = "manuscript",
    fix: bool = False,
    dry_run: bool = False,
    timeout: int = 60,
) -> dict:
    """Validate (and optionally renumber) figure/table reference order (issue #44).

    Args:
        project_dir: Project root.
        doc_type: ``manuscript``, ``supplementary``, or ``all``.
        fix: Apply rename + reference updates.
        dry_run: Preview the fix without writing.
        timeout: Subprocess timeout in seconds.
    """
    if fix and dry_run:
        return {
            "success": False,
            "error": "Choose either fix=True or dry_run=True, not both.",
        }
    project_path = resolve_project_path(project_dir)
    script = _script_path(project_path, "check_float_order.py")
    args = ["--doc-type", doc_type]
    if fix:
        args.append("--fix")
    if dry_run:
        args.append("--dry-run")
    return _run_script(script, project_path, args, timeout)


__all__ = ["check_references", "check_float_order"]

# EOF
