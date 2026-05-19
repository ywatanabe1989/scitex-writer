"""Tests for ``scitex_writer._usage.get_usage``."""

from __future__ import annotations

import importlib

import pytest


@pytest.fixture
def reload_usage(monkeypatch):
    """Reload `_branding` then `_usage` so brand changes propagate."""

    def _reload(brand: str | None = None, alias: str | None = None):
        if brand is not None:
            monkeypatch.setenv("SCITEX_WRITER_BRAND", brand)
        else:
            monkeypatch.delenv("SCITEX_WRITER_BRAND", raising=False)
        if alias is not None:
            monkeypatch.setenv("SCITEX_WRITER_ALIAS", alias)
        else:
            monkeypatch.delenv("SCITEX_WRITER_ALIAS", raising=False)
        from scitex_writer import _branding, _usage

        importlib.reload(_branding)
        return importlib.reload(_usage)

    return _reload


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
