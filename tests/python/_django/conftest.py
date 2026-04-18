"""Django test bootstrap — configures settings once for all tests in this pkg."""

from __future__ import annotations

import os

import django
from django.conf import settings


def _init_django() -> None:
    if settings.configured:
        return
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scitex_writer._django.settings")
    django.setup()


_init_django()
