#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: compile_tex_structure.py

import os
import re
import sys
from pathlib import Path

import pytest

# Add scripts/python to path for imports
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

from compile_tex_structure import (  # noqa: E402
    _is_style_input,
    _read_config_theme,
    _resolve_dark_mode,
    _style_fallback,
    compile_tex_structure,
    expand_inputs,
    generate_signature,
)


class TestGenerateSignature:
    """Test signature generation."""

    def test_generate_signature_contains_scitex_writer(self):
        """Signature should contain 'SciTeX Writer'."""
        # Arrange
        # Act
        signature = generate_signature()
        # Assert
        assert "SciTeX Writer" in signature

    def test_generate_signature_contains_version_scitex_writer_in_signature(self):
        # Arrange
        # Act
        signature = generate_signature()
        # Act
        # Assert
        assert "SciTeX Writer" in signature

    def test_generate_signature_contains_version_scitex_writer_unknown_in_signature_or_re_search_scitex_write(
        self,
    ):
        # Arrange
        # Act
        signature = generate_signature()
        # Act
        # Assert
        assert "SciTeX Writer unknown" in signature or re.search(
            r"SciTeX Writer \d+\.\d+", signature
        )

    def test_generate_signature_contains_engine(self):
        """Signature should contain engine information."""
        # Arrange
        # Act
        signature = generate_signature()
        # Assert
        assert ("LaTeX compilation engine:" in signature) and (
            "auto" in signature or "tectonic" in signature or "latexmk" in signature
        )

    def test_generate_signature_with_env_engine(self):
        """Signature should use SCITEX_WRITER_ENGINE if set."""
        # Arrange
        saved = os.environ.get("SCITEX_WRITER_ENGINE")
        os.environ["SCITEX_WRITER_ENGINE"] = "tectonic"
        try:
            # Act
            signature = generate_signature()
        finally:
            if saved is None:
                os.environ.pop("SCITEX_WRITER_ENGINE", None)
            else:
                os.environ["SCITEX_WRITER_ENGINE"] = saved
        # Assert
        assert "engine: tectonic" in signature

    def test_generate_signature_with_source_file(self, tmp_path):
        """Signature should include source file path when provided."""
        # Arrange
        source_file = tmp_path / "test.tex"
        # Act
        signature = generate_signature(source_file=source_file)
        # Assert
        assert ("Source:" in signature) and (str(source_file) in signature)

    def test_generate_signature_has_timestamp(self):
        """Signature should contain compilation timestamp."""
        # Arrange
        # Act
        signature = generate_signature()
        # Assert
        assert ("Compiled:" in signature) and (
            re.search("\\d{4}-\\d{2}-\\d{2}", signature)
        )

    def test_generate_signature_is_comment(self):
        """Signature should be LaTeX comments."""
        # Arrange
        # Act
        # Assert
        signature = generate_signature()
        lines = signature.split("\n")
        # Non-empty lines should start with %
        for line in lines:
            if line.strip():
                assert line.startswith("%")


