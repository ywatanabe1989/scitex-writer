#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: scripts/python/_build_id.py
# Purpose: Per-compilation build IDs, PDF metadata injection, build registry.
#
# Build IDs let a compiled PDF be uniquely identified after it leaves the
# repo (e.g. when emailed to a collaborator). The ID is embedded in the
# PDF /Info dictionary via \hypersetup{pdfsubject=build:...} and recorded
# in `.scitex/writer/builds/builds.json` so later runs can list, diff, or
# reproduce a specific build.

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def _git_head_sha() -> Optional[str]:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short=12", "HEAD"],
            stderr=subprocess.DEVNULL,
        )
        return out.decode().strip()
    except Exception:
        return None


def _git_is_dirty() -> bool:
    try:
        out = subprocess.check_output(
            ["git", "status", "--porcelain"],
            stderr=subprocess.DEVNULL,
        )
        return bool(out.strip())
    except Exception:
        return False


def generate_build_id() -> str:
    """Short unique per-compilation build ID (6 hex chars)."""
    parts = [
        _git_head_sha() or "nogit",
        "dirty" if _git_is_dirty() else "clean",
        datetime.now(timezone.utc).isoformat(timespec="microseconds"),
    ]
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:6]


def register_build(
    build_id: str,
    doc_type: str,
    output_tex: Path,
    project_root: Optional[Path] = None,
) -> Optional[Path]:
    """Append a build record to `.scitex/writer/builds/builds.json`.

    Best-effort: returns None on any failure so registry writes never
    break compilation. Keeps the last 500 entries.
    """
    try:
        if project_root is None:
            project_root = Path(os.environ.get("PROJECT_ROOT") or os.getcwd()).resolve()
        registry_dir = project_root / ".scitex" / "writer" / "builds"
        registry_dir.mkdir(parents=True, exist_ok=True)
        registry_path = registry_dir / "builds.json"

        entry = {
            "build_id": build_id,
            "doc_type": doc_type,
            "git_commit": _git_head_sha(),
            "git_dirty": _git_is_dirty(),
            "timestamp": (
                datetime.now(timezone.utc)
                .isoformat(timespec="seconds")
                .replace("+00:00", "Z")
            ),
            "output_tex": str(output_tex),
            "engine": (
                os.getenv("SCITEX_WRITER_SELECTED_ENGINE", "")
                or os.getenv("SCITEX_WRITER_ENGINE", "")
                or "auto"
            ),
        }

        if registry_path.exists():
            try:
                data = json.loads(registry_path.read_text())
            except Exception:
                data = {"builds": []}
        else:
            data = {"builds": []}
        data.setdefault("builds", []).append(entry)
        data["builds"] = data["builds"][-500:]
        registry_path.write_text(json.dumps(data, indent=2) + "\n")
        return registry_path
    except Exception:
        return None


def inject_build_metadata(content: str, build_id: str) -> str:
    r"""Inject ``\hypersetup{pdfsubject=build:...}`` before ``\begin{document}``.

    hyperref finalizes PDF /Info at ``\begin{document}``, so the metadata
    must appear before then. Also exposes ``\scitexBuildID`` and
    ``\scitexBuildIDFootnote`` macros so document templates can opt into
    a tiny footer, colophon, or watermark without further changes here.
    """
    marker = r"\begin{document}"
    if marker not in content:
        return content

    block = (
        "% --- scitex-writer build identifier "
        + "-" * 38
        + "\n"
        + f"\\providecommand{{\\scitexBuildID}}{{build:{build_id}}}\n"
        + r"\providecommand{\scitexBuildIDFootnote}"
        + r"{\tiny\textcolor{gray}{\scitexBuildID}}"
        + "\n"
        + "\\AtBeginDocument{%\n"
        + "  \\@ifpackageloaded{hyperref}{%\n"
        + f"    \\hypersetup{{pdfsubject={{build:{build_id}}},"
        + "pdfkeywords={scitex-writer}}%\n"
        + "  }{}%\n"
        + "}\n"
        + "% "
        + "-" * 76
        + "\n"
    )
    return content.replace(
        marker, r"\makeatletter " + block + r"\makeatother " + marker, 1
    )


__all__ = [
    "generate_build_id",
    "register_build",
    "inject_build_metadata",
]

# EOF
