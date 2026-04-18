#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Project state service — creation, caching.

A `ProjectState` holds per-project editor state (compile status, log, dark mode)
that Flask previously kept on the `WriterEditor` instance. Cached in-process
with a TTL so repeated HTTP requests for the same project reuse the same state.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

_project_cache: Dict[str, Tuple["ProjectState", float]] = {}
_CACHE_TTL_SECONDS = 3600


@dataclass
class ProjectState:
    """Per-project editor state (replaces Flask WriterEditor)."""

    project_dir: Path
    dark_mode: bool = False
    _compiling: bool = False
    _compile_result: Optional[Dict[str, Any]] = None
    _compile_log: str = ""
    _lock: Any = field(default=None, repr=False)

    def __post_init__(self) -> None:
        import threading

        self._lock = threading.Lock()


def get_or_create_project(project_dir: str) -> ProjectState:
    """Return a cached ProjectState for `project_dir`, creating one if missing.

    Raises FileNotFoundError if the directory does not exist.
    """
    _cleanup_expired()

    path = Path(project_dir).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Project directory not found: {path}")

    key = str(path)
    if key in _project_cache:
        state, _ = _project_cache[key]
        _project_cache[key] = (state, time.time())
        return state

    state = ProjectState(project_dir=path)
    _project_cache[key] = (state, time.time())
    logger.info("[Writer] Created project state for %s", path)
    return state


def remove_project(project_dir: str) -> None:
    """Evict a project from the cache."""
    key = str(Path(project_dir).resolve())
    _project_cache.pop(key, None)


def _cleanup_expired() -> None:
    now = time.time()
    expired = [
        k for k, (_, ts) in _project_cache.items() if now - ts > _CACHE_TTL_SECONDS
    ]
    for k in expired:
        _project_cache.pop(k, None)
