#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: compile_tex_structure.py
# Wave 2 cluster A batch 1 — NM+TQ003+TQ002+TQ007 cleanup.

import os
import re
import sys
from pathlib import Path

import pytest

# Add scripts/python to path for imports
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

from compile_tex_structure import (  # noqa: E402
    compile_tex_structure,
    expand_inputs,
    generate_signature,
)


@pytest.fixture
def env_engine_tectonic():
    """Set `SCITEX_WRITER_ENGINE=tectonic` for the lifetime of the test.

    Uses a real `yield` fixture (no monkeypatch) so teardown restores
    the original environment value even on test failure.
    """
    # Arrange
    sentinel = object()
    original = os.environ.get("SCITEX_WRITER_ENGINE", sentinel)
    os.environ["SCITEX_WRITER_ENGINE"] = "tectonic"
    yield "tectonic"
    if original is sentinel:
        os.environ.pop("SCITEX_WRITER_ENGINE", None)
    else:
        os.environ["SCITEX_WRITER_ENGINE"] = original


# ============================================================================
# generate_signature
# ============================================================================


def test_generate_signature_contains_scitex_writer_marker():
    """The compilation signature contains the literal 'SciTeX Writer' marker."""
    # Arrange
    # (no fixture state required)
    # Act
    signature = generate_signature()
    # Assert
    assert "SciTeX Writer" in signature


def test_generate_signature_contains_version_token():
    """The signature line contains either a numeric version or 'unknown'."""
    # Arrange
    # (no fixture state required)
    # Act
    signature = generate_signature()
    # Assert
    assert "SciTeX Writer unknown" in signature or re.search(
        r"SciTeX Writer \d+\.\d+", signature
    )


def test_generate_signature_contains_engine_label():
    """The signature contains the literal 'LaTeX compilation engine:' label."""
    # Arrange
    # (no fixture state required)
    # Act
    signature = generate_signature()
    # Assert
    assert "LaTeX compilation engine:" in signature


def test_generate_signature_with_env_engine_reports_tectonic(env_engine_tectonic):
    """When SCITEX_WRITER_ENGINE=tectonic, the signature reports `engine: tectonic`."""
    # Arrange
    # (env set by fixture)
    # Act
    signature = generate_signature()
    # Assert
    assert "engine: tectonic" in signature


def test_generate_signature_with_source_file_records_path(tmp_path):
    """A source_file argument is included verbatim in the signature output."""
    # Arrange
    source_file = tmp_path / "test.tex"
    # Act
    signature = generate_signature(source_file=source_file)
    # Assert
    assert str(source_file) in signature


def test_generate_signature_contains_compiled_label():
    """The signature contains the literal 'Compiled:' label."""
    # Arrange
    # (no fixture state required)
    # Act
    signature = generate_signature()
    # Assert
    assert "Compiled:" in signature


def test_generate_signature_contains_iso_date():
    """The signature contains a YYYY-MM-DD date token."""
    # Arrange
    # (no fixture state required)
    # Act
    signature = generate_signature()
    # Assert
    assert re.search(r"\d{4}-\d{2}-\d{2}", signature)


def test_generate_signature_non_empty_lines_are_latex_comments():
    """Every non-empty signature line begins with a `%` LaTeX comment marker."""
    # Arrange
    # (no fixture state required)
    # Act
    signature = generate_signature()
    # Assert
    assert all(line.startswith("%") for line in signature.split("\n") if line.strip())


# ============================================================================
# expand_inputs
# ============================================================================


def test_expand_inputs_simple_file_returns_content(tmp_path):
    """expand_inputs of a plain file returns the file's text content."""
    # Arrange
    test_file = tmp_path / "test.tex"
    test_file.write_text("Hello, world!")
    # Act
    result = expand_inputs(test_file)
    # Assert
    assert "Hello, world!" in result


def test_expand_inputs_input_command_inlines_child_content(tmp_path):
    """An `\\input{child}` command inlines the child file's content."""
    # Arrange
    (tmp_path / "child.tex").write_text("Child content here")
    parent = tmp_path / "parent.tex"
    parent.write_text("Start\n\\input{child}\nEnd")
    # Act
    result = expand_inputs(parent)
    # Assert
    assert "Child content here" in result


