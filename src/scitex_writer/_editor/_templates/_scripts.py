#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_editor/_templates/_scripts.py

"""JavaScript for the Writer GUI."""

from ._scripts_claims import CLAIMS_SCRIPTS
from ._scripts_editor import EDITOR_SCRIPTS
from ._scripts_ui import UI_SCRIPTS


def build_scripts() -> str:
    """Build inline JavaScript.

    Returns
    -------
    str
        Complete <script> block.
    """
    return (
        "<script>\n(function() {\n'use strict';\n"
        + EDITOR_SCRIPTS
        + UI_SCRIPTS
        + CLAIMS_SCRIPTS
        + "\n})();\n</script>"
    )


# EOF
