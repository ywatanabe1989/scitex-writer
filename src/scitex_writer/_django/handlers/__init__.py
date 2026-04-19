#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Handler package — thin Django wrappers around scitex-writer internals."""

from .bib import handle_bib_entries, handle_bib_files
from .claim import (
    handle_add_claim,
    handle_claim_chain,
    handle_get_claim,
    handle_list_claims,
    handle_remove_claim,
    handle_render_claims,
)
from .compile import handle_compile, handle_compile_status, handle_pdf
from .core import handle_ping, handle_project_info
from .files import handle_file, handle_list_files, handle_sections
from .media import handle_figures, handle_tables

# Endpoints where method on the same path selects a different handler are
# handled by the dispatcher itself; the map below resolves exact endpoint
# strings (after the leading slash) to (handler, allowed_methods) tuples.

# fmt: off
HANDLERS = {
    # Core
    "ping":                   (handle_ping,           ("GET",)),
    "api/project-info":       (handle_project_info,   ("GET",)),

    # Files
    "api/files":              (handle_list_files,     ("GET",)),
    "api/file":               (handle_file,           ("GET", "POST")),
    "api/sections":           (handle_sections,       ("GET",)),

    # Compile
    "api/compile":            (handle_compile,        ("POST",)),
    "api/compile/status":     (handle_compile_status, ("GET",)),
    "api/pdf":                (handle_pdf,            ("GET",)),

    # Bibliography
    "api/bib/files":          (handle_bib_files,      ("GET",)),
    "api/bib/entries":        (handle_bib_entries,    ("GET",)),

    # Media
    "api/figures":            (handle_figures,        ("GET",)),
    "api/tables":             (handle_tables,         ("GET",)),

    # Claims (non-parameterized)
    "api/claims":             (None,                  ("GET", "POST")),  # dispatched by method
    "api/claims/render":      (handle_render_claims,  ("POST",)),
}
# fmt: on

__all__ = [
    "HANDLERS",
    "handle_add_claim",
    "handle_claim_chain",
    "handle_get_claim",
    "handle_list_claims",
    "handle_remove_claim",
]