def test_expand_inputs_input_command_emits_file_header_comment(tmp_path):
    """An inlined `\\input{child}` is preceded by a `File: child` header."""
    # Arrange
    (tmp_path / "child.tex").write_text("X")
    parent = tmp_path / "parent.tex"
    parent.write_text("\\input{child}")
    # Act
    result = expand_inputs(parent)
    # Assert
    assert "File: child" in result


def test_expand_inputs_missing_input_emits_skipped_marker(tmp_path):
    """A missing `\\input{nonexistent}` target produces a SKIPPED marker."""
    # Arrange
    parent = tmp_path / "parent.tex"
    parent.write_text("\\input{nonexistent}")
    # Act
    result = expand_inputs(parent)
    # Assert
    assert "SKIPPED" in result


def test_expand_inputs_circular_reference_is_caught(tmp_path):
    """A self-referencing file is detected and emitted as SKIPPED."""
    # Arrange
    f = tmp_path / "circular.tex"
    f.write_text("Start\n\\input{circular}\nEnd")
    # Act
    result = expand_inputs(f)
    # Assert
    assert "SKIPPED" in result


def test_expand_inputs_max_depth_hits_recursion_limit(tmp_path):
    """A nested chain exceeding `max_depth` emits a Max-recursion or ERROR marker."""
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
    # Assert
    assert "ERROR" in result or "Max recursion depth" in result


def test_expand_inputs_commented_input_is_not_expanded(tmp_path):
    """A `% \\input{child}` comment line does not pull in the child file."""
    # Arrange
    (tmp_path / "child.tex").write_text("This should not appear")
    parent = tmp_path / "parent.tex"
    parent.write_text("Start\n% \\input{child}\nEnd")
    # Act
    result = expand_inputs(parent)
    # Assert
    assert "This should not appear" not in result


def test_expand_inputs_adds_tex_extension_when_missing(tmp_path):
    """`\\input{child}` (no .tex) still resolves to `child.tex`."""
    # Arrange
    (tmp_path / "child.tex").write_text("Child content")
    parent = tmp_path / "parent.tex"
    parent.write_text("\\input{child}")
    # Act
    result = expand_inputs(parent)
    # Assert
    assert "Child content" in result


def test_expand_inputs_two_level_nesting_inlines_leaf_content(tmp_path):
    """A two-level nested `\\input` chain inlines the leaf content."""
    # Arrange
    (tmp_path / "level2.tex").write_text("Level 2 content")
    (tmp_path / "level1.tex").write_text("Level 1 start\n\\input{level2}\nLevel 1 end")
    level0 = tmp_path / "level0.tex"
    level0.write_text("Level 0 start\n\\input{level1}\nLevel 0 end")
    # Act
    result = expand_inputs(level0)
    # Assert
    assert "Level 2 content" in result


def test_expand_inputs_nonexistent_top_level_file_is_skipped(tmp_path):
    """A nonexistent top-level path is reported via SKIPPED marker."""
    # Arrange
    nonexistent = tmp_path / "does_not_exist.tex"
    # Act
    result = expand_inputs(nonexistent)
    # Assert
    assert "SKIPPED" in result


# ============================================================================
# compile_tex_structure
# ============================================================================


def test_compile_tex_structure_simple_doc_returns_true(tmp_path):
    """compile_tex_structure returns True after compiling a minimal article."""
    # Arrange
    base = tmp_path / "base.tex"
    base.write_text(
        "\\documentclass{article}\n\\begin{document}\nHello\n\\end{document}"
    )
    output = tmp_path / "output.tex"
    # Act
    success = compile_tex_structure(base_tex=base, output_tex=output, verbose=False)
    # Assert
    assert success is True


