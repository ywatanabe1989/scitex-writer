"""Tests for ``scitex_writer._branding`` (BRAND_*, rebrand_text, helpers).

Branding is read from env vars at import time. Tests that need a
custom brand reload the module under monkey-patched env so the new
constants take effect.
"""

from __future__ import annotations

import importlib

import pytest


@pytest.fixture
def reload_branding(monkeypatch):
    """Reload `_branding` after setting env vars; restore on teardown."""

    def _reload(brand: str | None = None, alias: str | None = None):
        if brand is not None:
            monkeypatch.setenv("SCITEX_WRITER_BRAND", brand)
        else:
            monkeypatch.delenv("SCITEX_WRITER_BRAND", raising=False)
        if alias is not None:
            monkeypatch.setenv("SCITEX_WRITER_ALIAS", alias)
        else:
            monkeypatch.delenv("SCITEX_WRITER_ALIAS", raising=False)
        from scitex_writer import _branding

        return importlib.reload(_branding)

    return _reload


# ----- BRAND_* defaults ---------------------------------------------------- #


def test_default_brand_name_and_alias(reload_branding):
    mod = reload_branding(brand=None, alias=None)
    assert mod.BRAND_NAME == "scitex-writer"
    assert mod.BRAND_ALIAS == "sw"


def test_custom_brand_via_env(reload_branding):
    mod = reload_branding(brand="paperforge", alias="pf")
    assert mod.BRAND_NAME == "paperforge"
    assert mod.BRAND_ALIAS == "pf"


# ----- rebrand_text -------------------------------------------------------- #


def test_rebrand_text_returns_none_for_none_input(reload_branding):
    mod = reload_branding(brand="x", alias="y")
    assert mod.rebrand_text(None) is None


def test_rebrand_text_passthrough_when_default(reload_branding):
    """Default brand → text unchanged (no work to do)."""
    mod = reload_branding(brand=None, alias=None)
    text = "import scitex_writer as sw\nsw.compile()"
    assert mod.rebrand_text(text) == text


def test_rebrand_text_rewrites_import_alias(reload_branding):
    mod = reload_branding(brand="paperforge", alias="pf")
    src = "import scitex_writer as sw"
    out = mod.rebrand_text(src)
    assert out == "import paperforge as pf"


def test_rebrand_text_rewrites_from_import(reload_branding):
    mod = reload_branding(brand="paperforge", alias="pf")
    src = "from scitex_writer import compile_manuscript"
    out = mod.rebrand_text(src)
    assert "paperforge" in out
    assert "scitex_writer" not in out


def test_rebrand_text_rewrites_alias_in_examples(reload_branding):
    mod = reload_branding(brand="paperforge", alias="pf")
    src = "Run sw.compile() to build."
    assert "pf.compile()" in mod.rebrand_text(src)


def test_rebrand_text_rewrites_standalone_brand_name(reload_branding):
    mod = reload_branding(brand="paperforge", alias="pf")
    src = "Welcome to scitex-writer, the LaTeX tool."
    out = mod.rebrand_text(src)
    assert "paperforge" in out
    assert "scitex-writer" not in out


def test_rebrand_text_does_not_touch_urls(reload_branding):
    """URLs containing 'scitex-writer' should NOT be rewritten."""
    mod = reload_branding(brand="paperforge", alias="pf")
    src = "Clone https://github.com/ywatanabe1989/scitex-writer.git for source."
    out = mod.rebrand_text(src)
    # The URL path /scitex-writer.git should remain (preceded by `/`).
    assert "github.com/ywatanabe1989/scitex-writer.git" in out


def test_rebrand_docstring_modifies_in_place(reload_branding):
    mod = reload_branding(brand="paperforge", alias="pf")

    def f():
        """Run: import scitex_writer as sw"""

    mod.rebrand_docstring(f)
    assert "paperforge" in f.__doc__
    assert "scitex_writer" not in f.__doc__


def test_rebrand_docstring_handles_none_doc(reload_branding):
    mod = reload_branding(brand="paperforge", alias="pf")

    def f():
        pass

    # No docstring → no error.
    out = mod.rebrand_docstring(f)
    assert out is f


# ----- get_branded_import_example ----------------------------------------- #


def test_branded_import_example_default(reload_branding):
    mod = reload_branding(brand=None, alias=None)
    assert mod.get_branded_import_example() == "import scitex_writer as sw"


def test_branded_import_example_simple_brand(reload_branding):
    mod = reload_branding(brand="paperforge", alias="pf")
    assert mod.get_branded_import_example() == "import paperforge as pf"


def test_branded_import_example_dotted_brand_uses_from_form(reload_branding):
    """Dotted brand (e.g. `scitex.writer`) → `from scitex import writer as …`."""
    mod = reload_branding(brand="scitex.writer", alias="sw")
    out = mod.get_branded_import_example()
    assert out == "from scitex import writer as sw"
