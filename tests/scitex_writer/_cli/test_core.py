"""Top-level CLI shape: noun-groups visible, flat forms hidden back-compat.

scitex CLI canon (§1/§1b, ratified by scitex-dev 2026-07-09): a noun with 3+
sibling verbs gets a visible `<noun> <verb>` group; the old flat
`<verb>-<noun>` compound stays reachable but drops out of `--help`. `compile`
and `check` meet that bar; `export`/`introspect` (1-2 actions) don't, so their
flat forms stay the visible surface unchanged.
"""

import importlib


def _main_group():
    importlib.import_module("scitex_writer._cli.commands")
    from scitex_writer._cli._core import main_group

    return main_group


def test_compile_and_check_groups_are_registered_and_visible():
    # Arrange
    main_group = _main_group()
    # Act
    compile_cmd = main_group.commands["compile"]
    check_cmd = main_group.commands["check"]
    # Assert
    assert compile_cmd.hidden is False
    assert check_cmd.hidden is False


def test_flat_compile_and_check_aliases_are_hidden_but_reachable():
    # Arrange
    main_group = _main_group()
    flat_names = [
        "compile-manuscript",
        "compile-supplementary",
        "compile-revision",
        "compile-content",
        "check-limits",
        "check-overflow",
        "check-paper-symlink",
        "check-references",
    ]
    # Act
    commands = {name: main_group.commands.get(name) for name in flat_names}
    # Assert
    assert all(cmd is not None for cmd in commands.values())
    assert all(cmd.hidden is True for cmd in commands.values())


def test_export_and_show_api_flat_forms_stay_visible():
    # Arrange
    main_group = _main_group()
    # Act
    export_cmd = main_group.commands["export-manuscript"]
    show_api_cmd = main_group.commands["show-api"]
    # Assert
    assert export_cmd.hidden is False
    assert show_api_cmd.hidden is False


def test_compile_group_argv_reaches_manuscript_subcommand():
    # Arrange
    from scitex_writer._cli._core import main

    # Act
    exit_code = main(["compile", "manuscript", "--dry-run", "--json"])
    # Assert
    assert exit_code == 0


def test_check_group_argv_reaches_references_subcommand():
    # Arrange
    from scitex_writer._cli._core import main

    # Act
    exit_code = main(["check", "references", "--help"])
    # Assert
    assert exit_code == 0
