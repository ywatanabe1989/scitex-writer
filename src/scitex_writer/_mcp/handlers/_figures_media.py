#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/handlers/_figures_media.py

r"""The MEDIA half of the figure pipeline (port of ``process_figures.sh``).

Everything that touches image files, in the order ``process`` runs it:

1. :func:`init_figures`           -- create the figure dirs, clear ``compiled_dir/*.tex``,
                                     drop derived symlinks from ``jpg_dir`` while
                                     PRESERVING (and warning about) real user files.
2. :func:`ensure_lower_letter_id` -- ``01A_panel.png`` -> ``01a_panel.png``.
3. :func:`cleanup_panel_captions` -- delete stray ``NN<letter>_*.tex`` (panels get none).
4. :func:`ensure_caption`         -- default ``NN_*.tex`` where a MAIN figure has none.
5. :func:`convert_formats`        -- the cascade: PPTX->TIF, TIF->PNG, MMD->PNG, PNG->JPG.
6. :func:`compose_panels`         -- tile ``NN<letter>_*.jpg`` panels into ``NN.jpg``.
7. :func:`link_compilation_jpgs`  -- symlink each main JPG into ``jpg_dir`` (cp fallback).
8. :func:`create_placeholders`    -- a placeholder JPG for a declared-but-missing figure.

The LaTeX half lives in :mod:`._figures_tex`; :mod:`._figures_pipeline` reads the
config and runs both. See that module's docstring for the shell behaviours this
port deliberately changed (all of them silent degradations, never working paths).
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import List, Optional

from ..._utils._figure_image import (
    panel_letter,
    placeholder_jpg,
    tile_panels,
    to_jpg,
    to_png,
    trim_whitespace,
)

CAPTION_SOURCE_SUFFIXES = (
    ".tif",
    ".tiff",
    ".jpg",
    ".jpeg",
    ".png",
    ".svg",
    ".mmd",
    ".pptx",
)
"""Media kinds that entitle a MAIN figure to an auto-generated caption."""

REGENERABLE_SUFFIXES = (".png", ".tif", ".tiff", ".pptx", ".mmd", ".pdf", ".jpg")
"""Sources the cascade can regenerate a compilation JPG from (orphan detection)."""


def _default_caption(rel_path: str) -> str:
    """The placeholder caption written for a figure that has none (shell parity)."""
    return (
        f"%% Edit this file: {rel_path}\n"
        "\\caption{\\textbf{FIGURE TITLE HERE}\\\\\n"
        "\\smallskip\n"
        f"FIGURE LEGEND HERE. Edit this caption at \\url{{{rel_path}}}.\n"
        "}\n"
        "%%%% EOF\n"
    )


def numbered(directory: Path, *suffixes: str) -> List[Path]:
    """Sorted ``NN*<suffix>`` entries of ``directory`` (the shell's ``[0-9]*`` glob)."""
    if not directory.is_dir():
        return []
    found: List[Path] = []
    for suffix in suffixes:
        found += [
            path
            for path in directory.glob(f"[0-9]*{suffix}")
            if path.is_file() or path.is_symlink()
        ]
    return sorted(found, key=lambda p: p.name)


def mains(directory: Path, *suffixes: str) -> List[Path]:
    """The MAIN (non-panel) numbered files of ``directory``."""
    return [p for p in numbered(directory, *suffixes) if panel_letter(p.stem) is None]


def figure_number(stem: str) -> str:
    """``01_overview`` -> ``01``; a stem with no ``NN_`` prefix is its own number."""
    head = stem.split("_", 1)[0]
    return head if head.isdigit() else stem


def init_figures(
    figure_dir: Path, caption_media_dir: Path, jpg_dir: Path, compiled_dir: Path
) -> List[str]:
    """Stage 1: (re)create the figure dirs and clear DERIVED artifacts only.

    Compiled ``*.tex`` are stale by definition and always cleared (Issue #41: a
    renamed figure otherwise left its old float behind). In ``jpg_dir`` only
    SYMLINKS are dropped -- they are re-created from ``caption_and_media`` every
    run. A REAL file there is user-placed: a blanket wipe once destroyed figures
    that had no ``caption_and_media`` source to regenerate from, so it is
    preserved and reported as a warning instead.
    """
    for directory in (figure_dir, caption_media_dir, jpg_dir, compiled_dir):
        directory.mkdir(parents=True, exist_ok=True)
    for stale in compiled_dir.glob("*.tex"):
        stale.unlink()
    for entry in jpg_dir.iterdir():
        if entry.is_symlink():
            entry.unlink()

    warnings = []
    for orphan in sorted(jpg_dir.glob("*.jpg")):
        if not orphan.is_file():
            continue
        sources = (
            caption_media_dir / f"{orphan.stem}{suffix}"
            for suffix in REGENERABLE_SUFFIXES
        )
        if not any(source.exists() for source in sources):
            warnings.append(
                f"Preserving user-placed {orphan.name} in jpg_for_compilation "
                f"(no caption_and_media source to regenerate it from); move it to "
                f"caption_and_media/ to track it as a source."
            )
    return warnings


def ensure_lower_letter_id(caption_media_dir: Path) -> int:
    """Stage 2: lowercase an uppercase panel id (``01A_panel`` -> ``01a_panel``)."""
    renamed = 0
    for path in sorted(caption_media_dir.glob("[0-9]*")):
        letter = panel_letter(path.stem)
        if letter is None or not letter.isupper():
            continue
        index = path.name.index(letter)
        new_name = path.name[:index] + letter.lower() + path.name[index + 1 :]
        path.rename(path.with_name(new_name))
        renamed += 1
    return renamed


def cleanup_panel_captions(caption_media_dir: Path) -> int:
    """Stage 3: delete stray panel caption files -- a panel never carries a caption.

    Only the composed MAIN figure gets a ``\\caption``; a panel caption would
    render as a second, counter-numbered figure.
    """
    removed = 0
    for tex_file in numbered(caption_media_dir, ".tex"):
        if panel_letter(tex_file.stem) is not None:
            tex_file.unlink()
            removed += 1
    return removed


def ensure_caption(caption_media_dir: Path, project_path: Path) -> int:
    """Stage 4: write a default caption for every MAIN figure lacking one.

    A symlinked caption counts as present (the shell tested ``-f || -L``). The
    project's ``templates/.00_template.tex`` wins over the built-in default.
    """
    template = caption_media_dir / "templates" / ".00_template.tex"
    created = 0
    for image in mains(caption_media_dir, *CAPTION_SOURCE_SUFFIXES):
        caption_file = caption_media_dir / f"{image.stem}.tex"
        if caption_file.exists() or caption_file.is_symlink():
            continue
        if template.is_file():
            shutil.copyfile(template, caption_file)
        else:
            try:
                rel_path = str(caption_file.resolve().relative_to(project_path))
            except ValueError:
                rel_path = caption_file.name
            caption_file.write_text(_default_caption(rel_path), encoding="utf-8")
        created += 1
    return created


def pptx_to_tif(caption_media_dir: Path) -> int:
    """Cascade step 1: PPTX -> PDF -> PNG, refreshed when the source is newer.

    Requires ``libreoffice`` (rendering a slide deck has no Python equivalent that
    preserves its fonts and vector shapes). FAILS LOUD with an install hint when a
    ``.pptx`` is present and the binary is not -- the shell logged a warning and
    left the figure's ``.jpg`` missing, which breaks ``\\includegraphics`` far
    downstream with an opaque error.

    The shell's intermediate ``.tif`` (an ImageMagick ``-compress lzw`` artifact of
    ``convert``) is skipped: the deck is rasterized straight to the ``.png`` the
    rest of the cascade consumes, which is one fewer lossy hop and needs no
    ImageMagick.
    """
    sources = numbered(caption_media_dir, ".pptx")
    if not sources:
        return 0
    binary = shutil.which("libreoffice") or shutil.which("soffice")
    if binary is None:
        raise RuntimeError(
            f"{len(sources)} PPTX figure(s) need conversion but neither "
            f"'libreoffice' nor 'soffice' is on PATH. Fix: install LibreOffice "
            f"(apt install libreoffice-impress), or export the slide yourself and "
            f"place the .png beside the .pptx in {caption_media_dir}."
        )
    converted = 0
    for pptx_file in sources:
        pdf_file = pptx_file.with_suffix(".pdf")
        if pdf_file.exists() and pdf_file.stat().st_mtime >= pptx_file.stat().st_mtime:
            continue
        subprocess.run(
            [
                binary,
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                str(caption_media_dir),
                str(pptx_file),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        converted += 1

    from ..._utils._pdf_images import pdf_to_images

    for pdf_file in numbered(caption_media_dir, ".pdf"):
        png_file = caption_media_dir / f"{pdf_file.stem}.png"
        if png_file.exists() and png_file.stat().st_mtime >= pdf_file.stat().st_mtime:
            continue
        rendered = pdf_to_images(
            str(pdf_file), output_dir=str(caption_media_dir), pages=[0], dpi=600
        )
        if not rendered:
            raise RuntimeError(
                f"LibreOffice produced {pdf_file.name} but it has no renderable "
                f"first page. Re-export the slide and retry."
            )
        shutil.move(rendered[0]["path"], png_file)
        converted += 1
    return converted


def tif_to_png(caption_media_dir: Path) -> int:
    """Cascade step 2: TIF/TIFF -> PNG, refreshed when the source is newer."""
    converted = 0
    for tif_file in numbered(caption_media_dir, ".tif", ".tiff"):
        png_file = caption_media_dir / f"{tif_file.stem}.png"
        if png_file.exists() and png_file.stat().st_mtime >= tif_file.stat().st_mtime:
            continue
        to_png(tif_file, png_file)
        converted += 1
    return converted


def mmd_to_png(caption_media_dir: Path) -> int:
    """Cascade step 3: Mermaid ``.mmd`` -> PNG through the ``mmdc`` CLI.

    Prechecked by :func:`scitex_writer._utils._mermaid_precheck.check_mmdc_or_raise`:
    ``mmdc`` can be on PATH yet unable to start its headless chromium, in which case
    it writes a CORRUPT png. Fails loud with an install hint when a ``.mmd`` is
    present and mmdc is unusable (the shell warned and skipped).
    """
    sources = numbered(caption_media_dir, ".mmd")
    if not sources:
        return 0
    from ..._utils._mermaid_precheck import check_mmdc_or_raise

    binary = check_mmdc_or_raise()
    converted = 0
    for mmd_file in sources:
        png_file = caption_media_dir / f"{mmd_file.stem}.png"
        if png_file.exists() and png_file.stat().st_mtime >= mmd_file.stat().st_mtime:
            continue
        subprocess.run(
            [binary, "-i", str(mmd_file), "-o", str(png_file)],
            capture_output=True,
            text=True,
            check=True,
        )
        converted += 1
    return converted


def png_to_jpg(caption_media_dir: Path) -> int:
    """Cascade step 4: PNG -> JPG (alpha flattened onto white), refreshed if newer.

    A symlinked PNG is read through transparently (Pillow follows the link), so the
    shell's ``cp -L`` temp-file dance is gone.
    """
    converted = 0
    for png_file in numbered(caption_media_dir, ".png"):
        jpg_file = caption_media_dir / f"{png_file.stem}.jpg"
        source_mtime = png_file.resolve().stat().st_mtime
        if jpg_file.exists() and jpg_file.stat().st_mtime >= source_mtime:
            continue
        to_jpg(png_file, jpg_file)
        converted += 1
    return converted


def convert_formats(caption_media_dir: Path, pptx: bool = False) -> int:
    """Stage 5: run the whole conversion cascade; return the conversion count."""
    converted = 0
    if pptx:
        converted += pptx_to_tif(caption_media_dir)
    converted += tif_to_png(caption_media_dir)
    converted += mmd_to_png(caption_media_dir)
    converted += png_to_jpg(caption_media_dir)
    return converted


def panel_groups(caption_media_dir: Path) -> dict:
    """Map ``NN`` -> its sorted panel JPGs (``01a_x.jpg``, ``01b_y.jpg``, ...)."""
    groups: dict = {}
    for jpg_file in numbered(caption_media_dir, ".jpg"):
        letter: Optional[str] = panel_letter(jpg_file.stem)
        if letter is None:
            continue
        number = jpg_file.stem[: jpg_file.stem.index(letter)]
        groups.setdefault(number, []).append(jpg_file)
    for panels in groups.values():
        panels.sort(key=lambda p: p.name)
    return groups


def compose_panels(caption_media_dir: Path) -> int:
    """Stage 6: tile each panel group ``NN<letter>_*.jpg`` into a composite ``NN.jpg``.

    ``NN.jpg`` is exactly the name the float assembler falls back to when a figure
    ``NN_name`` has no ``NN_name.jpg`` of its own, so a panelled figure needs no
    special casing downstream. An existing ``NN.jpg`` is NEVER overwritten -- an
    author who composed the figure themselves keeps their version (shell parity).
    """
    composed = 0
    for number, panels in sorted(panel_groups(caption_media_dir).items()):
        composite = caption_media_dir / f"{number}.jpg"
        if composite.exists():
            continue
        tile_panels(panels, composite)
        composed += 1
    return composed


def link_compilation_jpgs(caption_media_dir: Path, jpg_dir: Path) -> List[str]:
    """Stage 7: place every MAIN JPG into ``jpg_dir`` as a symlink (cp fallback).

    Symlink-first (operator decision 1b, 2026-06-12) so an edit to the upstream
    ``caption_and_media`` copy shows up in the next compile with no re-copy step.
    A filesystem that rejects symlinks (a share mounted ``nosymlinks``) gets a copy
    plus a warning -- degraded, but never silently.
    """
    warnings = []
    for jpg_file in mains(caption_media_dir, ".jpg"):
        dest = jpg_dir / jpg_file.name
        if dest.exists() or dest.is_symlink():
            dest.unlink()
        try:
            dest.symlink_to(jpg_file.resolve())
        except OSError:
            shutil.copyfile(jpg_file, dest)
            warnings.append(
                f"Symlink unsupported on {jpg_dir}; copied {jpg_file.name} instead "
                f"(upstream edits will NOT propagate until the next render)."
            )
    return warnings


def create_placeholders(caption_media_dir: Path, jpg_dir: Path) -> int:
    """Stage 8: a placeholder JPG for every declared-but-missing figure.

    A declared-but-missing figure is normally caught FAIL-LOUD upstream by the
    figure-media gate (``check_figure_media.py``), which aborts the compile before
    this runs. This path only fills in when that gate is warn/off -- the explicit
    draft opt-in (e.g. the public template's example figures, which ship with a
    caption but no media). NEVER a ``.txt``: ``\\includegraphics`` wants a ``.jpg``.
    """
    created = 0
    for caption_file in mains(caption_media_dir, ".tex"):
        stem = caption_file.stem
        number = figure_number(stem)
        if (jpg_dir / f"{stem}.jpg").exists() or (jpg_dir / f"{number}.jpg").exists():
            continue
        placeholder_jpg(jpg_dir / f"{stem}.jpg", stem)
        created += 1
    return created


def crop_compilation_jpgs(jpg_dir: Path) -> int:
    """Optional stage: trim the uniform border off every JPG bound for compilation.

    A symlinked JPG is resolved first, so the crop lands on the real
    ``caption_and_media`` file rather than replacing the link with a file.
    """
    cropped = 0
    for jpg_file in sorted(jpg_dir.glob("*.jpg")):
        if trim_whitespace(jpg_file.resolve()):
            cropped += 1
    return cropped


__all__ = [
    "CAPTION_SOURCE_SUFFIXES",
    "REGENERABLE_SUFFIXES",
    "cleanup_panel_captions",
    "compose_panels",
    "convert_formats",
    "create_placeholders",
    "crop_compilation_jpgs",
    "ensure_caption",
    "ensure_lower_letter_id",
    "figure_number",
    "init_figures",
    "link_compilation_jpgs",
    "mains",
    "mmd_to_png",
    "numbered",
    "panel_groups",
    "png_to_jpg",
    "pptx_to_tif",
    "tif_to_png",
]

# EOF
