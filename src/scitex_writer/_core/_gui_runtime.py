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

#: Writer's fixed slot in the fleet-wide GUI port scheme. The GUI binds
#: exactly this port (or an explicit ``--port``) and fails loud when it is
#: taken — it never silently drifts to the next free port.
DEFAULT_PORT = 31298

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


def _listening_socket_inodes(port: int) -> set[str]:
    """Socket inodes of every process LISTENing on ``port``, from /proc/net."""
    inodes: set[str] = set()
    for proc_net in ("/proc/net/tcp", "/proc/net/tcp6"):
        try:
            lines = Path(proc_net).read_text().splitlines()[1:]
        except OSError:
            continue
        for line in lines:
            fields = line.split()
            if len(fields) < 10:
                continue
            # local_address is "HEXADDR:HEXPORT"; state 0A == TCP_LISTEN.
            _, _, hex_port = fields[1].rpartition(":")
            if fields[3] != "0A" or int(hex_port, 16) != port:
                continue
            inodes.add(fields[9])
    return inodes


def port_holder(port: int) -> Optional[dict]:
    """Identify the process LISTENing on ``port``: ``{pid, name}``, or None.

    Reads /proc directly rather than shelling out to ``ss``/``lsof``, which
    are absent from many containers — a hint that silently disappears in the
    exact minimal environment where the operator most needs it is not a hint.

    Only processes the caller can see are reported: an inode we cannot map to
    a pid (another user's process) yields ``{pid: None}``, so the caller says
    "another process" rather than inventing a wrong one.
    """
    inodes = _listening_socket_inodes(port)
    if not inodes:
        return None
    unreadable = False
    for proc_dir in Path("/proc").iterdir():
        if not proc_dir.name.isdigit():
            continue
        try:
            fds = list((proc_dir / "fd").iterdir())
        except PermissionError:
            # Some /proc mounts (hidepid, and our own agent containers) deny
            # this even for processes we own. That is NOT "somebody else's
            # process" — it is "we could not look". Say which.
            unreadable = True
            continue
        except OSError:
            continue  # vanished mid-scan — keep going
        for fd in fds:
            try:
                target = os.readlink(fd)
            except OSError:
                continue
            if target[8:-1] not in inodes or not target.startswith("socket:["):
                continue
            try:
                name = (proc_dir / "comm").read_text().strip()
            except OSError:
                name = "?"
            try:
                # NUL-separated argv. Carries the evidence needed to tell one
                # of OUR OWN orphaned editors from an unrelated squatter — a
                # comm of "python" says nothing, but the argv names the module.
                cmdline = (proc_dir / "cmdline").read_bytes().replace(b"\0", b" ")
                argv = cmdline.decode("utf-8", "replace").strip()
            except OSError:
                argv = ""
            return {"pid": int(proc_dir.name), "name": name, "cmdline": argv}
    # Something IS listening (we found the socket inode) but we could not put a
    # pid to it. Distinguish "not allowed to look" from "looked, found nobody":
    # reporting a /proc we cannot read as "another user's process" is a guess,
    # and a confident wrong answer is the bug this module exists to avoid.
    return {"pid": None, "name": None, "cmdline": "", "unreadable": unreadable}


def terminate(pid: int, timeout: float = 5.0) -> bool:
    """SIGTERM ``pid`` and wait for it to die. True when it is gone.

    Used by ``gui serve --force`` to reclaim the port from an ORPHANED editor
    of ours — one that never cleared its state file, so ``stop()`` (which reads
    that file) cannot see it. Escalates to SIGKILL only after SIGTERM has been
    given the full timeout to shut down cleanly.
    """
    if not pid_alive(pid):
        return True
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError:
        return not pid_alive(pid)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline and pid_alive(pid):
        time.sleep(0.1)
    if not pid_alive(pid):
        return True
    try:
        os.kill(pid, signal.SIGKILL)
    except OSError:
        return not pid_alive(pid)
    deadline = time.monotonic() + 2.0
    while time.monotonic() < deadline and pid_alive(pid):
        time.sleep(0.1)
    return not pid_alive(pid)


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
