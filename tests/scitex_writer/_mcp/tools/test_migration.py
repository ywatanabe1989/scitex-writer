#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: tests/scitex_writer/_mcp/tools/test_migration.py

"""Tests for the migration module (Overleaf import/export).

Wave 2 cluster C cleanup: PA-306 no-mocks + PA-307 (TQ001/TQ002/TQ003/TQ007).
The `clone_writer_project` collaborator is replaced via a hand-rolled fake
swapped onto the production module's attribute (no `unittest.mock`,
no `pytest_mock`, no `monkeypatch`).
"""

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


def _make_fake_clone():
    """Build a hand-rolled fake `clone_writer_project` callable.

    The fake materialises the minimal scitex-writer directory layout the
    importer expects, so the production overlay code can run end-to-end
    against real `tmp_path` filesystem state.
    """

    def fake_clone(project_dir, git_strategy="child", **kwargs):
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

    return fake_clone


@pytest.fixture
def fake_clone_writer_project():
    """Swap `clone_writer_project` for the fake on the production module.

    Uses bare `setattr`+restore (no `monkeypatch`, no `unittest.mock`).
    """
    from scitex_writer._project import _create as create_mod

    original = create_mod.clone_writer_project
    create_mod.clone_writer_project = _make_fake_clone()
    try:
        yield
    finally:
        create_mod.clone_writer_project = original


# ---------------------------------------------------------------------------
# Parsing tests
# ---------------------------------------------------------------------------


