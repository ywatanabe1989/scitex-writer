#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_editor/_routes_claim.py

"""Claim routes for the GUI editor.

Endpoints:
    GET  /api/claims                   — list all claims with previews
    GET  /api/claims/<id>              — get single claim with all styles
    POST /api/claims                   — add/update claim
    DELETE /api/claims/<id>            — remove claim
    GET  /api/claims/<id>/chain        — claim + optional Clew chain (Mermaid)
    POST /api/claims/render            — regenerate claims_rendered.tex
"""

from __future__ import annotations

from flask import jsonify, request


def register_claim_routes(app, editor):
    """Register claim API routes."""

    from ..._mcp.handlers._claim import (
        add_claim,
        get_claim,
        list_claims,
        remove_claim,
        render_claims,
    )

    @app.route("/api/claims")
    def api_list_claims():
        """List all claims in the project."""
        return jsonify(list_claims(str(editor.project_dir)))

    @app.route("/api/claims/<claim_id>")
    def api_get_claim(claim_id):
        """Get a specific claim with all style renderings."""
        return jsonify(get_claim(str(editor.project_dir), claim_id))

    @app.route("/api/claims", methods=["POST"])
    def api_add_claim():
        """Add or update a claim."""
        data = request.get_json() or {}
        required = {"claim_id", "claim_type", "value"}
        missing = required - data.keys()
        if missing:
            return jsonify(
                {"success": False, "error": f"Missing fields: {missing}"}
            ), 400
        return jsonify(
            add_claim(
                str(editor.project_dir),
                claim_id=data["claim_id"],
                claim_type=data["claim_type"],
                value=data["value"],
                context=data.get("context"),
                session_id=data.get("session_id"),
                output_file=data.get("output_file"),
                output_hash=data.get("output_hash"),
                test=data.get("test"),
            )
        )

    @app.route("/api/claims/<claim_id>", methods=["DELETE"])
    def api_remove_claim(claim_id):
        """Remove a claim."""
        return jsonify(remove_claim(str(editor.project_dir), claim_id))

    @app.route("/api/claims/<claim_id>/chain")
    def api_claim_chain(claim_id):
        """Get claim data + optional Clew verification chain as Mermaid diagram.

        Returns:
            claim: full claim data
            previews: nature/apa/plain renderings
            mermaid: Mermaid diagram code (if clew available and output_file set)
            clew_available: whether scitex.clew is importable
            has_provenance: whether claim has output_file/session_id
        """
        claim_result = get_claim(str(editor.project_dir), claim_id)
        if not claim_result.get("success"):
            return jsonify(claim_result)

        claim = claim_result["claim"]
        response = {
            "success": True,
            "claim_id": claim_id,
            "claim": claim,
            "previews": claim_result.get("previews", {}),
            "mermaid": None,
            "clew_available": False,
            "has_provenance": bool(claim.get("output_file") or claim.get("session_id")),
        }

        output_file = claim.get("output_file")
        session_id = claim.get("session_id")

        if output_file or session_id:
            try:
                from scitex.clew import generate_mermaid_dag

                response["clew_available"] = True
                kwargs = {}
                if output_file:
                    kwargs["target_file"] = output_file
                elif session_id:
                    kwargs["session_id"] = session_id
                mermaid_code = generate_mermaid_dag(**kwargs)
                response["mermaid"] = mermaid_code
            except Exception:
                pass  # Clew not available or chain lookup failed — degrade gracefully

        return jsonify(response)

    @app.route("/api/claims/render", methods=["POST"])
    def api_render_claims():
        """Regenerate 00_shared/claims_rendered.tex."""
        return jsonify(render_claims(str(editor.project_dir)))


# EOF
