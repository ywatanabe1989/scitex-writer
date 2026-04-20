# scitex_writer._django

Django app exposing the scitex-writer editor. Mirrors the
[`figrecipe/_django`](https://github.com/ywatanabe1989/figrecipe) pattern so a
single canonical implementation drives both local-dev (`scitex-writer gui`) and
cloud deployments (scitex-cloud `writer_app`).

## Layout

```
_django/
├── apps.py              WriterEditorConfig(ScitexAppConfig)
├── manifest.json        scitex-app manifest (slug="writer")
├── urls.py              path("", editor_page) + path("<path:endpoint>", api_dispatch)
├── views.py             editor_page + api_dispatch (HANDLERS lookup + claim params)
├── services.py          ProjectState dataclass + in-process cache with TTL
├── settings.py          Standalone settings (local dev only; cloud ignores)
├── _server.py           `scitex-writer gui` entry point (Django runserver bootstrap)
├── _standalone_urls.py  Root URLconf for standalone mode
├── handlers/
│   ├── core.py          ping, project-info
│   ├── files.py         file tree, read/write, sections
│   ├── compile.py       compile, status, pdf
│   ├── bib.py           bib files, entries
│   └── claim.py         list, get, add, remove, chain, render
├── templates/writer/
│   └── editor.html      SPA shell, references API_BASE via data-attr
└── static/writer/
    ├── css/editor.css   Extracted from the old _editor/_templates/_styles*.py
    └── js/editor.js     Extracted from the old _editor/_templates/_scripts*.py
```

## Local usage

```bash
scitex-writer gui ./my-paper
# → http://127.0.0.1:5050
```

Launches a local Django server bound to `_django.settings`. The project path is
passed via `?working_dir=<path>` query param or the `WRITER_WORKING_DIR` env
var.

## Cloud usage (consumption pattern)

scitex-cloud's `writer_app` becomes a thin wrapper, mirroring the figrecipe_app
pattern. Create `apps/workspace/writer_app/urls/writer.py`:

```python
from django.urls import path
from scitex_writer._django.views import api_dispatch as _raw_api_dispatch
from scitex_writer._django.views import editor_page


def _inject_project_context(request):
    """Inject working_dir from user's current project."""
    from apps.infra.project_app.services.project_utils import get_current_project

    if not request.user.is_authenticated:
        return
    if request.GET.get("working_dir"):
        return

    project = get_current_project(request, user=request.user)
    if project:
        mutable_get = request.GET.copy()
        mutable_get["working_dir"] = str(project.get_local_path())
        request.GET = mutable_get


def api_dispatch_with_context(request, endpoint):
    _inject_project_context(request)
    return _raw_api_dispatch(request, endpoint)


urlpatterns = [
    path("writer/", editor_page, name="writer_editor"),
    path("writer/<path:endpoint>", api_dispatch_with_context, name="writer_api"),
]
```

The JS in `static/writer/js/editor.js` reads `document.body.dataset.apiBase` so
the same bundle works whether mounted at `/` (local) or `/writer/` (cloud).
Render the template with `{"api_base": "/writer/"}` in the cloud view.

## API surface

| Method | Endpoint                     | Handler                |
|--------|------------------------------|------------------------|
| GET    | `/`                          | editor_page            |
| GET    | `/ping`                      | handle_ping            |
| GET    | `/api/project-info`          | handle_project_info    |
| GET    | `/api/files`                 | handle_list_files      |
| GET    | `/api/file?path=…`           | handle_file            |
| POST   | `/api/file`                  | handle_file            |
| GET    | `/api/sections?doc_type=…`   | handle_sections        |
| POST   | `/api/compile`               | handle_compile         |
| GET    | `/api/compile/status`        | handle_compile_status  |
| GET    | `/api/pdf?doc_type=…`        | handle_pdf             |
| GET    | `/api/bib/files`             | handle_bib_files       |
| GET    | `/api/bib/entries`           | handle_bib_entries     |
| GET    | `/api/claims`                | handle_list_claims     |
| POST   | `/api/claims`                | handle_add_claim       |
| GET    | `/api/claims/<id>`           | handle_get_claim       |
| DELETE | `/api/claims/<id>`           | handle_remove_claim    |
| GET    | `/api/claims/<id>/chain`     | handle_claim_chain     |
| POST   | `/api/claims/render`         | handle_render_claims   |

All endpoints resolve `working_dir` from `?working_dir=` or the
`WRITER_WORKING_DIR` env var. Cloud deployments inject it server-side from the
authenticated user's current project.

## Viewer module (PR2)

A viewer module for live-paper viewing (PDF.js overlays, `\vclaim` popups,
Clew DAG navigation) will be added alongside the editor in a follow-up PR,
backing scitex-cloud#133/#134/#137.