class TestParsing:
    def test_detect_main_tex_returns_non_none_when_documentclass_present(
        self, tmp_path
    ):
        from scitex_writer.migration._parsing import detect_main_tex

        # Arrange
        (tmp_path / "main.tex").write_text(r"\documentclass{article}", encoding="utf-8")
        (tmp_path / "helper.tex").write_text(r"\section{Foo}", encoding="utf-8")

        # Act
        result = detect_main_tex(tmp_path)

        # Assert
        assert result is not None

    def test_detect_main_tex_returns_main_tex_filename(self, tmp_path):
        from scitex_writer.migration._parsing import detect_main_tex

        # Arrange
        (tmp_path / "main.tex").write_text(r"\documentclass{article}", encoding="utf-8")
        (tmp_path / "helper.tex").write_text(r"\section{Foo}", encoding="utf-8")

        # Act
        result = detect_main_tex(tmp_path)

        # Assert
        assert result.name == "main.tex"

    def test_detect_main_tex_no_documentclass(self, tmp_path):
        from scitex_writer.migration._parsing import detect_main_tex

        # Arrange
        (tmp_path / "notes.tex").write_text("Just some text", encoding="utf-8")

        # Act
        result = detect_main_tex(tmp_path)

        # Assert
        assert result is None

    def test_detect_main_tex_prefers_main(self, tmp_path):
        from scitex_writer.migration._parsing import detect_main_tex

        # Arrange
        (tmp_path / "main.tex").write_text(r"\documentclass{article}", encoding="utf-8")
        (tmp_path / "paper.tex").write_text(
            r"\documentclass{article}", encoding="utf-8"
        )

        # Act
        result = detect_main_tex(tmp_path)

        # Assert
        assert result.name == "main.tex"

    def test_classify_section_by_filename_intro(self):
        from scitex_writer.migration._parsing import classify_section

        # Arrange
        path = Path("intro.tex")

        # Act
        result = classify_section(path, "")

        # Assert
        assert result == "introduction"

    def test_classify_section_by_filename_methods(self):
        from scitex_writer.migration._parsing import classify_section

        # Arrange
        path = Path("methods.tex")

        # Act
        result = classify_section(path, "")

        # Assert
        assert result == "methods"

    def test_classify_section_by_filename_results(self):
        from scitex_writer.migration._parsing import classify_section

        # Arrange
        path = Path("results.tex")

        # Act
        result = classify_section(path, "")

        # Assert
        assert result == "results"

    def test_classify_section_by_filename_discussion(self):
        from scitex_writer.migration._parsing import classify_section

        # Arrange
        path = Path("discussion.tex")

        # Act
        result = classify_section(path, "")

        # Assert
        assert result == "discussion"

    def test_classify_section_by_filename_abstract(self):
        from scitex_writer.migration._parsing import classify_section

        # Arrange
        path = Path("abstract.tex")

        # Act
        result = classify_section(path, "")

        # Assert
        assert result == "abstract"

    def test_classify_section_by_filename_unknown_returns_none(self):
        from scitex_writer.migration._parsing import classify_section

        # Arrange
        path = Path("random.tex")

        # Act
        result = classify_section(path, "")

        # Assert
        assert result is None

    def test_classify_section_by_heading_introduction(self):
        from scitex_writer.migration._parsing import classify_section

        # Arrange
        content = r"\section{Introduction and Background}"

        # Act
        result = classify_section(Path("ch1.tex"), content)

        # Assert
        assert result == "introduction"

    def test_classify_section_by_heading_experimental_is_methods(self):
        from scitex_writer.migration._parsing import classify_section

        # Arrange
        content = r"\section{Experimental Procedure}"

        # Act
        result = classify_section(Path("ch2.tex"), content)

        # Assert
        assert result == "methods"

    def test_extract_metadata_returns_title(self):
        from scitex_writer.migration._parsing import extract_metadata

        # Arrange
        content = r"""
\title{My Great Paper}
\author{Alice Bob}
\keywords{science, testing}
"""

        # Act
        meta = extract_metadata(content)

        # Assert
        assert meta["title"] == "My Great Paper"

    def test_extract_metadata_returns_authors_block(self):
        from scitex_writer.migration._parsing import extract_metadata

        # Arrange
        content = r"""
\title{My Great Paper}
\author{Alice Bob}
\keywords{science, testing}
"""

        # Act
        meta = extract_metadata(content)

        # Assert
        assert meta["authors_block"] == "Alice Bob"

    def test_extract_metadata_returns_keywords(self):
        from scitex_writer.migration._parsing import extract_metadata

        # Arrange
        content = r"""
\title{My Great Paper}
\author{Alice Bob}
\keywords{science, testing}
"""

        # Act
        meta = extract_metadata(content)

        # Assert
        assert meta["keywords"] == "science, testing"

    def test_extract_metadata_empty_title_is_none(self):
        from scitex_writer.migration._parsing import extract_metadata

        # Arrange
        content = "No metadata here"

        # Act
        meta = extract_metadata(content)

        # Assert
        assert meta["title"] is None

    def test_extract_metadata_empty_authors_block_is_none(self):
        from scitex_writer.migration._parsing import extract_metadata

        # Arrange
        content = "No metadata here"

        # Act
        meta = extract_metadata(content)

        # Assert
        assert meta["authors_block"] is None

    def test_extract_metadata_empty_keywords_is_none(self):
        from scitex_writer.migration._parsing import extract_metadata

        # Arrange
        content = "No metadata here"

        # Act
        meta = extract_metadata(content)

        # Assert
        assert meta["keywords"] is None

    def test_split_inline_sections_includes_introduction(self):
        from scitex_writer.migration._parsing import split_inline_sections

        # Arrange
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
        assert "introduction" in sections

    def test_split_inline_sections_includes_methods(self):
        from scitex_writer.migration._parsing import split_inline_sections

        # Arrange
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
        assert "methods" in sections

    def test_split_inline_sections_maps_conclusion_to_discussion(self):
        from scitex_writer.migration._parsing import split_inline_sections

        # Arrange
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
        assert "discussion" in sections

    def test_unique_dest_returns_unchanged_when_not_taken(self, tmp_path):
        from scitex_writer.migration._parsing import unique_dest

        # Arrange
        f = tmp_path / "test.txt"

        # Act
        result = unique_dest(f)

        # Assert
        assert result == f

    def test_unique_dest_appends_suffix_when_already_exists(self, tmp_path):
        from scitex_writer.migration._parsing import unique_dest

        # Arrange
        f = tmp_path / "test.txt"
        f.write_text("existing")

        # Act
        result = unique_dest(f)

        # Assert
        assert result.name == "test_1.txt"


# ---------------------------------------------------------------------------
# Import tests
# ---------------------------------------------------------------------------


