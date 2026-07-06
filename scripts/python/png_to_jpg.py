#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ROLE: engine-vendored — DO NOT edit here. `scitex-writer update-project`
# overwrites this file on every re-vendor; fix it upstream in the
# scitex-writer package instead (local edits are lost, and update-project
# may set it read-only in the consumer workspace after vendoring).
# File: scripts/python/png_to_jpg.py
# Purpose: Pillow-based PNG->JPG fallback for the figure pipeline, used when
#          ImageMagick (magick/convert) is absent. Flattens alpha onto a white
#          background and saves JPEG quality 95 (matching the ImageMagick
#          `-background white -flatten -quality 95` behavior). Also generates a
#          plain placeholder JPG (so a missing figure never leaves a broken
#          `.txt` where the compile expects a `.jpg`).
#
# Usage:
#   python3 png_to_jpg.py OUT.jpg --src IN.png
#   python3 png_to_jpg.py OUT.jpg --placeholder "Missing figure: NN"
#
# Exit 0 on success; non-zero (with a loud stderr hint) if Pillow is missing or
# conversion fails — the caller treats that as fail-loud, never a silent no-op.

import argparse
import sys


def _flatten_to_white(img):
    """Composite an image (any mode) onto an opaque white background, RGB."""
    from PIL import Image

    rgba = img.convert("RGBA")
    bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    return Image.alpha_composite(bg, rgba).convert("RGB")


def convert_png_to_jpg(src, dst, quality=95):
    """Convert a PNG (alpha flattened onto white) to JPEG at ``dst``."""
    from PIL import Image

    with Image.open(src) as img:
        _flatten_to_white(img).save(dst, "JPEG", quality=quality)


def write_placeholder_jpg(text, dst, size=(800, 600)):
    """Write a light-gray placeholder JPEG bearing ``text``."""
    from PIL import Image, ImageDraw

    img = Image.new("RGB", size, (211, 211, 211))
    draw = ImageDraw.Draw(img)
    draw.text((20, size[1] // 2), text, fill=(64, 64, 64))
    img.save(dst, "JPEG", quality=95)


def main(argv):
    parser = argparse.ArgumentParser(
        description="PNG->JPG (Pillow fallback) + placeholder JPG generator."
    )
    parser.add_argument("dst", help="output .jpg path")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--src", help="input .png to convert")
    group.add_argument("--placeholder", help="text for a placeholder JPG")
    args = parser.parse_args(argv[1:])

    try:
        if args.src is not None:
            convert_png_to_jpg(args.src, args.dst)
        else:
            write_placeholder_jpg(args.placeholder, args.dst)
    except ImportError:
        sys.stderr.write(
            "ERROR: Pillow not installed and ImageMagick unavailable — cannot "
            "render figures. Fix: install ImageMagick (magick/convert) or "
            "`pip install pillow`.\n"
        )
        return 1
    except Exception as exc:  # noqa: BLE001 - surface any conversion failure loudly
        sys.stderr.write(f"ERROR: PNG->JPG conversion failed for {args.dst}: {exc}\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

# EOF
