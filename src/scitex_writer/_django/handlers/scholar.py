#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scholar-bridge handlers (optional; degrade when scholar absent)."""

from __future__ import annotations

import json
import re

from django.http import JsonResponse

from scitex_writer._ports import scholar as _scholar
from scitex_writer._ports import scholar_cli as _scholar_cli


def handle_scholar_status(request, project):
    """Report the bridge's view of the project's scholar link."""
    root = _scholar.scholar_library_root(project.project_dir)
    return JsonResponse(
        {
            "scholar_importable": _scholar.SCHOLAR_AVAILABLE,
            "scholar_cli_on_path": _scholar_cli.scholar_cli_on_path(),
            "library_root": str(root) if root else None,
            "index_db_present": bool(root and (root / "index.db").is_file()),
        }
    )


def handle_scholar_library(request, project):
    """List all papers in the user's scholar library (paginated)."""
    root = _scholar.scholar_library_root(project.project_dir)
    if root is None:
        return JsonResponse({"entries": [], "count": 0, "reason": "no_library"})

    try:
        limit = max(1, min(int(request.GET.get("limit", "200")), 1000))
    except ValueError:
        limit = 200
    try:
        offset = max(0, int(request.GET.get("offset", "0")))
    except ValueError:
        offset = 0

    cards = _scholar.iter_library_cards(root)
    total = len(cards)
    window = cards[offset : offset + limit]
    return JsonResponse({"entries": window, "count": total, "offset": offset})


def handle_scholar_enrich(request, project):
    """Run ``scitex-scholar bibtex <bibliography.bib> --project <name>``."""
    bib = project.project_dir / "00_shared" / "bib_files" / "bibliography.bib"
    if not bib.is_file():
        return JsonResponse(
            {"ok": False, "log": f"No bibliography file at {bib}"}, status=400
        )
    project_name = project.project_dir.name
    ok, log = _scholar_cli.enrich_bib(bib, project_name)
    return JsonResponse({"ok": ok, "log": log})


def handle_scholar_add_to_manuscript(request, project):
    """Append a BibTeX entry for ``paper_id`` to bibliography.bib."""
    try:
        body = json.loads(request.body.decode() or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    paper_id = body.get("paper_id")
    if not paper_id:
        return JsonResponse({"error": "paper_id required"}, status=400)

    root = _scholar.scholar_library_root(project.project_dir)
    if root is None:
        return JsonResponse({"error": "No scholar library available"}, status=400)

    md = _scholar.metadata_for_paper_id(root, paper_id)
    if md is None:
        return JsonResponse({"error": f"Unknown paper_id: {paper_id}"}, status=404)

    citation_key = _derive_citation_key(md)
    bib_dir = project.project_dir / "00_shared" / "bib_files"
    bib_dir.mkdir(parents=True, exist_ok=True)
    bib_file = bib_dir / "bibliography.bib"
    existing = bib_file.read_text() if bib_file.exists() else ""

    citation_key = _unique_key(existing, citation_key)
    entry = _format_bib_entry(citation_key, md)

    with open(bib_file, "a", encoding="utf-8") as f:
        if existing and not existing.endswith("\n"):
            f.write("\n")
        f.write(entry + "\n")

    return JsonResponse({"ok": True, "citation_key": citation_key})


def _derive_citation_key(md: dict) -> str:
    m = md.get("metadata", {}) or {}
    basic = m.get("basic", {}) or {}
    authors = basic.get("authors") or []
    first = (authors[0] if authors else "Unknown") or "Unknown"
    last = first.split()[-1].strip(",.")
    last = re.sub(r"[^A-Za-z]", "", last) or "Unknown"
    year = basic.get("year") or "nd"
    return f"{last}{year}"


def _unique_key(existing_bib: str, key: str) -> str:
    if f"{{{key}," not in existing_bib and f"{{{key}\n" not in existing_bib:
        return key
    for suffix in "abcdefghijklmnopqrstuvwxyz":
        candidate = f"{key}{suffix}"
        if (
            f"{{{candidate}," not in existing_bib
            and f"{{{candidate}\n" not in existing_bib
        ):
            return candidate
    return f"{key}_{hash(existing_bib) & 0xFFFF:x}"


def _format_bib_entry(key: str, md: dict) -> str:
    m = md.get("metadata", {}) or {}
    basic = m.get("basic", {}) or {}
    id_ = m.get("id", {}) or {}
    pub = m.get("publication", {}) or {}
    fields = []
    if basic.get("title"):
        fields.append(f"  title   = {{{basic['title']}}}")
    authors = basic.get("authors") or []
    if authors:
        fields.append(f"  author  = {{{' and '.join(authors)}}}")
    if basic.get("year") is not None:
        fields.append(f"  year    = {{{basic['year']}}}")
    if pub.get("journal"):
        fields.append(f"  journal = {{{pub['journal']}}}")
    if id_.get("doi"):
        fields.append(f"  doi     = {{{id_['doi']}}}")
    body = ",\n".join(fields)
    return f"@article{{{key},\n{body}\n}}"