class TestImport:
    def test_import_dry_run_reports_success(self, simple_overleaf_zip, tmp_path):
        from scitex_writer.migration import from_overleaf

        # Arrange
        output_dir = str(tmp_path / "output")

        # Act
        result = from_overleaf(
            str(simple_overleaf_zip), output_dir=output_dir, dry_run=True
        )

        # Assert
        assert result["success"] is True

    def test_import_dry_run_flag_propagates_to_result(
        self, simple_overleaf_zip, tmp_path
    ):
        from scitex_writer.migration import from_overleaf

        # Arrange
        output_dir = str(tmp_path / "output")

        # Act
        result = from_overleaf(
            str(simple_overleaf_zip), output_dir=output_dir, dry_run=True
        )

        # Assert
        assert result["dry_run"] is True

    def test_import_dry_run_includes_mapping_report(
        self, simple_overleaf_zip, tmp_path
    ):
        from scitex_writer.migration import from_overleaf

        # Arrange
        output_dir = str(tmp_path / "output")

        # Act
        result = from_overleaf(
            str(simple_overleaf_zip), output_dir=output_dir, dry_run=True
        )

        # Assert
        assert "mapping_report" in result

    def test_import_dry_run_mapping_report_records_main_tex(
        self, simple_overleaf_zip, tmp_path
    ):
        from scitex_writer.migration import from_overleaf

        # Arrange
        output_dir = str(tmp_path / "output")

        # Act
        result = from_overleaf(
            str(simple_overleaf_zip), output_dir=output_dir, dry_run=True
        )

        # Assert
        assert result["mapping_report"]["main_tex"] == "main.tex"

    def test_import_dry_run_mapping_report_classifies_introduction(
        self, simple_overleaf_zip, tmp_path
    ):
        from scitex_writer.migration import from_overleaf

        # Arrange
        output_dir = str(tmp_path / "output")

        # Act
        result = from_overleaf(
            str(simple_overleaf_zip), output_dir=output_dir, dry_run=True
        )

        # Assert
        assert "introduction" in result["mapping_report"]["sections"]

    def test_import_dry_run_mapping_report_lists_bib_file(
        self, simple_overleaf_zip, tmp_path
    ):
        from scitex_writer.migration import from_overleaf

        # Arrange
        output_dir = str(tmp_path / "output")

        # Act
        result = from_overleaf(
            str(simple_overleaf_zip), output_dir=output_dir, dry_run=True
        )

        # Assert
        assert len(result["mapping_report"]["bib_files"]) == 1

    def test_import_dry_run_mapping_report_lists_image(
        self, simple_overleaf_zip, tmp_path
    ):
        from scitex_writer.migration import from_overleaf

        # Arrange
        output_dir = str(tmp_path / "output")

        # Act
        result = from_overleaf(
            str(simple_overleaf_zip), output_dir=output_dir, dry_run=True
        )

        # Assert
        assert len(result["mapping_report"]["images"]) >= 1

    def test_import_nonexistent_zip_reports_failure(self):
        from scitex_writer.migration import from_overleaf

        # Arrange
        missing_path = "/nonexistent/file.zip"

        # Act
        result = from_overleaf(missing_path)

        # Assert
        assert result["success"] is False

    def test_import_nonexistent_zip_error_mentions_not_found(self):
        from scitex_writer.migration import from_overleaf

        # Arrange
        missing_path = "/nonexistent/file.zip"

        # Act
        result = from_overleaf(missing_path)

        # Assert
        assert "not found" in result["error"].lower()

    def test_import_invalid_zip_reports_failure(self, tmp_path):
        from scitex_writer.migration import from_overleaf

        # Arrange
        fake = tmp_path / "fake.zip"
        fake.write_text("not a zip")

        # Act
        result = from_overleaf(str(fake))

        # Assert
        assert result["success"] is False

    def test_import_invalid_zip_error_mentions_not_a_valid_zip(self, tmp_path):
        from scitex_writer.migration import from_overleaf

        # Arrange
        fake = tmp_path / "fake.zip"
        fake.write_text("not a zip")

        # Act
        result = from_overleaf(str(fake))

        # Assert
        assert "not a valid zip" in result["error"].lower()

    def test_import_output_exists_no_force_reports_failure(
        self, simple_overleaf_zip, tmp_path
    ):
        from scitex_writer.migration import from_overleaf

        # Arrange
        out = tmp_path / "existing"
        out.mkdir()

        # Act
        result = from_overleaf(str(simple_overleaf_zip), output_dir=str(out))

        # Assert
        assert result["success"] is False

    def test_import_output_exists_no_force_error_mentions_already_exists(
        self, simple_overleaf_zip, tmp_path
    ):
        from scitex_writer.migration import from_overleaf

        # Arrange
        out = tmp_path / "existing"
        out.mkdir()

        # Act
        result = from_overleaf(str(simple_overleaf_zip), output_dir=str(out))

        # Assert
        assert "already exists" in result["error"].lower()

    def test_import_inline_dry_run_reports_success(self, inline_overleaf_zip, tmp_path):
        from scitex_writer.migration import from_overleaf

        # Arrange
        output_dir = str(tmp_path / "inline_out")

        # Act
        result = from_overleaf(
            str(inline_overleaf_zip), output_dir=output_dir, dry_run=True
        )

        # Assert
        assert result["success"] is True

    def test_import_inline_dry_run_metadata_title_is_extracted(
        self, inline_overleaf_zip, tmp_path
    ):
        from scitex_writer.migration import from_overleaf

        # Arrange
        output_dir = str(tmp_path / "inline_out")

        # Act
        result = from_overleaf(
            str(inline_overleaf_zip), output_dir=output_dir, dry_run=True
        )

        # Assert
        assert result["mapping_report"]["metadata"]["title"] == "Inline Paper"

    def test_import_success_creates_project_reports_success(
        self, simple_overleaf_zip, tmp_path, fake_clone_writer_project
    ):
        from scitex_writer.migration import from_overleaf

        # Arrange
        out = tmp_path / "imported_project"

        # Act
        result = from_overleaf(str(simple_overleaf_zip), output_dir=str(out))

        # Assert
        assert result["success"] is True

    def test_import_success_creates_project_dry_run_flag_false(
        self, simple_overleaf_zip, tmp_path, fake_clone_writer_project
    ):
        from scitex_writer.migration import from_overleaf

        # Arrange
        out = tmp_path / "imported_project"

        # Act
        result = from_overleaf(str(simple_overleaf_zip), output_dir=str(out))

        # Assert
        assert result["dry_run"] is False

    def test_import_success_creates_output_directory(
        self, simple_overleaf_zip, tmp_path, fake_clone_writer_project
    ):
        from scitex_writer.migration import from_overleaf

        # Arrange
        out = tmp_path / "imported_project"

        # Act
        from_overleaf(str(simple_overleaf_zip), output_dir=str(out))

        # Assert
        assert out.exists()

    def test_import_success_writes_introduction_section(
        self, simple_overleaf_zip, tmp_path, fake_clone_writer_project
    ):
        from scitex_writer.migration import from_overleaf

        # Arrange
        out = tmp_path / "imported_project"

        # Act
        from_overleaf(str(simple_overleaf_zip), output_dir=str(out))

        # Assert
        assert (out / "01_manuscript" / "contents" / "introduction.tex").exists()

    def test_import_success_introduction_section_content_contains_keyword(
        self, simple_overleaf_zip, tmp_path, fake_clone_writer_project
    ):
        from scitex_writer.migration import from_overleaf

        # Arrange
        out = tmp_path / "imported_project"

        # Act
        from_overleaf(str(simple_overleaf_zip), output_dir=str(out))

        # Assert
        intro_text = (
            out / "01_manuscript" / "contents" / "introduction.tex"
        ).read_text()
        assert "introduction" in intro_text.lower()

    def test_import_success_copies_bib_file(
        self, simple_overleaf_zip, tmp_path, fake_clone_writer_project
    ):
        from scitex_writer.migration import from_overleaf

        # Arrange
        out = tmp_path / "imported_project"

        # Act
        from_overleaf(str(simple_overleaf_zip), output_dir=str(out))

        # Assert
        bib_files = list((out / "00_shared" / "bib_files").glob("*.bib"))
        assert len(bib_files) >= 1

    def test_import_success_copies_image(
        self, simple_overleaf_zip, tmp_path, fake_clone_writer_project
    ):
        from scitex_writer.migration import from_overleaf

        # Arrange
        out = tmp_path / "imported_project"

        # Act
        from_overleaf(str(simple_overleaf_zip), output_dir=str(out))

        # Assert
        images = list(
            (out / "01_manuscript" / "contents" / "figures" / "caption_and_media").glob(
                "*"
            )
        )
        assert len(images) >= 1

    def test_import_success_writes_title_file(
        self, simple_overleaf_zip, tmp_path, fake_clone_writer_project
    ):
        from scitex_writer.migration import from_overleaf

        # Arrange
        out = tmp_path / "imported_project"

        # Act
        from_overleaf(str(simple_overleaf_zip), output_dir=str(out))

        # Assert
        assert (out / "00_shared" / "title.tex").exists()

    def test_import_success_title_file_contains_paper_title(
        self, simple_overleaf_zip, tmp_path, fake_clone_writer_project
    ):
        from scitex_writer.migration import from_overleaf

        # Arrange
        out = tmp_path / "imported_project"

        # Act
        from_overleaf(str(simple_overleaf_zip), output_dir=str(out))

        # Assert
        title = (out / "00_shared" / "title.tex").read_text()
        assert "Test Paper Title" in title

    def test_import_force_overwrites_reports_success(
        self, simple_overleaf_zip, tmp_path, fake_clone_writer_project
    ):
        from scitex_writer.migration import from_overleaf

        # Arrange
        out = tmp_path / "force_project"
        out.mkdir()
        (out / "marker.txt").write_text("old")

        # Act
        result = from_overleaf(
            str(simple_overleaf_zip), output_dir=str(out), force=True
        )

        # Assert
        assert result["success"] is True

    def test_import_force_overwrites_removes_old_marker_file(
        self, simple_overleaf_zip, tmp_path, fake_clone_writer_project
    ):
        from scitex_writer.migration import from_overleaf

        # Arrange
        out = tmp_path / "force_project"
        out.mkdir()
        (out / "marker.txt").write_text("old")

        # Act
        from_overleaf(str(simple_overleaf_zip), output_dir=str(out), force=True)

        # Assert
        assert not (out / "marker.txt").exists()


