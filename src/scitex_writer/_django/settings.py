#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Minimal standalone Django settings for `scitex-writer gui`.

Used only by the standalone launcher; cloud deployments ignore this
module and mount `scitex_writer._django.urls` under their own prefix.

Mirrors the `figrecipe._django.settings` pattern: bare-minimum installed
apps, optional `scitex_ui` for the shared workspace shell, and a SQLite
database so any future models (chat sessions, comments, versions) work
out of the box.
"""

from __future__ import annotations

import os
import secrets
import tempfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Fleet env-var convention is SCITEX_WRITER_<X>; the unprefixed
# WRITER_DJANGO_SECRET spelling is honoured for one deprecation cycle.
SECRET_KEY = (
    os.environ.get("SCITEX_WRITER_DJANGO_SECRET")
    or os.environ.get("WRITER_DJANGO_SECRET")
    or secrets.token_urlsafe(32)
)
DEBUG = os.environ.get("DJANGO_DEBUG", "true").lower() == "true"
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "0.0.0.0", "testserver"]

# "hub" | "standalone" — the browser tab alone must distinguish the two
# (operator request; scitex-hub PR #357 reads the same setting and defaults
# to "hub"). These settings only boot the STANDALONE server
# (`scitex-writer gui`), so standalone is the default here.
SCITEX_APP_MODE = os.environ.get("SCITEX_APP_MODE", "standalone")

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "scitex_writer._django.apps.WriterEditorConfig",
]

# Optional: scitex-ui supplies the workspace shell (template + CSS/JS assets)
try:
    import scitex_ui  # noqa: F401

    INSTALLED_APPS.append("scitex_ui")
except ImportError:
    pass

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "scitex_writer._django._standalone_urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                # Enables scitex-ui's element inspector (Alt+I / Ctrl+I) in the
                # standalone editor: sets `stx_element_inspector_enabled` so the
                # shared shell's `_element_inspector.html` partial injects the
                # inspector script (gated on DEBUG/staff, and DEBUG defaults on
                # for the local `scitex-writer gui` server). Without this the
                # partial emits only its placeholder comment and Alt+I/Ctrl+I
                # are no-ops.
                "scitex_ui.context_processors.element_inspector",
            ],
        },
    },
]

# SQLite lives in the temp dir so local runs don't pollute the project
_DB_DIR = Path(tempfile.gettempdir()) / "scitex_writer"
_DB_DIR.mkdir(parents=True, exist_ok=True)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(_DB_DIR / "db.sqlite3"),
    }
}

STATIC_URL = "/static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True

WRITER_TEMP_DIR = _DB_DIR
