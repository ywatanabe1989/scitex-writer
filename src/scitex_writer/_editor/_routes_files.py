#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_editor/_routes_files.py

"""File tree and file read/write routes."""

from pathlib import Path

from flask import jsonify, request


def _build_file_tree(root: Path, rel_base: Path = None) -> list:
    """Build a nested file tree structure."""
    if rel_base is None:
        rel_base = root

    entries = []
    try:
        items = sorted(root.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    except PermissionError:
        return entries

    skip_dirs = {
        ".git",
        "__pycache__",
        "node_modules",
        ".tox",
        "archive",
        "GITIGNORED",
        ".claude",
    }
    skip_extensions = {".aux", ".log", ".out", ".fls", ".fdb_latexmk", ".synctex.gz"}

    for item in items:
        if item.name.startswith(".") and item.name != ".gitignore":
            continue
        if item.name in skip_dirs:
            continue

        rel_path = str(item.relative_to(rel_base))

        if item.is_dir():
            children = _build_file_tree(item, rel_base)
            entries.append(
                {
                    "name": item.name,
                    "path": rel_path,
                    "type": "directory",
                    "children": children,
                }
            )
        else:
            if item.suffix in skip_extensions:
                continue
            entries.append(
                {
                    "name": item.name,
                    "path": rel_path,
                    "type": "file",
                    "extension": item.suffix,
                }
            )

    return entries


def register_file_routes(app, editor):
    """Register file-related routes."""

    @app.route("/api/files")
    def list_files():
        """Get project file tree."""
        tree = _build_file_tree(editor.project_dir)
        return jsonify({"tree": tree})

    @app.route("/api/file")
    def read_file():
        """Read a file's content."""
        rel_path = request.args.get("path", "")
        if not rel_path:
            return jsonify({"error": "No path specified"}), 400

        file_path = (editor.project_dir / rel_path).resolve()

        # Security: ensure path is within project
        if not str(file_path).startswith(str(editor.project_dir)):
            return jsonify({"error": "Access denied"}), 403

        if not file_path.exists():
            return jsonify({"error": "File not found"}), 404

        if not file_path.is_file():
            return jsonify({"error": "Not a file"}), 400

        try:
            content = file_path.read_text(encoding="utf-8")
            return jsonify(
                {
                    "path": rel_path,
                    "content": content,
                    "name": file_path.name,
                    "extension": file_path.suffix,
                }
            )
        except UnicodeDecodeError:
            return jsonify({"error": "Binary file cannot be displayed"}), 400

    @app.route("/api/file", methods=["POST"])
    def save_file():
        """Save file content."""
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data"}), 400

        rel_path = data.get("path", "")
        content = data.get("content", "")

        if not rel_path:
            return jsonify({"error": "No path specified"}), 400

        file_path = (editor.project_dir / rel_path).resolve()

        # Security: ensure path is within project
        if not str(file_path).startswith(str(editor.project_dir)):
            return jsonify({"error": "Access denied"}), 403

        try:
            file_path.write_text(content, encoding="utf-8")
            return jsonify({"success": True, "path": rel_path})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/sections")
    def list_sections():
        """List tex sections for a document type."""
        doc_type = request.args.get("doc_type", "manuscript")

        dir_map = {
            "manuscript": "01_manuscript/contents",
            "supplementary": "02_supplementary/contents",
            "revision": "03_revision/contents",
            "shared": "00_shared",
        }

        content_dir = editor.project_dir / dir_map.get(
            doc_type, "01_manuscript/contents"
        )
        sections = []

        if content_dir.exists():
            for f in sorted(content_dir.glob("*.tex")):
                sections.append(
                    {
                        "name": f.stem,
                        "path": str(f.relative_to(editor.project_dir)),
                        "filename": f.name,
                    }
                )

        return jsonify({"doc_type": doc_type, "sections": sections})


# EOF
