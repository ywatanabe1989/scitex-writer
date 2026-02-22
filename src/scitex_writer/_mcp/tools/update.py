#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/tools/update.py

"""MCP tool: update project engine files."""

from typing import Optional

from fastmcp import FastMCP

from ..handlers._update import update_project as _update_project


def register_tools(mcp: FastMCP) -> None:
    """Register update tools."""

    @mcp.tool()
    def writer_update_project(
        project_dir: str,
        branch: Optional[str] = None,
        tag: Optional[str] = None,
        dry_run: bool = False,
        force: bool = False,
    ) -> dict:
        """[writer] Update engine files of a scitex-writer project to the latest version.

        Replaces build scripts, LaTeX styles, and base LaTeX templates with the
        latest version from the installed scitex-writer package.  If branch or tag
        is specified, pulls from GitHub instead.

        User content is NEVER modified:
        - 00_shared/authors.tex, title.tex, keywords.tex, journal_name.tex
        - 00_shared/bib_files/bibliography.bib
        - 00_shared/claims.json
        - 01_manuscript/contents/
        - 02_supplementary/contents/
        - 03_revision/contents/

        Args:
            project_dir: Path to the scitex-writer project to update.
            branch: Pull from a specific template branch (requires internet).
            tag: Pull from a specific template tag/version (requires internet).
            dry_run: If True, report what would change without modifying files.
            force: If True, skip the uncommitted-changes git safety check.

        Returns:
            dict with success, updated_paths, skipped_paths, preserved_paths,
            git_safe, warnings, dry_run flag, and message.
        """
        return _update_project(
            project_dir, branch=branch, tag=tag, dry_run=dry_run, force=force
        )


# EOF
