#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_core/_gui_runtime.py

"""Runtime state for the writer GUI server (`gui serve/open/status/stop`).

State lives at ``<scope>/.scitex/writer/runtime/gui.json`` per the fleet
runtime-state layout, so ``gui status`` / ``gui stop`` in a fresh shell can
find a server launched earlier by ``gui serve`` / ``gui open``.

Pure state logic only — no Click, no Django. The CLI layer
(`_cli/commands/gui.py`) owns argument parsing and process spawning.
"""

from __future__ import annotations

import json
import os
import signal
import time
from pathlib import Path
from typing import Optional, Union

PathLike = Union[str, Path]

_STATE_FIELDS = ("pid", "port", "host", "project", "started_at")


def state_path() -> Path:
    """Resolve the GUI state-file path via the fleet local-state convention.

    ``SCITEX_WRITER_GUI_STATE`` overrides the resolved path (isolated CI
    runs, tests). Otherwise same resolution as ``_annotations/_db.py``
    (scope = current git root); swap to the public
    ``scitex_config.runtime_path`` once it exists
    (card: writer-migrate-runtime-db-path-to-public-scitex-config-api).
    """
    override = os.environ.get("SCITEX_WRITER_GUI_STATE")
    if override:
        return Path(override)
    from scitex_config._ecosystem import local_state

    return Path(local_state.runtime_path("writer", "gui.json"))


def read_state(path: Optional[PathLike] = None) -> Optional[dict]:
    """Return the persisted state dict, or None when absent/corrupt."""
    p = Path(path) if path is not None else state_path()
    try:
        loaded = json.loads(p.read_text())
    except (OSError, ValueError):
        return None
    return loaded if isinstance(loaded, dict) else None


def write_state(
    pid: int,
    port: int,
    host: str,
    project: str,
    path: Optional[PathLike] = None,
) -> Path:
    """Persist the running server's coordinates; returns the state-file path."""
    p = Path(path) if path is not None else state_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    state = {
        "pid": pid,
        "port": port,
        "host": host,
        "project": project,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    p.write_text(json.dumps(state, indent=2))
    return p


def clear_state(path: Optional[PathLike] = None) -> None:
    """Remove the state file. Idempotent."""
    p = Path(path) if path is not None else state_path()
    try:
        p.unlink()
    except OSError:
        pass


def pid_alive(pid: int) -> bool:
    """True when ``pid`` refers to a live process we could signal.

    A zombie still answers signal 0 but is already dead — without this
    check ``stop()`` would poll an exited-but-unreaped server for the
    full timeout and report ``terminated=False``.
    """
    if not isinstance(pid, int) or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    try:
        stat = Path(f"/proc/{pid}/stat").read_text()
        if stat.rpartition(")")[2].split()[0] == "Z":
            return False
    except (OSError, IndexError):
        pass
    return True


def status(path: Optional[PathLike] = None) -> dict:
    """Report the server's state, self-healing a stale file.

    A state file whose pid is dead (crash, kill -9) is removed so the next
    ``open`` auto-serves instead of pointing the browser at a dead port.
    """
    state = read_state(path)
    if state is None:
        return {"running": False}
    if not pid_alive(state.get("pid", -1)):
        clear_state(path)
        return {"running": False, "stale_state_cleared": True}
    url = f"http://{state.get('host')}:{state.get('port')}"
    return {"running": True, "url": url, **{k: state.get(k) for k in _STATE_FIELDS}}


def stop(path: Optional[PathLike] = None, timeout: float = 5.0) -> dict:
    """SIGTERM the recorded server and clear the state file. Idempotent."""
    current = status(path)
    if not current.get("running"):
        return {"stopped": False, "running": False}
    pid = current["pid"]
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError as exc:
        return {"stopped": False, "running": True, "pid": pid, "error": str(exc)}
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline and pid_alive(pid):
        time.sleep(0.1)
    clear_state(path)
    return {"stopped": True, "pid": pid, "terminated": not pid_alive(pid)}


# EOF