def test_compile_tex_structure_simple_doc_writes_output_file(tmp_path):
    """compile_tex_structure writes the output file on success."""
    # Arrange
    base = tmp_path / "base.tex"
    base.write_text("\\documentclass{article}\n\\begin{document}\nH\n\\end{document}")
    output = tmp_path / "output.tex"
    # Act
    compile_tex_structure(base_tex=base, output_tex=output, verbose=False)
    # Assert
    assert output.exists()


def test_compile_tex_structure_output_includes_signature(tmp_path):
    """The output file contains the SciTeX Writer signature marker."""
    # Arrange
    base = tmp_path / "base.tex"
    base.write_text("Content")
    output = tmp_path / "output.tex"
    # Act
    compile_tex_structure(base_tex=base, output_tex=output, verbose=False)
    # Assert
    assert "SciTeX Writer" in output.read_text()


def test_compile_tex_structure_inlines_child_input_in_output(tmp_path):
    """Child `\\input{}` content is inlined into the compiled output file."""
    # Arrange
    (tmp_path / "child.tex").write_text("Child content")
    base = tmp_path / "base.tex"
    base.write_text("Start\n\\input{child}\nEnd")
    output = tmp_path / "output.tex"
    # Act
    compile_tex_structure(base_tex=base, output_tex=output, verbose=False)
    # Assert
    assert "Child content" in output.read_text()


def test_compile_tex_structure_missing_base_returns_false(tmp_path):
    """A nonexistent base.tex causes compile_tex_structure to return False."""
    # Arrange
    base = tmp_path / "nonexistent.tex"
    output = tmp_path / "output.tex"
    # Act
    success = compile_tex_structure(base_tex=base, output_tex=output, verbose=False)
    # Assert
    assert success is False


def test_compile_tex_structure_creates_nested_output_dir(tmp_path):
    """compile_tex_structure creates the nested output directory on demand."""
    # Arrange
    base = tmp_path / "base.tex"
    base.write_text("Content")
    output_dir = tmp_path / "nested" / "dir"
    output = output_dir / "output.tex"
    # Act
    compile_tex_structure(base_tex=base, output_tex=output, verbose=False)
    # Assert
    assert output_dir.exists()


def test_compile_tex_structure_tectonic_mode_comments_out_lineno(tmp_path):
    """Tectonic mode rewrites `\\usepackage{lineno}` to a comment line."""
    # Arrange
    base = tmp_path / "base.tex"
    base.write_text("\\usepackage{lineno}\n\\begin{document}\nC\n\\end{document}")
    output = tmp_path / "output.tex"
    # Act
    compile_tex_structure(
        base_tex=base, output_tex=output, verbose=False, tectonic_mode=True
    )
    # Assert
    assert "% \\usepackage{lineno}" in output.read_text()


def test_compile_tex_structure_tectonic_mode_comments_out_bashful(tmp_path):
    """Tectonic mode rewrites `\\usepackage{bashful}` to a comment line."""
    # Arrange
    base = tmp_path / "base.tex"
    base.write_text("\\usepackage{bashful}\n\\begin{document}\nC\n\\end{document}")
    output = tmp_path / "output.tex"
    # Act
    compile_tex_structure(
        base_tex=base, output_tex=output, verbose=False, tectonic_mode=True
    )
    # Assert
    assert "% \\usepackage{bashful}" in output.read_text()


def test_compile_tex_structure_dark_mode_inlines_styling_block(tmp_path):
    """Dark mode injects the project's `dark_mode.tex` into the output."""
    # Arrange
    dark_dir = tmp_path / "00_shared" / "latex_styles"
    dark_dir.mkdir(parents=True)
    (dark_dir / "dark_mode.tex").write_text("\\pagecolor{black}\n\\color{white}")
    base = tmp_path / "01_manuscript" / "base.tex"
    base.parent.mkdir(parents=True)
    base.write_text("\\begin{document}\nC\n\\end{document}")
    output = tmp_path / "01_manuscript" / "output.tex"
    # Act
    compile_tex_structure(
        base_tex=base, output_tex=output, verbose=False, dark_mode=True
    )
    # Assert
    assert "pagecolor{black}" in output.read_text()


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v"])
