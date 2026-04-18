#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Views for the scitex-writer editor Django app.

Mirrors the figrecipe/_django/views.py pattern: one `editor_page` serves
the SPA shell; `api_dispatch` is a catch-all that routes `<path:endpoint>`
to the HANDLERS registry (with a few parameterized fallbacks for
`api/claims/<id>` and `api/claims/<id>/chain`).
"""

from __future__ import annotations

import logging
import os

from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt

from .handlers import (
    HANDLERS,
    handle_add_claim,
    handle_claim_chain,
    handle_get_claim,
    handle_list_claims,
    handle_remove_claim,
)
from .services import get_or_create_project

logger = logging.getLogger(__name__)


def _get_project(request):
    """Resolve the current project from ?working_dir= or WRITER_WORKING_DIR."""
    working_dir = request.GET.get("working_dir") or os.environ.get(
        "WRITER_WORKING_DIR", ""
    )
    if not working_dir:
        return None
    try:
        return get_or_create_project(working_dir)
    except FileNotFoundError:
        logger.warning("[Writer] Project not found: %s", working_dir)
        return None


def editor_page(request):
    """Serve the editor shell page."""
    project = _get_project(request)
    project_dir = str(project.project_dir) if project else ""
    html = render_to_string(
        "writer/editor.html",
        {
            "app_name": "writer",
            "app_label": "SciTeX Writer",
            "project_dir": project_dir,
            "dark_mode": project.dark_mode if project else False,
        },
        request=request,
    )
    return HttpResponse(html)


@csrf_exempt
def api_dispatch(request, endpoint):
    """Dispatch API calls to handler functions.

    Resolution order:
      1. Exact match in HANDLERS (with method allow-list check).
      2. Parameterized claim endpoints: `api/claims/<id>`, `api/claims/<id>/chain`.
      3. 404.
    """
    project = _get_project(request)
    if project is None:
        return JsonResponse(
            {"error": "No project loaded. Pass ?working_dir=<path>."}, status=400
        )

    entry = HANDLERS.get(endpoint)
    if entry is not None:
        handler, allowed_methods = entry
        if request.method not in allowed_methods:
            return JsonResponse(
                {"error": f"Method {request.method} not allowed"}, status=405
            )

        # Method-dispatched endpoints where HANDLERS maps to None
        if endpoint == "api/claims":
            handler = (
                handle_add_claim if request.method == "POST" else handle_list_claims
            )

        try:
            return handler(request, project)
        except Exception as exc:
            logger.exception("[Writer] API error on /%s", endpoint)
            return JsonResponse({"error": str(exc)}, status=500)

    # Parameterized: api/claims/<id> or api/claims/<id>/chain
    if endpoint.startswith("api/claims/"):
        rest = endpoint[len("api/claims/") :].strip("/")
        parts = rest.split("/") if rest else []
        if len(parts) == 1:
            claim_id = parts[0]
            try:
                if request.method == "DELETE":
                    return handle_remove_claim(request, project, claim_id)
                return handle_get_claim(request, project, claim_id)
            except Exception as exc:
                logger.exception("[Writer] claim %s", claim_id)
                return JsonResponse({"error": str(exc)}, status=500)
        if len(parts) == 2 and parts[1] == "chain":
            try:
                return handle_claim_chain(request, project, parts[0])
            except Exception as exc:
                logger.exception("[Writer] claim chain %s", parts[0])
                return JsonResponse({"error": str(exc)}, status=500)

    return JsonResponse({"error": f"Unknown endpoint: {endpoint}"}, status=404)
