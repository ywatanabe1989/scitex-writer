#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/handlers/_update/_source.py

"""Source resolution: find the scitex-writer package root."""

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from ._constants import TEMPLATE_REPO_URL


def find_package_root(branch: Optional[str], tag: Optional[str]) -> tuple[Path, bool]:
    """Return (source_dir, is_temp).

    Finds the scitex-writer package source root. Uses importlib.metadata
    for editable installs, falls back to navigating from __file__, and
    clones from GitHub if a specific branch/tag is requested.

    Returns
    -------
    source_dir : Path
        Root of the scitex-writer repository to copy from.
    is_temp : bool
        True if source_dir is a temporary clone that must be deleted.
    """
    if branch or tag:
        return _clone_from_github(branch, tag)

    # Try importlib.metadata (editable installs via PEP 610)
    root = _try_importlib_metadata()
    if root:
        return root, False

    # Try .pth file approach (pip editable install)
    root = _try_pth_file()
    if root:
        return root, False

    # Navigate up from this file:
    # _source.py -> _update/ -> handlers/ -> _mcp/ -> scitex_writer/ -> src/ -> repo_root/
    candidate = Path(__file__).resolve().parents[5]
    if is_valid_root(candidate):
        return candidate, False

    return _clone_from_github(branch, tag)


def is_valid_root(path: Path) -> bool:
    """Check if path looks like a scitex-writer repository root."""
    return (
        path.exists()
        and (path / "src" / "scitex_writer").is_dir()
        and (path / "scripts").is_dir()
        and (path / "compile.sh").is_file()
    )


def read_version(source_dir: Path) -> str:
    """Read package version from pyproject.toml."""
    pyproject = source_dir / "pyproject.toml"
    if pyproject.exists():
        try:
            text = pyproject.read_text()
            for line in text.splitlines():
                if line.strip().startswith("version"):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
        except Exception:
            pass
    return "unknown"


def _try_importlib_metadata() -> Optional[Path]:
    """Try to find the package root via importlib.metadata."""
    try:
        import importlib.metadata as _meta
        import json

        dist = _meta.distribution("scitex-writer")
        direct_url = dist.read_text("direct_url.json")
        if direct_url:
            info = json.loads(direct_url)
            url = info.get("url", "")
            if url.startswith("file://"):
                candidate = Path(url.replace("file://", ""))
                if is_valid_root(candidate):
                    return candidate
    except Exception:
        pass
    return None


def _try_pth_file() -> Optional[Path]:
    """Try to find the package root via .pth files."""
    try:
        import site

        dirs = site.getsitepackages()
        try:
            dirs.append(site.getusersitepackages())
        except AttributeError:
            pass
        for site_dir in dirs:
            site_path = Path(site_dir)
            for pth in site_path.glob("_scitex_writer*.pth"):
                src_dir = Path(pth.read_text().strip())
                candidate = src_dir.parent if src_dir.name == "src" else src_dir
                if is_valid_root(candidate):
                    return candidate
    except Exception:
        pass
    return None


def _clone_from_github(branch: Optional[str], tag: Optional[str]) -> tuple[Path, bool]:
    """Clone scitex-writer from GitHub. Returns (path, True)."""
    tmp_dir = tempfile.mkdtemp(prefix="scitex_writer_update_")
    tmp_path = Path(tmp_dir)
    cmd = ["git", "clone", "--depth", "1"]
    if branch:
        cmd.extend(["--branch", branch])
    elif tag:
        cmd.extend(["--branch", tag])
    cmd.extend([TEMPLATE_REPO_URL, str(tmp_path / "repo")])
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise RuntimeError(f"Git clone failed: {result.stderr.strip()}")
    return tmp_path / "repo", True


# EOF