class TestExpandInputs:
    """Test TeX input expansion."""

    def test_expand_inputs_simple_file(self, tmp_path):
        """Should read and return simple file content."""
        # Arrange
        test_file = tmp_path / "test.tex"
        test_file.write_text("Hello, world!")

        # Act
        result = expand_inputs(test_file)
        # Assert
        assert "Hello, world!" in result

    def test_expand_inputs_with_input_command(self, tmp_path):
        """Should expand \\input{} commands."""
        # Create child file
        # Arrange
        child_file = tmp_path / "child.tex"
        child_file.write_text("Child content here")

        # Create parent file that references child
        parent_file = tmp_path / "parent.tex"
        parent_file.write_text("Start\n\\input{child}\nEnd")

        # Act
        result = expand_inputs(parent_file)

        # Should contain both parent and child content
        # Assert
        assert (
            ("Start" in result)
            and ("Child content here" in result)
            and ("End" in result)
            and ("File: child" in result)
        )

    def test_expand_inputs_missing_file(self, tmp_path):
        """Should handle missing input file gracefully."""
        # Arrange
        parent_file = tmp_path / "parent.tex"
        parent_file.write_text("\\input{nonexistent}")

        # Act
        result = expand_inputs(parent_file)

        # Should contain SKIPPED comment
        # Assert
        assert ("SKIPPED" in result) and ("file not found" in result)

    def test_expand_inputs_circular_reference(self, tmp_path):
        """Should detect and prevent circular references."""
        # Create file that references itself
        # Arrange
        self_ref_file = tmp_path / "circular.tex"
        self_ref_file.write_text("Start\n\\input{circular}\nEnd")

        # Act
        result = expand_inputs(self_ref_file)

        # Should contain circular reference warning
        # Assert
        assert ("SKIPPED" in result) and (
            "circular reference" in result or "already processed" in result
        )

    def test_expand_inputs_max_depth(self, tmp_path):
        """Should stop at max recursion depth."""
        # Create deeply nested structure
        # Arrange
        files = []
        for i in range(15):
            f = tmp_path / f"level_{i}.tex"
            if i < 14:
                f.write_text(f"Level {i}\n\\input{{level_{i + 1}}}")
            else:
                f.write_text(f"Level {i}")
            files.append(f)

        # Act
        result = expand_inputs(files[0], max_depth=5)

        # Should stop before reaching the deepest level
        # Assert
        assert (
            ("Level 0" in result)
            and ("Level 5" in result or "Level 6" in result)
            and ("ERROR" in result or "Max recursion depth" in result)
        )

    def test_expand_inputs_commented_line_skipped(self, tmp_path):
        """Should skip \\input{} in commented lines."""
        # Arrange
        child_file = tmp_path / "child.tex"
        child_file.write_text("This should not appear")

        parent_file = tmp_path / "parent.tex"
        parent_file.write_text("Start\n% \\input{child}\nEnd")

        # Act
        result = expand_inputs(parent_file)

        # Should NOT expand commented input
        # Assert
        assert ("This should not appear" not in result) and (
            "% \\input{child}" in result
        )

    def test_expand_inputs_adds_tex_extension(self, tmp_path):
        """Should add .tex extension if not present."""
        # Arrange
        child_file = tmp_path / "child.tex"
        child_file.write_text("Child content")

        parent_file = tmp_path / "parent.tex"
        # Reference without .tex extension
        parent_file.write_text("\\input{child}")

        # Act
        result = expand_inputs(parent_file)

        # Should successfully expand even without .tex
        # Assert
        assert "Child content" in result

    def test_expand_inputs_nested_multiple_levels(self, tmp_path):
        """Should handle multiple levels of nesting."""
        # Arrange
        level2 = tmp_path / "level2.tex"
        level2.write_text("Level 2 content")

        level1 = tmp_path / "level1.tex"
        level1.write_text("Level 1 start\n\\input{level2}\nLevel 1 end")

        level0 = tmp_path / "level0.tex"
        level0.write_text("Level 0 start\n\\input{level1}\nLevel 0 end")

        # Act
        result = expand_inputs(level0)

        # All levels should be present
        # Assert
        assert (
            ("Level 0 start" in result)
            and ("Level 1 start" in result)
            and ("Level 2 content" in result)
            and ("Level 1 end" in result)
            and ("Level 0 end" in result)
        )

    def test_expand_inputs_nonexistent_file(self, tmp_path):
        """Should handle nonexistent file at top level."""
        # Arrange
        nonexistent = tmp_path / "does_not_exist.tex"

        # Act
        result = expand_inputs(nonexistent)

        # Should return SKIPPED message
        # Assert
        assert ("SKIPPED" in result) and ("file not found" in result)


