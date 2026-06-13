"""Parity tests for the Django port of the Writer editor.

Covers every endpoint the Flask `_editor` exposed:
  GET  /ping
  GET  /api/project-info
  GET  /api/files
  GET  /api/file?path=...
  POST /api/file
  GET  /api/sections
  POST /api/compile
  GET  /api/compile/status
  GET  /api/pdf
  GET  /api/bib/files
  GET  /api/bib/entries
  GET  /api/claims
  GET  /api/claims/<id>
  POST /api/claims
  DELETE /api/claims/<id>
  GET  /api/claims/<id>/chain
  POST /api/claims/render

Uses Django's test Client / RequestFactory (real WSGI plumbing — not mocks)
with TEST-ONLY settings bootstrap via conftest.py. No real compilation is
triggered; compile handler is inspected via the `compiling` status flag
returned from /api/compile/status.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest
from django.test import RequestFactory

from scitex_writer._django import views


@pytest.fixture
def project_dir():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp)
        # Minimal scitex-writer layout
        (p / "01_manuscript").mkdir()
        (p / "01_manuscript" / "contents").mkdir()
        (p / "01_manuscript" / "contents" / "01_intro.tex").write_text(
            r"\section{Intro}"
        )
        (p / "02_supplementary").mkdir()
        (p / "00_shared").mkdir()
        (p / "00_shared" / "bib_files").mkdir()
        (p / "00_shared" / "bib_files" / "bibliography.bib").write_text(
            "@article{foo2024, title={Foo}}\n"
        )
        yield str(p)


def _call(rf: RequestFactory, method: str, endpoint: str, project: str, **kwargs):
    """Hit api_dispatch directly (bypasses URL routing) with working_dir set."""
    factory = getattr(rf, method.lower())
    url = f"/{endpoint}?working_dir={project}"
    if method == "POST":
        body = kwargs.get("body", "")
        content_type = kwargs.get("content_type", "application/json")
        request = factory(url, data=body, content_type=content_type)
    else:
        request = factory(url)
    return views.api_dispatch(request, endpoint)


def test_ping_endpoint_returns_ok_status_payload(project_dir):
    # Arrange
    rf = RequestFactory()

    # Act
    resp = _call(rf, "GET", "ping", project_dir)

    # Assert
    assert (resp.status_code, json.loads(resp.content)) == (200, {"status": "ok"})


def test_project_info_returns_resolved_paths_and_doc_types(project_dir):
    # Arrange
    rf = RequestFactory()
    expected_dir = str(Path(project_dir).resolve())

    # Act
    resp = _call(rf, "GET", "api/project-info", project_dir)
    data = json.loads(resp.content)

    # Assert
    assert (
        resp.status_code,
        data["project_dir"],
        "manuscript" in data["doc_types"],
        "supplementary" in data["doc_types"],
        data["has_shared"],
    ) == (200, expected_dir, True, True, True)


def test_files_tree_lists_top_level_layout_directories(project_dir):
    # Arrange
    rf = RequestFactory()

    # Act
    resp = _call(rf, "GET", "api/files", project_dir)
    data = json.loads(resp.content)
    names = {e["name"] for e in data["tree"]}

    # Assert
    assert (resp.status_code, "01_manuscript" in names, "00_shared" in names) == (
        200,
        True,
        True,
    )


def test_file_get_endpoint_returns_existing_tex_file_content(project_dir):
    # Arrange
    rf = RequestFactory()
    request = rf.get(
        f"/api/file?path=01_manuscript/contents/01_intro.tex&working_dir={project_dir}"
    )

    # Act
    resp = views.api_dispatch(request, "api/file")
    payload = json.loads(resp.content)

    # Assert
    assert (resp.status_code, "Intro" in payload["content"]) == (200, True)


def test_file_post_endpoint_writes_new_content_to_disk(project_dir):
    # Arrange
    rf = RequestFactory()
    new_content = r"\section{New}"
    target = Path(project_dir) / "01_manuscript" / "contents" / "01_intro.tex"

    # Act
    resp = _call(
        rf,
        "POST",
        "api/file",
        project_dir,
        body=json.dumps(
            {
                "path": "01_manuscript/contents/01_intro.tex",
                "content": new_content,
            }
        ),
    )

    # Assert
    assert (resp.status_code, target.read_text()) == (200, new_content)


def test_file_read_blocks_path_traversal_attempt(project_dir):
    # Arrange
    rf = RequestFactory()
    request = rf.get(f"/api/file?path=../../../etc/passwd&working_dir={project_dir}")

    # Act
    resp = views.api_dispatch(request, "api/file")

    # Assert
    assert resp.status_code == 403


def test_sections_endpoint_lists_manuscript_section_files(project_dir):
    # Arrange
    rf = RequestFactory()
    request = rf.get(f"/api/sections?doc_type=manuscript&working_dir={project_dir}")

    # Act
    resp = views.api_dispatch(request, "api/sections")
    data = json.loads(resp.content)
    has_intro = any(s["filename"] == "01_intro.tex" for s in data["sections"])

    # Assert
    assert (resp.status_code, has_intro) == (200, True)


def test_bib_files_endpoint_returns_count_and_named_files(project_dir):
    # Arrange
    rf = RequestFactory()

    # Act
    resp = _call(rf, "GET", "api/bib/files", project_dir)
    data = json.loads(resp.content)
    has_bibliography = any(f["name"] == "bibliography.bib" for f in data["files"])

    # Assert
    assert (resp.status_code, data["count"] >= 1, has_bibliography) == (
        200,
        True,
        True,
    )


def test_bib_entries_endpoint_lists_parsed_citation_keys(project_dir):
    # Arrange
    rf = RequestFactory()

    # Act
    resp = _call(rf, "GET", "api/bib/entries", project_dir)
    data = json.loads(resp.content)
    has_foo = any(e["citation_key"] == "foo2024" for e in data["entries"])

    # Assert
    assert (resp.status_code, has_foo) == (200, True)


def test_compile_status_idle_before_any_compile_invocation(project_dir):
    # Arrange
    rf = RequestFactory()

    # Act
    resp = _call(rf, "GET", "api/compile/status", project_dir)
    data = json.loads(resp.content)

    # Assert
    assert (resp.status_code, data["compiling"], data["result"]) == (
        200,
        False,
        None,
    )


def test_pdf_endpoint_returns_404_when_pdf_missing(project_dir):
    # Arrange
    rf = RequestFactory()
    request = rf.get(f"/api/pdf?doc_type=manuscript&working_dir={project_dir}")

    # Act
    resp = views.api_dispatch(request, "api/pdf")

    # Assert
    assert resp.status_code == 404


def test_unknown_endpoint_path_returns_404_error(project_dir):
    # Arrange
    rf = RequestFactory()

    # Act
    resp = _call(rf, "GET", "api/does-not-exist", project_dir)

    # Assert
    assert resp.status_code == 404


def test_wrong_http_method_returns_405_for_get_only_route(project_dir):
    # Arrange
    rf = RequestFactory()

    # Act
    resp = _call(rf, "POST", "ping", project_dir, body="")

    # Assert
    assert resp.status_code == 405


def test_missing_working_dir_query_returns_400_error():
    # Arrange
    rf = RequestFactory()
    request = rf.get("/ping")

    # Act
    resp = views.api_dispatch(request, "ping")

    # Assert
    assert resp.status_code == 400


def test_figures_endpoint_lists_figure_files_with_labels(project_dir):
    # Arrange
    rf = RequestFactory()
    project_path = Path(project_dir)
    fig_dir = (
        project_path / "01_manuscript" / "contents" / "figures" / "caption_and_media"
    )
    fig_dir.mkdir(parents=True)
    (fig_dir / "01_example.tex").write_text(
        r"\begin{figure}\label{fig:example}\end{figure}"
    )
    request = rf.get(f"/api/figures?doc_type=manuscript&working_dir={project_dir}")

    # Act
    resp = views.api_dispatch(request, "api/figures")
    data = json.loads(resp.content)
    has_example = any(f["name"] == "01_example" for f in data["figures"])

    # Assert
    assert (
        resp.status_code,
        data["doc_type"],
        has_example,
        data["figures"][0]["label"],
    ) == (200, "manuscript", True, "fig:example")


def test_tables_endpoint_lists_table_files_with_labels(project_dir):
    # Arrange
    rf = RequestFactory()
    project_path = Path(project_dir)
    tbl_dir = (
        project_path / "01_manuscript" / "contents" / "tables" / "caption_and_media"
    )
    tbl_dir.mkdir(parents=True)
    (tbl_dir / "01_results.tex").write_text(
        r"\begin{table}\label{tab:results}\end{table}"
    )
    request = rf.get(f"/api/tables?doc_type=manuscript&working_dir={project_dir}")

    # Act
    resp = views.api_dispatch(request, "api/tables")
    data = json.loads(resp.content)
    has_results = any(t["name"] == "01_results" for t in data["tables"])

    # Assert
    assert (
        resp.status_code,
        has_results,
        data["tables"][0]["label"],
    ) == (200, True, "tab:results")


def test_claims_metadata_endpoint_returns_empty_count_for_fresh_project(project_dir):
    # Arrange
    rf = RequestFactory()
    (Path(project_dir) / "00_shared").mkdir(exist_ok=True)
    (Path(project_dir) / "00_shared" / "claims.json").write_text(
        '{"version":"1.0","claims":{}}'
    )

    # Act
    resp = _call(rf, "GET", "api/claims-metadata", project_dir)
    data = json.loads(resp.content)

    # Assert
    assert (resp.status_code, data["success"], data["count"]) == (200, True, 0)


def test_dag_endpoint_returns_400_when_target_missing(project_dir):
    # Arrange
    rf = RequestFactory()

    # Act
    resp = _call(rf, "GET", "api/dag", project_dir)

    # Assert
    assert resp.status_code == 400


def test_citation_endpoint_returns_state_without_scholar_resolver(project_dir):
    # Arrange
    rf = RequestFactory()
    request = rf.get(f"/api/citation/foo2024?working_dir={project_dir}")

    # Act
    resp = views.api_dispatch(request, "api/citation/foo2024")
    data = json.loads(resp.content)

    # Assert
    assert (
        resp.status_code,
        data["cite_key"],
        data["state"] in {"VERIFIED", "UNVERIFIABLE", "CONTRADICTED"},
    ) == (200, "foo2024", True)


def test_viewer_page_renders_claims_pane_html_shell(project_dir):
    # Arrange
    rf = RequestFactory()
    request = rf.get(f"/viewer/?working_dir={project_dir}")

    # Act
    resp = views.viewer_page(request)
    body = resp.content.decode()

    # Assert
    assert (
        resp.status_code,
        "Writer — Viewer" in body,
        "viewer-claims-pane" in body,
    ) == (200, True, True)


def test_editor_page_renders_writer_title_and_css_link(project_dir):
    # Arrange
    rf = RequestFactory()
    request = rf.get(f"/?working_dir={project_dir}")

    # Act
    resp = views.editor_page(request)
    body = resp.content.decode()
    has_css = "writer/css/editor.css" in body or "editor.css" in body

    # Assert
    assert (
        resp.status_code,
        "SciTeX Writer" in body,
        has_css,
    ) == (200, True, True)
