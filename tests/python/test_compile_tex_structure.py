#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: compile_tex_structure.py

import os
import re
import sys
from pathlib import Path

import pytest

# Add scripts/python to path for imports
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

from compile_tex_structure import (
    compile_tex_structure,
    expand_inputs,
    generate_signature,
)


class TestGenerateSignature:
    """Test signature generation."""

    def test_generate_signature_contains_scitex_writer(self):
        """Signature should contain 'SciTeX Writer'."""
        signature = generate_signature()
        assert "SciTeX Writer" in signature

    def test_generate_signature_contains_version(self):
        """Signature should contain version number or 'unknown'."""
        signature = generate_signature()
        # Should have version line
        assert "SciTeX Writer" in signature
        # Version is present (either from pyproject.toml or 'unknown')
        assert "SciTeX Writer unknown" in signature or re.search(
            r"SciTeX Writer \d+\.\d+", signature
        )

    def test_generate_signature_contains_engine(self):
        """Signature should contain engine information."""
        signature = generate_signature()
        assert "LaTeX compilation engine:" in signature
        # Default should be 'auto' if env vars not set
        assert "auto" in signature or "tectonic" in signature or "latexmk" in signature

    def test_generate_signature_with_env_engine(self, monkeypatch):
        """Signature should use SCITEX_WRITER_ENGINE if set."""
        monkeypatch.setenv("SCITEX_WRITER_ENGINE", "tectonic")
        signature = generate_signature()
        assert "engine: tectonic" in signature

    def test_generate_signature_with_source_file(self, tmp_path):
        """Signature should include source file path when provided."""
        source_file = tmp_path / "test.tex"
        signature = generate_signature(source_file=source_file)
        assert "Source:" in signature
        assert str(source_file) in signature

    def test_generate_signature_has_timestamp(self):
        """Signature should contain compilation timestamp."""
        signature = generate_signature()
        assert "Compiled:" in signature
        # Should match date format YYYY-MM-DD
        assert re.search(r"\d{4}-\d{2}-\d{2}", signature)

    def test_generate_signature_is_comment(self):
        """Signature should be LaTeX comments."""
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
        test_file = tmp_path / "test.tex"
        test_file.write_text("Hello, world!")

        result = expand_inputs(test_file)
        assert "Hello, world!" in result

    def test_expand_inputs_with_input_command(self, tmp_path):
        """Should expand \\input{} commands."""
        # Create child file
        child_file = tmp_path / "child.tex"
        child_file.write_text("Child content here")

        # Create parent file that references child
        parent_file = tmp_path / "parent.tex"
        parent_file.write_text("Start\n\\input{child}\nEnd")

        result = expand_inputs(parent_file)

        # Should contain both parent and child content
        assert "Start" in result
        assert "Child content here" in result
        assert "End" in result
        # Should have header comment for expanded file
        assert "File: child" in result

    def test_expand_inputs_missing_file(self, tmp_path):
        """Should handle missing input file gracefully."""
        parent_file = tmp_path / "parent.tex"
        parent_file.write_text("\\input{nonexistent}")

        result = expand_inputs(parent_file)

        # Should contain SKIPPED comment
        assert "SKIPPED" in result
        assert "file not found" in result

    def test_expand_inputs_circular_reference(self, tmp_path):
        """Should detect and prevent circular references."""
        # Create file that references itself
        self_ref_file = tmp_path / "circular.tex"
        self_ref_file.write_text("Start\n\\input{circular}\nEnd")

        result = expand_inputs(self_ref_file)

        # Should contain circular reference warning
        assert "SKIPPED" in result
        assert "circular reference" in result or "already processed" in result

    def test_expand_inputs_max_depth(self, tmp_path):
        """Should stop at max recursion depth."""
        # Create deeply nested structure
        files = []
        for i in range(15):
            f = tmp_path / f"level_{i}.tex"
            if i < 14:
                f.write_text(f"Level {i}\n\\input{{level_{i + 1}}}")
            else:
                f.write_text(f"Level {i}")
            files.append(f)

        result = expand_inputs(files[0], max_depth=5)

        # Should stop before reaching the deepest level
        assert "Level 0" in result
        assert "Level 5" in result or "Level 6" in result
        # Should hit depth limit
        assert "ERROR" in result or "Max recursion depth" in result

    def test_expand_inputs_commented_line_skipped(self, tmp_path):
        """Should skip \\input{} in commented lines."""
        child_file = tmp_path / "child.tex"
        child_file.write_text("This should not appear")

        parent_file = tmp_path / "parent.tex"
        parent_file.write_text("Start\n% \\input{child}\nEnd")

        result = expand_inputs(parent_file)

        # Should NOT expand commented input
        assert "This should not appear" not in result
        # Original comment should be preserved
        assert "% \\input{child}" in result

    def test_expand_inputs_adds_tex_extension(self, tmp_path):
        """Should add .tex extension if not present."""
        child_file = tmp_path / "child.tex"
        child_file.write_text("Child content")

        parent_file = tmp_path / "parent.tex"
        # Reference without .tex extension
        parent_file.write_text("\\input{child}")

        result = expand_inputs(parent_file)

        # Should successfully expand even without .tex
        assert "Child content" in result

    def test_expand_inputs_nested_multiple_levels(self, tmp_path):
        """Should handle multiple levels of nesting."""
        level2 = tmp_path / "level2.tex"
        level2.write_text("Level 2 content")

        level1 = tmp_path / "level1.tex"
        level1.write_text("Level 1 start\n\\input{level2}\nLevel 1 end")

        level0 = tmp_path / "level0.tex"
        level0.write_text("Level 0 start\n\\input{level1}\nLevel 0 end")

        result = expand_inputs(level0)

        # All levels should be present
        assert "Level 0 start" in result
        assert "Level 1 start" in result
        assert "Level 2 content" in result
        assert "Level 1 end" in result
        assert "Level 0 end" in result

    def test_expand_inputs_nonexistent_file(self, tmp_path):
        """Should handle nonexistent file at top level."""
        nonexistent = tmp_path / "does_not_exist.tex"

        result = expand_inputs(nonexistent)

        # Should return SKIPPED message
        assert "SKIPPED" in result
        assert "file not found" in result