class TestCompileTexStructure:
    """Test full TeX structure compilation."""

    def test_compile_tex_structure_creates_output(self, tmp_path):
        """Should create output file."""
        # Arrange
        base_file = tmp_path / "base.tex"
        base_file.write_text(
            "\\documentclass{article}\n\\begin{document}\nHello\n\\end{document}"
        )

        output_file = tmp_path / "output.tex"

        # Act
        success = compile_tex_structure(
            base_tex=base_file, output_tex=output_file, verbose=False
        )

        # Assert
        assert (success is True) and (output_file.exists())

    def test_compile_tex_structure_contains_signature(self, tmp_path):
        """Output should contain compilation signature."""
        # Arrange
        base_file = tmp_path / "base.tex"
        base_file.write_text("Content")

        output_file = tmp_path / "output.tex"

        compile_tex_structure(base_tex=base_file, output_tex=output_file, verbose=False)

        # Act
        output_content = output_file.read_text()
        # Assert
        assert ("SciTeX Writer" in output_content) and ("Compiled:" in output_content)

    def test_compile_tex_structure_expands_inputs(self, tmp_path):
        """Should expand \\input{} commands in base file."""
        # Arrange
        child_file = tmp_path / "child.tex"
        child_file.write_text("Child content")

        base_file = tmp_path / "base.tex"
        base_file.write_text("Start\n\\input{child}\nEnd")

        output_file = tmp_path / "output.tex"

        compile_tex_structure(base_tex=base_file, output_tex=output_file, verbose=False)

        # Act
        output_content = output_file.read_text()
        # Assert
        assert "Child content" in output_content

    def test_compile_tex_structure_missing_base_file(self, tmp_path):
        """Should return False for missing base file."""
        # Arrange
        base_file = tmp_path / "nonexistent.tex"
        output_file = tmp_path / "output.tex"

        # Act
        success = compile_tex_structure(
            base_tex=base_file, output_tex=output_file, verbose=False
        )

        # Assert
        assert (success is False) and (not output_file.exists())

    def test_compile_tex_structure_creates_output_dir(self, tmp_path):
        """Should create output directory if it doesn't exist."""
        # Arrange
        base_file = tmp_path / "base.tex"
        base_file.write_text("Content")

        output_dir = tmp_path / "nested" / "dir"
        output_file = output_dir / "output.tex"

        # Act
        success = compile_tex_structure(
            base_tex=base_file, output_tex=output_file, verbose=False
        )

        # Assert
        assert (success is True) and (output_dir.exists()) and (output_file.exists())

    def test_tectonic_mode_comments_out_lineno(self, tmp_path):
        """Tectonic mode should comment out lineno package."""
        # Arrange
        base_file = tmp_path / "base.tex"
        base_file.write_text(
            "\\usepackage{lineno}\n\\linenumbers\n\\begin{document}\nContent\n\\end{document}"
        )

        output_file = tmp_path / "output.tex"

        compile_tex_structure(
            base_tex=base_file,
            output_tex=output_file,
            verbose=False,
            tectonic_mode=True,
        )

        # Act
        output_content = output_file.read_text()
        # lineno package should be commented out
        # Assert
        assert ("% \\usepackage{lineno}" in output_content) and (
            "% \\linenumbers" in output_content
        )

    def test_tectonic_mode_comments_out_bashful(self, tmp_path):
        """Tectonic mode should comment out bashful package."""
        # Arrange
        base_file = tmp_path / "base.tex"
        base_file.write_text(
            "\\usepackage{bashful}\n\\begin{document}\nContent\n\\end{document}"
        )

        output_file = tmp_path / "output.tex"

        compile_tex_structure(
            base_tex=base_file,
            output_tex=output_file,
            verbose=False,
            tectonic_mode=True,
        )

        # Act
        output_content = output_file.read_text()
        # bashful package should be commented out
        # Assert
        assert "% \\usepackage{bashful}" in output_content

    def test_dark_mode_injection_dark_mode_styling_in_output_content_and_pagecolor_black_in_o(
        self, tmp_path
    ):
        # Arrange
        dark_mode_dir = tmp_path / "00_shared" / "latex_styles"
        dark_mode_dir.mkdir(parents=True)
        dark_mode_file = dark_mode_dir / "dark_mode.tex"
        dark_mode_file.write_text(
            "% Dark mode test content\n\\pagecolor{black}\n\\color{white}"
        )
        base_file = tmp_path / "01_manuscript" / "base.tex"
        base_file.parent.mkdir(parents=True)
        base_file.write_text("\\begin{document}\nContent\n\\end{document}")
        output_file = tmp_path / "01_manuscript" / "output.tex"
        compile_tex_structure(
            base_tex=base_file, output_tex=output_file, verbose=False, dark_mode=True
        )
        # Act
        output_content = output_file.read_text()
        # Act
        # Assert
        assert ("Dark mode styling" in output_content) and (
            "pagecolor{black}" in output_content
        )

    def test_dark_mode_injection_dark_pos_doc_pos(self, tmp_path):
        # Arrange
        dark_mode_dir = tmp_path / "00_shared" / "latex_styles"
        dark_mode_dir.mkdir(parents=True)
        dark_mode_file = dark_mode_dir / "dark_mode.tex"
        dark_mode_file.write_text(
            "% Dark mode test content\n\\pagecolor{black}\n\\color{white}"
        )
        base_file = tmp_path / "01_manuscript" / "base.tex"
        base_file.parent.mkdir(parents=True)
        base_file.write_text("\\begin{document}\nContent\n\\end{document}")
        output_file = tmp_path / "01_manuscript" / "output.tex"
        compile_tex_structure(
            base_tex=base_file, output_tex=output_file, verbose=False, dark_mode=True
        )
        output_content = output_file.read_text()
        # Should have dark mode comment
        # Dark mode should come before \begin{document}
        dark_pos = output_content.find("Dark mode")
        # Act
        doc_pos = output_content.find("\\begin{document}")
        # Act
        # Assert
        assert dark_pos < doc_pos


