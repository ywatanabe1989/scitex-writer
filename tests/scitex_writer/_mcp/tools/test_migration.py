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
        # Arrange
        from scitex_writer.migration._parsing import detect_main_tex

        (tmp_path / "main.tex").write_text(r"\documentclass{article}", encoding="utf-8")
        (tmp_path / "helper.tex").write_text(r"\section{Foo}", encoding="utf-8")

        # Act
        result = detect_main_tex(tmp_path)
        # Assert
        assert (result is not None) and (result.name == 'main.tex')

    def test_detect_main_tex_no_documentclass(self, tmp_path):
        # Arrange
        from scitex_writer.migration._parsing import detect_main_tex

        (tmp_path / "notes.tex").write_text("Just some text", encoding="utf-8")

        # Act
        result = detect_main_tex(tmp_path)
        # Assert
        assert result is None

    def test_detect_main_tex_prefers_main(self, tmp_path):
        # Arrange
        from scitex_writer.migration._parsing import detect_main_tex

        (tmp_path / "main.tex").write_text(r"\documentclass{article}", encoding="utf-8")
        (tmp_path / "paper.tex").write_text(
            r"\documentclass{article}", encoding="utf-8"
        )

        # Act
        result = detect_main_tex(tmp_path)
        # Assert
        assert result.name == "main.tex"

    def test_classify_section_by_filename(self):
        # Arrange
        # Act
        from scitex_writer.migration._parsing import classify_section

        # Assert
        assert (classify_section(Path('intro.tex'), '') == 'introduction') and (classify_section(Path('methods.tex'), '') == 'methods') and (classify_section(Path('results.tex'), '') == 'results') and (classify_section(Path('discussion.tex'), '') == 'discussion') and (classify_section(Path('abstract.tex'), '') == 'abstract') and (classify_section(Path('random.tex'), '') is None)

    def test_classify_section_by_heading_classify_section_path_ch1_tex_content_introduction(self):
        # Arrange
        from scitex_writer.migration._parsing import classify_section
        # Act
        content = r"\section{Introduction and Background}"
        # Act
        # Assert
        assert classify_section(Path("ch1.tex"), content) == "introduction"

    def test_classify_section_by_heading_classify_section_path_ch2_tex_content_methods(self):
        # Arrange
        from scitex_writer.migration._parsing import classify_section
        content = r"\section{Introduction and Background}"
        # Act
        content = r"\section{Experimental Procedure}"
        # Act
        # Assert
        assert classify_section(Path("ch2.tex"), content) == "methods"


    def test_extract_metadata_meta_title_my_great_paper_and_meta_authors_block_a(self):
        # Arrange
        from scitex_writer.migration._parsing import extract_metadata

        content = r"""
\title{My Great Paper}
\author{Alice Bob}
\keywords{science, testing}
"""
        # Act
        meta = extract_metadata(content)
        # Assert
        assert (meta['title'] == 'My Great Paper') and (meta['authors_block'] == 'Alice Bob') and (meta['keywords'] == 'science, testing')

    def test_extract_metadata_empty(self):
        # Arrange
        from scitex_writer.migration._parsing import extract_metadata

        # Act
        meta = extract_metadata("No metadata here")
        # Assert
        assert (meta['title'] is None) and (meta['authors_block'] is None) and (meta['keywords'] is None)

    def test_split_inline_sections(self):
        # Arrange
        from scitex_writer.migration._parsing import split_inline_sections

        content = r"""
\section{Introduction}
Intro text.
\section{Methods}
Methods text.
\section{Conclusion}
Conclusion text.
"""
        # Act
        sections = split_inline_sections(content)
        # Assert
        assert ('introduction' in sections) and ('methods' in sections) and ('discussion' in sections)

    def test_unique_dest_unique_dest_f_f(self, tmp_path):
        # Arrange
        from scitex_writer.migration._parsing import unique_dest
        # Act
        f = tmp_path / "test.txt"
        # Act
        # Assert
        assert unique_dest(f) == f

    def test_unique_dest_result_name_equals_test_1_txt(self, tmp_path):
        # Arrange
        from scitex_writer.migration._parsing import unique_dest
        f = tmp_path / "test.txt"
        f.write_text("existing")
        # Act
        result = unique_dest(f)
        # Act
        # Assert
        assert result.name == "test_1.txt"



# ---------------------------------------------------------------------------
# Import tests
# ---------------------------------------------------------------------------


