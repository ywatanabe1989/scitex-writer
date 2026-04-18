#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bibliography browsing handlers."""

from __future__ import annotations

import re

from django.http import JsonResponse


def handle_bib_files(request, project):
    bib_dir = project.project_dir / "00_shared" / "bib_files"
    if not bib_dir.exists():
        return JsonResponse({"files": [], "count": 0})

    files = []
    for bib_file in sorted(bib_dir.glob("*.bib")):
        content = bib_file.read_text(encoding="utf-8")
        files.append(
            {
                "name": bib_file.name,
                "path": str(bib_file.relative_to(project.project_dir)),
                "entry_count": content.count("@"),
                "is_merged": bib_file.name == "bibliography.bib",
            }
        )
    return JsonResponse({"files": files, "count": len(files)})


def handle_bib_entries(request, project):
    bib_dir = project.project_dir / "00_shared" / "bib_files"
    if not bib_dir.exists():
        return JsonResponse({"entries": [], "count": 0})

    entries = []
    pattern = r"@(\w+)\{([^,\s]+)"
    for bib_file in sorted(bib_dir.glob("*.bib")):
        content = bib_file.read_text(encoding="utf-8")
        for match in re.finditer(pattern, content):
            entry_type, citation_key = match.groups()
            entries.append(
                {
                    "citation_key": citation_key,
                    "entry_type": entry_type,
                    "bibfile": bib_file.name,
                }
            )
    return JsonResponse({"entries": entries, "count": len(entries)})