def _theme_project(tmp_path, theme):
    """Build a minimal project (config/ + 01_manuscript/base.tex) for theme tests."""
    (tmp_path / "config").mkdir(exist_ok=True)
    (tmp_path / "01_manuscript").mkdir(exist_ok=True)
    base = tmp_path / "01_manuscript" / "base.tex"
    base.write_text("\\begin{document}\nx\n\\end{document}")
    if theme is not None:
        (tmp_path / "config" / "config_manuscript.yaml").write_text(f"theme: {theme}\n")
    return base


@pytest.fixture
def clean_dark_env():
    """Save/restore the env vars theme resolution reads (no monkeypatch)."""
    keys = ("SCITEX_WRITER_DARK_MODE", "SCITEX_WRITER_DOC_TYPE")
    saved = {k: os.environ.get(k) for k in keys}
    os.environ.pop("SCITEX_WRITER_DARK_MODE", None)
    os.environ["SCITEX_WRITER_DOC_TYPE"] = "manuscript"
    yield
    for k, v in saved.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v


class TestThemeResolution:
    """theme: light|dark knob (precedence: flag > env > config > light)."""

    def test_resolve_dark_mode_flag_beats_config_light(self, tmp_path, clean_dark_env):
        # Arrange
        base = _theme_project(tmp_path, "light")
        # Act
        result = _resolve_dark_mode(True, base)
        # Assert
        assert result is True

    def test_resolve_dark_mode_config_dark_with_no_flag_or_env(
        self, tmp_path, clean_dark_env
    ):
        # Arrange
        base = _theme_project(tmp_path, "dark")
        # Act
        result = _resolve_dark_mode(False, base)
        # Assert
        assert result is True

    def test_resolve_dark_mode_env_false_beats_config_dark(
        self, tmp_path, clean_dark_env
    ):
        # Arrange
        base = _theme_project(tmp_path, "dark")
        os.environ["SCITEX_WRITER_DARK_MODE"] = "false"
        # Act
        result = _resolve_dark_mode(False, base)
        # Assert
        assert result is False

    def test_read_config_theme_invalid_value_raises_systemexit(
        self, tmp_path, clean_dark_env
    ):
        # Arrange
        base = _theme_project(tmp_path, "drak")
        # Act
        raises_systemexit = pytest.raises(SystemExit)
        # Assert
        with raises_systemexit:
            _read_config_theme(base)

    def test_read_config_theme_missing_config_defaults_to_light(
        self, tmp_path, clean_dark_env
    ):
        # Arrange
        base = _theme_project(tmp_path, None)
        # Act
        result = _read_config_theme(base)
        # Assert
        assert result == "light"


