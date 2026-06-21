"""Tests for ``scitex_writer._branding`` (BRAND_*, rebrand_text, helpers).

Branding is read from env vars at import time. Tests that need a
custom brand reload the module under monkey-patched env so the new
constants take effect.
"""

from __future__ import annotations

import importlib
import os

import pytest

_BRAND_VARS = ("SCITEX_WRITER_BRAND", "SCITEX_WRITER_ALIAS")


@pytest.fixture
def reload_branding():
    """Reload `_branding` after setting env vars; restore on teardown.

    Snapshots the brand env vars and restores them on teardown — a real
    env mutation with cleanup, no monkeypatch fixture.
    """
    saved = {k: os.environ.get(k) for k in _BRAND_VARS}

    def _set(name: str, value: str | None) -> None:
        if value is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = value

    def _reload(brand: str | None = None, alias: str | None = None):
        _set("SCITEX_WRITER_BRAND", brand)
        _set("SCITEX_WRITER_ALIAS", alias)
        from scitex_writer import _branding

        return importlib.reload(_branding)

    try:
        yield _reload
    finally:
        for key, value in saved.items():
            _set(key, value)
        from scitex_writer import _branding

        importlib.reload(_branding)


# ----- BRAND_* defaults ---------------------------------------------------- #


def test_default_brand_name_and_alias(reload_branding):
    # Arrange
    # Act
    mod = reload_branding(brand=None, alias=None)
    # Assert
    assert (mod.BRAND_NAME == "scitex-writer") and (mod.BRAND_ALIAS == "sw")


def test_custom_brand_via_env(reload_branding):
    # Arrange
    # Act
    mod = reload_branding(brand="paperforge", alias="pf")
    # Assert
    assert (mod.BRAND_NAME == "paperforge") and (mod.BRAND_ALIAS == "pf")


# ----- rebrand_text -------------------------------------------------------- #


def test_rebrand_text_returns_none_for_none_input(reload_branding):
    # Arrange
    # Act
    mod = reload_branding(brand="x", alias="y")
    # Assert
    assert mod.rebrand_text(None) is None


def test_rebrand_text_passthrough_when_default(reload_branding):
    """Default brand → text unchanged (no work to do)."""
    # Arrange
    mod = reload_branding(brand=None, alias=None)
    # Act
    text = "import scitex_writer as sw\nsw.compile()"
    # Assert
    assert mod.rebrand_text(text) == text


def test_rebrand_text_rewrites_import_alias(reload_branding):
    # Arrange
    mod = reload_branding(brand="paperforge", alias="pf")
    src = "import scitex_writer as sw"
    # Act
    out = mod.rebrand_text(src)
    # Assert
    assert out == "import paperforge as pf"


def test_rebrand_text_rewrites_from_import(reload_branding):
    # Arrange
    mod = reload_branding(brand="paperforge", alias="pf")
    src = "from scitex_writer import compile_manuscript"
    # Act
    out = mod.rebrand_text(src)
    # Assert
    assert ("paperforge" in out) and ("scitex_writer" not in out)


def test_rebrand_text_rewrites_alias_in_examples(reload_branding):
    # Arrange
    mod = reload_branding(brand="paperforge", alias="pf")
    # Act
    src = "Run sw.compile() to build."
    # Assert
    assert "pf.compile()" in mod.rebrand_text(src)


def test_rebrand_text_rewrites_standalone_brand_name(reload_branding):
    # Arrange
    mod = reload_branding(brand="paperforge", alias="pf")
    src = "Welcome to scitex-writer, the LaTeX tool."
    # Act
    out = mod.rebrand_text(src)
    # Assert
    assert ("paperforge" in out) and ("scitex-writer" not in out)


def test_rebrand_text_does_not_touch_urls(reload_branding):
    """URLs containing 'scitex-writer' should NOT be rewritten."""
    # Arrange
    mod = reload_branding(brand="paperforge", alias="pf")
    src = "Clone https://github.com/ywatanabe1989/scitex-writer.git for source."
    # Act
    out = mod.rebrand_text(src)
    # The URL path /scitex-writer.git should remain (preceded by `/`).
    # Assert
    assert "github.com/ywatanabe1989/scitex-writer.git" in out


def test_rebrand_docstring_modifies_in_place(reload_branding):
    # Arrange
    mod = reload_branding(brand="paperforge", alias="pf")

    def f():
        """Run: import scitex_writer as sw"""

    # Act
    mod.rebrand_docstring(f)
    # Assert
    assert ("paperforge" in f.__doc__) and ("scitex_writer" not in f.__doc__)


def test_rebrand_docstring_handles_none_doc(reload_branding):
    # Arrange
    mod = reload_branding(brand="paperforge", alias="pf")

    def f():
        pass

    # No docstring → no error.
    # Act
    out = mod.rebrand_docstring(f)
    # Assert
    assert out is f


# ----- get_branded_import_example ----------------------------------------- #


def test_branded_import_example_default(reload_branding):
    # Arrange
    # Act
    mod = reload_branding(brand=None, alias=None)
    # Assert
    assert mod.get_branded_import_example() == "import scitex_writer as sw"


def test_branded_import_example_simple_brand(reload_branding):
    # Arrange
    # Act
    mod = reload_branding(brand="paperforge", alias="pf")
    # Assert
    assert mod.get_branded_import_example() == "import paperforge as pf"


def test_branded_import_example_dotted_brand_uses_from_form(reload_branding):
    """Dotted brand (e.g. `scitex.writer`) → `from scitex import writer as …`."""
    # Arrange
    mod = reload_branding(brand="scitex.writer", alias="sw")
    # Act
    out = mod.get_branded_import_example()
    # Assert
    assert out == "from scitex import writer as sw"
