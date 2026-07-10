#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_cli/commands/__init__.py

"""Command registry for the scitex-writer CLI.

Importing this package imports every command module for its side effect:
each module's ``@main_group.command`` / ``@main_group.group`` decorators run
at import time and register onto the root group in ``.._core``. After all
modules are imported, the post-registration wiring runs (top-level aliases,
optional scitex_dev subcommands, shell completion, skills, containers).
"""

from __future__ import annotations

from .._core import (
    _alias_top_level,
    _mount_optional_subcommands,
    main_group,
)

# Import every command module — decorators register onto main_group.
from . import (  # noqa: F401
    bib,
    checks,
    compile,
    deps,
    export,
    figures,
    gui,
    guidelines,
    introspect,
    mcp,
    migration,
    misc,
    project,
    prompts,
    tables,
)

# =========================================================================
# §1 flat top-level aliases — same Click Command objects attached to two
# parents, so behaviour is identical.
#
# `compile` and `check` are noun-groups (scitex CLI canon §1: 3+ sibling
# verbs -> tree form) — their flat forms are HIDDEN back-compat shims.
# `export`/`introspect` groups stay hidden this round (1-2 actions; canon
# prefers the compound-leaf there), so their flat forms stay the VISIBLE
# surface — unchanged from before.
# =========================================================================

_alias_top_level(compile.compile_manuscript, "compile-manuscript", hidden=True)
_alias_top_level(compile.compile_supplementary, "compile-supplementary", hidden=True)
_alias_top_level(compile.compile_revision, "compile-revision", hidden=True)
_alias_top_level(compile.compile_content, "compile-content", hidden=True)
_alias_top_level(checks.check_limits_cmd, "check-limits", hidden=True)
_alias_top_level(checks.check_overflow_cmd, "check-overflow", hidden=True)
_alias_top_level(checks.check_paper_symlink_cmd, "check-paper-symlink", hidden=True)
_alias_top_level(checks.check_references_cmd, "check-references", hidden=True)
_alias_top_level(export.export_manuscript, "export-manuscript")
_alias_top_level(introspect.introspect_show_api, "show-api")


# =========================================================================
# Optional: docs / skills subcommands (from scitex_dev) — mounted if available
# =========================================================================

_mount_optional_subcommands()


# §1a: install-shell-completion + print-shell-completion (canonical leaves)
try:
    from scitex_dev._cli._completion import attach_shell_completion

    attach_shell_completion(main_group, prog_name="scitex-writer")
except ImportError:
    pass


# Wire in the skills group (list/get/install).
from .._skills import skills_group as _skills_group  # noqa: E402

main_group.add_command(_skills_group)


# Wire in the containers group (sub-tool SIF installer — texlive, ...).
# Per operator design 8566: scitex-writer owns its own SIFs under
# ~/.scitex/writer/containers/; the build engine is shared with sac
# via scitex-container for uniform versioning + pinning.
from ..install import containers_group as _containers_group  # noqa: E402

main_group.add_command(_containers_group)


# EOF
