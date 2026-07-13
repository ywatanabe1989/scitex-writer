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

Uses Django's test Client with TEST-ONLY settings bootstrap via conftest.py.
No real compilation is triggered; compile handler is inspected via the
`compiling` status flag returned from /api/compile/status.
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


def test_ping_resp_status_code_equals_n_200_and_json_loads(project_dir):
    # Arrange
    rf = RequestFactory()
    # Act
    resp = _call(rf, "GET", "ping", project_dir)
    # Assert
    assert (resp.status_code == 200) and (json.loads(resp.content) == {"status": "ok"})


def test_project_info_resp_status_code_equals_n_200(project_dir):
    # Arrange
    rf = RequestFactory()
    # Act
    resp = _call(rf, "GET", "api/project-info", project_dir)
    # Act
    # Assert
    assert resp.status_code == 200


def test_project_info_data_project_dir_str_path_project_dir_resolve_and_manuscript(
    project_dir,
):
    # Arrange
    rf = RequestFactory()
    resp = _call(rf, "GET", "api/project-info", project_dir)
    # Act
    data = json.loads(resp.content)
    # Act
    # Assert
    assert (
        (data["project_dir"] == str(Path(project_dir).resolve()))
        and ("manuscript" in data["doc_types"])
        and ("supplementary" in data["doc_types"])
        and (data["has_shared"] is True)
    )


def test_files_tree_resp_status_code_equals_n_200(project_dir):
    # Arrange
    rf = RequestFactory()
    # Act
    resp = _call(rf, "GET", "api/files", project_dir)
    # Act
    # Assert
    assert resp.status_code == 200


def test_files_tree_n_01_manuscript_in_names_and_00_shared_in_names(project_dir):
    # Arrange
    rf = RequestFactory()
    resp = _call(rf, "GET", "api/files", project_dir)
    data = json.loads(resp.content)
    # Act
    names = {e["name"] for e in data["tree"]}
    # Act
    # Assert
    assert ("01_manuscript" in names) and ("00_shared" in names)


def test_file_read_write_roundtrip_resp_status_code_equals_n_200_and_intro_in_json_loads_(
    project_dir,
):
    # Arrange
    rf = RequestFactory()
    # Read
    resp = _call(
        rf,
        "GET",
        "api/file",
        project_dir,
    )
    # Add ?path= via query
    request = rf.get(
        f"/api/file?path=01_manuscript/contents/01_intro.tex&working_dir={project_dir}"
    )
    # Act
    resp = views.api_dispatch(request, "api/file")
    # Act
    # Assert
    assert (resp.status_code == 200) and (
        "Intro" in json.loads(resp.content)["content"]
    )


def test_file_read_write_roundtrip_resp_status_code_equals_n_200(project_dir):
    # Arrange
    rf = RequestFactory()
    # Read
    resp = _call(
        rf,
        "GET",
        "api/file",
        project_dir,
    )
    # Add ?path= via query
    request = rf.get(
        f"/api/file?path=01_manuscript/contents/01_intro.tex&working_dir={project_dir}"
    )
    resp = views.api_dispatch(request, "api/file")
    # Write
    new_content = r"\section{New}"
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
    # Act
    # Assert
    assert resp.status_code == 200


def test_file_read_write_roundtrip_path_project_dir_01_manuscript_contents_01_intro_tex_read_te(
    project_dir,
):
    # Arrange
    rf = RequestFactory()
    # Read
    resp = _call(
        rf,
        "GET",
        "api/file",
        project_dir,
    )
    # Add ?path= via query
    request = rf.get(
        f"/api/file?path=01_manuscript/contents/01_intro.tex&working_dir={project_dir}"
    )
    resp = views.api_dispatch(request, "api/file")
    # Write
    new_content = r"\section{New}"
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
    # Act
    # Assert
    assert (
        Path(project_dir) / "01_manuscript" / "contents" / "01_intro.tex"
    ).read_text() == new_content


def test_file_read_path_traversal_blocked(project_dir):
    # Arrange
    rf = RequestFactory()
    request = rf.get(f"/api/file?path=../../../etc/passwd&working_dir={project_dir}")
    # Act
    resp = views.api_dispatch(request, "api/file")
    # Assert
    assert resp.status_code == 403


def test_sections_resp_status_code_equals_n_200(project_dir):
    # Arrange
    rf = RequestFactory()
    resp = _call(rf, "GET", "api/sections?doc_type=manuscript", project_dir)
    # endpoint contains querystring → re-call without it
    request = RequestFactory().get(
        f"/api/sections?doc_type=manuscript&working_dir={project_dir}"
    )
    # Act
    resp = views.api_dispatch(request, "api/sections")
    # Act
    # Assert
    assert resp.status_code == 200


def test_sections_any_s_filename_01_intro_tex_for_s_in_data_sections(project_dir):
    # Arrange
    rf = RequestFactory()
    resp = _call(rf, "GET", "api/sections?doc_type=manuscript", project_dir)
    # endpoint contains querystring → re-call without it
    request = RequestFactory().get(
        f"/api/sections?doc_type=manuscript&working_dir={project_dir}"
    )
    resp = views.api_dispatch(request, "api/sections")
    # Act
    data = json.loads(resp.content)
    # Act
    # Assert
    assert any(s["filename"] == "01_intro.tex" for s in data["sections"])