class TestCompileTexStructure:
    """Test full TeX structure compilation."""

    def test_compile_tex_structure_creates_output(self, tmp_path):
        """Should create output file."""
        base_file = tmp_path / "base.tex"
        base_file.write_text(
            "\\documentclass{article}\n\\begin{document}\nHello\n\\end{document}"
        )

        output_file = tmp_path / "output.tex"

        success = compile_tex_structure(
            base_tex=base_file, output_tex=output_file, verbose=False
        )

        assert success is True
        assert output_file.exists()

    def test_compile_tex_structure_contains_signature(self, tmp_path):
        """Output should contain compilation signature."""
        base_file = tmp_path / "base.tex"
        base_file.write_text("Content")

        output_file = tmp_path / "output.tex"

        compile_tex_structure(base_tex=base_file, output_tex=output_file, verbose=False)

        output_content = output_file.read_text()
        assert "SciTeX Writer" in output_content
        assert "Compiled:" in output_content

    def test_compile_tex_structure_expands_inputs(self, tmp_path):
        """Should expand \\input{} commands in base file."""
        child_file = tmp_path / "child.tex"
        child_file.write_text("Child content")

        base_file = tmp_path / "base.tex"
        base_file.write_text("Start\n\\input{child}\nEnd")

        output_file = tmp_path / "output.tex"

        compile_tex_structure(base_tex=base_file, output_tex=output_file, verbose=False)

        output_content = output_file.read_text()
        assert "Child content" in output_content

    def test_compile_tex_structure_missing_base_file(self, tmp_path):
        """Should return False for missing base file."""
        base_file = tmp_path / "nonexistent.tex"
        output_file = tmp_path / "output.tex"

        success = compile_tex_structure(
            base_tex=base_file, output_tex=output_file, verbose=False
        )

        assert success is False
        assert not output_file.exists()

    def test_compile_tex_structure_creates_output_dir(self, tmp_path):
        """Should create output directory if it doesn't exist."""
        base_file = tmp_path / "base.tex"
        base_file.write_text("Content")

        output_dir = tmp_path / "nested" / "dir"
        output_file = output_dir / "output.tex"

        success = compile_tex_structure(
            base_tex=base_file, output_tex=output_file, verbose=False
        )

        assert success is True
        assert output_dir.exists()
        assert output_file.exists()

    def test_tectonic_mode_comments_out_lineno(self, tmp_path):
        """Tectonic mode should comment out lineno package."""
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

        output_content = output_file.read_text()
        # lineno package should be commented out
        assert "% \\usepackage{lineno}" in output_content
        # linenumbers command should be commented out
        assert "% \\linenumbers" in output_content

    def test_tectonic_mode_comments_out_bashful(self, tmp_path):
        """Tectonic mode should comment out bashful package."""
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

        output_content = output_file.read_text()
        # bashful package should be commented out
        assert "% \\usepackage{bashful}" in output_content

    def test_dark_mode_injection(self, tmp_path):
        """Dark mode should inject styling before document."""
        # Create the dark_mode.tex file structure
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
        assert "Dark mode styling" in output_content
        # Should have dark mode content
        assert "pagecolor{black}" in output_content
        # Dark mode should come before \begin{document}
        dark_pos = output_content.find("Dark mode")
        doc_pos = output_content.find("\\begin{document}")
        assert dark_pos < doc_pos


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v"])
