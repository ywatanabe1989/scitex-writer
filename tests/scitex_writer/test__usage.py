"""Tests for ``scitex_writer._usage.get_usage``."""

from __future__ import annotations

import importlib
import os

import pytest

_BRAND_VARS = ("SCITEX_WRITER_BRAND", "SCITEX_WRITER_ALIAS")


@pytest.fixture
def reload_usage():
    """Reload `_branding` then `_usage` so brand changes propagate.

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
        from scitex_writer import _branding, _usage

        importlib.reload(_branding)
        return importlib.reload(_usage)

    try:
        yield _reload
    finally:
        for key, value in saved.items():
            _set(key, value)
        # Restore the modules to their unbranded baseline for other tests.
        from scitex_writer import _branding, _usage

        importlib.reload(_branding)
        importlib.reload(_usage)


def test_get_usage_returns_str(reload_usage):
    # Arrange
    mod = reload_usage()
    # Act
    out = mod.get_usage()
    # Assert
    assert (isinstance(out, str)) and (len(out) > 0)


def test_get_usage_contains_brand_name_default(reload_usage):
    # Arrange
    mod = reload_usage()
    # Act
    out = mod.get_usage()
    # Assert
    assert "scitex-writer" in out


def test_get_usage_uses_custom_brand(reload_usage):
    # Arrange
    mod = reload_usage(brand="paperforge", alias="pf")
    # Act
    out = mod.get_usage()
    # Assert
    assert "paperforge" in out


def test_get_usage_includes_import_example(reload_usage):
    # Arrange
    mod = reload_usage()
    # Act
    out = mod.get_usage()
    # Should embed an `import scitex_writer …` style snippet for users.
    # Assert
    assert "import" in out


def test_get_usage_uses_custom_alias_in_example(reload_usage):
    # Arrange
    mod = reload_usage(brand="paperforge", alias="pf")
    # Act
    out = mod.get_usage()
    # Assert
    assert "pf" in out  # alias appears at least once in branded examples


def test_get_usage_idempotent_for_same_brand(reload_usage):
    """Two calls with same env yield the same string."""
    # Arrange
    # Act
    mod = reload_usage(brand="paperforge", alias="pf")
    # Assert
    assert mod.get_usage() == mod.get_usage()


def test_get_usage_documents_project_structure(reload_usage):
    # Arrange
    mod = reload_usage()
    # Act
    out = mod.get_usage()
    # The README-shaped layout block is expected.
    # Assert
    assert "Project Structure" in out
