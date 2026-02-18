#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_editor/_routes_core.py

"""Core routes: main page, health check, project info."""

from flask import jsonify, render_template_string


def register_core_routes(app, editor):
    """Register core routes with the Flask app."""
    from ._templates import build_html

    @app.route("/")
    def index():
        """Main editor page."""
        html = build_html(
            project_dir=str(editor.project_dir),
            dark_mode=editor.dark_mode,
        )
        return render_template_string(html)

    @app.route("/ping")
    def ping():
        """Health check."""
        return jsonify({"status": "ok"})

    @app.route("/api/project-info")
    def project_info():
        """Project structure information."""
        project_dir = editor.project_dir
        doc_types = []
        for name, subdir in [
            ("manuscript", "01_manuscript"),
            ("supplementary", "02_supplementary"),
            ("revision", "03_revision"),
        ]:
            if (project_dir / subdir).exists():
                doc_types.append(name)

        has_shared = (project_dir / "00_shared").exists()

        return jsonify(
            {
                "project_dir": str(project_dir),
                "project_name": project_dir.name,
                "doc_types": doc_types,
                "has_shared": has_shared,
            }
        )


# EOF
