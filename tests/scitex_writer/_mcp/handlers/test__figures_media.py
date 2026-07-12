#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: tests/scitex_writer/_mcp/handlers/test__figures_media.py

"""Tests for the MEDIA half of the figure pipeline (port of process_figures.sh).

Real image files under ``tmp_path`` throughout -- no mocks, no monkeypatch. Each
class covers one stage of the shell cascade it replaces.
"""

import shutil

import pytest
from PIL import Image

from scitex_writer._mcp.handlers import _figures_media
from scitex_writer._utils._mermaid_precheck import MermaidDependencyError

_HAS_LIBREOFFICE = bool(shutil.which("libreoffice") or shutil.which("soffice"))
_HAS_MMDC = bool(shutil.which("mmdc"))


def _png(path, size=(40, 30), color=(200, 30, 30)):
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, color).save(path, "PNG")
    return path


def _jpg(path, size=(40, 30), color=(200, 30, 30)):
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, color).save(path, "JPEG")
    return path


def _dirs(tmp_path):
    """Return (figure_dir, caption_media_dir, jpg_dir, compiled_dir), all created."""
    figure_dir = tmp_path / "figures"
    caption_media_dir = figure_dir / "caption_and_media"
    jpg_dir = caption_media_dir / "jpg_for_compilation"
    compiled_dir = figure_dir / "compiled"
    for directory in (figure_dir, caption_media_dir, jpg_dir, compiled_dir):
        directory.mkdir(parents=True, exist_ok=True)
    return figure_dir, caption_media_dir, jpg_dir, compiled_dir


class TestInitFigures:
    def test_stale_compiled_tex_is_cleared(self, tmp_path):
        # Arrange: Issue #41 -- a renamed figure otherwise leaves its old float.
        figure_dir, cam, jpg_dir, compiled = _dirs(tmp_path)
        stale = compiled / "99_stale.tex"
        stale.write_text("stale", encoding="utf-8")
        # Act
        _figures_media.init_figures(figure_dir, cam, jpg_dir, compiled)
        # Assert
        assert not stale.exists()

    def test_derived_symlink_is_dropped(self, tmp_path):
        # Arrange
        figure_dir, cam, jpg_dir, compiled = _dirs(tmp_path)
        source = _jpg(cam / "01_a.jpg")
        link = jpg_dir / "01_a.jpg"
        link.symlink_to(source)
        # Act
        _figures_media.init_figures(figure_dir, cam, jpg_dir, compiled)
        # Assert
        assert not link.is_symlink()

    def test_user_placed_orphan_jpg_is_preserved(self, tmp_path):
        # Arrange: a blanket rm here once DESTROYED figures with no upstream source.
        figure_dir, cam, jpg_dir, compiled = _dirs(tmp_path)
        orphan = _jpg(jpg_dir / "07_handmade.jpg")
        # Act
        _figures_media.init_figures(figure_dir, cam, jpg_dir, compiled)
        # Assert
        assert orphan.is_file()

    def test_orphan_jpg_is_reported_as_a_warning(self, tmp_path):
        # Arrange
        figure_dir, cam, jpg_dir, compiled = _dirs(tmp_path)
        _jpg(jpg_dir / "07_handmade.jpg")
        # Act
        warnings = _figures_media.init_figures(figure_dir, cam, jpg_dir, compiled)
        # Assert
        assert len(warnings) == 1 and "07_handmade.jpg" in warnings[0]


class TestLowerLetterId:
    def test_uppercase_panel_id_is_lowercased(self, tmp_path):
        # Arrange
        _, cam, _, _ = _dirs(tmp_path)
        _png(cam / "01A_left.png")
        # Act
        renamed = _figures_media.ensure_lower_letter_id(cam)
        # Assert
        assert renamed == 1 and (cam / "01a_left.png").exists()

    def test_main_figure_name_is_untouched(self, tmp_path):
        # Arrange
        _, cam, _, _ = _dirs(tmp_path)
        _png(cam / "01_Overview.png")
        # Act
        renamed = _figures_media.ensure_lower_letter_id(cam)
        # Assert
        assert renamed == 0 and (cam / "01_Overview.png").exists()


class TestPanelCaptions:
    def test_stray_panel_caption_is_deleted(self, tmp_path):
        # Arrange: a panel caption renders as a second, counter-numbered figure.
        _, cam, _, _ = _dirs(tmp_path)
        panel_caption = cam / "01a_left.tex"
        panel_caption.write_text("\\caption{Panel}", encoding="utf-8")
        # Act
        removed = _figures_media.cleanup_panel_captions(cam)
        # Assert
        assert removed == 1 and not panel_caption.exists()

    def test_main_caption_is_kept(self, tmp_path):
        # Arrange
        _, cam, _, _ = _dirs(tmp_path)
        main_caption = cam / "01_overview.tex"
        main_caption.write_text("\\caption{Main}", encoding="utf-8")
        # Act
        removed = _figures_media.cleanup_panel_captions(cam)
        # Assert
        assert removed == 0 and main_caption.exists()


