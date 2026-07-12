#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_compile/_runner.py

"""
Compilation script execution.

Executes LaTeX compilation scripts and captures results.
"""

from __future__ import annotations

import os
from datetime import datetime
from logging import getLogger
from pathlib import Path
from typing import Callable, Optional

from .._dataclasses import CompilationResult
from .._dataclasses.config import DOC_TYPE_DIRS
from .._utils._pdf_pages import produced_page_count
from ._execute import _execute_with_callbacks, _run_sh_command
from ._parser import parse_output
from ._validator import validate_before_compile

logger = getLogger(__name__)

EXIT_PROMOTED_WITH_WARNINGS = 3
"""The compile scripts' exit code for "a valid PDF was produced and promoted,
but the engine exited non-zero" -- in practice a non-fatal bibtex error on a
stub/duplicate bib entry, which makes latexmk exit 12 even though pdfTeX
finalized a complete PDF. Set by
modules/compilation_compiled_tex_to_compiled_pdf.sh and propagated by
compile_{manuscript,supplementary,revision}.sh.

It is a DISTINCT code, not 0, precisely so the state stays distinguishable from
a clean compile: the PDF is kept (destroying a usable manuscript over a
warning-grade bib problem is the bug being fixed here), but no one -- human or
caller -- is told the run was clean."""

_PROMOTED_WARNING = (
    "PDF PROMOTED despite a non-zero engine exit: the document compiled to "
    "{pages} page(s), but the engine reported an error -- usually a non-fatal "
    "bibtex problem such as a stub or duplicate bib entry. The PDF is usable; "
    "FIX THE BIBLIOGRAPHY BEFORE SUBMISSION (see the .log / .blg)."
)


def _doc_latex_log(project_dir: Path, doc_type: str) -> Path:
    """The document's OWN LaTeX log -- where pdfTeX writes "Output written on".

    Deliberately not `_find_output_files`'s "newest *.log", which can be the
    tee'd global.log rather than the document's own log.
    """
    return project_dir / DOC_TYPE_DIRS[doc_type] / "logs" / f"{doc_type}.log"


def _get_compile_script(project_dir: Path, doc_type: str) -> Path:
    """
    Get compile script path for document type.

    Parameters
    ----------
    project_dir : Path
        Path to project directory
    doc_type : str
        Document type ('manuscript', 'supplementary', 'revision')

    Returns
    -------
    Path
        Path to compilation script
    """
    script_map = {
        "manuscript": project_dir / "scripts" / "shell" / "compile_manuscript.sh",
        "supplementary": project_dir / "scripts" / "shell" / "compile_supplementary.sh",
        "revision": project_dir / "scripts" / "shell" / "compile_revision.sh",
    }
    return script_map.get(doc_type)


def _find_output_files(
    project_dir: Path,
    doc_type: str,
) -> tuple:
    """
    Find generated output files after compilation.

    Parameters
    ----------
    project_dir : Path
        Path to project directory
    doc_type : str
        Document type

    Returns
    -------
    tuple
        (output_pdf, diff_pdf, log_file)
    """
    doc_dir = project_dir / DOC_TYPE_DIRS[doc_type]

    # Find generated PDF
    pdf_name = f"{doc_type}.pdf"
    potential_pdf = doc_dir / pdf_name
    output_pdf = potential_pdf if potential_pdf.exists() else None

    # Check for diff PDF
    diff_name = f"{doc_type}_diff.pdf"
    potential_diff = doc_dir / diff_name
    diff_pdf = potential_diff if potential_diff.exists() else None

    # Find log file
    log_dir = doc_dir / "logs"
    log_file = None
    if log_dir.exists():
        log_files = list(log_dir.glob("*.log"))
        if log_files:
            log_file = max(log_files, key=lambda p: p.stat().st_mtime)

    return output_pdf, diff_pdf, log_file


