#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: tests/scitex_writer/_mcp/handlers/test__figures_tex.py

r"""Tests for the LaTeX half of the figure pipeline (port of 04_compilation.src).

Real caption files and real image files under ``tmp_path`` -- no mocks. The
no-figures cases are the guard against an empty manuscript emitting a stray
placeholder float; the guarded end-block is the guard against a figure placed
inline with ``\scitexfig`` being duplicated at the end of the document.
"""

import pytest
from PIL import Image

from scitex_writer._mcp.handlers import _figures_tex


def _tree(tmp_path):
    """Return (caption_media_dir, jpg_dir, compiled_dir, compiled_file)."""
    cam = tmp_path / "figures/caption_and_media"
    jpg_dir = cam / "jpg_for_compilation"
    compiled = tmp_path / "figures/compiled"
    for directory in (cam, jpg_dir, compiled):
        directory.mkdir(parents=True, exist_ok=True)
    return cam, jpg_dir, compiled, compiled / "FINAL.tex"


def _jpg(path):
    Image.new("RGB", (40, 30), (200, 30, 30)).save(path, "JPEG")
    return path


def _seed_figure(tmp_path, caption="\\caption{\\textbf{Overview}\\\\ Legend.}\n"):
    """One captioned, compiled figure with real media; returns the tree."""
    cam, jpg_dir, compiled, final = _tree(tmp_path)
    (cam / "01_overview.tex").write_text(
        f"%% Edit this file: x\n{caption}", encoding="utf-8"
    )
    _jpg(jpg_dir / "01_overview.jpg")
    _figures_tex.compile_legends(cam, compiled)
    return cam, jpg_dir, compiled, final


class TestCompileLegends:
    def test_caption_is_compiled_into_the_compiled_dir(self, tmp_path):
        # Arrange
        cam, _, compiled, _ = _tree(tmp_path)
        (cam / "01_overview.tex").write_text("\\caption{X}\n", encoding="utf-8")
        # Act
        count = _figures_tex.compile_legends(cam, compiled)
        # Assert
        assert count == 1 and (compiled / "01_overview.tex").exists()

    def test_comment_lines_are_stripped_from_the_body(self, tmp_path):
        # Arrange: the "%% Edit this file:" hint must never reach the PDF.
        cam, _, compiled, _ = _tree(tmp_path)
        (cam / "01_overview.tex").write_text(
            "%% Edit this file: contents/01_overview.tex\n\\caption{X}\n",
            encoding="utf-8",
        )
        # Act
        _figures_tex.compile_legends(cam, compiled)
        # Assert
        assert "Edit this file" not in (compiled / "01_overview.tex").read_text()

    def test_panel_caption_is_not_compiled(self, tmp_path):
        # Arrange
        cam, _, compiled, _ = _tree(tmp_path)
        (cam / "01a_left.tex").write_text("\\caption{Panel}\n", encoding="utf-8")
        # Act
        count = _figures_tex.compile_legends(cam, compiled)
        # Assert
        assert count == 0


class TestReadCaption:
    def test_authored_title_is_lifted_for_the_bookmark(self, tmp_path):
        # Arrange
        caption_file = tmp_path / "01_overview.tex"
        caption_file.write_text(
            "\\caption{\\textbf{Seizure onset.}\\\\ Legend.}", encoding="utf-8"
        )
        # Act
        _, _, title = _figures_tex.read_caption(caption_file, "01")
        # Assert
        assert title == "Seizure onset"

    def test_missing_caption_falls_back_to_a_generated_one(self, tmp_path):
        # Arrange
        absent = tmp_path / "02_none.tex"
        # Act
        caption, _, _ = _figures_tex.read_caption(absent, "02")
        # Assert
        assert "Description for figure 02" in caption

    def test_caption_footnote_is_split_out(self, tmp_path):
        # Arrange: a \footnote INSIDE a float does not render.
        caption_file = tmp_path / "01_overview.tex"
        caption_file.write_text(
            "\\caption{Legend.\\captionfootnote{Funding.}}", encoding="utf-8"
        )
        # Act
        _, footnote, _ = _figures_tex.read_caption(caption_file, "01")
        # Assert
        assert footnote == "Funding."


