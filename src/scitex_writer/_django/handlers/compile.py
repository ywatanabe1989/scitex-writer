#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compilation and PDF serving handlers."""

from __future__ import annotations

import json
import threading

from django.http import FileResponse, JsonResponse


def _do_compile(project, doc_type: str, draft: bool, dark_mode: bool) -> None:
    from scitex_writer import compile as sw_compile

    project_str = str(project.project_dir)
    kwargs = {"draft": draft, "dark_mode": dark_mode, "quiet": True}
    try:
        if doc_type == "manuscript":
            result = sw_compile.manuscript(project_str, **kwargs)
        elif doc_type == "supplementary":
            result = sw_compile.supplementary(project_str, **kwargs)
        elif doc_type == "revision":
            result = sw_compile.revision(project_str, **kwargs)
        else:
            result = {"success": False, "error": f"Unknown doc_type: {doc_type}"}

        project._compile_result = result
        if isinstance(result, dict):
            project._compile_log = result.get("log", result.get("output", ""))
        else:
            project._compile_log = str(result)
    except Exception as exc:
        project._compile_result = {"success": False, "error": str(exc)}
        project._compile_log = str(exc)
    finally:
        project._compiling = False


def handle_compile(request, project):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    if project._compiling:
        return JsonResponse({"error": "Compilation already in progress"}, status=409)

    try:
        data = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        data = {}

    doc_type = data.get("doc_type", "manuscript")
    draft = bool(data.get("draft", False))
    # Dark mode from request body (current UI theme) falls back to
    # ProjectState.dark_mode which is persisted per-project.
    dark_mode = bool(data.get("dark_mode", project.dark_mode))
    project.dark_mode = dark_mode

    project._compiling = True
    project._compile_log = ""
    project._compile_result = None

    thread = threading.Thread(
        target=_do_compile,
        args=(project, doc_type, draft, dark_mode),
        daemon=True,
    )
    thread.start()

    return JsonResponse(
        {"status": "started", "doc_type": doc_type, "dark_mode": dark_mode}
    )


def handle_compile_status(request, project):
    return JsonResponse(
        {
            "compiling": project._compiling,
            "result": project._compile_result,
            "log": project._compile_log,
        }
    )


def handle_pdf(request, project):
    doc_type = request.GET.get("doc_type", "manuscript")
    pdf_map = {
        "manuscript": "01_manuscript/manuscript.pdf",
        "supplementary": "02_supplementary/supplementary.pdf",
        "revision": "03_revision/revision.pdf",
    }
    rel_path = pdf_map.get(doc_type)
    if not rel_path:
        return JsonResponse({"error": f"Unknown doc_type: {doc_type}"}, status=400)

    pdf_path = project.project_dir / rel_path
    if not pdf_path.exists():
        return JsonResponse({"error": "PDF not found. Compile first."}, status=404)

    as_attachment = request.GET.get("download") in ("1", "true")
    return FileResponse(
        open(pdf_path, "rb"),
        content_type="application/pdf",
        filename=f"{doc_type}.pdf",
        as_attachment=as_attachment,
    )
