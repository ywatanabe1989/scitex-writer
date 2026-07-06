#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/handlers/_compile.py

"""Compilation handlers: manuscript, supplementary, revision."""

from ..utils import resolve_project_path, run_compile_script


def _auto_render_claims(project_path) -> None:
    """Regenerate claims_rendered.tex from claims.json (\\vclaim SSoT), fail loud.

    claims.json is the source of truth for \\vclaim values; a stale
    claims_rendered.tex would ship outdated values into the PDF. If claims.json
    is absent there is nothing to render. If rendering fails, raise rather than
    compile with a stale file — a render failure when claims.json is present is
    always a defect (malformed JSON / broken claim definition).
    """
    claims_json = project_path / "00_shared" / "claims.json"
    if not claims_json.exists():
        return
    from ._claim import render_claims

    result = render_claims(str(project_path))
    if not result.get("success"):
        raise RuntimeError(
            f"Failed to render claims_rendered.tex from {claims_json}: "
            f"{result.get('error', 'unknown error')}. Fix claims.json or the "
            f"claim definitions; compiling now would ship a stale "
            f"claims_rendered.tex."
        )


def _inject_version_stamp(project_path) -> None:
    """Write 00_shared/scitex_writer_version.tex for PDF metadata (best-effort)."""
    try:
        from scitex_writer import __version__

        version_tex = project_path / "00_shared" / "scitex_writer_version.tex"
        version_tex.write_text(
            f"\\def\\ScitexWriterVersion{{{__version__}}}\n"
            f"\\hypersetup{{pdfcreator={{Compiled by SciTeX Writer v{__version__}}}}}\n"
        )
    except Exception:
        pass  # Never block compilation due to version stamp


def compile_manuscript(
    project_dir: str,
    timeout: int = 300,
    no_figs: bool = False,
    no_tables: bool = False,
    no_diff: bool = False,
    draft: bool = False,
    dark_mode: bool = False,
    quiet: bool = False,
    verbose: bool = False,
    engine: str | None = None,
) -> dict:
    """Compile manuscript to PDF."""
    project_path = resolve_project_path(project_dir)
    _auto_render_claims(project_path)
    _inject_version_stamp(project_path)
    return run_compile_script(
        project_path,
        "manuscript",
        timeout=timeout,
        no_figs=no_figs,
        no_tables=no_tables,
        no_diff=no_diff,
        draft=draft,
        dark_mode=dark_mode,
        quiet=quiet,
        verbose=verbose,
        engine=engine,
    )


def compile_supplementary(
    project_dir: str,
    timeout: int = 300,
    no_figs: bool = False,
    no_tables: bool = False,
    no_diff: bool = False,
    draft: bool = False,
    dark_mode: bool = False,
    quiet: bool = False,
    engine: str | None = None,
) -> dict:
    """Compile supplementary materials to PDF."""
    project_path = resolve_project_path(project_dir)
    _auto_render_claims(project_path)
    _inject_version_stamp(project_path)
    return run_compile_script(
        project_path,
        "supplementary",
        timeout=timeout,
        no_figs=no_figs,
        no_tables=no_tables,
        no_diff=no_diff,
        draft=draft,
        dark_mode=dark_mode,
        quiet=quiet,
        engine=engine,
    )


def compile_revision(
    project_dir: str,
    track_changes: bool = False,
    timeout: int = 300,
    no_diff: bool = True,
    draft: bool = False,
    dark_mode: bool = False,
    quiet: bool = False,
    engine: str | None = None,
) -> dict:
    """Compile revision document to PDF."""
    project_path = resolve_project_path(project_dir)
    _auto_render_claims(project_path)
    _inject_version_stamp(project_path)
    return run_compile_script(
        project_path,
        "revision",
        timeout=timeout,
        no_diff=no_diff,
        draft=draft,
        dark_mode=dark_mode,
        quiet=quiet,
        track_changes=track_changes,
        engine=engine,
    )


# EOF
