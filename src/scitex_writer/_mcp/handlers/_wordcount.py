#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/handlers/_wordcount.py

"""Word-count handler: per-section word + element counts written to files.

A pure-Python port of ``scripts/shell/modules/count_words.sh``. It resolves the
per-doc-type paths from ``config/config_<doc_type>.yaml`` (the same keys the
shell read via ``yq``), counts words per abstract/IMRaD section with
``texcount``, counts figure/table elements by counting compiled ``[0-9]*.tex``
files, and writes one integer per key into ``misc.wordcount_dir`` -- exactly the
files the manuscript's ``\\readwordcount`` reads.

Fail-loud + never-empty: a missing/unreadable source contributes 0 (never an
empty file), so the downstream ``\\num{}`` can never receive an empty argument
(the siunitx "Invalid number" fatal that failed every latexmk pass). A missing
config / texcount / doc dir returns an explicit error dict with an actionable
hint -- never a silent fallback.
"""

import re
import subprocess
from pathlib import Path
from shutil import which
from typing import Dict, Optional

from ..utils import resolve_project_path
from ..._dataclasses import WordCountResult

DOC_DIRS = {
    "manuscript": "01_manuscript",
    "supplementary": "02_supplementary",
    "revision": "03_revision",
}

# Abstract + IMRaD sections (word counts). Order preserved for stable output.
_ABSTRACT = "abstract"
_IMRD = ("introduction", "methods", "results", "discussion")
_WORD_SECTIONS = (_ABSTRACT,) + _IMRD

# Config key paths (the same ones count_words.sh read via yq).
_CFG_DOC_ROOT = ("paths", "doc_root_dir")
_CFG_FIG_DIR = ("figures", "compiled_dir")
_CFG_TAB_DIR = ("tables", "compiled_dir")
_CFG_WC_DIR = ("misc", "wordcount_dir")

# Compiled element files look like "01_....tex"; headers / FINAL are excluded.
_ELEMENT_GLOB = "[0-9]*.tex"
_EXCLUDE_NAMES = ("FINAL.tex",)


def _cfg_get(cfg: dict, path, default=None):
    """Nested dict lookup by a key-tuple; ``default`` if any level is absent."""
    cur = cfg
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def _resolve(project_path: Path, rel) -> Optional[Path]:
    """Resolve a config path (possibly ``./``-relative) against the project root."""
    if not rel:
        return None
    rel = str(rel)
    if rel.startswith("./"):
        rel = rel[2:]
    return (project_path / rel).resolve()


def _count_elements(compiled_dir: Optional[Path]) -> int:
    """Count compiled element ``.tex`` files (figures or tables); 0 if none.

    Excludes ``*_Header.tex`` and ``FINAL.tex`` -- matches count_words.sh."""
    if not compiled_dir or not compiled_dir.is_dir():
        return 0
    n = 0
    for f in compiled_dir.glob(_ELEMENT_GLOB):
        if f.name in _EXCLUDE_NAMES or f.name.endswith("_Header.tex"):
            continue
        n += 1
    return n


def _count_words_texcount(texcount: str, section_tex: Path) -> int:
    """Words in one section via ``texcount -inc -1 -sum``; 0 when absent/empty.

    NEVER returns a non-int: extract the first integer texcount prints, else 0
    (the never-empty invariant that protects the manuscript's \\num{})."""
    if not section_tex.exists():
        return 0
    try:
        out = subprocess.run(
            [texcount, str(section_tex), "-inc", "-1", "-sum"],
            capture_output=True,
            text=True,
            timeout=30,
        ).stdout
    except (subprocess.TimeoutExpired, OSError):
        return 0
    m = re.search(r"\d+", out)
    return int(m.group(0)) if m else 0


def count_words(project_dir: str, doc_type: str = "manuscript") -> dict:
    """Count words + figures + tables for a document type and write count files.

    Parameters
    ----------
    project_dir : str
        Path to the scitex-writer project directory.
    doc_type : str
        One of 'manuscript' (default), 'supplementary', 'revision'.

    Returns
    -------
    dict
        ``{success, doc_type, counts, total, output_files, error}`` -- the
        serialized :class:`WordCountResult`. ``success`` is explicit; on failure
        ``error`` carries an actionable hint (fail-loud, never a silent empty).
    """
    try:
        if doc_type not in DOC_DIRS:
            return {
                "success": False,
                "error": (
                    f"Invalid doc_type '{doc_type}'. "
                    f"Must be one of: {tuple(DOC_DIRS)}"
                ),
            }

        project_path = resolve_project_path(project_dir)

        config_path = project_path / "config" / f"config_{doc_type}.yaml"
        if not config_path.exists():
            return {
                "success": False,
                "error": (
                    f"Config not found: {config_path}. "
                    f"Run `scitex-writer update-project` or check --doc-type."
                ),
            }
        try:
            import yaml
        except ImportError:
            return {
                "success": False,
                "error": "PyYAML not installed. Fix: pip install pyyaml",
            }
        try:
            cfg = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as e:
            return {"success": False, "error": f"{config_path} is not valid YAML: {e}"}

        wc_dir = _resolve(project_path, _cfg_get(cfg, _CFG_WC_DIR))
        if wc_dir is None:
            return {
                "success": False,
                "error": (
                    f"misc.wordcount_dir is missing in {config_path}; "
                    f"cannot write count files."
                ),
            }
        doc_root = _resolve(
            project_path, _cfg_get(cfg, _CFG_DOC_ROOT, DOC_DIRS[doc_type])
        )
        fig_dir = _resolve(project_path, _cfg_get(cfg, _CFG_FIG_DIR))
        tab_dir = _resolve(project_path, _cfg_get(cfg, _CFG_TAB_DIR))

        texcount = which("texcount")
        if not texcount:
            return {
                "success": False,
                "error": (
                    "texcount not found. Fix: install texlive-binaries "
                    "(provides texcount) or add it to PATH."
                ),
            }

        # init(): clear stale *.txt then recreate (mirror count_words.sh).
        wc_dir.mkdir(parents=True, exist_ok=True)
        for stale in wc_dir.glob("*.txt"):
            stale.unlink()

        counts: Dict[str, int] = {}
        output_files = []

        def _write(key: str, value: int) -> None:
            value = int(value)
            counts[key] = value
            out = wc_dir / f"{key}_count.txt"
            out.write_text(f"{value}\n", encoding="utf-8")
            output_files.append(str(out))

        _write("figure", _count_elements(fig_dir))
        _write("table", _count_elements(tab_dir))
        contents = doc_root / "contents"
        for sec in _WORD_SECTIONS:
            _write(sec, _count_words_texcount(texcount, contents / f"{sec}.tex"))
        imrd_total = sum(counts[s] for s in _IMRD)
        _write("imrd", imrd_total)

        result = WordCountResult(
            success=True,
            doc_type=doc_type,
            counts=counts,
            total=imrd_total,
            output_files=output_files,
        )
        result.validate()
        return result.to_dict()
    except Exception as e:
        return {"success": False, "error": str(e)}


__all__ = ["count_words"]

# EOF
