#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/handlers/_export.py

"""Export handlers: arXiv manuscript packaging."""


import subprocess

from ..utils import resolve_project_path


def export_manuscript(
    project_dir: str,
    output_dir: str | None = None,
    format: str = "arxiv",
) -> dict:
    """Export manuscript as arXiv-ready tarball."""
    project_path = resolve_project_path(project_dir)
    export_script = project_path / "scripts" / "shell" / "export_arxiv.sh"

    if not export_script.exists():
        return {
            "success": False,
            "error": f"export_arxiv.sh not found at {export_script}",
        }

    cmd = ["env", "-u", "BASH_ENV", "/bin/bash", str(export_script)]

    if output_dir:
        cmd.extend(["--output-dir", output_dir])

    try:
        result = subprocess.run(
            cmd,
            cwd=str(project_path),
            capture_output=True,
            text=True,
            timeout=60,
        )

        default_output = str(project_path / "01_manuscript" / "export")
        tarball_dir = output_dir or default_output
        tarball_path = f"{tarball_dir}/manuscript.tar.gz"

        if result.returncode == 0:
            return {
                "success": True,
                "tarball_path": tarball_path,
                "message": "Manuscript exported for arXiv",
                "stdout": result.stdout[-2000:]
                if len(result.stdout) > 2000
                else result.stdout,
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
                "error": f"Export failed with exit code {result.returncode}",
            }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Export timed out after 60 seconds",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# EOF
