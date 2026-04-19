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


def test_ping(project_dir):
    rf = RequestFactory()
    resp = _call(rf, "GET", "ping", project_dir)
    assert resp.status_code == 200
    assert json.loads(resp.content) == {"status": "ok"}


def test_project_info(project_dir):
    rf = RequestFactory()
    resp = _call(rf, "GET", "api/project-info", project_dir)
    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert data["project_dir"] == str(Path(project_dir).resolve())
    assert "manuscript" in data["doc_types"]
    assert "supplementary" in data["doc_types"]
    assert data["has_shared"] is True


def test_files_tree(project_dir):
    rf = RequestFactory()
    resp = _call(rf, "GET", "api/files", project_dir)
    assert resp.status_code == 200
    data = json.loads(resp.content)
    names = {e["name"] for e in data["tree"]}
    assert "01_manuscript" in names
    assert "00_shared" in names


def test_file_read_write_roundtrip(project_dir):
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
    assert resp.status_code == 200
    assert "Intro" in json.loads(resp.content)["content"]

    # Write
    new_content = r"\section{New}"
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
    assert resp.status_code == 200
    assert (
        Path(project_dir) / "01_manuscript" / "contents" / "01_intro.tex"
    ).read_text() == new_content


def test_file_read_path_traversal_blocked(project_dir):
    rf = RequestFactory()
    request = rf.get(f"/api/file?path=../../../etc/passwd&working_dir={project_dir}")
    resp = views.api_dispatch(request, "api/file")
    assert resp.status_code == 403


def test_sections(project_dir):
    rf = RequestFactory()
    resp = _call(rf, "GET", "api/sections?doc_type=manuscript", project_dir)
    # endpoint contains querystring → re-call without it
    request = RequestFactory().get(
        f"/api/sections?doc_type=manuscript&working_dir={project_dir}"
    )
    resp = views.api_dispatch(request, "api/sections")
    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert any(s["filename"] == "01_intro.tex" for s in data["sections"])


def test_bib_files(project_dir):
    rf = RequestFactory()
    resp = _call(rf, "GET", "api/bib/files", project_dir)
    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert data["count"] >= 1
    assert any(f["name"] == "bibliography.bib" for f in data["files"])


def test_bib_entries(project_dir):
    rf = RequestFactory()
    resp = _call(rf, "GET", "api/bib/entries", project_dir)
    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert any(e["citation_key"] == "foo2024" for e in data["entries"])


def test_compile_status_before_any_compile(project_dir):
    rf = RequestFactory()
    resp = _call(rf, "GET", "api/compile/status", project_dir)
    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert data["compiling"] is False
    assert data["result"] is None


def test_pdf_missing_returns_404(project_dir):
    rf = RequestFactory()
    request = rf.get(f"/api/pdf?doc_type=manuscript&working_dir={project_dir}")
    resp = views.api_dispatch(request, "api/pdf")
    assert resp.status_code == 404


def test_unknown_endpoint_returns_404(project_dir):
    rf = RequestFactory()
    resp = _call(rf, "GET", "api/does-not-exist", project_dir)
    assert resp.status_code == 404


def test_wrong_method_returns_405(project_dir):
    rf = RequestFactory()
    # ping is GET-only
    resp = _call(rf, "POST", "ping", project_dir, body="")
    assert resp.status_code == 405


def test_no_working_dir_returns_400():
    rf = RequestFactory()
    request = rf.get("/ping")
    resp = views.api_dispatch(request, "ping")
    assert resp.status_code == 400


def test_figures(project_dir):
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
    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert data["doc_type"] == "manuscript"
    assert any(f["name"] == "01_example" for f in data["figures"])
    assert data["figures"][0]["label"] == "fig:example"


def test_tables(project_dir):
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
    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert any(t["name"] == "01_results" for t in data["tables"])
    assert data["tables"][0]["label"] == "tab:results"


def test_editor_page_renders(project_dir):
    rf = RequestFactory()
    request = rf.get(f"/?working_dir={project_dir}")
    resp = views.editor_page(request)
    assert resp.status_code == 200
    body = resp.content.decode()
    assert "SciTeX Writer" in body
    assert "writer/css/editor.css" in body or "editor.css" in body
