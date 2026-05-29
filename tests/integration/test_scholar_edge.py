#!/usr/bin/env python3
"""Per-edge integration + degradation tests (scitex-scholar edge).

scitex-writer wires into scitex-scholar as an OPTIONAL collaborator for
bibliography enrichment. The coupling lives in two ports:

- ``scitex_writer._ports.scholar`` — a Python bridge that resolves a project's
  scholar *library* (DOIs / paper-ids / browse cards) by reading the on-disk
  library. It gates on ``SCHOLAR_AVAILABLE``, set from
  ``scitex_dev.try_import_optional("scitex_scholar")`` (returns ``None`` on a
  failed import). The library-reading functions are pure filesystem walks, so
  they must keep working even when scholar is absent.
- ``scitex_writer._ports.scholar_cli`` — shells out to ``scitex-scholar`` for
  the **Enrich bibliography** action. It detects availability via PATH lookup
  *or* ``import scitex_scholar`` (``_python_module_available``), and when
  neither is reachable ``enrich_bib`` returns a documented, caller-safe
  ``(False, "...pip install...")`` rather than raising.

The two test kinds every optional edge should have
--------------------------------------------------
1. INTEGRATION (collaborator PRESENT): guard with
   ``pytest.importorskip("scitex_scholar")`` so minimal installs skip instead
   of erroring, then assert the real enrichment/availability path works.

2. DEGRADATION (collaborator ABSENT): simulate scholar missing in a hermetic,
   reversible way (snapshot ``sys.modules``, shadow ``scitex_scholar`` with
   ``None`` so a fresh import raises ImportError, reload the two ports), then
   assert the documented graceful contract:
     - ``scholar.SCHOLAR_AVAILABLE`` flips to ``False``;
     - ``scholar_cli._python_module_available()`` returns ``False``;
     - the pure library-reading functions still return their normal
       "nothing found" values (``None`` / ``[]``) instead of raising;
     - ``enrich_bib`` returns the ``(False, <pip-install hint>)`` sentinel.

Conventions honoured (so this stays a clean template):
  - One assertion per test (TQ007): shared setup is lifted into fixtures.
  - Explicit Arrange / Act / Assert markers in every test (TQ002).
  - No ``monkeypatch`` / ``mocker`` (banned): the scholar-absent fixture
    hand-swaps ``sys.modules`` and restores it exactly on teardown.

Empirically verified contract (this venv, scholar editable-installed)
---------------------------------------------------------------------
  PRESENT : SCHOLAR_AVAILABLE=True,  _python_module_available()=True
  ABSENT  : SCHOLAR_AVAILABLE=False, _python_module_available()=False,
            scholar_library_root()/metadata_for_doi() -> None,
            iter_library_cards() -> [],
            enrich_bib(..., cli_available=lambda: False)
                -> (False, "scitex-scholar is not installed. Run `pip install ...")
"""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest

# ===========================================================================
# 1. INTEGRATION  —  scitex-scholar PRESENT
# ===========================================================================
scitex_scholar = pytest.importorskip("scitex_scholar")


def _write_metadata(root: Path, paper_id: str, **ids) -> None:
    """Write a scholar-library MASTER/<id>/metadata.json (mirrors test_scholar)."""
    entry = root / "MASTER" / paper_id
    entry.mkdir(parents=True)
    md = {
        "metadata": {
            "id": {"doi": ids.get("doi")},
            "basic": {
                "title": ids.get("title", "t"),
                "year": ids.get("year", 2024),
            },
            "publication": {"journal": "J"},
        }
    }
    (entry / "metadata.json").write_text(json.dumps(md))


def test_scholar_available_flag_true_when_present():
    """With scholar importable, the bridge advertises it as available."""
    # Arrange
    from scitex_writer._ports import scholar

    # Act
    available = scholar.SCHOLAR_AVAILABLE
    # Assert
    assert available is True


def test_python_module_available_true_when_present():
    """The CLI port's module probe sees the importable scholar package."""
    # Arrange
    from scitex_writer._ports import scholar_cli

    # Act
    available = scholar_cli._python_module_available()
    # Assert
    assert available is True


def test_enrich_path_resolves_doi_from_library(tmp_path):
    """The enrichment path reads the scholar library and resolves a DOI."""
    # Arrange
    from scitex_writer._ports import scholar

    _write_metadata(tmp_path, "AAA", doi="10.1/aaa", title="alpha")
    # Act
    md = scholar.metadata_for_doi(tmp_path, "10.1/AAA")  # case-insensitive
    # Assert
    assert md is not None and md["_paper_id"] == "AAA"


