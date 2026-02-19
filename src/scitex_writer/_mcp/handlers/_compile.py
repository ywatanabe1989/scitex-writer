#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/handlers/_compile.py

"""Compilation handlers: manuscript, supplementary, revision."""

from __future__ import annotations

from ..utils import resolve_project_path, run_compile_script


def _auto_render_claims(project_path) -> None:
    """Render claims_rendered.tex if claims.json exists (silent, best-effort)."""
    claims_json = project_path / "00_shared" / "claims.json"
    if claims_json.exists():
        try:
            from ._claim import render_claims

            render_claims(str(project_path))
        except Exception:
            pass  # Never block compilation due to claims rendering


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