class TestEnsureCaption:
    def test_default_caption_created_for_uncaptioned_figure(self, tmp_path):
        # Arrange
        _, cam, _, _ = _dirs(tmp_path)
        _png(cam / "01_overview.png")
        # Act
        created = _figures_media.ensure_caption(cam, tmp_path)
        # Assert
        assert created == 1 and (cam / "01_overview.tex").exists()

    def test_default_caption_carries_edit_hint(self, tmp_path):
        # Arrange
        _, cam, _, _ = _dirs(tmp_path)
        _png(cam / "01_overview.png")
        # Act
        _figures_media.ensure_caption(cam, tmp_path)
        # Assert
        assert "FIGURE TITLE HERE" in (cam / "01_overview.tex").read_text()

    def test_panel_gets_no_caption(self, tmp_path):
        # Arrange
        _, cam, _, _ = _dirs(tmp_path)
        _png(cam / "01a_left.png")
        # Act
        created = _figures_media.ensure_caption(cam, tmp_path)
        # Assert
        assert created == 0 and not (cam / "01a_left.tex").exists()

    def test_existing_caption_is_not_overwritten(self, tmp_path):
        # Arrange
        _, cam, _, _ = _dirs(tmp_path)
        _png(cam / "01_overview.png")
        authored = "\\caption{\\textbf{Mine}\\\\ Authored.}\n"
        (cam / "01_overview.tex").write_text(authored, encoding="utf-8")
        # Act
        created = _figures_media.ensure_caption(cam, tmp_path)
        # Assert
        assert created == 0 and (cam / "01_overview.tex").read_text() == authored

    def test_project_template_wins_over_builtin_default(self, tmp_path):
        # Arrange
        _, cam, _, _ = _dirs(tmp_path)
        _png(cam / "01_overview.png")
        (cam / "templates").mkdir()
        (cam / "templates/.00_template.tex").write_text(
            "\\caption{PROJECT TEMPLATE}\n", encoding="utf-8"
        )
        # Act
        _figures_media.ensure_caption(cam, tmp_path)
        # Assert
        assert "PROJECT TEMPLATE" in (cam / "01_overview.tex").read_text()


class TestConversionCascade:
    def test_tif_is_converted_to_png(self, tmp_path):
        # Arrange
        _, cam, _, _ = _dirs(tmp_path)
        Image.new("RGB", (20, 20), (0, 90, 0)).save(cam / "01_overview.tif", "TIFF")
        # Act
        converted = _figures_media.tif_to_png(cam)
        # Assert
        assert converted == 1 and (cam / "01_overview.png").exists()

    def test_png_is_converted_to_jpg(self, tmp_path):
        # Arrange
        _, cam, _, _ = _dirs(tmp_path)
        _png(cam / "01_overview.png")
        # Act
        converted = _figures_media.png_to_jpg(cam)
        # Assert
        assert converted == 1 and (cam / "01_overview.jpg").exists()

    def test_up_to_date_jpg_is_not_reconverted(self, tmp_path):
        # Arrange
        _, cam, _, _ = _dirs(tmp_path)
        _png(cam / "01_overview.png")
        _figures_media.png_to_jpg(cam)
        # Act
        converted = _figures_media.png_to_jpg(cam)
        # Assert
        assert converted == 0

    def test_cascade_walks_tif_to_png_to_jpg(self, tmp_path):
        # Arrange
        _, cam, _, _ = _dirs(tmp_path)
        Image.new("RGB", (20, 20), (0, 90, 0)).save(cam / "01_overview.tif", "TIFF")
        # Act
        _figures_media.convert_formats(cam)
        # Assert
        assert (cam / "01_overview.jpg").exists()

    @pytest.mark.skipif(
        _HAS_LIBREOFFICE, reason="LibreOffice installed: fail-loud path unreachable"
    )
    def test_missing_libreoffice_fails_loud_for_pptx(self, tmp_path):
        # Arrange: the shell warned and left the .jpg missing -- an opaque LaTeX
        # failure much later. Absent LibreOffice must abort with an install hint.
        _, cam, _, _ = _dirs(tmp_path)
        (cam / "01_slide.pptx").write_bytes(b"PK\x03\x04 not really a deck")
        # Act
        # Assert
        with pytest.raises(RuntimeError, match="libreoffice"):
            _figures_media.pptx_to_tif(cam)

    @pytest.mark.skipif(_HAS_MMDC, reason="mmdc installed: fail-loud path unreachable")
    def test_missing_mmdc_fails_loud_for_mermaid(self, tmp_path):
        # Arrange: same contract for Mermaid sources.
        _, cam, _, _ = _dirs(tmp_path)
        (cam / "02_flow.mmd").write_text("graph TD;\nA-->B;\n", encoding="utf-8")
        # Act
        # Assert
        with pytest.raises(MermaidDependencyError, match="mmdc"):
            _figures_media.mmd_to_png(cam)


