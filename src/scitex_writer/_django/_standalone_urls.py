#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Root URLconf for standalone local-dev (`scitex-writer gui`).

Cloud deployments do not use this — they include the app's URL module
directly under their own prefix, mirroring how scitex-cloud mounts
`figrecipe._django` under `/figrecipe/`.
"""

from django.urls import include, path

urlpatterns = [
    path("", include("scitex_writer._django.urls")),
]
