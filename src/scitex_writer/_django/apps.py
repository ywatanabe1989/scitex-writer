#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import warnings

try:
    from scitex_app.embed import ScitexAppConfig
except ImportError:
    # Falling back to a plain Django AppConfig means the editor loses the
    # scitex-app workspace shell. That is a real downgrade, so SAY SO — a
    # silent base-class swap left the editor looking installed and behaving
    # differently, with nothing to explain why.
    from django.apps import AppConfig as ScitexAppConfig

    warnings.warn(
        "scitex-app is not installed: the writer editor is running without "
        "the workspace shell. Install it with: pip install scitex-writer[editor]",
        RuntimeWarning,
        stacklevel=2,
    )


class WriterEditorConfig(ScitexAppConfig):
    name = "scitex_writer._django"
    label = "writer_editor"
    verbose_name = "SciTeX Writer Editor"
