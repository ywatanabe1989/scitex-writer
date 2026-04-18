#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""URL patterns for the scitex-writer editor Django app."""

from django.urls import path

from . import views

app_name = "writer"

urlpatterns = [
    path("", views.editor_page, name="editor"),
    path("<path:endpoint>", views.api_dispatch, name="api"),
]
