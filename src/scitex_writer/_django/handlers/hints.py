#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hints handler — serves the manuscript-hints feed to the editor UI.

Thin Django wrapper; the read logic lives in
``scitex_writer._mcp.handlers._hints`` (framework-agnostic), mirroring the
claim/bib/media handlers.
"""

from __future__ import annotations

from django.http import JsonResponse


def handle_hints(request, project):
    """GET the manuscript-hints feed for the current project.

    Always 200 with a feed object (empty feed when the paper has not been
    compiled since the feature landed) — the Details pane renders "no hints"
    for an empty feed, never an error state.
    """
    from ..._mcp.handlers._hints import get_hints

    return JsonResponse(get_hints(str(project.project_dir)))
