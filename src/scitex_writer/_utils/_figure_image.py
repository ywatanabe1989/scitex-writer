#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_utils/_figure_image.py

r"""The single image backend of the writer's figure engine (Pillow).

Absorbs ``scripts/python/png_to_jpg.py`` + ``scripts/python/tile_panels.py`` into
the package and REPLACES the shell engine's ImageMagick-first cascade
(``magick`` -> ``convert`` -> ``mogrify`` -> ``montage``, each with a silent
``command -v`` fallthrough) with ONE Pillow backend.

Why one backend (same reasoning as ``_csv_table``): the shell picked a different
tool per host, so the SAME manuscript produced different bytes on different
machines -- and when NO ImageMagick binary was present, ``crop_image`` and
``tile_with_imagemagick`` degraded SILENTLY (crop became a no-op; tiling
``cp``-ed the first panel and called it a composite). Pillow is already a core
runtime dependency of this package, so one backend is always available and the
output is host-independent by construction.

Every entry point here fails LOUD -- a missing/unreadable image raises rather
than leaving a ``.jpg`` absent, because an absent ``.jpg`` silently breaks the
figure's ``\includegraphics`` far downstream in the LaTeX run.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import List, Optional, Sequence, Tuple, Union

JPEG_QUALITY = 95
"""JPEG quality of every JPG this engine writes (the shell's ``-quality 95``)."""

PANEL_SPACING = 20
"""Pixels of white gutter between tiled panels (the shell's ``-geometry +20+20``)."""

PLACEHOLDER_SIZE = (800, 600)
"""Pixel size of a missing-figure placeholder (the shell's ``-size 800x600``)."""

TRIM_FUZZ = 16
"""Per-channel tolerance when trimming a border (ImageMagick's ``-fuzz``)."""

_LABEL_FONTS = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/liberation-serif/LiberationSerif-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
)


def _open(path: Union[str, Path]):
    """Open an image, raising an actionable error when it cannot be read."""
    from PIL import Image, UnidentifiedImageError

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")
    try:
        return Image.open(path)
    except UnidentifiedImageError as exc:
        raise ValueError(
            f"{path} is not a readable image (corrupt, or an unsupported format "
            f"for Pillow). Re-export it as PNG/TIFF/JPEG."
        ) from exc


def flatten_to_white(image):
    """Composite any image mode onto an opaque white background, as RGB.

    JPEG has no alpha channel: without this an RGBA source saves with a BLACK
    background (Pillow) or is rejected outright, both of which silently ruin a
    transparent-background figure.
    """
    from PIL import Image

    rgba = image.convert("RGBA")
    background = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    return Image.alpha_composite(background, rgba).convert("RGB")


def to_jpg(
    src: Union[str, Path], dst: Union[str, Path], quality: int = JPEG_QUALITY
) -> Path:
    """Convert any Pillow-readable image to JPEG, flattening alpha onto white.

    Parity with the shell's ``magick <src> -background white -flatten -quality 95``.
    """
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    with _open(src) as image:
        flatten_to_white(image).save(dst, "JPEG", quality=quality)
    return dst


def to_png(src: Union[str, Path], dst: Union[str, Path]) -> Path:
    """Convert any Pillow-readable image (typically TIF/TIFF) to PNG.

    Alpha is PRESERVED here -- PNG supports it, and the flatten happens later in
    :func:`to_jpg`. Parity with the shell's ``convert <tif> <png>``.
    """
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    with _open(src) as image:
        if image.mode not in ("RGB", "RGBA", "L", "LA", "P"):
            image = image.convert("RGBA")
        image.save(dst, "PNG")
    return dst


def trim_whitespace(path: Union[str, Path], fuzz: int = TRIM_FUZZ) -> bool:
    """Crop uniform border padding off an image IN PLACE; True if anything went.

    The Pillow equivalent of ``mogrify -trim +repage``: the border colour is read
    from the top-left pixel and the image is cropped to the bounding box of
    everything that differs from it by more than ``fuzz``.

    The tolerance is not optional. A JPEG's hard edges ring: a red square on white
    leaves a halo of near-white pixels several px out, so a zero-tolerance bounding
    box "crops" almost nothing. ImageMagick carries ``-fuzz`` for exactly this
    reason. A fully uniform image is left untouched -- cropping it to its (empty)
    bbox would destroy the figure.
    """
    from PIL import Image, ImageChops

    path = Path(path)
    with _open(path) as image:
        rgb = image.convert("RGB")
        border = Image.new("RGB", rgb.size, rgb.getpixel((0, 0)))
        difference = ImageChops.difference(rgb, border).convert("L")
        mask = difference.point(lambda level: 255 if level > fuzz else 0)
        bbox = mask.getbbox()
        if bbox is None or bbox == (0, 0, rgb.width, rgb.height):
            return False
        rgb.crop(bbox).save(path, "JPEG", quality=JPEG_QUALITY)
    return True


