#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_editor/_routes_bib.py

"""Bibliography browsing routes."""

import re

from flask import jsonify


def register_bib_routes(app, editor):
    """Register bibliography routes."""

    @app.route("/api/bib/files")
    def bib_files():
        """List bibliography files."""
        bib_dir = editor.project_dir / "00_shared" / "bib_files"
        if not bib_dir.exists():
            return jsonify({"files": [], "count": 0})

        files = []
        for bib_file in sorted(bib_dir.glob("*.bib")):
            content = bib_file.read_text(encoding="utf-8")
            entry_count = content.count("@")
            files.append(
                {
                    "name": bib_file.name,
                    "path": str(bib_file.relative_to(editor.project_dir)),
                    "entry_count": entry_count,
                    "is_merged": bib_file.name == "bibliography.bib",
                }
            )

        return jsonify({"files": files, "count": len(files)})

    @app.route("/api/bib/entries")
    def bib_entries():
        """List all bibliography entries."""
        bib_dir = editor.project_dir / "00_shared" / "bib_files"
        if not bib_dir.exists():
            return jsonify({"entries": [], "count": 0})

        entries = []
        for bib_file in sorted(bib_dir.glob("*.bib")):
            content = bib_file.read_text(encoding="utf-8")
            pattern = r"@(\w+)\{([^,\s]+)"
            for match in re.finditer(pattern, content):
                entry_type, citation_key = match.groups()
                entries.append(
                    {
                        "citation_key": citation_key,
                        "entry_type": entry_type,
                        "bibfile": bib_file.name,
                    }
                )

        return jsonify({"entries": entries, "count": len(entries)})


# EOF