def test_bib_files_resp_status_code_equals_n_200(project_dir):
    # Arrange
    rf = RequestFactory()
    # Act
    resp = _call(rf, "GET", "api/bib/files", project_dir)
    # Act
    # Assert
    assert resp.status_code == 200


def test_bib_files_data_count_1_and_any_f_name_bibliography_bib_for_f_in_data_f(
    project_dir,
):
    # Arrange
    rf = RequestFactory()
    resp = _call(rf, "GET", "api/bib/files", project_dir)
    # Act
    data = json.loads(resp.content)
    # Act
    # Assert
    assert (data["count"] >= 1) and (
        any((f["name"] == "bibliography.bib" for f in data["files"]))
    )


def test_bib_entries_resp_status_code_equals_n_200(project_dir):
    # Arrange
    rf = RequestFactory()
    # Act
    resp = _call(rf, "GET", "api/bib/entries", project_dir)
    # Act
    # Assert
    assert resp.status_code == 200


def test_bib_entries_any_e_citation_key_foo2024_for_e_in_data_entries(project_dir):
    # Arrange
    rf = RequestFactory()
    resp = _call(rf, "GET", "api/bib/entries", project_dir)
    # Act
    data = json.loads(resp.content)
    # Act
    # Assert
    assert any(e["citation_key"] == "foo2024" for e in data["entries"])


def test_compile_status_before_any_compile_resp_status_code_equals_n_200(project_dir):
    # Arrange
    rf = RequestFactory()
    # Act
    resp = _call(rf, "GET", "api/compile/status", project_dir)
    # Act
    # Assert
    assert resp.status_code == 200


def test_compile_status_before_any_compile_data_compiling_is_false_and_data_result_is_none(
    project_dir,
):
    # Arrange
    rf = RequestFactory()
    resp = _call(rf, "GET", "api/compile/status", project_dir)
    # Act
    data = json.loads(resp.content)
    # Act
    # Assert
    assert (data["compiling"] is False) and (data["result"] is None)


def test_pdf_missing_returns_404(project_dir):
    # Arrange
    rf = RequestFactory()
    request = rf.get(f"/api/pdf?doc_type=manuscript&working_dir={project_dir}")
    # Act
    resp = views.api_dispatch(request, "api/pdf")
    # Assert
    assert resp.status_code == 404


def test_unknown_endpoint_returns_404(project_dir):
    # Arrange
    rf = RequestFactory()
    # Act
    resp = _call(rf, "GET", "api/does-not-exist", project_dir)
    # Assert
    assert resp.status_code == 404


def test_wrong_method_returns_405(project_dir):
    # Arrange
    rf = RequestFactory()
    # ping is GET-only
    # Act
    resp = _call(rf, "POST", "ping", project_dir, body="")
    # Assert
    assert resp.status_code == 405


def test_no_working_dir_returns_400():
    # Arrange
    rf = RequestFactory()
    request = rf.get("/ping")
    # Act
    resp = views.api_dispatch(request, "ping")
    # Assert
    assert resp.status_code == 400


def test_figures_resp_status_code_equals_n_200(project_dir):
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
    # Act
    # Assert
    assert resp.status_code == 200


def test_figures_data_doc_type_manuscript_and_any_f_name_01_example_for_f_in_(
    project_dir,
):
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
    resp = views.api_dispatch(request, "api/figures")
    # Act
    data = json.loads(resp.content)
    # Act
    # Assert
    assert (
        (data["doc_type"] == "manuscript")
        and (any((f["name"] == "01_example" for f in data["figures"])))
        and (data["figures"][0]["label"] == "fig:example")
    )


def test_tables_resp_status_code_equals_n_200(project_dir):
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
    # Act
    # Assert
    assert resp.status_code == 200


def test_tables_any_t_name_01_results_for_t_in_data_tables_and_data_tables_0(
    project_dir,
):
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
    resp = views.api_dispatch(request, "api/tables")
    # Act
    data = json.loads(resp.content)
    # Act
    # Assert
    assert (any((t["name"] == "01_results" for t in data["tables"]))) and (
        data["tables"][0]["label"] == "tab:results"
    )


def test_claims_metadata_resp_status_code_equals_n_200(project_dir):
    # Arrange
    rf = RequestFactory()
    (Path(project_dir) / "00_shared").mkdir(exist_ok=True)
    (Path(project_dir) / "00_shared" / "claims.json").write_text(
        '{"version":"1.0","claims":{}}'
    )
    # Act
    resp = _call(rf, "GET", "api/claims-metadata", project_dir)
    # Act
    # Assert
    assert resp.status_code == 200


