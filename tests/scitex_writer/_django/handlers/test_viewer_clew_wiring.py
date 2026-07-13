#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Writer must call Clew with the signature Clew actually publishes.

THE BUG THIS PINS. `_claim_verification_state` called
`verify_chain(target_file=...)` and `verify_chain(session_id=...)`. Clew's
`verify_chain` takes a single positional `target` and has NEITHER keyword, so
EVERY call raised TypeError. It was logged at DEBUG and returned as a per-claim
state of "ERROR" — which reads as "this claim could not be verified" when the
truth was "writer called Clew wrong". Forty claims in a real manuscript verified
as zero, and the failure never surfaced.

These tests read the SOURCE, not a mock, and check writer's call against Clew's
REAL published signature (via inspect). A mock would have happily accepted
`target_file=` and told us everything was fine — which is exactly how this
shipped. No mocks, no monkeypatch (PA-306 / STX-NM002).
"""

import ast
import inspect
import pathlib

import pytest

import scitex_writer._django.handlers.viewer as viewer_mod

_SRC = pathlib.Path(viewer_mod.__file__).read_text()
_TREE = ast.parse(_SRC)


def _verification_fn():
    """The `_claim_verification_state` FunctionDef node, or raise if it moved."""
    for node in ast.walk(_TREE):
        if (
            isinstance(node, ast.FunctionDef)
            and node.name == "_claim_verification_state"
        ):
            return node
    raise AssertionError("_claim_verification_state disappeared from viewer.py")


def _calls_named(tree, func_name):
    """Every Call node in the source invoking `func_name`."""
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            name = getattr(fn, "id", None) or getattr(fn, "attr", None)
            if name == func_name:
                out.append(node)
    return out


class TestVerifyChainCallMatchesClew:
    def test_verify_chain_is_never_called_with_dict_unpacking(self):
        # Arrange: the ORIGINAL bug was `verify_chain(**args)`, with `args`
        # built at runtime as {"target_file": ...} — a keyword Clew does not
        # have. Unpacking hides the call shape from every static check, which
        # is why the TypeError shipped. Forbid the pattern, not just the one
        # wrong key: a checkable call is the whole point.
        calls = _calls_named(_TREE, "verify_chain")

        # Act
        unpacked = [c for c in calls for k in c.keywords if k.arg is None]

        # Assert
        assert unpacked == []

    def test_every_verify_chain_keyword_exists_in_clews_signature(self):
        # Arrange: the real published signature, not a mock's idea of it. A mock
        # would have happily accepted `target_file=` and told us it was fine.
        clew = pytest.importorskip("scitex_clew")
        allowed = set(inspect.signature(clew.verify_chain).parameters)

        # Act
        used = {
            k.arg
            for c in _calls_named(_TREE, "verify_chain")
            for k in c.keywords
            if k.arg
        }

        # Assert
        assert used <= allowed

    def test_no_target_file_key_is_built_anywhere_in_the_verifier(self):
        # Arrange: `target_file` is not a Clew parameter and never was. Catch it
        # as a dict key too, since that is how it reached Clew last time.
        fn_src = _verification_fn()

        # Act
        keys = [
            n.value
            for n in ast.walk(fn_src)
            if isinstance(n, ast.Constant) and n.value == "target_file"
        ]

        # Assert
        assert keys == []


class TestVerifyClaimIsUsed:
    def test_viewer_imports_clews_per_claim_entry_point(self):
        # Arrange: Clew ships verify_claim for exactly this; writer hand-rolled
        # the verdict out of verify_chain and got the call wrong.
        imported = {
            alias.name
            for node in ast.walk(_TREE)
            if isinstance(node, ast.ImportFrom) and node.module == "scitex_clew"
            for alias in node.names
        }

        # Act
        uses_per_claim_api = "verify_claim" in imported

        # Assert
        assert uses_per_claim_api

    def test_verify_claim_exists_in_the_installed_clew(self):
        # Arrange
        clew = pytest.importorskip("scitex_clew")

        # Act
        fn = getattr(clew, "verify_claim", None)

        # Assert
        assert callable(fn)


class TestWiringErrorsAreNotSwallowed:
    def test_type_error_is_re_raised_not_reported_as_claim_error(self):
        # Arrange: a TypeError is OUR call being wrong, not a fact about the
        # claim. Swallowing it as state="ERROR" is how the bug stayed invisible.
        fn_src = _verification_fn()

        # Act
        reraises = any(
            isinstance(h.type, ast.Name)
            and h.type.id == "TypeError"
            and any(isinstance(s, ast.Raise) for s in h.body)
            for t in ast.walk(fn_src)
            if isinstance(t, ast.Try)
            for h in t.handlers
        )

        # Assert
        assert reraises