# ---------------------------------------------------------------------------
# Export tests
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_scitex_project(tmp_path):
    """Create a minimal scitex-writer project structure for export testing.

    Note: the fixture name is historical; nothing here uses mocking. It builds
    a real on-disk project layout under `tmp_path`.
    """
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
    def test_export_nonexistent_project_reports_failure(self):
        from scitex_writer.migration import to_overleaf

        # Arrange
        missing_path = "/nonexistent/project"

        # Act
        result = to_overleaf(missing_path)

        # Assert
        assert result["success"] is False

    def test_export_not_a_project_reports_failure(self, tmp_path):
        from scitex_writer.migration import to_overleaf

        # Arrange
        bare_dir = str(tmp_path)

        # Act
        result = to_overleaf(bare_dir)

        # Assert
        assert result["success"] is False

    def test_export_not_a_project_error_mentions_does_not_look_like(self, tmp_path):
        from scitex_writer.migration import to_overleaf

        # Arrange
        bare_dir = str(tmp_path)

        # Act
        result = to_overleaf(bare_dir)

        # Assert
        assert "does not look like" in result["error"].lower()

    def test_export_dry_run_reports_success(self, mock_scitex_project):
        from scitex_writer.migration import to_overleaf

        # Arrange
        project_dir = str(mock_scitex_project)

        # Act
        result = to_overleaf(project_dir, dry_run=True)

        # Assert
        assert result["success"] is True

    def test_export_dry_run_flag_propagates_to_result(self, mock_scitex_project):
        from scitex_writer.migration import to_overleaf

        # Arrange
        project_dir = str(mock_scitex_project)

        # Act
        result = to_overleaf(project_dir, dry_run=True)

        # Assert
        assert result["dry_run"] is True

    def test_export_dry_run_reports_positive_file_count(self, mock_scitex_project):
        from scitex_writer.migration import to_overleaf

        # Arrange
        project_dir = str(mock_scitex_project)

        # Act
        result = to_overleaf(project_dir, dry_run=True)

        # Assert
        assert result["file_count"] > 0

    def test_export_dry_run_includes_main_tex_in_files_included(
        self, mock_scitex_project
    ):
        from scitex_writer.migration import to_overleaf

        # Arrange
        project_dir = str(mock_scitex_project)

        # Act
        result = to_overleaf(project_dir, dry_run=True)

        # Assert
        assert "main.tex" in result["files_included"]

    def test_export_dry_run_includes_references_bib_in_files_included(
        self, mock_scitex_project
    ):
        from scitex_writer.migration import to_overleaf

        # Arrange
        project_dir = str(mock_scitex_project)

        # Act
        result = to_overleaf(project_dir, dry_run=True)

        # Assert
        assert "references.bib" in result["files_included"]

    def test_export_creates_zip_reports_success(self, mock_scitex_project, tmp_path):
        from scitex_writer.migration import to_overleaf

        # Arrange
        zip_out = tmp_path / "export.zip"

        # Act
        result = to_overleaf(str(mock_scitex_project), output_path=str(zip_out))

        # Assert
        assert result["success"] is True

    def test_export_creates_zip_dry_run_flag_false(self, mock_scitex_project, tmp_path):
        from scitex_writer.migration import to_overleaf

        # Arrange
        zip_out = tmp_path / "export.zip"

        # Act
        result = to_overleaf(str(mock_scitex_project), output_path=str(zip_out))

        # Assert
        assert result["dry_run"] is False

    def test_export_creates_zip_file_on_disk(self, mock_scitex_project, tmp_path):
        from scitex_writer.migration import to_overleaf

        # Arrange
        zip_out = tmp_path / "export.zip"

        # Act
        to_overleaf(str(mock_scitex_project), output_path=str(zip_out))

        # Assert
        assert zip_out.exists()

    def test_export_creates_zip_contains_main_tex(self, mock_scitex_project, tmp_path):
        from scitex_writer.migration import to_overleaf

        # Arrange
        zip_out = tmp_path / "export.zip"

        # Act
        to_overleaf(str(mock_scitex_project), output_path=str(zip_out))

        # Assert
        with zipfile.ZipFile(zip_out) as zf:
            assert "main.tex" in zf.namelist()

    def test_export_creates_zip_contains_references_bib(
        self, mock_scitex_project, tmp_path
    ):
        from scitex_writer.migration import to_overleaf

        # Arrange
        zip_out = tmp_path / "export.zip"

        # Act
        to_overleaf(str(mock_scitex_project), output_path=str(zip_out))

        # Assert
        with zipfile.ZipFile(zip_out) as zf:
            assert "references.bib" in zf.namelist()

    def test_export_creates_zip_contains_sections_dir(
        self, mock_scitex_project, tmp_path
    ):
        from scitex_writer.migration import to_overleaf

        # Arrange
        zip_out = tmp_path / "export.zip"

        # Act
        to_overleaf(str(mock_scitex_project), output_path=str(zip_out))

        # Assert
        with zipfile.ZipFile(zip_out) as zf:
            assert any("sections/" in n for n in zf.namelist())

    def test_export_creates_zip_contains_images_dir(
        self, mock_scitex_project, tmp_path
    ):
        from scitex_writer.migration import to_overleaf

        # Arrange
        zip_out = tmp_path / "export.zip"

        # Act
        to_overleaf(str(mock_scitex_project), output_path=str(zip_out))

        # Assert
        with zipfile.ZipFile(zip_out) as zf:
            assert any("images/" in n for n in zf.namelist())

    def test_export_creates_zip_main_tex_has_documentclass(
        self, mock_scitex_project, tmp_path
    ):
        from scitex_writer.migration import to_overleaf

        # Arrange
        zip_out = tmp_path / "export.zip"

        # Act
        to_overleaf(str(mock_scitex_project), output_path=str(zip_out))

        # Assert
        with zipfile.ZipFile(zip_out) as zf:
            main_content = zf.read("main.tex").decode()
            assert r"\documentclass" in main_content

    def test_export_creates_zip_main_tex_has_title(self, mock_scitex_project, tmp_path):
        from scitex_writer.migration import to_overleaf

        # Arrange
        zip_out = tmp_path / "export.zip"

        # Act
        to_overleaf(str(mock_scitex_project), output_path=str(zip_out))

        # Assert
        with zipfile.ZipFile(zip_out) as zf:
            main_content = zf.read("main.tex").decode()
            assert r"\title{My Test Title}" in main_content


