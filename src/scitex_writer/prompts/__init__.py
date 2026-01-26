#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-27
# File: src/scitex_writer/prompts/__init__.py

"""Action prompts for scientific manuscript workflows.

Currently provides AI2 Asta prompt generation for finding
related papers and potential collaborators.

Usage::

    from scitex_writer.prompts import generate_asta

    result = generate_asta(project_path, search_type="related")
    print(result["prompt"])

For IMRAD writing guidelines, use scitex_writer.guidelines instead.
"""

from ._ai2 import generate_ai2_prompt

# Convenience alias
generate_asta = generate_ai2_prompt

__all__ = [
    "generate_ai2_prompt",
    "generate_asta",
]

# EOF
