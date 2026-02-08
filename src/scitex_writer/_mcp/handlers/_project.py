#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/handlers/_project.py

"""Project management handlers: clone, info, PDF paths, document types."""

from __future__ import annotations

import shutil
import subprocess
from typing import Literal, Optional

from ..utils import resolve_project_path


def clone_project(
    project_dir: str,
    git_strategy: Literal["child", "parent", "origin", "none"] = "child",
    branch: Optional[str] = None,
    tag: Optional[str] = None,
) -> dict:
    """Create a new writer project from template."""
    try:
        project_path = resolve_project_path(project_dir)

        if project_path.exists():
            return {
                "success": False,
                "error": f"Directory already exists: {project_path}",
            }

        repo_url = "https://github.com/ywatanabe1989/scitex-writer.git"
        cmd = ["git", "clone"]

        if branch:
            cmd.extend(["--branch", branch])
        elif tag:
            cmd.extend(["--branch", tag])

        cmd.extend([repo_url, str(project_path)])
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            return {"success": False, "error": f"Git clone failed: {result.stderr}"}

        if git_strategy == "none":
            git_dir = project_path / ".git"
            if git_dir.exists():
                shutil.rmtree(git_dir)
        elif git_strategy == "child":
            git_dir = project_path / ".git"
            if git_dir.exists():
                shutil.rmtree(git_dir)
            subprocess.run(["git", "init"], cwd=str(project_path), capture_output=True)
            subprocess.run(
                ["git", "add", "."], cwd=str(project_path), capture_output=True
            )
            subprocess.run(
                ["git", "commit", "-m", "Initial commit from scitex-writer template"],
                cwd=str(project_path),
                capture_output=True,
            )

        return {
            "success": True,
            "project_path": str(project_path),
            "git_strategy": git_strategy,
            "structure": {
                "00_shared": "Shared resources",
                "01_manuscript": "Main manuscript",
                "02_supplementary": "Supplementary materials",
                "03_revision": "Revision documents",
            },
            "message": f"Successfully created writer project at {project_path}",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_project_info(project_dir: str) -> dict:
    """Get writer project information."""
    try:
        project_path = resolve_project_path(project_dir)

        if not project_path.exists():
            return {"success": False, "error": f"Project not found: {project_path}"}

        dirs = {
            "shared": project_path / "00_shared",
            "manuscript": project_path / "01_manuscript",
            "supplementary": project_path / "02_supplementary",
            "revision": project_path / "03_revision",
            "scripts": project_path / "scripts",
        }

        pdfs = {
            "manuscript": project_path / "01_manuscript" / "manuscript.pdf",
            "supplementary": project_path / "02_supplementary" / "supplementary.pdf",
            "revision": project_path / "03_revision" / "revision.pdf",
        }

        compiled_pdfs = {k: str(v) if v.exists() else None for k, v in pdfs.items()}

        git_root = None
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=str(project_path),
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                git_root = result.stdout.strip()
        except Exception:
            pass

        return {
            "success": True,
            "project_name": project_path.name,
            "project_dir": str(project_path),
            "git_root": git_root,
            "documents": {k: str(v) for k, v in dirs.items() if v.exists()},
            "compiled_pdfs": compiled_pdfs,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_pdf(
    project_dir: str,
    doc_type: Literal["manuscript", "supplementary", "revision"] = "manuscript",
) -> dict:
    """Get path to compiled PDF."""
    try:
        project_path = resolve_project_path(project_dir)
        pdf_paths = {
            "manuscript": project_path / "01_manuscript" / "manuscript.pdf",
            "supplementary": project_path / "02_supplementary" / "supplementary.pdf",
            "revision": project_path / "03_revision" / "revision.pdf",
        }

        pdf_path = pdf_paths.get(doc_type)
        if pdf_path and pdf_path.exists():
            return {
                "success": True,
                "exists": True,
                "doc_type": doc_type,
                "pdf_path": str(pdf_path),
            }
        else:
            return {
                "success": True,
                "exists": False,
                "doc_type": doc_type,
                "pdf_path": None,
                "message": f"No compiled PDF found for {doc_type}",
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_document_types() -> dict:
    """List available document types."""
    return {
        "success": True,
        "document_types": [
            {"id": "manuscript", "name": "Manuscript", "directory": "01_manuscript"},
            {
                "id": "supplementary",
                "name": "Supplementary",
                "directory": "02_supplementary",
            },
            {
                "id": "revision",
                "name": "Revision",
                "directory": "03_revision",
                "supports_track_changes": True,
            },
        ],
        "shared_directory": {"id": "shared", "directory": "00_shared"},
    }


# EOF
