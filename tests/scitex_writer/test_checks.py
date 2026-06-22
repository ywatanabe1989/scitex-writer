"""Tests for ``scitex_writer.checks`` (references, float_order wrappers)."""

from __future__ import annotations

from scitex_writer import checks


class _RecordingHandler:
    """Real callable that records its call args and returns a canned dict.

    Injected via the ``handler=`` seam on checks.references /
    checks.float_order so the thin wrappers are exercised without
    patching module internals or running the real (subprocess-heavy)
    check scripts.
    """

    def __init__(self, result: dict | None = None):
        self.calls: list[tuple] = []
        self.result = {} if result is None else result

    def __call__(self, *args):
        self.calls.append(args)
        return self.result


def test_module_exports_references_float_order_and_limits():
    # Arrange
    # Act
    exported = checks.__all__
    # Assert
    assert exported == ["references", "float_order", "limits"]


def test_references_forwards_all_arguments_to_handler():
    # Arrange
    handler = _RecordingHandler({"success": True})
    # Act
    checks.references("/path", doc_type="manuscript", parse_log=True, handler=handler)
    # Assert
    assert handler.calls == [("/path", "manuscript", True)]


def test_references_returns_handler_result_unchanged():
    # Arrange
    handler = _RecordingHandler({"success": True, "exit_code": 0})
    # Act
    out = checks.references("/path", handler=handler)
    # Assert
    assert out == {"success": True, "exit_code": 0}


def test_limits_forwards_all_arguments_to_handler():
    # Arrange
    handler = _RecordingHandler({"success": True})
    # Act
    checks.limits("/path", doc_type="supplementary", strict=True, handler=handler)
    # Assert
    assert handler.calls == [("/path", "supplementary", True)]


def test_limits_default_doc_type_is_manuscript_nonstrict():
    # Arrange
    handler = _RecordingHandler({"success": True})
    # Act
    checks.limits("/path", handler=handler)
    # Assert
    assert handler.calls == [("/path", "manuscript", False)]


def test_references_default_doc_type_is_all():
    # Arrange
    handler = _RecordingHandler()
    # Act
    checks.references("/p", handler=handler)
    # Assert
    assert handler.calls[0][1] == "all"


def test_float_order_default_doc_type_is_manuscript():
    # Arrange
    handler = _RecordingHandler({"success": True})
    # Act
    checks.float_order("/p", handler=handler)
    # Assert
    assert handler.calls[0][1] == "manuscript"


def test_float_order_default_fix_and_dry_run_are_false():
    # Arrange
    handler = _RecordingHandler({"success": True})
    # Act
    checks.float_order("/p", handler=handler)
    # Assert
    assert handler.calls[0][2:] == (False, False)


def test_float_order_dry_run_flag_passes_through():
    # Arrange
    handler = _RecordingHandler({"success": True})
    # Act
    checks.float_order("/p", fix=False, dry_run=True, handler=handler)
    # Assert
    assert handler.calls[0][2:] == (False, True)


def test_float_order_fix_flag_passes_through():
    # Arrange
    handler = _RecordingHandler({"success": True})
    # Act
    checks.float_order("/p", fix=True, handler=handler)
    # Assert
    assert handler.calls[0][2] is True


def test_references_propagates_handler_error_envelope():
    # Arrange
    handler = _RecordingHandler(
        {
            "success": False,
            "exit_code": 1,
            "stdout": "",
            "stderr": "fail",
            "summary": {"errors": 3},
        }
    )
    # Act
    out = checks.references("/p", handler=handler)
    # Assert
    assert out["summary"]["errors"] == 3
