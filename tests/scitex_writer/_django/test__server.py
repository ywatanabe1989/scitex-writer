#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: src/scitex_writer/_django/_server.py

"""`run()` must not hide a broken editor behind a working-looking one.

Why this file exists: `run()` used to wrap `django.setup()`, the `migrate`
call, AND the `scitex_app` import in a single `try/except ImportError: pass`.
Any ImportError raised anywhere in that block — a broken Django app, a
half-installed dependency — was swallowed, and the editor silently downgraded
to a bare runserver without the workspace shell. The operator saw a server
come up with no way to know it was the degraded one.

The optional-dependency downgrade is legitimate, but it must be the ONLY thing
that except clause can catch, and it must announce itself. Everything else
propagates. This is the same silent-fallback family as the port slide that
`gui serve` used to do (bind the next free port instead of failing).

These tests read the function's own syntax tree, so a future edit that widens
the except back over `django.setup()` fails HERE instead of in production.
"""

import ast
import inspect
import textwrap

from scitex_writer._django import _server

_RUN_TREE = ast.parse(textwrap.dedent(inspect.getsource(_server.run)))


def _import_guarded_try_blocks() -> list[ast.Try]:
    """Every `try` in `run()` whose handlers catch ImportError."""
    return [
        node
        for node in ast.walk(_RUN_TREE)
        if isinstance(node, ast.Try)
        and any(
            isinstance(handler.type, ast.Name) and handler.type.id == "ImportError"
            for handler in node.handlers
        )
    ]


def test_import_guard_protects_only_import_statements():
    # Arrange
    guarded_statements = [
        statement for block in _import_guarded_try_blocks() for statement in block.body
    ]
    # Act
    non_imports = [
        statement
        for statement in guarded_statements
        if not isinstance(statement, (ast.Import, ast.ImportFrom))
    ]
    # Assert
    assert non_imports == []


def test_import_guard_announces_the_degraded_fallback():
    # Arrange
    handlers = [
        handler for block in _import_guarded_try_blocks() for handler in block.handlers
    ]
    # Act
    handler_source = " ".join(
        ast.dump(statement) for handler in handlers for statement in handler.body
    )
    # Assert
    assert "print" in handler_source


def test_django_setup_is_never_import_guarded():
    # Arrange
    guarded_nodes = {
        id(node)
        for block in _import_guarded_try_blocks()
        for statement in block.body
        for node in ast.walk(statement)
    }
    # Act
    guarded_setup_calls = [
        node
        for node in ast.walk(_RUN_TREE)
        if isinstance(node, ast.Attribute)
        and node.attr == "setup"
        and id(node) in guarded_nodes
    ]
    # Assert
    assert guarded_setup_calls == []
