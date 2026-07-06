"""split_caption_footnote rewrites \\captionfootnote{...} to \\protect\\footnotemark."""

import importlib.util
from pathlib import Path

_HELPER = (
    Path(__file__).resolve().parents[3] / "scripts/python/caption_footnote_split.py"
)


def _load():
    spec = importlib.util.spec_from_file_location("caption_footnote_split", _HELPER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_marker_replaced_with_footnotemark():
    # Arrange
    mod = _load()
    caption = "\\caption{\\textbf{T}\\\\ Legend.\\captionfootnote{Disclosure.}}"
    # Act
    transformed, _ = mod.split_caption_footnote(caption)
    # Assert
    assert "\\protect\\footnotemark" in transformed


def test_marker_removed_from_caption():
    # Arrange
    mod = _load()
    caption = "\\caption{\\textbf{T}\\\\ Legend.\\captionfootnote{Disclosure.}}"
    # Act
    transformed, _ = mod.split_caption_footnote(caption)
    # Assert
    assert "\\captionfootnote" not in transformed


def test_footnote_text_extracted():
    # Arrange
    mod = _load()
    caption = "\\caption{\\textbf{T}\\\\ Legend.\\captionfootnote{Disclosure.}}"
    # Act
    _, footnote = mod.split_caption_footnote(caption)
    # Assert
    assert footnote == "Disclosure."


def test_nested_braces_in_footnote_preserved():
    # Arrange
    mod = _load()
    caption = "\\caption{Legend.\\captionfootnote{See \\textbf{ref} for detail.}}"
    # Act
    _, footnote = mod.split_caption_footnote(caption)
    # Assert
    assert footnote == "See \\textbf{ref} for detail."


def test_no_marker_returns_input_unchanged():
    # Arrange
    mod = _load()
    caption = "\\caption{\\textbf{T}\\\\ Plain legend with no footnote.}"
    # Act
    transformed, _ = mod.split_caption_footnote(caption)
    # Assert
    assert transformed == caption


def test_no_marker_reports_no_footnote():
    # Arrange
    mod = _load()
    caption = "\\caption{\\textbf{T}\\\\ Plain legend with no footnote.}"
    # Act
    _, footnote = mod.split_caption_footnote(caption)
    # Assert
    assert footnote is None