# ---------------------------------------------------------------------------
# Module API tests
# ---------------------------------------------------------------------------


class TestModuleAPI:
    def test_migration_in_package_all(self):
        import scitex_writer as sw

        # Arrange
        all_names = sw.__all__

        # Act
        present = "migration" in all_names

        # Assert
        assert present is True

    def test_from_overleaf_is_callable(self):
        from scitex_writer import migration

        # Arrange
        target = migration.from_overleaf

        # Act
        is_callable = callable(target)

        # Assert
        assert is_callable is True

    def test_to_overleaf_is_callable(self):
        from scitex_writer import migration

        # Arrange
        target = migration.to_overleaf

        # Act
        is_callable = callable(target)

        # Assert
        assert is_callable is True

    def test_cli_migration_help_exits_zero(self):
        import subprocess

        # Arrange
        cmd = ["scitex-writer", "migration", "--help"]

        # Act
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

        # Assert
        assert result.returncode == 0

    def test_cli_migration_help_mentions_import(self):
        import subprocess

        # Arrange
        cmd = ["scitex-writer", "migration", "--help"]

        # Act
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

        # Assert
        assert "import" in result.stdout

    def test_cli_migration_help_mentions_export(self):
        import subprocess

        # Arrange
        cmd = ["scitex-writer", "migration", "--help"]

        # Act
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

        # Assert
        assert "export" in result.stdout


# EOF
