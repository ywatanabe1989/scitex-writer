#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bibliography browsing handlers."""

from __future__ import annotations

import re

from django.http import JsonResponse

from scitex_writer._ports import scholar as _scholar


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


_ENTRY_HEAD_RE = re.compile(r"@(\w+)\{([^,\s]+)", re.IGNORECASE)
_DOI_FIELD_RE = re.compile(r"doi\s*=\s*[{\"]([^}\"]+)", re.IGNORECASE)
_TITLE_FIELD_RE = re.compile(r"title\s*=\s*[{\"]([^}\"]+)", re.IGNORECASE)


def handle_bib_entries(request, project):
    bib_dir = project.project_dir / "00_shared" / "bib_files"
    if not bib_dir.exists():
        return JsonResponse({"entries": [], "count": 0})

    library_root = _scholar.scholar_library_root(project.project_dir)

    entries = []
    for bib_file in sorted(bib_dir.glob("*.bib")):
        content = bib_file.read_text(encoding="utf-8")
        for block in _iter_bib_blocks(content):
            head = _ENTRY_HEAD_RE.search(block)
            if not head:
                continue
            entry_type, citation_key = head.groups()
            doi_m = _DOI_FIELD_RE.search(block)
            title_m = _TITLE_FIELD_RE.search(block)
            entry = {
                "citation_key": citation_key,
                "entry_type": entry_type,
                "bibfile": bib_file.name,
                "doi": doi_m.group(1) if doi_m else None,
                "title": title_m.group(1) if title_m else None,
            }
            if library_root is not None and entry["doi"]:
                md = _scholar.metadata_for_doi(library_root, entry["doi"])
                if md is not None:
                    entry["scholar"] = _compact_scholar(md)
            entries.append(entry)
    return JsonResponse({"entries": entries, "count": len(entries)})


def _iter_bib_blocks(content: str):
    """Yield each `@type{...}` block so field extraction stays scoped."""
    starts = [m.start() for m in re.finditer(r"@\w+\{", content)]
    starts.append(len(content))
    for i in range(len(starts) - 1):
        yield content[starts[i] : starts[i + 1]]


def _compact_scholar(md: dict) -> dict:
    m = md.get("metadata", {}) or {}
    basic = m.get("basic", {}) or {}
    id_ = m.get("id", {}) or {}
    pub = m.get("publication", {}) or {}
    access = m.get("access", {}) or {}
    citation = m.get("citation_count", {}) or {}
    return {
        "paper_id": md.get("_paper_id"),
        "title": basic.get("title"),
        "authors": basic.get("authors"),
        "year": basic.get("year"),
        "abstract": basic.get("abstract"),
        "doi": id_.get("doi"),
        "arxiv_id": id_.get("arxiv_id"),
        "pmid": id_.get("pmid"),
        "journal": pub.get("journal"),
        "short_journal": pub.get("short_journal"),
        "impact_factor": pub.get("impact_factor"),
        "citation_count": citation.get("total"),
        "is_open_access": access.get("is_open_access"),
        "oa_url": access.get("oa_url"),
    }
