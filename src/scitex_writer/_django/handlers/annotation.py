#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Annotation handlers — thin Django wrappers over ``scitex_writer._annotations``.

Spike 0 of the PDF-annotation → agent-feedback loop
(``docs/04_DESIGN_PDF_ANNOTATION_FEEDBACK_LOOP.md`` §3, §6.1): POST + GET
only, ``kind=text_comment``, ``source_ref`` page-only. Mirrors the
``scholar.py`` POST idiom and the model-less thin-wrapper layering of
``claim.py``. All persist / resolve / emit logic lives in the
framework-agnostic ``_annotations`` module.
"""

from __future__ import annotations

import json
from pathlib import Path

from django.http import JsonResponse

from ..._annotations import add_annotation, list_annotations


def _db_path_for(project) -> Path:
    """Project-scoped runtime DB (``<proj>/.scitex/writer/runtime/writer.db``).

    The design doc names ``local_state.runtime_path("writer","writer.db")``;
    that helper resolves scope from the server's cwd, but the Django server
    serves arbitrary manuscript ``working_dir``s, so we pin the DB under the
    *manuscript* project root (the location the doc actually names) to keep
    each manuscript's annotations with its own sources.
    """
    return project.project_dir / ".scitex" / "writer" / "runtime" / "writer.db"


def handle_add_annotation(request, project):
    """POST /api/annotations — persist one text-comment annotation and emit."""
    try:
        body = json.loads(request.body.decode() or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    try:
        result = add_annotation(
            body,
            project=project.project_dir.name,
            db_path=_db_path_for(project),
        )
    except ValueError as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)

    return JsonResponse(result)


def handle_list_annotations(request, project):
    """GET /api/annotations — list annotations (filter by doc_type/status/build_id)."""
    annotations = list_annotations(
        db_path=_db_path_for(project),
        doc_type=request.GET.get("doc_type") or None,
        status=request.GET.get("status") or None,
        build_id=request.GET.get("build_id") or None,
    )
    return JsonResponse({"annotations": annotations, "count": len(annotations)})
