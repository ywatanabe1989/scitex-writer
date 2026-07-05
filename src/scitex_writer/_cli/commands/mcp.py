#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_cli/commands/mcp.py

"""mcp command group (MCP server: install / list-tools / doctor / start)."""

from __future__ import annotations

import click

from .._core import main_group
from .._helpers import _emit_json

# =========================================================================
# mcp group
# =========================================================================


@main_group.group("mcp", invoke_without_command=True)
@click.pass_context
def mcp_group(ctx):
    """MCP (Model Context Protocol) server commands.

    \b
    Example:
        $ scitex-writer mcp start
        $ scitex-writer mcp list-tools -vv
        $ scitex-writer mcp doctor
        $ scitex-writer mcp install
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@mcp_group.command(
    "show-installation",
    hidden=True,
    context_settings={"ignore_unknown_options": True},
)
@click.pass_context
def mcp_show_installation_deprecated(ctx):
    """(deprecated) Renamed to `install`."""
    click.echo(
        "error: `scitex-writer mcp show-installation` was renamed to "
        "`scitex-writer mcp install`.\n"
        "Re-run with: scitex-writer mcp install",
        err=True,
    )
    ctx.exit(2)


@mcp_group.command("install")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Accepted for §2; this verb is informational, never mutates state.",
)
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    help="Accepted for §2; this verb is informational, never mutates state.",
)
def mcp_install(as_json, dry_run, yes):
    """Show Claude Desktop installation guide for the scitex-writer MCP server.

    (rename of show-installation)

    \b
    Example:
        $ scitex-writer mcp install
    """
    del dry_run, yes  # audit §2 — no-op flags
    from ..mcp import cmd_config

    return cmd_config()


@mcp_group.command("list-tools")
@click.option(
    "-v", "--verbose", count=True, help="Verbosity: -v desc, -vv +params, -vvv full."
)
@click.option("-c", "--compact", is_flag=True, help="Compact signatures (single line).")
@click.option(
    "-m",
    "--module",
    "module_filter",
    default=None,
    help="Filter by module (bib/compile/figures/tables/project/guidelines/prompts/general).",
)
@click.option("--json", "as_json", is_flag=True, default=False, help="Output as JSON.")
def mcp_list_tools(verbose, compact, module_filter, as_json):
    """List all available MCP tools exposed by scitex-writer.

    \b
    Example:
        $ scitex-writer mcp list-tools
        $ scitex-writer mcp list-tools -vv
        $ scitex-writer mcp list-tools --module bib --json
    """
    from ..mcp import cmd_list_tools

    return cmd_list_tools(
        verbose=verbose, compact=compact, module=module_filter, as_json=as_json
    )


@mcp_group.command("doctor")
@click.option("--json", "as_json", is_flag=True, default=False, help="Output as JSON.")
def mcp_doctor(as_json):
    """Check MCP server health and configuration.

    \b
    Example:
        $ scitex-writer mcp doctor
    """
    from ..mcp import cmd_doctor

    return cmd_doctor()


@mcp_group.command("start")
@click.option(
    "-t",
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport: stdio (default) or sse.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Print what would happen without starting the server.",
)
@click.option("--yes", "-y", is_flag=True, default=False, help="Skip confirmations.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def mcp_start(transport, dry_run, yes, as_json):
    """Start the scitex-writer MCP server.

    \b
    Example:
        $ scitex-writer mcp start
        $ scitex-writer mcp start --transport sse
        $ scitex-writer mcp start --dry-run
    """
    if dry_run:
        msg = {"would_start": True, "transport": transport}
        if as_json:
            _emit_json(msg)
        else:
            click.echo(f"Would start MCP server (transport={transport}).")
        return 0
    from ..mcp import cmd_start

    return cmd_start(transport=transport)


# EOF
