#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: tests/python/test_migration.py

"""Tests for the migration module (Overleaf import/export)."""

import zipfile
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def simple_overleaf_zip(tmp_path):
    """Create a minimal Overleaf-style ZIP for testing."""
    project_dir = tmp_path / "overleaf_project"
    project_dir.mkdir()

    # main.tex with \documentclass and inline metadata
    (project_dir / "main.tex").write_text(
        r"""\documentclass{article}
\title{Test Paper Title}
\author{John Doe}
\begin{document}
\maketitle
\input{sections/introduction}
\input{sections/methods}
\input{sections/results}
\input{sections/discussion}
\bibliography{refs}
\end{document}
""",
        encoding="utf-8",
    )

    # Sections
    sections = project_dir / "sections"
    sections.mkdir()
    (sections / "introduction.tex").write_text(
        r"\section{Introduction}" "\nThis is the introduction.",
        encoding="utf-8",
    )
    (sections / "methods.tex").write_text(
        r"\section{Methods}" "\nThese are the methods.",
        encoding="utf-8",
    )
    (sections / "results.tex").write_text(
        r"\section{Results}" "\nThese are the results.",
        encoding="utf-8",
    )
    (sections / "discussion.tex").write_text(
        r"\section{Discussion}" "\nThis is the discussion.",
        encoding="utf-8",
    )

    # Bibliography
    (project_dir / "refs.bib").write_text(
        "@article{doe2025, author={Doe}, title={Test}, year={2025}}\n",
        encoding="utf-8",
    )

    # Image
    images = project_dir / "images"
    images.mkdir()
    (images / "fig1.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)

    # Create ZIP
    zip_path = tmp_path / "test_project.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for f in project_dir.rglob("*"):
            if f.is_file():
                zf.write(f, f.relative_to(project_dir))

    return zip_path


@pytest.fixture
def inline_overleaf_zip(tmp_path):
    """Overleaf ZIP with all content inline in main.tex (no \\input)."""
    project_dir = tmp_path / "inline_project"
    project_dir.mkdir()

    (project_dir / "main.tex").write_text(
        r"""\documentclass{article}
\title{Inline Paper}
\author{Jane Doe}
\begin{document}
\maketitle
\begin{abstract}
This is the abstract.
\end{abstract}
\section{Introduction}
Intro text here.
\section{Methods}
Methods text here.
\section{Results}
Results text here.
\section{Discussion}
Discussion text here.
\end{document}
""",
        encoding="utf-8",
    )

    zip_path = tmp_path / "inline_project.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for f in project_dir.rglob("*"):
            if f.is_file():
                zf.write(f, f.relative_to(project_dir))

    return zip_path


# ---------------------------------------------------------------------------
# Parsing tests
# ---------------------------------------------------------------------------


class TestParsing:
    def test_detect_main_tex(self, tmp_path):
        from scitex_writer.migration._parsing import detect_main_tex

        (tmp_path / "main.tex").write_text(r"\documentclass{article}", encoding="utf-8")
        (tmp_path / "helper.tex").write_text(r"\section{Foo}", encoding="utf-8")

        result = detect_main_tex(tmp_path)
        assert result is not None
        assert result.name == "main.tex"

    def test_detect_main_tex_no_documentclass(self, tmp_path):
        from scitex_writer.migration._parsing import detect_main_tex

        (tmp_path / "notes.tex").write_text("Just some text", encoding="utf-8")

        result = detect_main_tex(tmp_path)
        assert result is None

    def test_detect_main_tex_prefers_main(self, tmp_path):
        from scitex_writer.migration._parsing import detect_main_tex

        (tmp_path / "main.tex").write_text(r"\documentclass{article}", encoding="utf-8")
        (tmp_path / "paper.tex").write_text(
            r"\documentclass{article}", encoding="utf-8"
        )

        result = detect_main_tex(tmp_path)
        assert result.name == "main.tex"

    def test_classify_section_by_filename(self):
        from scitex_writer.migration._parsing import classify_section

        assert classify_section(Path("intro.tex"), "") == "introduction"
        assert classify_section(Path("methods.tex"), "") == "methods"
        assert classify_section(Path("results.tex"), "") == "results"
        assert classify_section(Path("discussion.tex"), "") == "discussion"
        assert classify_section(Path("abstract.tex"), "") == "abstract"
        assert classify_section(Path("random.tex"), "") is None

    def test_classify_section_by_heading(self):
        from scitex_writer.migration._parsing import classify_section

        content = r"\section{Introduction and Background}"
        assert classify_section(Path("ch1.tex"), content) == "introduction"

        content = r"\section{Experimental Procedure}"
        assert classify_section(Path("ch2.tex"), content) == "methods"

    def test_extract_metadata(self):
        from scitex_writer.migration._parsing import extract_metadata

        content = r"""
\title{My Great Paper}
\author{Alice Bob}
\keywords{science, testing}
"""
        meta = extract_metadata(content)
        assert meta["title"] == "My Great Paper"
        assert meta["authors_block"] == "Alice Bob"
        assert meta["keywords"] == "science, testing"

    def test_extract_metadata_empty(self):
        from scitex_writer.migration._parsing import extract_metadata

        meta = extract_metadata("No metadata here")
        assert meta["title"] is None
        assert meta["authors_block"] is None
        assert meta["keywords"] is None

    def test_split_inline_sections(self):
        from scitex_writer.migration._parsing import split_inline_sections

        content = r"""
\section{Introduction}
Intro text.
\section{Methods}
Methods text.
\section{Conclusion}
Conclusion text.
"""
        sections = split_inline_sections(content)
        assert "introduction" in sections
        assert "methods" in sections
        assert "discussion" in sections  # conclusion maps to discussion

    def test_unique_dest(self, tmp_path):
        from scitex_writer.migration._parsing import unique_dest

        f = tmp_path / "test.txt"
        assert unique_dest(f) == f

        f.write_text("existing")
        result = unique_dest(f)
        assert result.name == "test_1.txt"


# ---------------------------------------------------------------------------
# Import tests
# ---------------------------------------------------------------------------


class TestImport:
    def test_import_dry_run(self, simple_overleaf_zip, tmp_path):
        from scitex_writer.migration import from_overleaf

        result = from_overleaf(
            str(simple_overleaf_zip),
            output_dir=str(tmp_path / "output"),
            dry_run=True,
        )

        assert result["success"] is True
        assert result["dry_run"] is True
        assert "mapping_report" in result
        report = result["mapping_report"]
        assert report["main_tex"] == "main.tex"
        assert "introduction" in report["sections"]
        assert len(report["bib_files"]) == 1
        assert len(report["images"]) >= 1

    def test_import_nonexistent_zip(self):
        from scitex_writer.migration import from_overleaf

        result = from_overleaf("/nonexistent/file.zip")
        assert result["success"] is False
        assert "not found" in result["error"].lower()

    def test_import_invalid_zip(self, tmp_path):
        from scitex_writer.migration import from_overleaf

        fake = tmp_path / "fake.zip"
        fake.write_text("not a zip")
        result = from_overleaf(str(fake))
        assert result["success"] is False
        assert "not a valid zip" in result["error"].lower()

    def test_import_output_exists_no_force(self, simple_overleaf_zip, tmp_path):
        from scitex_writer.migration import from_overleaf

        out = tmp_path / "existing"
        out.mkdir()
        result = from_overleaf(str(simple_overleaf_zip), output_dir=str(out))
        assert result["success"] is False
        assert "already exists" in result["error"].lower()

    def test_import_inline_dry_run(self, inline_overleaf_zip, tmp_path):
        from scitex_writer.migration import from_overleaf

        result = from_overleaf(
            str(inline_overleaf_zip),
            output_dir=str(tmp_path / "inline_out"),
            dry_run=True,
        )

        assert result["success"] is True
        report = result["mapping_report"]
        assert report["metadata"]["title"] == "Inline Paper"

    def test_import_success_creates_project(self, simple_overleaf_zip, tmp_path):
        from unittest.mock import patch

        from scitex_writer.migration import from_overleaf

        out = tmp_path / "imported_project"

        def fake_clone(project_dir, git_strategy="child", **kwargs):
            """Create minimal scitex-writer directory structure."""
            p = Path(project_dir)
            p.mkdir(parents=True, exist_ok=True)
            (p / "00_shared" / "bib_files").mkdir(parents=True)
            (p / "00_shared" / "latex_styles").mkdir(parents=True)
            (p / "01_manuscript" / "contents" / "figures" / "caption_and_media").mkdir(
                parents=True
            )
            (p / "01_manuscript" / "contents" / "tables" / "caption_and_media").mkdir(
                parents=True
            )
            for sec in ["abstract", "introduction", "methods", "results", "discussion"]:
                (p / "01_manuscript" / "contents" / f"{sec}.tex").write_text("")
            return True

        with patch(
            "scitex_writer._project._create.clone_writer_project",
            side_effect=fake_clone,
        ):
            result = from_overleaf(str(simple_overleaf_zip), output_dir=str(out))

        assert result["success"] is True
        assert result["dry_run"] is False
        assert out.exists()

        # Sections were written
        contents = out / "01_manuscript" / "contents"
        assert (contents / "introduction.tex").exists()
        intro_text = (contents / "introduction.tex").read_text()
        assert "introduction" in intro_text.lower()

        # Bib was copied
        bib_files = list((out / "00_shared" / "bib_files").glob("*.bib"))
        assert len(bib_files) >= 1

        # Image was copied
        images = list((contents / "figures" / "caption_and_media").glob("*"))
        assert len(images) >= 1

        # Metadata was written
        assert (out / "00_shared" / "title.tex").exists()
        title = (out / "00_shared" / "title.tex").read_text()
        assert "Test Paper Title" in title

    def test_import_force_overwrites(self, simple_overleaf_zip, tmp_path):
        from unittest.mock import patch

        from scitex_writer.migration import from_overleaf

        out = tmp_path / "force_project"
        out.mkdir()
        (out / "marker.txt").write_text("old")

        def fake_clone(project_dir, git_strategy="child", **kwargs):
            p = Path(project_dir)
            p.mkdir(parents=True, exist_ok=True)
            (p / "00_shared" / "bib_files").mkdir(parents=True)
            (p / "01_manuscript" / "contents" / "figures" / "caption_and_media").mkdir(
                parents=True
            )
            (p / "01_manuscript" / "contents" / "tables" / "caption_and_media").mkdir(
                parents=True
            )
            for sec in ["abstract", "introduction", "methods", "results", "discussion"]:
                (p / "01_manuscript" / "contents" / f"{sec}.tex").write_text("")
            return True

        with patch(
            "scitex_writer._project._create.clone_writer_project",
            side_effect=fake_clone,
        ):
            result = from_overleaf(
                str(simple_overleaf_zip), output_dir=str(out), force=True
            )

        assert result["success"] is True
        assert not (out / "marker.txt").exists()


# ---------------------------------------------------------------------------
# Export tests
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_scitex_project(tmp_path):
    """Create a minimal scitex-writer project structure for export testing."""
    proj = tmp_path / "mock_project"
    proj.mkdir()

    shared = proj / "00_shared"
    shared.mkdir()
    (shared / "title.tex").write_text("My Test Title\n")
    (shared / "authors.tex").write_text("Test Author\n")

    bib_dir = shared / "bib_files"
    bib_dir.mkdir()
    (bib_dir / "refs.bib").write_text(
        "@article{test2025, author={A}, title={B}, year={2025}}\n"
    )

    contents = proj / "01_manuscript" / "contents"
    contents.mkdir(parents=True)
    (contents / "introduction.tex").write_text(
        r"\section{Introduction}" "\nIntro content.\n"
    )
    (contents / "methods.tex").write_text(r"\section{Methods}" "\nMethods content.\n")
    (contents / "results.tex").write_text(r"\section{Results}" "\nResults content.\n")
    (contents / "discussion.tex").write_text(
        r"\section{Discussion}" "\nDiscussion content.\n"
    )

    fig_dir = contents / "figures" / "caption_and_media"
    fig_dir.mkdir(parents=True)
    (fig_dir / "fig1.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 50)

    return proj


class TestExport:
    def test_export_nonexistent_project(self):
        from scitex_writer.migration import to_overleaf

        result = to_overleaf("/nonexistent/project")
        assert result["success"] is False

    def test_export_not_a_project(self, tmp_path):
        from scitex_writer.migration import to_overleaf

        result = to_overleaf(str(tmp_path))
        assert result["success"] is False
        assert "does not look like" in result["error"].lower()

    def test_export_dry_run(self, mock_scitex_project):
        from scitex_writer.migration import to_overleaf

        result = to_overleaf(str(mock_scitex_project), dry_run=True)

        assert result["success"] is True
        assert result["dry_run"] is True
        assert result["file_count"] > 0
        assert "main.tex" in result["files_included"]
        assert "references.bib" in result["files_included"]

    def test_export_creates_zip(self, mock_scitex_project, tmp_path):
        from scitex_writer.migration import to_overleaf

        zip_out = tmp_path / "export.zip"
        result = to_overleaf(str(mock_scitex_project), output_path=str(zip_out))

        assert result["success"] is True
        assert result["dry_run"] is False
        assert zip_out.exists()

        # Verify ZIP contents
        with zipfile.ZipFile(zip_out) as zf:
            names = zf.namelist()
            assert "main.tex" in names
            assert "references.bib" in names
            assert any("sections/" in n for n in names)
            assert any("images/" in n for n in names)

            # main.tex has documentclass and title
            main_content = zf.read("main.tex").decode()
            assert r"\documentclass" in main_content
            assert r"\title{My Test Title}" in main_content


# ---------------------------------------------------------------------------
# Module API tests
# ---------------------------------------------------------------------------


class TestModuleAPI:
    def test_migration_in_all(self):
        import scitex_writer as sw

        assert "migration" in sw.__all__

    def test_from_overleaf_callable(self):
        from scitex_writer import migration

        assert callable(migration.from_overleaf)

    def test_to_overleaf_callable(self):
        from scitex_writer import migration

        assert callable(migration.to_overleaf)

    def test_cli_help(self):
        import subprocess

        result = subprocess.run(
            ["scitex-writer", "migration", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "import" in result.stdout
        assert "export" in result.stdout


# EOF
