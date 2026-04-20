#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Django app exposing the scitex-writer editor (and viewer in PR2).

Consumed by scitex-cloud's `writer_app` as a thin wrapper — mirrors the
figrecipe/_django pattern so a single canonical implementation drives both
local-dev (`scitex-writer gui`) and cloud deployments.
"""

default_app_config = "scitex_writer._django.apps.WriterEditorConfig"
