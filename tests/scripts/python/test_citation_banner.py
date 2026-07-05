#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: _citation_banner.py (citation-gate banner render layer)

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

from _citation_banner import (  # noqa: E402
    banner_tex_path,
    build_banner_tex,
    reset_banner,
    write_banner_tex,
)


class TestBuildBannerTex:
    def test_header_marks_the_pdf_not_for_submission(self):
        # Arrange
        failing = [("Foo2020", 'note="Auto-generated stub"')]
        # Act
        tex = build_banner_tex(failing)
        # Assert
        assert "NOT FOR SUBMISSION" in tex

    def test_each_failing_key_appears_in_the_banner(self):
        # Arrange
        failing = [("Foo2020", "stub"), ("Bar2019", "stub")]
        # Act
        tex = build_banner_tex(failing)
        # Assert
        assert ("Foo2020" in tex) and ("Bar2019" in tex)

    def test_clew_unreachable_adds_not_verified_line(self):
        # Arrange
        failing = []
        # Act
        tex = build_banner_tex(failing, clew_unreachable=True)
        # Assert
        assert "UNREACHABLE" in tex

    def test_latex_specials_in_key_are_escaped(self):
        # Arrange
        failing = [("Foo_2020", "stub")]
        # Act
        tex = build_banner_tex(failing)
        # Assert
        assert "Foo\\_2020" in tex

    def test_banner_block_is_self_contained_group(self):
        # Arrange
        failing = [("Foo2020", "stub")]
        # Act
        tex = build_banner_tex(failing)
        # Assert
        assert tex.count(r"\begingroup") == 1 and tex.count(r"\endgroup") == 1


class TestWriteAndResetBanner:
    def test_write_creates_artifact_at_expected_path(self, tmp_path):
        # Arrange
        failing = [("Foo2020", "stub")]
        # Act
        path = write_banner_tex(tmp_path, failing)
        # Assert
        assert path == banner_tex_path(tmp_path) and path.is_file()

    def test_reset_removes_a_previously_written_banner(self, tmp_path):
        # Arrange
        write_banner_tex(tmp_path, [("Foo2020", "stub")])
        # Act
        reset_banner(tmp_path)
        # Assert
        assert not banner_tex_path(tmp_path).exists()

    def test_reset_is_a_noop_when_no_banner_exists(self, tmp_path):
        # Arrange
        # (no banner written)
        # Act
        reset_banner(tmp_path)
        # Assert
        assert not banner_tex_path(tmp_path).exists()


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