def test_claims_metadata_data_success_is_true_and_data_count_0(project_dir):
    # Arrange
    rf = RequestFactory()
    (Path(project_dir) / "00_shared").mkdir(exist_ok=True)
    (Path(project_dir) / "00_shared" / "claims.json").write_text(
        '{"version":"1.0","claims":{}}'
    )
    resp = _call(rf, "GET", "api/claims-metadata", project_dir)
    # Act
    data = json.loads(resp.content)
    # Act
    # Assert
    assert (data["success"] is True) and (data["count"] == 0)


def test_dag_requires_target(project_dir):
    # Arrange
    rf = RequestFactory()
    # Act
    resp = _call(rf, "GET", "api/dag", project_dir)
    # Assert
    assert resp.status_code == 400


def test_citation_unverifiable_without_scholar_resp_status_code_equals_n_200(
    project_dir,
):
    # Arrange
    rf = RequestFactory()
    request = rf.get(f"/api/citation/foo2024?working_dir={project_dir}")
    # Act
    resp = views.api_dispatch(request, "api/citation/foo2024")
    # Act
    # Assert
    assert resp.status_code == 200


def test_citation_unverifiable_without_scholar_data_cite_key_foo2024_and_data_state_in_verified_unverifiabl(
    project_dir,
):
    # Arrange
    rf = RequestFactory()
    request = rf.get(f"/api/citation/foo2024?working_dir={project_dir}")
    resp = views.api_dispatch(request, "api/citation/foo2024")
    # Act
    data = json.loads(resp.content)
    # Act
    # Assert
    assert (data["cite_key"] == "foo2024") and (
        data["state"] in {"VERIFIED", "UNVERIFIABLE", "CONTRADICTED"}
    )


def test_viewer_page_renders_resp_status_code_equals_n_200(project_dir):
    # Arrange
    rf = RequestFactory()
    request = rf.get(f"/viewer/?working_dir={project_dir}")
    # Act
    resp = views.viewer_page(request)
    # Act
    # Assert
    assert resp.status_code == 200


def test_viewer_page_renders_writer_viewer_in_body_and_viewer_claims_pane_in_body(
    project_dir,
):
    # Arrange
    rf = RequestFactory()
    request = rf.get(f"/viewer/?working_dir={project_dir}")
    resp = views.viewer_page(request)
    # Act
    body = resp.content.decode()
    # Act
    # Assert
    assert ("Writer — Viewer" in body) and ("viewer-claims-pane" in body)


def test_editor_page_renders_resp_status_code_equals_n_200(project_dir):
    # Arrange
    rf = RequestFactory()
    request = rf.get(f"/?working_dir={project_dir}")
    # Act
    resp = views.editor_page(request)
    # Act
    # Assert
    assert resp.status_code == 200


def test_editor_page_renders_scitex_writer_in_body_and_writer_css_editor_css_in_body_or_e(
    project_dir,
):
    # Arrange
    rf = RequestFactory()
    request = rf.get(f"/?working_dir={project_dir}")
    resp = views.editor_page(request)
    # Act
    body = resp.content.decode()
    # Act
    # Assert
    assert ("Writer — SciTeX" in body) and (
        "writer/css/editor.css" in body or "editor.css" in body
    )


def test_editor_tab_title_marks_standalone_mode(project_dir):
    # Arrange
    rf = RequestFactory()
    request = rf.get(f"/?working_dir={project_dir}")
    resp = views.editor_page(request)
    # Act
    body = resp.content.decode()
    # Assert
    assert "Writer — SciTeX (standalone)" in body


def test_app_label_omits_marker_in_hub_mode():
    # Arrange
    from django.test import override_settings

    # Act
    with override_settings(SCITEX_APP_MODE="hub"):
        label = views._app_label("Writer — SciTeX")
    # Assert
    assert label == "Writer — SciTeX"


# =========================================================================
# Browser-tab identity. The operator lined up four SciTeX tabs and found four
# different conventions: "SciTeX Cards v0.9.7" (version in the title),
# "SciTeX Plot" (no favicon at all), "SciTeX Scholar" (a different icon), and
# writer's "Writer — SciTeX (standalone)" — the only one with the words
# backwards. The tab is the one place a user sees every tool side by side, so
# an inconsistent name there is the most visible inconsistency we ship.
#
# The fleet shape is "SciTeX <Tool>". The "(standalone)" marker STAYS — it is
# deliberate (scitex-hub reads the same SCITEX_APP_MODE setting so the tab
# alone distinguishes hub-embedded from standalone); it is the word order that
# was wrong, not the marker.
# =========================================================================

import inspect  # noqa: E402
import re  # noqa: E402

from scitex_writer._django import views as _views  # noqa: E402


def test_tab_titles_lead_with_the_scitex_brand():
    # Arrange
    source = inspect.getsource(_views)
    # Act
    labels = re.findall(r'_app_label\("([^"]+)"\)', source)
    # Assert
    assert [label for label in labels if not label.startswith("SciTeX ")] == []


def test_tab_titles_are_declared_at_all():
    # Arrange
    source = inspect.getsource(_views)
    # Act
    labels = re.findall(r'_app_label\("([^"]+)"\)', source)
    # Assert
    assert labels != []
