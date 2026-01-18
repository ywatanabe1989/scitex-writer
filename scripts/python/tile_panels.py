#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-28 17:52:54 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/neurovista/paper/scripts/python/tile_panels.py
# ----------------------------------------
from __future__ import annotations

import os

__FILE__ = "./scripts/python/tile_panels.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Auto-detects panel images using naming convention
  - Creates tiled figures with automatic layout
  - Adds panel labels (A, B, C, D)
  - Integrates with SciTeX figure processing

Dependencies:
  - packages:
    - PIL (Pillow)
    - numpy

IO:
  - input-files:
    - .XX_name_A.jpg, .XX_name_B.jpg, etc.
  - output-files:
    - .XX_name.jpg (tiled composite)
"""

import argparse
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def detect_panels(figure_base, search_dir):
    """Detect panel files following naming convention."""
    panels = {}
    search_path = Path(search_dir)

    # Extract figure ID from base (e.g., "01" from "01_demographic_data")
    figure_id = figure_base.split("_")[0]  # XX_name -> XX

    # Look for panel files: 01a_name.jpg, 01b_name.jpg, etc. (new naming convention)
    for panel_file in search_path.glob(f"{figure_id}[a-zA-Z]_*.jpg"):
        # Extract panel letter from filename (e.g., "a" from "01a_name.jpg")
        filename = panel_file.stem
        # Find the position where the figure ID ends and panel letter begins
        id_part = f"{figure_id}"
        panel_letter = filename[
            len(id_part)
        ].upper()  # Get the letter and convert to uppercase
        panels[panel_letter] = str(panel_file)

    return dict(sorted(panels.items()))  # Sort by panel letter


def calculate_layout(num_panels):
    """Calculate optimal grid layout for given number of panels."""
    if num_panels == 1:
        return (1, 1)
    elif num_panels == 2:
        return (1, 2)  # 1 row, 2 cols
    elif num_panels == 3:
        return (1, 3)  # 1 row, 3 cols
    elif num_panels == 4:
        return (2, 2)  # 2 rows, 2 cols
    elif num_panels <= 6:
        return (2, 3)  # 2 rows, 3 cols
    elif num_panels <= 9:
        return (3, 3)  # 3 rows, 3 cols
    else:
        # For larger numbers, try to make it roughly square
        cols = math.ceil(math.sqrt(num_panels))
        rows = math.ceil(num_panels / cols)
        return (rows, cols)


def add_panel_label(image, label, position="top-left", font_size=72):
    """Add prominent panel label for presentations."""
    draw = ImageDraw.Draw(image)

    # Try to get a larger font, fall back to default
    font = None
    try:
        # Try system fonts in order of preference
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/System/Library/Fonts/Arial.ttf",
            "/Windows/Fonts/arial.ttf",
        ]
        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, font_size)
                break
            except:
                continue
    except:
        pass

    # If no TTF font found, use default
    if font is None:
        font = ImageFont.load_default()

    # Make labels VERY prominent - large white box with thick border
    margin = 30
    x, y = margin, margin

    # Very large white box with black text - unmissable for presentations
    padding = 20
    box_size = 120

    # Create elegant transparent label - no background box needed
    # Just use text with strong outline for visibility

    # Center the text in the box with large font
    text_x = x + (box_size - padding) // 3
    text_y = y + (box_size - padding) // 3

    # Create elegant text with strong white outline for visibility on any background
    outline_width = 4

    # Draw white outline
    for offset_x in range(-outline_width, outline_width + 1):
        for offset_y in range(-outline_width, outline_width + 1):
            if offset_x != 0 or offset_y != 0:  # Don't draw on center
                draw.text(
                    (text_x + offset_x, text_y + offset_y),
                    label,
                    fill="white",
                    font=font,
                )

    # Draw black text on top for maximum contrast
    draw.text((text_x, text_y), label, fill="black", font=font)

    # print(f"Added BOLD label '{label}' at position ({text_x}, {text_y}) with box size {box_size}")
    return image


def add_panel_label_to_composite(
    composite_image, label, panel_x, panel_y, font_size=200
):
    """Add panel label directly to the composite tiled image."""
    draw = ImageDraw.Draw(composite_image)

    # Use a proper TrueType font - prefer serif for scientific papers
    font = None
    font_paths = [
        "/usr/share/fonts/liberation-serif/LiberationSerif-Bold.ttf",  # Serif for papers
        "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf",  # Fallback sans
        "/usr/share/fonts/liberation-sans/LiberationSans-Bold.ttf",
    ]

    for font_path in font_paths:
        try:
            font = ImageFont.truetype(font_path, font_size)
            # print(f"Using font: {font_path}")
            break
        except:
            continue

    if font is None:
        # print("Warning: No TrueType font found, using default")
        font = ImageFont.load_default()

    # Position label in top-left corner of this panel
    margin = 80
    text_x = panel_x + margin
    text_y = panel_y + margin

    # Draw the label using the proper font
    # First draw a white outline for contrast
    outline_width = 5
    for offset_x in range(-outline_width, outline_width + 1):
        for offset_y in range(-outline_width, outline_width + 1):
            if offset_x != 0 or offset_y != 0:
                draw.text(
                    (text_x + offset_x, text_y + offset_y),
                    label,
                    fill="white",
                    font=font,
                )

    # Then draw black text on top
    draw.text((text_x, text_y), label, fill="black", font=font)

    # print(f"Added label '{label}' to composite at ({text_x}, {text_y}) with font size {font_size}")


def tile_images(panels, output_path, spacing=20, dpi=300):
    """Create tiled image from panel dictionary."""
    if not panels:
        # print("No panels found for tiling")
        return False

    # Load all panel images (without labels yet)
    images = {}
    for label, path in panels.items():
        try:
            img = Image.open(path)
            images[label] = img
            # print(f"Loaded panel {label}: {img.size}")
        except Exception:
            # print(f"Error loading panel {label} from {path}: {e}")
            return False

    if not images:
        # print("No valid images loaded")
        return False

    # Calculate layout
    num_panels = len(images)
    rows, cols = calculate_layout(num_panels)
    # print(f"Using {rows}x{cols} layout for {num_panels} panels")

    # Force all panels to exactly the same dimensions for perfect consistency
    # Use dimensions from panels A, B, C (which are the same) as the standard
    standard_panels = [img for label, img in images.items() if label in ["A", "B", "C"]]
    if standard_panels:
        target_width = standard_panels[0].width  # Use A, B, C dimensions
        target_height = standard_panels[0].height
    else:
        # Fallback to reasonable dimensions
        target_width = 1889
        target_height = 1200

    # print(f"Forcing all panels to exact same size: {target_width}×{target_height}")

    # Resize ALL panels (including A, B, C) to ensure perfect consistency
    for label in images:
        images[label].size
        images[label] = images[label].resize(
            (target_width, target_height), Image.Resampling.LANCZOS
        )
        # print(f"Panel {label}: {original_size} → {target_width}×{target_height}")

    # Calculate final image dimensions
    total_width = cols * target_width + (cols - 1) * spacing
    total_height = rows * target_height + (rows - 1) * spacing

    # Create composite image
    composite = Image.new("RGB", (total_width, total_height), "white")

    # Place images in grid and add labels AFTER tiling
    panel_labels = sorted(images.keys())
    for i, label in enumerate(panel_labels):
        if i >= rows * cols:
            break  # Skip extra panels if any

        row = i // cols
        col = i % cols

        x = col * (target_width + spacing)
        y = row * (target_height + spacing)

        composite.paste(images[label], (x, y))
        # print(f"Placed panel {label} at position ({row}, {col})")

        # Now add the label to the composite image at the correct position
        add_panel_label_to_composite(composite, label, x, y)
        # print(f"Added label {label} to tiled image at position ({x}, {y})")

    # Save with high quality
    composite.save(output_path, "JPEG", quality=95, dpi=(dpi, dpi))
    # print(f"Tiled figure saved: {output_path}")
    # print(f"Final dimensions: {composite.size}")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Tile figure panels with automatic layout"
    )
    parser.add_argument(
        "--figure-base",
        required=True,
        help="Base figure name (e.g., .01_workflow)",
    )
    parser.add_argument(
        "--search-dir",
        required=True,
        help="Directory to search for panel files",
    )
    parser.add_argument("--output", required=True, help="Output tiled image path")
    parser.add_argument(
        "--spacing",
        type=int,
        default=20,
        help="Spacing between panels in pixels",
    )
    parser.add_argument("--dpi", type=int, default=300, help="Output DPI")

    args = parser.parse_args()

    # Detect panels
    panels = detect_panels(args.figure_base, args.search_dir)

    if not panels:
        # print(f"No panels found for {args.figure_base} in {args.search_dir}")
        # print("Looking for files like: {}_A.jpg, {}_B.jpg, etc.".format(args.figure_base, args.figure_base))
        return 1

    # print(f"Found {len(panels)} panels: {list(panels.keys())}")

    # Create tiled image
    if tile_images(panels, args.output, args.spacing, args.dpi):
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())

# EOF
