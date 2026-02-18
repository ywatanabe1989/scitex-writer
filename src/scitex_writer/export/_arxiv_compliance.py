#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/export/_arxiv_compliance.py

"""Compliance checking for arXiv submission.

Pure functions to validate manuscript metadata and LaTeX structure
against arXiv submission requirements.  No Django or ORM dependencies.
"""

import re
from typing import Any, Dict

# arXiv limits
MAX_TITLE_LENGTH = 256
MAX_ABSTRACT_LENGTH = 1920
MIN_ABSTRACT_LENGTH = 100


def check_compliance(
    title: str,
    abstract: str,
    latex_content: str,
) -> Dict[str, Any]:
    """Check manuscript compliance with arXiv requirements.

    Args:
        title: Manuscript title.
        abstract: Manuscript abstract.
        latex_content: Full LaTeX source.

    Returns:
        Dict with keys: is_compliant (bool), errors (list), warnings (list),
        checks (dict of sub-check results).
    """
    result = {
        "is_compliant": True,
        "errors": [],
        "warnings": [],
        "checks": {},
    }

    title_check = _check_title(title)
    result["checks"]["title"] = title_check
    if not title_check["passed"]:
        result["errors"].extend(title_check["errors"])
        result["is_compliant"] = False

    abstract_check = _check_abstract(abstract)
    result["checks"]["abstract"] = abstract_check
    if not abstract_check["passed"]:
        result["errors"].extend(abstract_check["errors"])
        result["is_compliant"] = False

    latex_check = check_latex_structure(latex_content)
    result["checks"]["latex"] = latex_check
    if not latex_check["passed"]:
        result["errors"].extend(latex_check["errors"])
        result["is_compliant"] = False

    return result


def _check_title(title: str) -> Dict[str, Any]:
    """Check title compliance."""
    errors = []
    warnings = []

    if not title or not title.strip():
        errors.append("Title is required")
    elif len(title) > MAX_TITLE_LENGTH:
        errors.append(f"Title exceeds maximum length of {MAX_TITLE_LENGTH} characters")

    if title and len(title) < 10:
        warnings.append("Title is very short")

    return {"passed": len(errors) == 0, "errors": errors, "warnings": warnings}


def _check_abstract(abstract: str) -> Dict[str, Any]:
    """Check abstract compliance."""
    errors = []
    warnings = []

    if not abstract or not abstract.strip():
        errors.append("Abstract is required")
    else:
        if len(abstract) > MAX_ABSTRACT_LENGTH:
            errors.append(
                f"Abstract exceeds maximum length of {MAX_ABSTRACT_LENGTH} characters"
            )
        elif len(abstract) < MIN_ABSTRACT_LENGTH:
            warnings.append(
                f"Abstract is shorter than recommended minimum of {MIN_ABSTRACT_LENGTH} characters"
            )

    return {"passed": len(errors) == 0, "errors": errors, "warnings": warnings}


def check_latex_structure(latex_content: str) -> Dict[str, Any]:
    """Check LaTeX structure compliance.

    Args:
        latex_content: Full LaTeX source string.

    Returns:
        Dict with passed (bool), errors (list), warnings (list).
    """
    errors = []
    warnings = []

    if not re.search(r"\\documentclass", latex_content):
        errors.append("Missing \\documentclass declaration")

    if not re.search(r"\\begin\{document\}", latex_content):
        errors.append("Missing \\begin{document}")
    if not re.search(r"\\end\{document\}", latex_content):
        errors.append("Missing \\end{document}")

    if not re.search(r"\\title\{", latex_content):
        warnings.append("Missing \\title command")
    if not re.search(r"\\author\{", latex_content):
        warnings.append("Missing \\author command")

    return {"passed": len(errors) == 0, "errors": errors, "warnings": warnings}


# EOF
