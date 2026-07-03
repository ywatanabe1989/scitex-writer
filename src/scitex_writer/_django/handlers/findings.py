#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Findings handler — serves the manuscript-findings feed to the editor UI.

Thin Django wrapper; the read logic lives in
``scitex_writer._mcp.handlers._findings`` (framework-agnostic), mirroring the
claim/bib/media handlers.
"""

from __future__ import annotations

from django.http import JsonResponse


def handle_findings(request, project):
    """GET the manuscript-findings feed for the current project.

    Always 200 with a feed object (empty feed when the paper has not been
    compiled since the feature landed) — the Details pane renders "no
    notifications" for an empty feed, never an error state.
    """
    from ..._mcp.handlers._findings import get_findings

    return JsonResponse(get_findings(str(project.project_dir)))
