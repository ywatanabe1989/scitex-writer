"""Tests for ``scitex_writer.checks`` (references, float_order wrappers)."""

from __future__ import annotations

from scitex_writer import checks


def test_module_exports_only_documented_api():
    # Arrange
    # Act
    # Assert
    assert (checks.__all__ == ['references', 'float_order']) and (hasattr(checks, 'references')) and (hasattr(checks, 'float_order'))


def test_references_delegates_to_handler(monkeypatch):
    # Arrange
    captured = {}

    def _fake_check_references(project_dir, doc_type, parse_log):
        captured["args"] = (project_dir, doc_type, parse_log)
        return {"success": True, "exit_code": 0, "summary": {"errors": 0}}

    monkeypatch.setattr(checks, "_check_references", _fake_check_references)
    # Act
    out = checks.references("/path", doc_type="manuscript", parse_log=True)
    # Assert
    assert (captured['args'] == ('/path', 'manuscript', True)) and (out['success'] is True)


def test_references_default_doc_type(monkeypatch):
    # Arrange
    captured = {}

    def _fake(project_dir, doc_type, parse_log):
        captured["doc_type"] = doc_type
        return {}

    monkeypatch.setattr(checks, "_check_references", _fake)
    # Act
    checks.references("/p")
    # Assert
    assert captured["doc_type"] == "all"


def test_float_order_default_doc_type(monkeypatch):
    # Arrange
    captured = {}

    def _fake(project_dir, doc_type, fix, dry_run):
        captured.update(
            project_dir=project_dir, doc_type=doc_type, fix=fix, dry_run=dry_run
        )
        return {"success": True}

    monkeypatch.setattr(checks, "_check_float_order", _fake)
    # Act
    checks.float_order("/p")
    # Assert
    assert (captured['doc_type'] == 'manuscript') and (captured['fix'] is False) and (captured['dry_run'] is False)


def test_float_order_dry_run_passthrough(monkeypatch):
    # Arrange
    captured = {}

    def _fake(project_dir, doc_type, fix, dry_run):
        captured.update(fix=fix, dry_run=dry_run)
        return {"success": True}

    monkeypatch.setattr(checks, "_check_float_order", _fake)
    # Act
    checks.float_order("/p", fix=False, dry_run=True)
    # Assert
    assert (captured['fix'] is False) and (captured['dry_run'] is True)


def test_float_order_fix_passthrough(monkeypatch):
    # Arrange
    captured = {}

    def _fake(project_dir, doc_type, fix, dry_run):
        captured["fix"] = fix
        return {"success": True}

    monkeypatch.setattr(checks, "_check_float_order", _fake)
    # Act
    checks.float_order("/p", fix=True)
    # Assert
    assert captured["fix"] is True


def test_references_propagates_handler_errors(monkeypatch):
    """Handler-side error envelope passes through unchanged."""

    # Arrange
    def _fake(project_dir, doc_type, parse_log):
        return {
            "success": False,
            "exit_code": 1,
            "stdout": "",
            "stderr": "fail",
            "summary": {"errors": 3},
        }

    monkeypatch.setattr(checks, "_check_references", _fake)
    # Act
    out = checks.references("/p")
    # Assert
    assert (out['success'] is False) and (out['summary']['errors'] == 3)
