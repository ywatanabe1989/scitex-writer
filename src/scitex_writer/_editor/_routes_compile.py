#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_editor/_routes_compile.py

"""Compilation and PDF serving routes."""

import threading

from flask import jsonify, request, send_file


def register_compile_routes(app, editor):
    """Register compilation routes."""

    @app.route("/api/compile", methods=["POST"])
    def compile_document():
        """Trigger document compilation."""
        if editor._compiling:
            return jsonify({"error": "Compilation already in progress"}), 409

        data = request.get_json() or {}
        doc_type = data.get("doc_type", "manuscript")
        draft = data.get("draft", False)

        def _do_compile():
            editor._compiling = True
            editor._compile_log = ""
            editor._compile_result = None
            try:
                from scitex_writer import compile as sw_compile

                project_str = str(editor.project_dir)
                if doc_type == "manuscript":
                    result = sw_compile.manuscript(project_str, draft=draft, quiet=True)
                elif doc_type == "supplementary":
                    result = sw_compile.supplementary(
                        project_str, draft=draft, quiet=True
                    )
                elif doc_type == "revision":
                    result = sw_compile.revision(project_str, draft=draft, quiet=True)
                else:
                    result = {
                        "success": False,
                        "error": f"Unknown doc_type: {doc_type}",
                    }

                editor._compile_result = result
                if isinstance(result, dict):
                    editor._compile_log = result.get("log", result.get("output", ""))
                else:
                    editor._compile_log = str(result)
            except Exception as e:
                editor._compile_result = {"success": False, "error": str(e)}
                editor._compile_log = str(e)
            finally:
                editor._compiling = False

        thread = threading.Thread(target=_do_compile, daemon=True)
        thread.start()

        return jsonify({"status": "started", "doc_type": doc_type})

    @app.route("/api/compile/status")
    def compile_status():
        """Get compilation status."""
        return jsonify(
            {
                "compiling": editor._compiling,
                "result": editor._compile_result,
                "log": editor._compile_log,
            }
        )

    @app.route("/api/pdf")
    def serve_pdf():
        """Serve compiled PDF."""
        doc_type = request.args.get("doc_type", "manuscript")
        request.args.get("t", "")  # Cache buster (ignored)

        pdf_map = {
            "manuscript": "01_manuscript/manuscript.pdf",
            "supplementary": "02_supplementary/supplementary.pdf",
            "revision": "03_revision/revision.pdf",
        }

        rel_path = pdf_map.get(doc_type)
        if not rel_path:
            return jsonify({"error": f"Unknown doc_type: {doc_type}"}), 400

        pdf_path = editor.project_dir / rel_path
        if not pdf_path.exists():
            return jsonify({"error": "PDF not found. Compile first."}), 404

        return send_file(
            str(pdf_path),
            mimetype="application/pdf",
            as_attachment=False,
            download_name=f"{doc_type}.pdf",
        )


# EOF