@pytest.fixture
def chdir_tmp(tmp_path):
    """Run the test with cwd = tmp_path (real chdir, restored on teardown).

    _style_fallback resolves 00_shared/latex_styles relative to cwd (= project
    root in the real pipeline, like ./-prefixed inputs). No monkeypatch: we set
    the real cwd and restore it.
    """
    prev = os.getcwd()
    os.chdir(tmp_path)
    try:
        yield tmp_path
    finally:
        os.chdir(prev)


class TestStyleFallbackAndFailLoud:
    """latex_styles \\input falls back to 00_shared/latex_styles; a still-missing
    preamble style input fails loud (no silent broken-PDF on exit 0)."""

    def test_is_style_input_true_for_latex_styles_path(self):
        # Arrange
        path = "contents/latex_styles/packages.tex"
        # Act
        result = _is_style_input(path)
        # Assert
        assert result is True

    def test_is_style_input_false_for_content_path(self):
        # Arrange
        path = "contents/methods.tex"
        # Act
        result = _is_style_input(path)
        # Assert
        assert result is False

    def test_style_fallback_resolves_from_00shared(self, chdir_tmp):
        """A latex_styles input missing in contents/ resolves to 00_shared."""
        # Arrange
        (chdir_tmp / "00_shared" / "latex_styles").mkdir(parents=True)
        (chdir_tmp / "00_shared" / "latex_styles" / "packages.tex").write_text("PKG")
        # Act
        resolved = _style_fallback(
            Path("01_manuscript/contents/latex_styles/packages.tex")
        )
        # Assert
        assert resolved == Path("00_shared") / "latex_styles" / "packages.tex"

    def test_style_fallback_none_for_non_style(self, chdir_tmp):
        # Arrange
        target = Path("01_manuscript/contents/methods.tex")
        # Act
        resolved = _style_fallback(target)
        # Assert
        assert resolved is None

    def test_expand_resolves_style_via_00shared_fallback(self, chdir_tmp):
        """A \\input of a contents/latex_styles file inlines the 00_shared copy."""
        # Arrange
        (chdir_tmp / "00_shared" / "latex_styles").mkdir(parents=True)
        (chdir_tmp / "00_shared" / "latex_styles" / "packages.tex").write_text("PKGMARK")
        (chdir_tmp / "01_manuscript").mkdir(parents=True)
        base = chdir_tmp / "01_manuscript" / "base.tex"
        base.write_text("\\input{contents/latex_styles/packages}")
        errors = []
        # Act
        out = expand_inputs(base, errors=errors)
        # Assert
        assert ("PKGMARK" in out) and (errors == [])

    def test_missing_style_input_records_fatal_error(self, chdir_tmp):
        """A style input absent in BOTH contents/ and 00_shared is fail-loud."""
        # Arrange
        (chdir_tmp / "01_manuscript").mkdir(parents=True)
        base = chdir_tmp / "01_manuscript" / "base.tex"
        base.write_text("\\input{contents/latex_styles/packages}")
        errors = []
        # Act
        out = expand_inputs(base, errors=errors)
        # Assert
        assert (len(errors) == 1) and ("FATAL" in out) and ("PKGMARK" not in out)

    def test_missing_non_style_input_is_skipped_not_fatal(self, chdir_tmp):
        """A missing NON-style \\input keeps the historical skip (not fatal)."""
        # Arrange
        (chdir_tmp / "01_manuscript").mkdir(parents=True)
        base = chdir_tmp / "01_manuscript" / "base.tex"
        base.write_text("\\input{contents/optional_section}")
        errors = []
        # Act
        out = expand_inputs(base, errors=errors)
        # Assert
        assert (errors == []) and ("SKIPPED" in out)

    def test_compile_aborts_on_missing_style_input(self, chdir_tmp):
        """compile_tex_structure returns False when a preamble style is missing."""
        # Arrange
        (chdir_tmp / "01_manuscript").mkdir(parents=True)
        base = chdir_tmp / "01_manuscript" / "base.tex"
        base.write_text("\\input{contents/latex_styles/packages}")
        output = chdir_tmp / "01_manuscript" / "out.tex"
        # Act
        success = compile_tex_structure(base_tex=base, output_tex=output, verbose=False)
        # Assert
        assert success is False


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v"])
