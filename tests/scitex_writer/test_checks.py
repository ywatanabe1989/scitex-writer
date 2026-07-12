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


def test_module_exports_references_float_order_limits_and_overflow():
    # Arrange
    # Act
    exported = checks.__all__
    # Assert
    assert exported == [
        "references",
        "float_order",
        "limits",
        "overflow",
        "paper_symlink",
        "media_provenance",
        "caption_footnote",
        "ref_integrity",
        "table_decimals",
        "citation_trust",
    ]


def test_citation_trust_forwards_all_arguments_to_handler():
    # Arrange
    handler = _RecordingHandler({"success": True})
    # Act
    checks.citation_trust(
        "/path",
        level="error",
        offline=True,
        min_confidence=0.9,
        no_cache=True,
        handler=handler,
    )
    # Assert
    assert handler.calls == [("/path", "error", True, 0.9, True)]


def test_citation_trust_defaults_are_none_level_online_cached():
    # Arrange
    handler = _RecordingHandler({"success": True})
    # Act
    checks.citation_trust("/path", handler=handler)
    # Assert
    assert handler.calls == [("/path", None, False, None, False)]


def test_ref_integrity_forwards_all_arguments_to_handler():
    # Arrange
    handler = _RecordingHandler({"success": True})
    # Act
    checks.ref_integrity(
        "/path",
        doc_type="supplementary",
        level="error",
        handler=handler,
    )
    # Assert
    assert handler.calls == [("/path", "supplementary", "error")]


def test_ref_integrity_defaults_are_all_doctype_none_level():
    # Arrange
    handler = _RecordingHandler({"success": True})
    # Act
    checks.ref_integrity("/path", handler=handler)
    # Assert
    assert handler.calls == [("/path", "all", None)]


def test_caption_footnote_forwards_all_arguments_to_handler():
    # Arrange
    handler = _RecordingHandler({"success": True})
    # Act
    checks.caption_footnote(
        "/path",
        doc_type="supplementary",
        level="error",
        handler=handler,
    )
    # Assert
    assert handler.calls == [("/path", "supplementary", "error")]


def test_caption_footnote_defaults_are_all_doctype_none_level():
    # Arrange
    handler = _RecordingHandler({"success": True})
    # Act
    checks.caption_footnote("/path", handler=handler)
    # Assert
    assert handler.calls == [("/path", "all", None)]


def test_media_provenance_forwards_all_arguments_to_handler():
    # Arrange
    handler = _RecordingHandler({"success": True})
    # Act
    checks.media_provenance(
        "/path",
        doc_type="supplementary",
        level="error",
        require_under_scripts=True,
        handler=handler,
    )
    # Assert
    assert handler.calls == [("/path", "supplementary", "error", True)]


def test_media_provenance_defaults_are_all_none_level_nonstrict():
    # Arrange
    handler = _RecordingHandler({"success": True})
    # Act
    checks.media_provenance("/path", handler=handler)
    # Assert
    assert handler.calls == [("/path", "all", None, False)]


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
