#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_cli/_core.py

"""scitex-writer CLI root group + dispatch.

Holds the Click root ``main_group`` (imported by every command module so its
decorators register at import time), the backward-compat argv rewrites, the
top-level alias helper, the optional-subcommand mount, and the ``main(argv)``
entry point.
"""

from __future__ import annotations

import sys

import click

from .. import __version__
from ._helpers import _print_help_recursive

# =========================================================================
# Root group
# =========================================================================


@click.group(
    invoke_without_command=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.version_option(__version__, "-V", "--version", prog_name="scitex-writer")
@click.option(
    "--help-recursive",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=_print_help_recursive,
    help="Show help for the root command and every subcommand.",
)
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    default=False,
    help="Emit machine-readable JSON output where supported.",
)
@click.pass_context
def main_group(ctx, as_json):
    """scitex-writer (v{version}) - LaTeX manuscript compilation system with MCP server.

    \b
    Configuration precedence (highest -> lowest):
      1. Explicit CLI flags
      2. ./config.yaml (project-local)
      3. $SCITEX_WRITER_CONFIG (path to a YAML file)
      4. ~/.scitex/writer/config.yaml (user-wide)
      5. Built-in defaults

    \b
    Example:
        $ scitex-writer compile manuscript
        $ scitex-writer bib list-entries --json
        $ scitex-writer mcp list-tools -vv
    """
    ctx.ensure_object(dict)
    ctx.obj["as_json"] = as_json
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# Inject the package version into the root group's help text so that
# `scitex-writer --help` shows `scitex-writer (vX.Y.Z) — ...` without
# manual updates. importlib.metadata keeps the literal in sync.
main_group.help = (main_group.help or "").replace("{version}", __version__)


# =========================================================================
# §1 flat top-level aliases — verb-shaped groups (compile/export/introspect)
# are kept as hidden back-compat shims; the canonical forms are flat
# `<verb>-<noun>` commands at the top level. Same Click Command objects are
# attached to two parents, so behaviour is identical.
# =========================================================================


def _alias_top_level(cmd: click.Command, new_name: str) -> None:
    """Re-attach a Click command at the top level under a flat verb-noun name.

    The `.name` attribute is updated so audit traversal (which classifies by
    `cmd.name`, not by the parent's commands-dict key) sees the canonical
    `<verb>-<noun>` form. The original group registration is preserved on
    the hidden back-compat group.
    """
    import copy as _copy

    clone = _copy.copy(cmd)
    clone.name = new_name
    main_group.add_command(clone, name=new_name)


# =========================================================================
# Optional: docs / skills subcommands (from scitex_dev) — mounted if available
# =========================================================================


def _mount_optional_subcommands():
    """Mount scitex_dev `docs` and `skills` subcommands if available.

    These come from scitex_dev as Click groups; if present, attach them to
    main_group so they show up under `scitex-writer docs ...` / `skills ...`.
    """
    try:
        from scitex_dev.cli import register_docs_subcommand_click

        register_docs_subcommand_click(main_group, package="scitex-writer")
    except Exception:
        pass
    try:
        from scitex_dev.cli import register_skills_subcommand_click

        register_skills_subcommand_click(main_group, package="scitex-writer")
    except Exception:
        pass


# =========================================================================
# Backward-compat shim: translate deprecated argv tokens to canonical names
# =========================================================================


_TOP_RENAMES = {
    "update": "update-project",
    "usage": "show-usage",
}

# old `<verb> <noun>` -> canonical flat `<verb>-<noun>`
# (groups are kept as hidden back-compat shims; this rewrite is so users
# typing the old form land on the canonical command path so help/usage
# reflects current naming).
_FLAT_RENAMES = {
    ("compile", "manuscript"): "compile-manuscript",
    ("compile", "supplementary"): "compile-supplementary",
    ("compile", "revision"): "compile-revision",
    ("compile", "content"): "compile-content",
    ("export", "manuscript"): "export-manuscript",
    ("introspect", "api"): "show-api",
    ("introspect", "show-api"): "show-api",
}

# old `<group> <leaf>` -> `<group> <new-leaf>` (group preserved)
_LEAF_RENAMES = {
    ("mcp", "installation"): "install",
    ("mcp", "show-installation"): "install",
    ("guidelines", "introduction"): "show-introduction",
    ("guidelines", "methods"): "show-methods",
    ("guidelines", "discussion"): "show-discussion",
    ("guidelines", "abstract"): "show-abstract",
    ("guidelines", "proofread"): "show-proofread",
    ("prompts", "asta"): "show-asta",
}


def _rewrite_argv(argv):
    """Translate deprecated subcommand names to canonical Click names."""
    if not argv:
        return argv
    i = 0
    while i < len(argv) and argv[i].startswith("-"):
        i += 1
    if i >= len(argv):
        return argv
    sub = argv[i]
    if sub in _TOP_RENAMES:
        argv = argv[:i] + [_TOP_RENAMES[sub]] + argv[i + 1 :]
        return argv
    if i + 1 < len(argv):
        pair = (sub, argv[i + 1])
        if pair in _FLAT_RENAMES:
            return argv[:i] + [_FLAT_RENAMES[pair]] + argv[i + 2 :]
        if pair in _LEAF_RENAMES:
            return argv[: i + 1] + [_LEAF_RENAMES[pair]] + argv[i + 2 :]
    return argv


# =========================================================================
# Entry point
# =========================================================================


def main(argv: list = None) -> int:
    """Entry point. Returns exit code (0 on success).

    Wraps Click so callers (and tests) that pass argv lists keep working.
    Translates deprecated subcommand names to canonical Click names.
    """
    raw = list(sys.argv[1:]) if argv is None else list(argv)
    raw = _rewrite_argv(raw)
    try:
        result = main_group.main(
            args=raw, prog_name="scitex-writer", standalone_mode=False
        )
        # Click commands may return an int exit code from their callback
        if isinstance(result, int):
            return result
        return 0
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
        return code
    except click.exceptions.UsageError as e:
        click.echo(f"Error: {e.format_message()}", err=True)
        return 2
    except click.exceptions.Abort:
        click.echo("Aborted.", err=True)
        return 1


# EOF
