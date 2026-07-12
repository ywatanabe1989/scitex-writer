#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_compile/_execute.py

"""Subprocess execution for the compile path.

The two executors `run_compile` dispatches to, split out of `_runner` so that
module stays about ORCHESTRATION (validate -> build command -> interpret result)
rather than process plumbing. `_run_sh_command` is the default; the streaming
`_execute_with_callbacks` is used when the caller wants line-by-line output.

Both return the same dict shape -- {stdout, stderr, exit_code, success} -- which
is also the contract of the `command_runner` injection seam on `run_compile`.
NOTE `success` here means "exit code 0" and nothing more; the compile scripts'
exit 3 ("PDF produced but engine exited non-zero") is interpreted in `_runner`,
not here.
"""

from __future__ import annotations

import fcntl
import os
import subprocess
import time
from pathlib import Path
from typing import Callable, Optional

def _execute_with_callbacks(
    command: list,
    cwd: Path,
    timeout: int,
    log_callback: Optional[Callable[[str], None]] = None,
) -> dict:
    """
    Execute command with line-by-line output capture and callbacks.

    Parameters
    ----------
    command : list
        Command to execute as list
    cwd : Path
        Working directory
    timeout : int
        Timeout in seconds
    log_callback : Optional[Callable[[str], None]]
        Called with each output line

    Returns
    -------
    dict
        Dict with stdout, stderr, exit_code, success
    """
    # Set environment for unbuffered output
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    process = subprocess.Popen(
        command,
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=0,  # Unbuffered
        cwd=str(cwd),
        env=env,
    )

    stdout_lines = []
    stderr_lines = []
    start_time = time.time()

    # Make file descriptors non-blocking
    def make_non_blocking(fd):
        flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

    make_non_blocking(process.stdout)
    make_non_blocking(process.stderr)

    stdout_buffer = b""
    stderr_buffer = b""

    try:
        while True:
            # Check timeout
            if timeout and (time.time() - start_time) > timeout:
                process.kill()
                timeout_msg = f"[ERROR] Command timed out after {timeout} seconds"
                if log_callback:
                    log_callback(timeout_msg)
                stderr_lines.append(timeout_msg)
                break

            # Check if process has finished
            poll_result = process.poll()

            # Read from stdout
            try:
                chunk = process.stdout.read()
                if chunk:
                    stdout_buffer += chunk
                    # Process complete lines
                    while b"\n" in stdout_buffer:
                        line, stdout_buffer = stdout_buffer.split(b"\n", 1)
                        line_str = line.decode("utf-8", errors="replace")
                        stdout_lines.append(line_str)
                        if log_callback:
                            log_callback(line_str)
            except (IOError, BlockingIOError):
                pass

            # Read from stderr
            try:
                chunk = process.stderr.read()
                if chunk:
                    stderr_buffer += chunk
                    # Process complete lines
                    while b"\n" in stderr_buffer:
                        line, stderr_buffer = stderr_buffer.split(b"\n", 1)
                        line_str = line.decode("utf-8", errors="replace")
                        stderr_lines.append(line_str)
                        if log_callback:
                            log_callback(f"[STDERR] {line_str}")
            except (IOError, BlockingIOError):
                pass

            # If process finished, do final read and break
            if poll_result is not None:
                # Process remaining buffer content
                if stdout_buffer:
                    line_str = stdout_buffer.decode("utf-8", errors="replace")
                    stdout_lines.append(line_str)
                    if log_callback:
                        log_callback(line_str)

                if stderr_buffer:
                    line_str = stderr_buffer.decode("utf-8", errors="replace")
                    stderr_lines.append(line_str)
                    if log_callback:
                        log_callback(f"[STDERR] {line_str}")

                break

            # Small sleep to prevent CPU spinning
            time.sleep(0.05)

    except Exception:
        process.kill()
        raise

    return {
        "stdout": "\n".join(stdout_lines),
        "stderr": "\n".join(stderr_lines),
        "exit_code": process.returncode,
        "success": process.returncode == 0,
    }


def _run_sh_command(
    cmd: list,
    verbose: bool = True,
    timeout: int = 300,
    stream_output: bool = True,
) -> dict:
    """
    Run shell command and return result dictionary.

    Replaces scitex.sh.sh() dependency.
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
            "success": result.returncode == 0,
        }
    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": f"Command timed out after {timeout} seconds",
            "exit_code": -1,
            "success": False,
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "exit_code": -1,
            "success": False,
        }

__all__ = ["_execute_with_callbacks", "_run_sh_command"]

# EOF
