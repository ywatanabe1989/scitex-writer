#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/handlers/_engine_paths.py

"""Config loading + path resolution shared by the ported engine pipelines.

Every shell module the engine port replaces began the same way: source
``config/load_config.sh``, which ``yq``-read ``config/config_<doc_type>.yaml`` and
exported the resulting paths as environment variables. The Python pipelines read
the SAME file and the SAME keys -- this module is that step, once, so the diff and
archive pipelines cannot drift apart on how a config path is resolved.

The boundary check is the part that matters: a config path is resolved against the
project root and then ASSERTED to stay inside it, so a ``..`` in the YAML cannot
make a pipeline write outside the project.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

DOC_DIRS = {
    "manuscript": "01_manuscript",
    "supplementary": "02_supplementary",
    "revision": "03_revision",
}


def cfg_get(cfg: dict, path, default=None):
    """Nested dict lookup by a key-tuple; ``default`` if any level is absent."""
    cur = cfg
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def resolve_one(project_path: Path, rel) -> Optional[Path]:
    """Resolve a config path (possibly ``./``-relative) against the project root."""
    if not rel:
        return None
    rel = str(rel)
    if rel.startswith("./"):
        rel = rel[2:]
    return (project_path / rel).resolve()


def within(boundary: Path, target: Path) -> bool:
    """True iff ``target`` resolves to a path inside ``boundary`` (guard ``..``)."""
    try:
        target.resolve().relative_to(boundary)
        return True
    except ValueError:
        return False


def load_doc_config(project_path: Path, doc_type: str):
    """Return ``(cfg, error)`` for the doc type's ``config/config_<doc_type>.yaml``."""
    config_path = project_path / "config" / f"config_{doc_type}.yaml"
    if not config_path.exists():
        return None, (
            f"Config not found: {config_path}. "
            f"Run `scitex-writer update-project` or check --doc-type."
        )
    try:
        import yaml
    except ImportError:
        return None, "PyYAML not installed. Fix: pip install pyyaml"
    try:
        return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}, None
    except yaml.YAMLError as e:
        return None, f"{config_path} is not valid YAML: {e}"


def resolve_paths(project_path: Path, cfg: dict, keys: dict, section: str):
    """Return ``(paths, error)``: every requested config path, boundary-checked.

    ``keys`` maps a friendly name to the key-tuple to look up; ``section`` names
    the config section for the error message.
    """
    paths = {}
    for name, key in keys.items():
        resolved = resolve_one(project_path, cfg_get(cfg, key))
        if resolved is None:
            return None, (
                f"{'.'.join(key)} is missing in the config; cannot resolve the "
                f"{name.replace('_', ' ')}."
            )
        paths[name] = resolved

    boundary = project_path.resolve()
    if not all(within(boundary, p) for p in paths.values()):
        return None, (
            f"Refusing to run: a {section}.* path resolves OUTSIDE the project "
            f"root {boundary} (config path escape via '..'?)."
        )
    return paths, None


__all__ = [
    "DOC_DIRS",
    "cfg_get",
    "load_doc_config",
    "resolve_one",
    "resolve_paths",
    "within",
]

# EOF
