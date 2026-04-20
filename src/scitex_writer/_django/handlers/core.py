#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Core handlers: health check, project info."""

from __future__ import annotations

from django.http import JsonResponse


def handle_ping(request, project):
    return JsonResponse({"status": "ok"})


def handle_project_info(request, project):
    project_dir = project.project_dir
    doc_types = []
    for name, subdir in [
        ("manuscript", "01_manuscript"),
        ("supplementary", "02_supplementary"),
        ("revision", "03_revision"),
    ]:
        if (project_dir / subdir).exists():
            doc_types.append(name)

    return JsonResponse(
        {
            "project_dir": str(project_dir),
            "project_name": project_dir.name,
            "doc_types": doc_types,
            "has_shared": (project_dir / "00_shared").exists(),
        }
    )
