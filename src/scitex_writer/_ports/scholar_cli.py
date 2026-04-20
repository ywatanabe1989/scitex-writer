"""scitex-scholar CLI shell-out helpers.

Writer's UI renders the **Enrich bibliography** button unconditionally.
On click, the handler shells out to ``scitex-scholar`` if the binary is
on PATH, otherwise returns an install-help message. No Python import
coupling to scitex-scholar.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def scholar_cli_on_path() -> bool:
    return shutil.which("scitex-scholar") is not None or _python_module_available()


def _python_module_available() -> bool:
    """Fallback: `python -m scitex_scholar` works even without a console script."""
    try:
        import scitex_scholar  # noqa: F401

        return True
    except ImportError:
        return False


def _command_prefix() -> list[str]:
    cli = shutil.which("scitex-scholar")
    if cli:
        return [cli]
    import sys

    return [sys.executable, "-m", "scitex_scholar"]


def enrich_bib(
    bib_path: Path, project_name: str, timeout_s: int = 600
) -> tuple[bool, str]:
    """Run ``scitex-scholar bibtex <bib> --project <name>``.

    Returns ``(ok, combined_stdout_stderr)``. Caller streams the string
    to a log drawer.
    """
    if not scholar_cli_on_path():
        return (
            False,
            "scitex-scholar is not installed. Run `pip install scitex-scholar` "
            "(or `pip install scitex-writer[scholar]`) then click again.",
        )
    cmd = _command_prefix() + ["bibtex", str(bib_path), "--project", project_name]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s)
        return r.returncode == 0, (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        return False, f"scitex-scholar timed out after {timeout_s}s"
    except OSError as exc:
        return False, f"Could not run scitex-scholar: {exc}"


def link_project_tree(project_dir: Path, timeout_s: int = 30) -> tuple[bool, str]:
    """Idempotently run ``scitex-scholar link-project-tree <project_dir>``."""
    if not scholar_cli_on_path():
        return False, "scitex-scholar not installed"
    cmd = _command_prefix() + ["link-project-tree", str(project_dir)]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s)
        return r.returncode == 0, (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        return False, f"link-project-tree timed out after {timeout_s}s"
    except OSError as exc:
        return False, f"Could not run scitex-scholar: {exc}"
