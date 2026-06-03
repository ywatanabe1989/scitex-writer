"""``scitex-writer install`` — wrapper-side SIF installer.

Per operator design 8566: each scitex-* package owns its own SIF
artifacts under ``~/.scitex/<pkg>/containers/``. scitex-writer owns
its LaTeX (``texlive``) and Mermaid (``mermaid``) sub-tools; wrapper
agents (proj-neurovista etc.) bind from the canonical path
``~/.scitex/writer/containers/<tool>.sif:/opt/<tool>.sif:ro``.

This module ships the install verbs that BUILD those SIFs in-place.
The build itself is delegated to ``scitex_container.apptainer.build``
— the same engine sac uses for its own ``:base`` / ``:scitex`` SIFs.
Delegating means:

  * Uniform build mechanism across every scitex-* package SIF
    (one engine, one log shape, one skip-rebuild heuristic).
  * Free version pinning: scitex-container writes a per-image
    ``.def-hash`` next to the artifact + a timestamped ``.build-*.log``
    + a snapshot of the recipe alongside the SIF.
  * Top-level symlink at ``<containers>/<image_name>.sif`` so
    ``sac image list`` (which globs ``~/.scitex/*/containers/*.sif``
    per the convention) sees the artifact without scitex-writer
    needing to know about sac.

Out of scope: raw ``apptainer build`` shell-outs. Hand-rolled apptainer
calls would diverge in shape from sac's build artifacts and lose the
pinning the operator asked for.
"""

from __future__ import annotations

from pathlib import Path

import click

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

# Each install target is a (def-file-stem, recipe-path) pair. New
# sub-tools register here; the install group's click.Choice + dispatch
# both read from this dict so a single addition lights up the CLI +
# tests + docs in one shot.
_RECIPES_DIR = (
    Path(__file__).resolve().parent.parent.parent.parent / "scripts" / "containers"
)

_SUB_TOOLS: dict[str, str] = {
    "texlive-sif": "texlive.def",
    # "mermaid-sif": "mermaid.def",   # follow-up: enable when canonicalized
}


def _output_dir() -> Path:
    """The per-package containers root under the operator convention.

    ``~/.scitex/writer/containers/`` — sac's generic ``image list`` glob
    (``~/.scitex/*/containers/*.sif``) discovers any SIF dropped here
    automatically, so this is the only path the wrapper bind needs to
    know about.
    """
    return Path.home() / ".scitex" / "writer" / "containers"


def _resolve_recipe(target: str) -> Path:
    """Map a CLI target (``texlive-sif``) to its shipped .def file."""
    if target not in _SUB_TOOLS:
        raise click.UsageError(
            f"unknown install target {target!r}; choose from {sorted(_SUB_TOOLS)}"
        )
    return _RECIPES_DIR / _SUB_TOOLS[target]


def _image_name_for(target: str) -> str:
    """Drop the ``-sif`` suffix to get the artifact's base name.

    The artifact lands at ``<output_dir>/<image_name>/<image_name>.sif``
    with a top-level symlink ``<output_dir>/<image_name>.sif`` — that
    top-level link is what sac's ``image list`` glob surfaces and what
    wrapper specs bind from.
    """
    return target.removesuffix("-sif")


# ---------------------------------------------------------------------------
# Group + verbs
# ---------------------------------------------------------------------------


@click.group("install")
def install_group() -> None:
    """Install scitex-writer's owned sub-tool SIFs.

    \b
    Targets:
      texlive-sif   ~/.scitex/writer/containers/texlive.sif (TeX Live)

    Each target writes:
      ~/.scitex/writer/containers/<name>/<name>.sif       (the built image)
      ~/.scitex/writer/containers/<name>.sif              (top-level symlink)
      ~/.scitex/writer/containers/<name>.def              (recipe snapshot)
      ~/.scitex/writer/containers/<name>/.def-hash        (skip-rebuild guard)
      ~/.scitex/writer/containers/<name>/<name>.build-<ts>.log
    """


@install_group.command("texlive-sif")
@click.option(
    "-y",
    "--yes",
    is_flag=True,
    default=False,
    help="Skip confirmation. Re-runs against an existing artifact use "
    "scitex-container's .def-hash skip-rebuild guard automatically.",
)
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Overwrite an existing SIF / sandbox even if the .def-hash matches "
    "(bypasses scitex-container's skip-rebuild guard).",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Resolve paths + print what would happen; do not invoke apptainer.",
)
def install_texlive_sif(yes: bool, force: bool, dry_run: bool) -> None:
    """Build the TeX Live sub-tool SIF.

    Delegates to ``scitex_container.apptainer.build``; the artifact
    lands at ``~/.scitex/writer/containers/texlive.sif`` (top-level
    symlink) so wrapper agents bind from a stable path regardless of
    rebuilds.

    \b
    Example:
      $ scitex-writer install texlive-sif -y
      $ scitex-writer install texlive-sif -y --force
    """
    _run_install("texlive-sif", yes=yes, force=force, dry_run=dry_run)


# ---------------------------------------------------------------------------
# Shared installer body
# ---------------------------------------------------------------------------


def _run_install(target: str, *, yes: bool, force: bool, dry_run: bool) -> None:
    """Resolve inputs, gate on ``--yes``, delegate to scitex-container.

    Pulled out of the click verb so per-target verbs stay 3 lines
    each (the verb only carries CLI metadata; the dispatch is
    shared). Mirrors how sac's ``image build`` carves the
    click-glue away from the build logic.
    """
    recipe = _resolve_recipe(target)
    if not recipe.is_file():
        raise click.UsageError(
            f"recipe not found: {recipe}. Re-check the install set "
            f"in src/scitex_writer/_cli/install.py:_SUB_TOOLS or the "
            f"scripts/containers/ tree."
        )

    image_name = _image_name_for(target)
    output_dir = _output_dir()

    if dry_run:
        click.echo(
            f"[dry-run] would build {image_name!r} from {recipe} "
            f"→ {output_dir / f'{image_name}.sif'} "
            f"(force={force})"
        )
        return

    if not yes:
        click.echo(
            f"Refusing to build {target!r} without --yes/-y. Re-run "
            f"with `-y` to confirm; the resulting SIF lands at "
            f"{output_dir / f'{image_name}.sif'}.",
            err=True,
        )
        raise SystemExit(2)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Delegate to scitex-container's build engine. Imports are inside
    # the body so the module loads cleanly on hosts without
    # scitex-container installed (the verb still surfaces in `--help`;
    # the actual call raises a clean ImportError with install hint).
    try:
        from scitex_container.apptainer import build as sc_build
    except ImportError as exc:
        raise click.ClickException(
            "scitex-container is required for `scitex-writer install` "
            "but is not installed. Run `uv pip install scitex-container` "
            "(or `pip install scitex-container`) and retry."
        ) from exc

    try:
        output = sc_build(
            def_path=recipe,
            output_dir=output_dir,
            image_name=image_name,
            force=force,
        )
    except (FileNotFoundError, RuntimeError) as exc:
        raise click.ClickException(f"apptainer build failed: {exc}") from exc

    click.echo(f"built {output}")


__all__ = [
    "install_group",
    "install_texlive_sif",
]
