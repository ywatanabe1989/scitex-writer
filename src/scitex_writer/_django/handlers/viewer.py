#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Viewer handlers — claims metadata sidecar, DAG, citation verification.

Backs the live-paper viewer (issue #82 / cloud #133):
- GET /api/claims-metadata — claims.json + per-claim verification state
- GET /api/dag?target=…    — Clew DAG as Mermaid code
- GET /api/citation/<key>  — scitex-scholar verification state
"""

from __future__ import annotations

import logging

from django.http import JsonResponse

logger = logging.getLogger(__name__)

# Verification states mirrored from scitex-scholar's schema.
_CITATION_VERIFIED = "VERIFIED"
_CITATION_UNVERIFIABLE = "UNVERIFIABLE"
_CITATION_CONTRADICTED = "CONTRADICTED"


def handle_claims_metadata(request, project):
    """Return all claims with verification state (clew-aware if available)."""
    from ..._mcp.handlers._claim import list_claims

    result = list_claims(str(project.project_dir))
    if not result.get("success"):
        return JsonResponse(result, status=500)

    # Augment each claim with its Clew verification state if available.
    for claim in result.get("claims", []):
        claim["verification"] = _claim_verification_state(project, claim)

    return JsonResponse(result)


def handle_dag(request, project):
    """Return Mermaid DAG code for a target file or session."""
    target_file = request.GET.get("target")
    session_id = request.GET.get("session")
    claim_id = request.GET.get("claim")

    if claim_id:
        from ..._mcp.handlers._claim import get_claim

        claim_result = get_claim(str(project.project_dir), claim_id)
        if not claim_result.get("success"):
            return JsonResponse(claim_result, status=404)
        claim = claim_result["claim"]
        target_file = target_file or claim.get("output_file")
        session_id = session_id or claim.get("session_id")

    if not target_file and not session_id:
        return JsonResponse(
            {
                "success": False,
                "error": "Pass ?target=<file>, ?session=<id>, or ?claim=<id>",
            },
            status=400,
        )

    try:
        from scitex.clew import generate_mermaid_dag

        kwargs: dict = {}
        if target_file:
            kwargs["target_file"] = target_file
        elif session_id:
            kwargs["session_id"] = session_id
        mermaid = generate_mermaid_dag(**kwargs)
        return JsonResponse(
            {
                "success": True,
                "target_file": target_file,
                "session_id": session_id,
                "mermaid": mermaid,
            }
        )
    except ImportError:
        return JsonResponse(
            {"success": False, "error": "scitex-clew not installed"},
            status=501,
        )
    except Exception as exc:
        logger.exception("[viewer] DAG generation failed")
        return JsonResponse({"success": False, "error": str(exc)}, status=500)


def handle_citation(request, project, cite_key: str):
    """Return verification state for a bibliography citation key.

    Consumes scitex-scholar when available; degrades to UNVERIFIABLE with a
    clear reason otherwise so the frontend can show a consistent badge.
    """
    try:
        from scitex_scholar import verify_citation  # type: ignore

        state = verify_citation(str(project.project_dir), cite_key)
        return JsonResponse({"success": True, "cite_key": cite_key, **state})
    except ImportError:
        return JsonResponse(
            {
                "success": True,
                "cite_key": cite_key,
                "state": _CITATION_UNVERIFIABLE,
                "reason": "scitex-scholar not installed",
            }
        )
    except Exception as exc:
        logger.exception("[viewer] citation %s", cite_key)
        return JsonResponse(
            {"success": False, "cite_key": cite_key, "error": str(exc)},
            status=500,
        )


def _claim_verification_state(project, claim: dict) -> dict:
    """Best-effort Clew verification for a claim."""
    output_file = claim.get("output_file")
    session_id = claim.get("session_id")
    if not (output_file or session_id):
        return {"state": "NO_PROVENANCE"}

    try:
        from scitex.clew import verify_chain

        args = {}
        if output_file:
            args["target_file"] = output_file
        elif session_id:
            args["session_id"] = session_id
        status = verify_chain(**args)
        return {
            "state": status.status.name if hasattr(status, "status") else str(status),
            "target_file": output_file,
            "session_id": session_id,
        }
    except ImportError:
        return {"state": "CLEW_MISSING"}
    except Exception as exc:
        logger.debug("[viewer] verify_chain failed: %s", exc)
        return {"state": "ERROR", "error": str(exc)}
