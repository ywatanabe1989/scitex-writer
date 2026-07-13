#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: src/scitex_writer/_django/apps.py

"""The remedy we print must actually deliver the thing it names.

Why this file exists: when scitex-app was missing, `_server.py` told the user
`pip install scitex-writer[editor]` and `apps.py` quietly swapped its base
class for a plain Django AppConfig. But the `editor` extra was DECLARED EMPTY
(`editor = []`), and scitex-app was not a dependency of writer anywhere. So the
instruction installed nothing, the user stayed exactly as broken, and the editor
kept running without the workspace shell — while telling them the fix.

An install instruction that resolves to a no-op is worse than no instruction:
the user believes they have tried the fix. These tests read the real pyproject
and pin the promise — the extra named in the error message must provide the
module whose absence triggered it.
"""

import sys
from pathlib import Path

import tomllib

_PYPROJECT = Path(__file__).resolve().parents[3] / "pyproject.toml"

# The module whose absence degrades the editor, and the extra our error
# messages tell the user to install to get it back.
_DEGRADING_IMPORT = "scitex_app"
_ADVERTISED_EXTRA = "editor"


def _optional_dependencies() -> dict[str, list[str]]:
    data = tomllib.loads(_PYPROJECT.read_text())
    return data["project"]["optional-dependencies"]


def _editor_extra() -> list[str]:
    return _optional_dependencies()[_ADVERTISED_EXTRA]


def test_editor_extra_is_not_empty():
    # Arrange
    extra = _editor_extra()
    # Act
    is_empty = extra == []
    # Assert
    assert not is_empty


def test_editor_extra_provides_the_module_it_promises():
    # Arrange
    extra = _editor_extra()
    # Act
    provides = [req for req in extra if _DEGRADING_IMPORT.replace("_", "-") in req]
    # Assert
    assert provides != []


def test_editor_extra_floors_scitex_app_at_the_embed_release():
    # Arrange
    extra = _editor_extra()
    # Act
    pins = [req for req in extra if req.startswith("scitex-app")]
    # Assert
    assert pins == ["scitex-app>=0.4.0"]


def test_app_config_is_importable():
    # Arrange
    sys.modules.pop("scitex_writer._django.apps", None)
    # Act
    from scitex_writer._django.apps import WriterEditorConfig

    # Assert
    assert WriterEditorConfig.label == "writer_editor"