def test_enrich_path_browses_library_cards(tmp_path):
    """Browse view yields one compact card per library record."""
    # Arrange
    from scitex_writer._ports import scholar

    _write_metadata(tmp_path, "NEW", doi="10.1/n", year=2025, title="new")
    # Act
    cards = scholar.iter_library_cards(tmp_path)
    # Assert
    assert [c["paper_id"] for c in cards] == ["NEW"]


# ===========================================================================
# 2. DEGRADATION  —  scitex-scholar ABSENT
# ===========================================================================
@pytest.fixture
def scholar_absent():
    """Make ``import scitex_scholar`` fail for the duration of the test.

    Hermetic and reversible:
      1. snapshot the whole ``sys.modules`` so teardown restores it exactly;
      2. evict ``scitex_scholar`` (and its submodules) and shadow the name with
         ``None`` so a *fresh* ``import scitex_scholar`` raises ImportError;
      3. reload the two writer ports so they re-run their optional-import
         guards under the missing dependency.

    Yields the freshly-reloaded ``(scholar, scholar_cli)`` port modules.
    """
    # Ensure both ports are importable before we tear scholar down.
    import scitex_writer._ports.scholar as scholar
    import scitex_writer._ports.scholar_cli as scholar_cli

    # 1. Full snapshot for an exact restore.
    snapshot = dict(sys.modules)

    # 2. Evict scholar + submodules, then shadow with None (fresh import fails).
    for name in list(sys.modules):
        if name == "scitex_scholar" or name.startswith("scitex_scholar."):
            del sys.modules[name]
    sys.modules["scitex_scholar"] = None  # type: ignore[assignment]

    # 3. Re-run the ports' guards under the missing dependency.
    scholar = importlib.reload(scholar)
    scholar_cli = importlib.reload(scholar_cli)
    try:
        yield scholar, scholar_cli
    finally:
        # Exact restore, then reload the ports against the real scholar again
        # so later tests / sessions see the genuine module.
        sys.modules.clear()
        sys.modules.update(snapshot)
        importlib.reload(scholar)
        importlib.reload(scholar_cli)


def test_scholar_available_flag_false_when_absent(scholar_absent):
    """SCHOLAR_AVAILABLE flips to False under a missing scholar."""
    # Arrange
    scholar, _scholar_cli = scholar_absent
    # Act
    available = scholar.SCHOLAR_AVAILABLE
    # Assert
    assert available is False


def test_python_module_available_false_when_absent(scholar_absent):
    """The CLI port's module probe reports scholar unreachable."""
    # Arrange
    _scholar, scholar_cli = scholar_absent
    # Act
    available = scholar_cli._python_module_available()
    # Assert
    assert available is False


def test_library_root_returns_none_when_absent(scholar_absent, tmp_path):
    """The pure library walk still answers (None) instead of raising."""
    # Arrange
    scholar, _scholar_cli = scholar_absent
    # Act
    root = scholar.scholar_library_root(tmp_path)
    # Assert
    assert root is None


def test_metadata_for_doi_returns_none_when_absent(scholar_absent, tmp_path):
    """DOI resolution degrades to None (caller falls back to bare bib card)."""
    # Arrange
    scholar, _scholar_cli = scholar_absent
    # Act
    md = scholar.metadata_for_doi(tmp_path, "10.1/whatever")
    # Assert
    assert md is None


def test_iter_library_cards_returns_empty_when_absent(scholar_absent, tmp_path):
    """Browse view degrades to an empty list rather than raising."""
    # Arrange
    scholar, _scholar_cli = scholar_absent
    # Act
    cards = scholar.iter_library_cards(tmp_path)
    # Assert
    assert cards == []


def test_enrich_bib_returns_false_sentinel_when_absent(scholar_absent):
    """enrich_bib degrades to its documented (False, ...) sentinel."""
    # Arrange
    _scholar, scholar_cli = scholar_absent
    cli_available = lambda: False  # noqa: E731 - scholar CLI not reachable
    # Act
    ok, _msg = scholar_cli.enrich_bib(
        Path("/tmp/x.bib"), "proj", cli_available=cli_available
    )
    # Assert
    assert ok is False


def test_enrich_bib_message_points_at_install_when_absent(scholar_absent):
    """The degraded enrich_bib message guides the user to install scholar."""
    # Arrange
    _scholar, scholar_cli = scholar_absent
    cli_available = lambda: False  # noqa: E731
    # Act
    _ok, msg = scholar_cli.enrich_bib(
        Path("/tmp/x.bib"), "proj", cli_available=cli_available
    )
    # Assert
    assert "pip install" in msg