class TestImport:
    def test_import_dry_run_result_success_is_true_and_result_dry_run_is_true_and_mappin(self, simple_overleaf_zip, tmp_path):
        # Arrange
        from scitex_writer.migration import from_overleaf
        # Act
        result = from_overleaf(
            str(simple_overleaf_zip),
            output_dir=str(tmp_path / "output"),
            dry_run=True,
        )
        # Act
        # Assert
        assert (result['success'] is True) and (result['dry_run'] is True) and ('mapping_report' in result)

    def test_import_dry_run_report_main_tex_main_tex_and_introduction_in_report_sections(self, simple_overleaf_zip, tmp_path):
        # Arrange
        from scitex_writer.migration import from_overleaf
        result = from_overleaf(
            str(simple_overleaf_zip),
            output_dir=str(tmp_path / "output"),
            dry_run=True,
        )
        # Act
        report = result["mapping_report"]
        # Act
        # Assert
        assert (report['main_tex'] == 'main.tex') and ('introduction' in report['sections']) and (len(report['bib_files']) == 1) and (len(report['images']) >= 1)


    def test_import_nonexistent_zip(self):
        # Arrange
        from scitex_writer.migration import from_overleaf

        # Act
        result = from_overleaf("/nonexistent/file.zip")
        # Assert
        assert (result['success'] is False) and ('not found' in result['error'].lower())

    def test_import_invalid_zip(self, tmp_path):
        # Arrange
        from scitex_writer.migration import from_overleaf

        fake = tmp_path / "fake.zip"
        fake.write_text("not a zip")
        # Act
        result = from_overleaf(str(fake))
        # Assert
        assert (result['success'] is False) and ('not a valid zip' in result['error'].lower())

    def test_import_output_exists_no_force(self, simple_overleaf_zip, tmp_path):
        # Arrange
        from scitex_writer.migration import from_overleaf

        out = tmp_path / "existing"
        out.mkdir()
        # Act
        result = from_overleaf(str(simple_overleaf_zip), output_dir=str(out))
        # Assert
        assert (result['success'] is False) and ('already exists' in result['error'].lower())

    def test_import_inline_dry_run_result_success_is_true(self, inline_overleaf_zip, tmp_path):
        # Arrange
        from scitex_writer.migration import from_overleaf
        # Act
        result = from_overleaf(
            str(inline_overleaf_zip),
            output_dir=str(tmp_path / "inline_out"),
            dry_run=True,
        )
        # Act
        # Assert
        assert result["success"] is True

    def test_import_inline_dry_run_report_metadata_title_inline_paper(self, inline_overleaf_zip, tmp_path):
        # Arrange
        from scitex_writer.migration import from_overleaf
        result = from_overleaf(
            str(inline_overleaf_zip),
            output_dir=str(tmp_path / "inline_out"),
            dry_run=True,
        )
        # Act
        report = result["mapping_report"]
        # Act
        # Assert
        assert report["metadata"]["title"] == "Inline Paper"


    def test_import_success_creates_project_result_success_is_true_and_result_dry_run_is_false_and_out_e(self, simple_overleaf_zip, tmp_path):
        # Arrange
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
        # Act
        with patch(
            "scitex_writer._project._create.clone_writer_project",
            side_effect=fake_clone,
        ):
            result = from_overleaf(str(simple_overleaf_zip), output_dir=str(out))
        # Act
        # Assert
        assert (result['success'] is True) and (result['dry_run'] is False) and (out.exists())

    def test_import_success_creates_project_contents_introduction_tex_exists(self, simple_overleaf_zip, tmp_path):
        # Arrange
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
        # Sections were written
        # Act
        contents = out / "01_manuscript" / "contents"
        # Act
        # Assert
        assert (contents / "introduction.tex").exists()

    def test_import_success_creates_project_introduction_in_intro_text_lower(self, simple_overleaf_zip, tmp_path):
        # Arrange
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
        # Act
        with patch(
            "scitex_writer._project._create.clone_writer_project",
            side_effect=fake_clone,
        ):
            result = from_overleaf(str(simple_overleaf_zip), output_dir=str(out))
        # Assert
        assert (result['success'] is True) and (result['dry_run'] is False) and (out.exists())
        # Sections were written
        contents = out / "01_manuscript" / "contents"
        assert (contents / "introduction.tex").exists()
        intro_text = (contents / "introduction.tex").read_text()
        # Act
        # Assert
        assert "introduction" in intro_text.lower()

    def test_import_success_creates_project_len_bib_files_1(self, simple_overleaf_zip, tmp_path):
        # Arrange
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
        # Act
        with patch(
            "scitex_writer._project._create.clone_writer_project",
            side_effect=fake_clone,
        ):
            result = from_overleaf(str(simple_overleaf_zip), output_dir=str(out))
        # Assert
        assert (result['success'] is True) and (result['dry_run'] is False) and (out.exists())
        # Sections were written
        contents = out / "01_manuscript" / "contents"
        assert (contents / "introduction.tex").exists()
        intro_text = (contents / "introduction.tex").read_text()
        assert "introduction" in intro_text.lower()
        # Bib was copied
        bib_files = list((out / "00_shared" / "bib_files").glob("*.bib"))
        # Act
        # Assert
        assert len(bib_files) >= 1

    def test_import_success_creates_project_len_images_1_and_out_00_shared_title_tex_exists(self, simple_overleaf_zip, tmp_path):
        # Arrange
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
        # Act
        with patch(
            "scitex_writer._project._create.clone_writer_project",
            side_effect=fake_clone,
        ):
            result = from_overleaf(str(simple_overleaf_zip), output_dir=str(out))
        # Assert
        assert (result['success'] is True) and (result['dry_run'] is False) and (out.exists())
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
        # Act
        # Assert
        assert (len(images) >= 1) and ((out / '00_shared' / 'title.tex').exists())

    def test_import_success_creates_project_test_paper_title_in_title(self, simple_overleaf_zip, tmp_path):
        # Arrange
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
        # Act
        with patch(
            "scitex_writer._project._create.clone_writer_project",
            side_effect=fake_clone,
        ):
            result = from_overleaf(str(simple_overleaf_zip), output_dir=str(out))
        # Assert
        assert (result['success'] is True) and (result['dry_run'] is False) and (out.exists())
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
        assert (len(images) >= 1) and ((out / '00_shared' / 'title.tex').exists())
        title = (out / "00_shared" / "title.tex").read_text()
        # Act
        # Assert
        assert "Test Paper Title" in title


    def test_import_force_overwrites(self, simple_overleaf_zip, tmp_path):
        # Arrange
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

        # Act
        with patch(
            "scitex_writer._project._create.clone_writer_project",
            side_effect=fake_clone,
        ):
            result = from_overleaf(
                str(simple_overleaf_zip), output_dir=str(out), force=True
            )

        # Assert
        assert (result['success'] is True) and (not (out / 'marker.txt').exists())


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
        # Arrange
        from scitex_writer.migration import to_overleaf

        # Act
        result = to_overleaf("/nonexistent/project")
        # Assert
        assert result["success"] is False

    def test_export_not_a_project(self, tmp_path):
        # Arrange
        from scitex_writer.migration import to_overleaf

        # Act
        result = to_overleaf(str(tmp_path))
        # Assert
        assert (result['success'] is False) and ('does not look like' in result['error'].lower())

    def test_export_dry_run(self, mock_scitex_project):
        # Arrange
        from scitex_writer.migration import to_overleaf

        # Act
        result = to_overleaf(str(mock_scitex_project), dry_run=True)

        # Assert
        assert (result['success'] is True) and (result['dry_run'] is True) and (result['file_count'] > 0) and ('main.tex' in result['files_included']) and ('references.bib' in result['files_included'])

    def test_export_creates_zip(self, mock_scitex_project, tmp_path):
        # Arrange
        from scitex_writer.migration import to_overleaf

        zip_out = tmp_path / "export.zip"
        # Act
        result = to_overleaf(str(mock_scitex_project), output_path=str(zip_out))

        # Assert
        assert (result['success'] is True) and (result['dry_run'] is False) and (zip_out.exists())

        # Verify ZIP contents
        with zipfile.ZipFile(zip_out) as zf:
            names = zf.namelist()
            assert ('main.tex' in names) and ('references.bib' in names) and (any(('sections/' in n for n in names))) and (any(('images/' in n for n in names)))

            # main.tex has documentclass and title
            main_content = zf.read("main.tex").decode()
            assert ('\\documentclass' in main_content) and ('\\title{My Test Title}' in main_content)


# ---------------------------------------------------------------------------
# Module API tests
# ---------------------------------------------------------------------------


class TestModuleAPI:
    def test_migration_in_all(self):
        # Arrange
        # Act
        import scitex_writer as sw

        # Assert
        assert "migration" in sw.__all__

    def test_from_overleaf_callable(self):
        # Arrange
        # Act
        from scitex_writer import migration

        # Assert
        assert callable(migration.from_overleaf)

    def test_to_overleaf_callable(self):
        # Arrange
        # Act
        from scitex_writer import migration

        # Assert
        assert callable(migration.to_overleaf)

    def test_cli_help_result_returncode_equals_n_0_and_import_in_re(self):
        # Arrange
        import subprocess

        # Act
        result = subprocess.run(
            ["scitex-writer", "migration", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        # Assert
        assert (result.returncode == 0) and ('import' in result.stdout) and ('export' in result.stdout)


# EOF