def placeholder_jpg(
    dst: Union[str, Path],
    figure_name: str,
    size: Tuple[int, int] = PLACEHOLDER_SIZE,
) -> Path:
    """Write a light-gray "Missing Figure" placeholder JPEG.

    NEVER a ``.txt``: ``\\includegraphics`` expects a ``.jpg``, and a stray text
    file breaks the compile with an opaque error far from the real cause.
    """
    from PIL import Image, ImageDraw

    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", size, (211, 211, 211))
    draw = ImageDraw.Draw(image)
    draw.text((20, size[1] // 2), f"Missing Figure\n{figure_name}", fill=(64, 64, 64))
    image.save(dst, "JPEG", quality=JPEG_QUALITY)
    return dst


def calculate_layout(num_panels: int) -> Tuple[int, int]:
    """Grid ``(rows, cols)`` for ``num_panels`` panels (port of tile_panels.py)."""
    if num_panels <= 0:
        raise ValueError(f"num_panels must be positive, got {num_panels}")
    fixed = {1: (1, 1), 2: (1, 2), 3: (1, 3), 4: (2, 2), 5: (2, 3), 6: (2, 3)}
    if num_panels in fixed:
        return fixed[num_panels]
    if num_panels <= 9:
        return (3, 3)
    cols = math.ceil(math.sqrt(num_panels))
    return (math.ceil(num_panels / cols), cols)


def panel_letter(stem: str) -> Optional[str]:
    """The panel letter of a stem like ``01a_overview`` -> ``"a"``; None if not one.

    A PANEL is ``<digits><letter>_<rest>``. A MAIN figure (``01_overview``) has no
    letter and returns None -- this single predicate is what keeps captions,
    linking and tiling from ever treating a panel as a figure.
    """
    index = 0
    while index < len(stem) and stem[index].isdigit():
        index += 1
    if index == 0 or index >= len(stem):
        return None
    if not stem[index].isalpha():
        return None
    if index + 1 >= len(stem) or stem[index + 1] != "_":
        return None
    return stem[index]


def _label_font(size: int):
    from PIL import ImageFont

    for candidate in _LABEL_FONTS:
        if Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size)
            except OSError:
                continue
    return ImageFont.load_default()


def _draw_panel_label(canvas, label: str, x: int, y: int, font_size: int) -> None:
    """Stamp a panel label (A, B, ...) with a white outline for contrast."""
    from PIL import ImageDraw

    draw = ImageDraw.Draw(canvas)
    font = _label_font(font_size)
    margin = max(8, font_size // 3)
    text_x, text_y = x + margin, y + margin
    outline = max(1, font_size // 20)
    for dx in range(-outline, outline + 1):
        for dy in range(-outline, outline + 1):
            if dx or dy:
                draw.text((text_x + dx, text_y + dy), label, fill="white", font=font)
    draw.text((text_x, text_y), label, fill="black", font=font)


def tile_panels(
    panels: Sequence[Union[str, Path]],
    dst: Union[str, Path],
    spacing: int = PANEL_SPACING,
    dpi: int = 300,
) -> Path:
    """Tile panel images into ONE labelled composite JPEG at ``dst``.

    Panels are placed in reading order into the :func:`calculate_layout` grid, all
    resized to the FIRST panel's dimensions (so the grid is regular), separated by
    ``spacing`` px of white, and stamped with uppercase labels ``A``, ``B``, ...
    in reading order.

    Raises ValueError on an empty panel list -- the shell's silent
    ``cp <first panel> <composite>`` "fallback" is exactly the bug this replaces.
    """
    from PIL import Image

    panels = [Path(p) for p in panels]
    if not panels:
        raise ValueError(f"Cannot tile {dst}: no panel images were given.")

    images: List = [_open(p).convert("RGB") for p in panels]
    try:
        width, height = images[0].size
        rows, cols = calculate_layout(len(images))
        canvas = Image.new(
            "RGB",
            (
                cols * width + (cols - 1) * spacing,
                rows * height + (rows - 1) * spacing,
            ),
            "white",
        )
        font_size = max(24, height // 12)
        for index, image in enumerate(images):
            if image.size != (width, height):
                image = image.resize((width, height), Image.Resampling.LANCZOS)
            x = (index % cols) * (width + spacing)
            y = (index // cols) * (height + spacing)
            canvas.paste(image, (x, y))
            _draw_panel_label(canvas, chr(ord("A") + index), x, y, font_size)
    finally:
        for image in images:
            image.close()

    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(dst, "JPEG", quality=JPEG_QUALITY, dpi=(dpi, dpi))
    return dst


__all__ = [
    "JPEG_QUALITY",
    "PANEL_SPACING",
    "PLACEHOLDER_SIZE",
    "TRIM_FUZZ",
    "calculate_layout",
    "flatten_to_white",
    "panel_letter",
    "placeholder_jpg",
    "tile_panels",
    "to_jpg",
    "to_png",
    "trim_whitespace",
]

# EOF
