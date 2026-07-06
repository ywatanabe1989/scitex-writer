#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_cli/commands/deps.py

"""``list-deps`` command — scitex-writer's native (apt) system dependencies.

scitex-writer is the single source of truth for its LaTeX-toolchain apt
packages (``scitex_writer._core._system_deps``), declared to the ecosystem via
the ``scitex_dev.system_deps`` entry-point. This command is the leaf-local
view of that list: ``scitex-writer list-deps`` prints the apt packages (the
fleet-wide aggregate across every leaf is a separate surface,
``scitex-dev ecosystem system-deps``).

Deliberately scitex_dev-free: it reads the local provider table
(``APT_PACKAGES`` / ``_PACKAGES``) directly, so it never triggers the
``scitex_dev`` import chain (and its historical import-time ``--version``
fast-path).
"""

from __future__ import annotations

import click

from .._core import main_group
from .._helpers import _emit_json

# =========================================================================
# list-deps  (flat verb-noun top-level command, per §1 — same house style
# as compile-manuscript / check-limits / export-manuscript)
# =========================================================================


@main_group.command("list-deps")
@click.option(
    "--apt",
    "as_apt",
    is_flag=True,
    default=False,
    help="Emit the full `apt-get install ...` one-liner instead of one name per line.",
)
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    default=False,
    help="Emit JSON (package/purpose/provider).",
)
def list_deps_cmd(as_apt, as_json):
    """Print scitex-writer's required system (apt) packages — the LaTeX toolchain.

    Default output is one apt package name per line (pipe/build friendly).
    ``--apt`` prints the ready-to-paste ``apt-get install`` command; ``--json``
    prints package/purpose/provider. These are the same packages scitex-writer
    declares to ``scitex-dev ecosystem system-deps`` via the
    ``scitex_dev.system_deps`` entry-point.

    \b
    Example:
        $ scitex-writer list-deps
        $ scitex-writer list-deps --apt
        $ scitex-writer list-deps --json
    """
    from ..._core._system_deps import _PACKAGES, APT_PACKAGES

    if as_json:
        _emit_json(
            [
                {"package": pkg, "purpose": purpose, "provider": "scitex-writer"}
                for pkg, purpose in _PACKAGES
            ]
        )
        return 0
    if as_apt:
        click.echo(
            "apt-get install -y --no-install-recommends " + " ".join(APT_PACKAGES)
        )
        return 0
    click.echo("\n".join(APT_PACKAGES))
    return 0


# EOF