def run_compile(
    doc_type: str,
    project_dir: Path,
    timeout: int = 300,
    track_changes: bool = False,
    no_figs: bool = False,
    ppt2tif: bool = False,
    crop_tif: bool = False,
    quiet: bool = False,
    verbose: bool = False,
    force: bool = False,
    log_callback: Optional[Callable[[str], None]] = None,
    progress_callback: Optional[Callable[[int, str], None]] = None,
    command_runner: Optional[Callable[..., dict]] = None,
) -> CompilationResult:
    """
    Run compilation script and parse results with optional callbacks.

    Parameters
    ----------
    doc_type : str
        Document type ('manuscript', 'supplementary', 'revision')
    project_dir : Path
        Path to project directory (containing 01_manuscript/, etc.)
    timeout : int
        Timeout in seconds
    track_changes : bool
        Enable change tracking (revision only)
    no_figs : bool
        Exclude figures for quick compilation (manuscript only)
    ppt2tif : bool
        Convert PowerPoint to TIF on WSL
    crop_tif : bool
        Crop TIF images to remove excess whitespace
    quiet : bool
        Suppress detailed logs for LaTeX compilation
    verbose : bool
        Show detailed logs for LaTeX compilation
    force : bool
        Force full recompilation, ignore cache (manuscript only)
    log_callback : Optional[Callable[[str], None]]
        Called with each log line
    progress_callback : Optional[Callable[[int, str], None]]
        Called with progress updates (percent, step)

    command_runner : Optional[Callable[..., dict]]
        Executor for the non-callback path, same shape as
        :func:`_run_sh_command` (cmd, verbose, timeout, stream_output) ->
        dict. Defaults to :func:`_run_sh_command`. Exposed so callers and
        tests can supply an alternate executor without patching internals.

    Returns
    -------
    CompilationResult
        Compilation status and outputs
    """
    if command_runner is None:
        command_runner = _run_sh_command

    start_time = datetime.now()
    project_dir = Path(project_dir).absolute()

    # Helper for progress tracking
    def progress(percent: int, step: str):
        if progress_callback:
            progress_callback(percent, step)
        logger.info(f"Progress: {percent}% - {step}")

    # Helper for logging
    def log(message: str):
        if log_callback:
            log_callback(message)
        logger.info(message)

    # Progress: Starting
    progress(0, "Starting compilation...")
    log("[INFO] Starting LaTeX compilation...")

    # Validate project structure before compilation
    try:
        progress(5, "Validating project structure...")
        validate_before_compile(project_dir, doc_type)
        log("[INFO] Project structure validated")
    except Exception as e:
        error_msg = f"[ERROR] Validation failed: {e}"
        log(error_msg)
        return CompilationResult(
            success=False,
            exit_code=1,
            stdout="",
            stderr=str(e),
            duration=0.0,
        )

    # Get compile script
    compile_script = _get_compile_script(project_dir, doc_type)
    if not compile_script or not compile_script.exists():
        error_msg = f"[ERROR] Compilation script not found: {compile_script}"
        log(error_msg)
        return CompilationResult(
            success=False,
            exit_code=127,
            stdout="",
            stderr=error_msg,
            duration=0.0,
        )

    # Build command
    progress(10, "Preparing compilation command...")
    script_path = compile_script.absolute()
    cmd = [str(script_path)]

    # Add document-specific options
    if doc_type == "revision":
        if track_changes:
            cmd.append("--track-changes")

    elif doc_type == "manuscript":
        if no_figs:
            cmd.append("--no_figs")
        if ppt2tif:
            cmd.append("--ppt2tif")
        if crop_tif:
            cmd.append("--crop_tif")
        if quiet:
            cmd.append("--quiet")
        elif verbose:
            cmd.append("--verbose")
        if force:
            cmd.append("--force")

    elif doc_type == "supplementary":
        if not no_figs:  # For supplementary, --figs means include figures (default)
            cmd.append("--figs")
        if ppt2tif:
            cmd.append("--ppt2tif")
        if crop_tif:
            cmd.append("--crop_tif")
        if quiet:
            cmd.append("--quiet")

    log(f"[INFO] Running: {' '.join(cmd)}")
    log(f"[INFO] Working directory: {project_dir}")

    try:
        cwd_original = Path.cwd()
        os.chdir(project_dir)

        try:
            progress(15, "Executing LaTeX compilation...")

            # Use callbacks version if callbacks provided
            if log_callback:
                result_dict = _execute_with_callbacks(
                    command=cmd,
                    cwd=project_dir,
                    timeout=timeout,
                    log_callback=log_callback,
                )
            else:
                # Use simple subprocess execution
                result_dict = command_runner(
                    cmd,
                    verbose=True,
                    timeout=timeout,
                    stream_output=True,
                )

            result = type(
                "Result",
                (),
                {
                    "returncode": result_dict["exit_code"],
                    "stdout": result_dict["stdout"],
                    "stderr": result_dict["stderr"],
                },
            )()

            duration = (datetime.now() - start_time).total_seconds()
        finally:
            os.chdir(cwd_original)

        # Find output files. Exit 3 means the script PRODUCED and promoted a PDF
        # and told us so; its artifacts must be located exactly as on exit 0 --
        # blanking them out is what USED to throw away a perfectly good PDF.
        promoted = result.returncode == EXIT_PROMOTED_WITH_WARNINGS
        if result.returncode == 0 or promoted:
            progress(90, "Compilation finished, locating output files...")
            output_pdf, diff_pdf, log_file = _find_output_files(project_dir, doc_type)
            if output_pdf:
                log(f"[SUCCESS] PDF generated: {output_pdf}")
        else:
            output_pdf, diff_pdf, log_file = None, None, None
            log(f"[ERROR] Compilation failed with exit code {result.returncode}")

        # Parse errors and warnings
        progress(95, "Parsing compilation logs...")
        errors, warnings = parse_output(result.stdout, result.stderr, log_file=log_file)

        # A promoted run is a success ONLY if a real PDF with pages > 0 exists.
        # We re-derive that here rather than trusting the exit code, so a shell
        # that claims 3 without an artifact can never become a silent success:
        # no PDF (or a zero-page husk) still FAILS, exactly like any other
        # non-zero exit. This is the "produced a PDF" vs "produced nothing" line.
        success = result.returncode == 0
        if promoted:
            pages = (
                produced_page_count(output_pdf, _doc_latex_log(project_dir, doc_type))
                if output_pdf
                else 0
            )
            if pages > 0:
                success = True
                warnings.insert(0, _PROMOTED_WARNING.format(pages=pages))
                log(f"[WARNING] {_PROMOTED_WARNING.format(pages=pages)}")
            else:
                output_pdf = None
                errors.insert(
                    0,
                    "Compile reported a promoted PDF (exit 3) but no PDF with "
                    "pages > 0 exists. Treating as a FAILURE.",
                )
                log(f"[ERROR] {errors[0]}")

        compilation_result = CompilationResult(
            success=success,
            exit_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            output_pdf=output_pdf,
            diff_pdf=diff_pdf,
            log_file=log_file,
            duration=duration,
            errors=errors,
            warnings=warnings,
            message=(
                f"Compiled WITH WARNINGS (exit {result.returncode}): "
                "a PDF was produced but the engine reported an error"
                if (promoted and success)
                else None
            ),
        )

        if compilation_result.success:
            progress(100, "Complete with warnings!" if promoted else "Complete!")
            log(f"[SUCCESS] Compilation succeeded in {duration:.2f}s")
        else:
            progress(100, "Compilation failed")
            if errors:
                log(f"[ERROR] Found {len(errors)} errors")

        return compilation_result

    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        logger.error(f"Compilation error: {e}")
        return CompilationResult(
            success=False,
            exit_code=1,
            stdout="",
            stderr=str(e),
            duration=duration,
        )


__all__ = ["run_compile"]

# EOF