class TestFigureFloat:
    def test_float_embeds_the_absolute_image_path(self, tmp_path):
        # Arrange: absolute for every engine (the shell only did this for tectonic).
        image = tmp_path / "01_overview.jpg"
        # Act
        lines = _figures_tex.figure_float(
            "01", "01_overview", image, "\\caption{X}", None, "", "0.78\\textheight"
        )
        # Assert
        assert f"{{{image}}}" in "\n".join(lines)

    def test_authored_label_is_not_duplicated(self, tmp_path):
        # Arrange
        caption = "\\caption{X}\n\\label{fig:mine}"
        # Act
        lines = _figures_tex.figure_float(
            "01",
            "01_overview",
            tmp_path / "a.jpg",
            caption,
            None,
            "",
            "0.78\\textheight",
        )
        # Assert
        assert "\\label{fig:01_overview}" not in "\n".join(lines)

    def test_footnotetext_lands_after_the_float_closes(self, tmp_path):
        # Arrange
        lines = _figures_tex.figure_float(
            "01",
            "01_overview",
            tmp_path / "a.jpg",
            "\\caption{X\\protect\\footnotemark}",
            "Funding.",
            "",
            "0.78\\textheight",
        )
        # Act
        body = "\n".join(lines)
        # Assert
        assert body.index("\\end{figure*}") < body.index("\\footnotetext{Funding.}")

    def test_height_cap_is_applied(self, tmp_path):
        # Arrange
        lines = _figures_tex.figure_float(
            "01",
            "01_overview",
            tmp_path / "a.jpg",
            "\\caption{X}",
            None,
            "",
            "0.5\\textheight",
        )
        # Act
        body = "\n".join(lines)
        # Assert
        assert "totalheight=0.5\\textheight" in body


class TestGather:
    def test_final_tex_guards_inline_placed_figure(self, tmp_path):
        # Arrange
        cam, jpg_dir, compiled, final = _seed_figure(tmp_path)
        # Act
        _figures_tex.compile_figure_tex_files(cam, jpg_dir, compiled, final)
        # Assert
        assert "\\ifcsname scitexfigplaced@01\\endcsname" in final.read_text()

    def test_placeable_copy_is_written_by_number(self, tmp_path):
        # Arrange
        cam, jpg_dir, compiled, final = _seed_figure(tmp_path)
        # Act
        _figures_tex.compile_figure_tex_files(cam, jpg_dir, compiled, final)
        # Assert
        assert (compiled / "_placeable/01.tex").exists()

    def test_panel_composite_is_used_when_no_named_jpg_exists(self, tmp_path):
        # Arrange: a panelled figure's media is the composite NN.jpg.
        cam, jpg_dir, compiled, final = _tree(tmp_path)
        (cam / "01_overview.tex").write_text("\\caption{X}\n", encoding="utf-8")
        _jpg(jpg_dir / "01.jpg")
        _figures_tex.compile_legends(cam, compiled)
        # Act
        result = _figures_tex.compile_figure_tex_files(cam, jpg_dir, compiled, final)
        # Assert
        assert result["figures"][0]["image"].endswith("/01.jpg")

    def test_no_figures_emits_fallback_header(self, tmp_path):
        # Arrange
        cam, jpg_dir, compiled, final = _tree(tmp_path)
        # Act
        result = _figures_tex.compile_figure_tex_files(cam, jpg_dir, compiled, final)
        # Assert
        assert result["fallback_header"] is True and result["figure_count"] == 0

    def test_fallback_header_emits_no_figure_float(self, tmp_path):
        # Arrange
        cam, jpg_dir, compiled, final = _tree(tmp_path)
        # Act
        _figures_tex.compile_figure_tex_files(cam, jpg_dir, compiled, final)
        header = (compiled / "00_Figures_Header.tex").read_text()
        active = "\n".join(
            line for line in header.splitlines() if not line.lstrip().startswith("%")
        )
        # Assert
        assert "\\begin{figure" not in active

    def test_real_figure_replaces_fallback_header(self, tmp_path):
        # Arrange
        cam, jpg_dir, compiled, final = _seed_figure(tmp_path)
        # Act
        _figures_tex.compile_figure_tex_files(cam, jpg_dir, compiled, final)
        # Assert
        assert not (compiled / "00_Figures_Header.tex").exists()


class TestVisibility:
    def test_marker_is_written_when_a_jpg_exists(self, tmp_path):
        # Arrange
        _, jpg_dir, compiled, _ = _tree(tmp_path)
        _jpg(jpg_dir / "01_overview.jpg")
        # Act
        enabled = _figures_tex.handle_figure_visibility(jpg_dir, compiled, False)
        # Assert
        assert enabled is True and (compiled / ".figures_enabled").exists()

    def test_marker_is_cleared_under_no_figs(self, tmp_path):
        # Arrange
        _, jpg_dir, compiled, _ = _tree(tmp_path)
        _jpg(jpg_dir / "01_overview.jpg")
        (compiled / ".figures_enabled").write_text("stale", encoding="utf-8")
        # Act
        enabled = _figures_tex.handle_figure_visibility(jpg_dir, compiled, True)
        # Assert
        assert enabled is False and not (compiled / ".figures_enabled").exists()


if __name__ == "__main__":
    import sys

    sys.exit(pytest.main([__file__, "-v"]))

# EOF
