#!/usr/bin/env python3
# -*- coding: utf-8 -*-
try:
    from scitex_app._django import ScitexAppConfig
except ImportError:
    from django.apps import AppConfig as ScitexAppConfig


class WriterEditorConfig(ScitexAppConfig):
    name = "scitex_writer._django"
    label = "writer_editor"
    verbose_name = "SciTeX Writer Editor"