class TestComposePanels:
    def test_panels_are_tiled_into_a_numbered_composite(self, tmp_path):
        # Arrange
        _, cam, _, _ = _dirs(tmp_path)
        _jpg(cam / "01a_left.jpg")
        _jpg(cam / "01b_right.jpg", color=(20, 20, 200))
        # Act
        composed = _figures_media.compose_panels(cam)
        # Assert
        assert composed == 1 and (cam / "01.jpg").exists()

    def test_composite_is_wider_than_one_panel(self, tmp_path):
        # Arrange: the shell `cp`-ed the FIRST panel and called it a composite.
        _, cam, _, _ = _dirs(tmp_path)
        _jpg(cam / "01a_left.jpg")
        _jpg(cam / "01b_right.jpg", color=(20, 20, 200))
        # Act
        _figures_media.compose_panels(cam)
        # Assert
        with Image.open(cam / "01.jpg") as image:
            assert image.width == 100

    def test_authored_composite_is_never_overwritten(self, tmp_path):
        # Arrange
        _, cam, _, _ = _dirs(tmp_path)
        _jpg(cam / "01a_left.jpg")
        _jpg(cam / "01b_right.jpg", color=(20, 20, 200))
        _jpg(cam / "01.jpg", size=(200, 200), color=(1, 2, 3))
        # Act
        composed = _figures_media.compose_panels(cam)
        # Assert
        assert composed == 0

    def test_lone_panel_still_composes(self, tmp_path):
        # Arrange
        _, cam, _, _ = _dirs(tmp_path)
        _jpg(cam / "03a_only.jpg")
        # Act
        composed = _figures_media.compose_panels(cam)
        # Assert
        assert composed == 1 and (cam / "03.jpg").exists()


class TestLinkAndPlaceholders:
    def test_main_jpg_is_symlinked_into_compilation_dir(self, tmp_path):
        # Arrange
        _, cam, jpg_dir, _ = _dirs(tmp_path)
        _jpg(cam / "01_overview.jpg")
        # Act
        _figures_media.link_compilation_jpgs(cam, jpg_dir)
        # Assert
        assert (jpg_dir / "01_overview.jpg").is_symlink()

    def test_panel_jpg_is_not_linked(self, tmp_path):
        # Arrange: only the composed MAIN figure belongs in jpg_for_compilation.
        _, cam, jpg_dir, _ = _dirs(tmp_path)
        _jpg(cam / "01a_left.jpg")
        # Act
        _figures_media.link_compilation_jpgs(cam, jpg_dir)
        # Assert
        assert not (jpg_dir / "01a_left.jpg").exists()

    def test_missing_figure_gets_a_placeholder_jpg(self, tmp_path):
        # Arrange: a caption with no media (the draft opt-in path).
        _, cam, jpg_dir, _ = _dirs(tmp_path)
        (cam / "01_overview.tex").write_text("\\caption{X}", encoding="utf-8")
        # Act
        created = _figures_media.create_placeholders(cam, jpg_dir)
        # Assert
        assert created == 1 and (jpg_dir / "01_overview.jpg").is_file()

    def test_present_figure_gets_no_placeholder(self, tmp_path):
        # Arrange
        _, cam, jpg_dir, _ = _dirs(tmp_path)
        (cam / "01_overview.tex").write_text("\\caption{X}", encoding="utf-8")
        _jpg(jpg_dir / "01_overview.jpg")
        # Act
        created = _figures_media.create_placeholders(cam, jpg_dir)
        # Assert
        assert created == 0

    def test_panelled_figure_needs_no_placeholder(self, tmp_path):
        # Arrange: its media is the composite NN.jpg, not NN_name.jpg.
        _, cam, jpg_dir, _ = _dirs(tmp_path)
        (cam / "01_overview.tex").write_text("\\caption{X}", encoding="utf-8")
        _jpg(jpg_dir / "01.jpg")
        # Act
        created = _figures_media.create_placeholders(cam, jpg_dir)
        # Assert
        assert created == 0


class TestCrop:
    def test_padded_compilation_jpg_is_trimmed(self, tmp_path):
        # Arrange: the shell's crop silently did NOTHING without ImageMagick.
        _, cam, jpg_dir, _ = _dirs(tmp_path)
        canvas = Image.new("RGB", (60, 60), (255, 255, 255))
        canvas.paste(Image.new("RGB", (20, 20), (255, 0, 0)), (20, 20))
        canvas.save(jpg_dir / "01_overview.jpg", "JPEG", quality=95)
        # Act
        cropped = _figures_media.crop_compilation_jpgs(jpg_dir)
        # Assert
        assert cropped == 1


if __name__ == "__main__":
    import sys

    sys.exit(pytest.main([__file__, "-v"]))

# EOF
