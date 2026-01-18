#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: optimize_figure.py

import os
import sys
from pathlib import Path

# Add scripts/python to path for imports
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))


# Add your tests here
def test_placeholder():
    """TODO: Add tests for optimize_figure.py"""
    pass


if __name__ == "__main__":
    import pytest

    pytest.main([os.path.abspath(__file__), "-v"])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/scitex-writer/scripts/python/optimize_figure.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# """
# Automatic Figure Optimization for SciTex
#
# This script automatically optimizes figures for publication by:
# 1. Analyzing image dimensions and aspect ratio
# 2. Resizing to optimal resolution for publication
# 3. Enhancing image quality if needed
# 4. Cropping excess whitespace
#
# Usage:
#   python optimize_figure.py --input <input_file> [--output <output_file>] [--dpi <dpi>] [--quality <quality>] [--max-width <pixels>] [--max-height <pixels>]
#
# Options:
#   --input FILE       Input image file (required)
#   --output FILE      Output image file (default: same as input with _optimized suffix)
#   --dpi INT          Target DPI (default: 300)
#   --quality INT      JPEG quality (1-100, default: 90)
#   --max-width INT    Maximum width in pixels (default: 2000)
#   --max-height INT   Maximum height in pixels (default: 2000)
#   --no-crop          Disable automatic cropping (default: crop enabled)
#   --verbose          Enable verbose output
# """
#
# import os
# import sys
# import argparse
# import numpy as np
# from PIL import Image, ImageChops, ImageEnhance, ImageOps
# import logging
#
# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     datefmt='%Y-%m-%d %H:%M:%S'
# )
# logger = logging.getLogger(__name__)
#
# def parse_arguments():
#     """Parse command line arguments."""
#     parser = argparse.ArgumentParser(description='Optimize figures for publication')
#     parser.add_argument('--input', required=True, help='Input image file')
#     parser.add_argument('--output', help='Output image file')
#     parser.add_argument('--dpi', type=int, default=300, help='Target DPI')
#     parser.add_argument('--quality', type=int, default=90, help='JPEG quality (1-100)')
#     parser.add_argument('--max-width', type=int, default=2000, help='Maximum width in pixels')
#     parser.add_argument('--max-height', type=int, default=2000, help='Maximum height in pixels')
#     parser.add_argument('--no-crop', action='store_true', help='Disable automatic cropping')
#     parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
#     return parser.parse_args()
#
# def crop_whitespace(image, padding=10):
#     """
#     Crop excess whitespace from the image.
#
#     Args:
#         image: PIL Image object
#         padding: Number of pixels to keep as padding around content
#
#     Returns:
#         PIL Image with whitespace removed
#     """
#     # Convert to grayscale for analysis
#     bg = Image.new(image.mode, image.size, image.getpixel((0,0)))
#     diff = ImageChops.difference(image, bg)
#     diff = ImageChops.add(diff, diff, 2.0, -100)
#     bbox = diff.getbbox()
#
#     if bbox:
#         # Add padding
#         bbox = (
#             max(0, bbox[0] - padding),
#             max(0, bbox[1] - padding),
#             min(image.width, bbox[2] + padding),
#             min(image.height, bbox[3] + padding)
#         )
#         return image.crop(bbox)
#     return image
#
# def compute_optimal_size(width, height, max_width, max_height, target_dpi=300):
#     """
#     Compute the optimal image size based on max dimensions and DPI.
#
#     Args:
#         width: Current width in pixels
#         height: Current height in pixels
#         max_width: Maximum allowed width in pixels
#         max_height: Maximum allowed height in pixels
#         target_dpi: Target DPI for the image
#
#     Returns:
#         Tuple of (new_width, new_height)
#     """
#     # Calculate aspect ratio
#     aspect_ratio = width / height
#
#     # First check if the image exceeds maximum dimensions
#     if width > max_width or height > max_height:
#         # Scale down to fit within max dimensions
#         if width / max_width > height / max_height:
#             # Width is the limiting factor
#             new_width = max_width
#             new_height = int(new_width / aspect_ratio)
#         else:
#             # Height is the limiting factor
#             new_height = max_height
#             new_width = int(new_height * aspect_ratio)
#     else:
#         # Image is within size limits, check if DPI is sufficient
#         # For publication quality, typically want 300 DPI at print size
#         # Assume 8 inch width for a typical publication
#         publication_width_px = 8 * target_dpi
#         if width < publication_width_px * 0.8:  # If image is less than 80% of desired resolution
#             scale_factor = publication_width_px / width
#             # Limit scaling to 2x to avoid artifacts
#             scale_factor = min(scale_factor, 2.0)
#             new_width = int(width * scale_factor)
#             new_height = int(height * scale_factor)
#         else:
#             # Image is already good quality, no resizing needed
#             new_width, new_height = width, height
#
#     # Ensure dimensions are even numbers (helps with certain compression algorithms)
#     new_width = (new_width // 2) * 2
#     new_height = (new_height // 2) * 2
#
#     return new_width, new_height
#
# def enhance_image_quality(image):
#     """
#     Apply basic enhancement to improve image quality.
#
#     Args:
#         image: PIL Image object
#
#     Returns:
#         Enhanced PIL Image
#     """
#     # Convert to RGB if needed
#     if image.mode != 'RGB':
#         image = image.convert('RGB')
#
#     # Apply moderate contrast enhancement
#     enhancer = ImageEnhance.Contrast(image)
#     image = enhancer.enhance(1.1)
#
#     # Apply moderate sharpening
#     enhancer = ImageEnhance.Sharpness(image)
#     image = enhancer.enhance(1.2)
#
#     return image
#
# def optimize_figure(input_path, output_path=None, target_dpi=300, quality=90,
#                    max_width=2000, max_height=2000, no_crop=False, verbose=False):
#     """
#     Optimize a figure for publication quality.
#
#     Args:
#         input_path: Path to input image
#         output_path: Path to save optimized image (default: auto-generate)
#         target_dpi: Target DPI for the image
#         quality: JPEG quality (1-100)
#         max_width: Maximum width in pixels
#         max_height: Maximum height in pixels
#         no_crop: If True, don't crop whitespace
#         verbose: Enable verbose logging
#
#     Returns:
#         Path to the optimized image
#     """
#     if verbose:
#         logger.setLevel(logging.DEBUG)
#
#     # Generate output path if not provided
#     if not output_path:
#         name, ext = os.path.splitext(input_path)
#         output_path = f"{name}_optimized{ext}"
#
#     logger.info(f"Processing: {input_path}")
#     logger.info(f"Output will be saved to: {output_path}")
#
#     try:
#         # Load the image
#         img = Image.open(input_path)
#         original_width, original_height = img.size
#         logger.info(f"Original dimensions: {original_width}x{original_height} pixels")
#
#         # Step 1: Crop excess whitespace if enabled
#         if not no_crop:
#             logger.debug("Cropping excess whitespace...")
#             img = crop_whitespace(img)
#             cropped_width, cropped_height = img.size
#             logger.info(f"After cropping: {cropped_width}x{cropped_height} pixels")
#             if original_width * original_height > 0:
#                 crop_percentage = 100 - (cropped_width * cropped_height * 100) / (original_width * original_height)
#                 logger.info(f"Removed {crop_percentage:.1f}% of whitespace")
#
#         # Step 2: Determine optimal size
#         current_width, current_height = img.size
#         new_width, new_height = compute_optimal_size(
#             current_width, current_height, max_width, max_height, target_dpi
#         )
#
#         if new_width != current_width or new_height != current_height:
#             logger.info(f"Resizing to {new_width}x{new_height} pixels")
#             # Use high-quality resampling
#             img = img.resize((new_width, new_height), Image.LANCZOS)
#         else:
#             logger.info("Image dimensions are already optimal")
#
#         # Step 3: Enhance image quality
#         logger.debug("Enhancing image quality...")
#         img = enhance_image_quality(img)
#
#         # Step 4: Save with appropriate settings
#         logger.debug(f"Saving with quality={quality}...")
#
#         # Determine format-specific options
#         save_args = {}
#         ext = os.path.splitext(output_path)[1].lower()
#
#         if ext == '.jpg' or ext == '.jpeg':
#             save_args = {'quality': quality, 'optimize': True, 'progressive': True}
#         elif ext == '.png':
#             save_args = {'optimize': True}
#         elif ext == '.tif' or ext == '.tiff':
#             save_args = {'compression': 'tiff_lzw'}
#
#         # Ensure the output directory exists
#         os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
#
#         # Save the optimized image
#         img.save(output_path, **save_args)
#
#         logger.info("Optimization complete")
#         logger.info(f"Final dimensions: {new_width}x{new_height} pixels")
#
#         # Calculate file size reduction
#         original_size = os.path.getsize(input_path)
#         optimized_size = os.path.getsize(output_path)
#         size_reduction = 100 - (optimized_size * 100 / original_size)
#         logger.info(f"File size: {original_size/1024:.1f}KB → {optimized_size/1024:.1f}KB ({size_reduction:.1f}% reduction)")
#
#         return output_path
#
#     except Exception as e:
#         logger.error(f"Error processing image: {e}")
#         return None
#
# def main():
#     """Main function."""
#     args = parse_arguments()
#
#     if not os.path.exists(args.input):
#         logger.error(f"Input file not found: {args.input}")
#         sys.exit(1)
#
#     result = optimize_figure(
#         args.input,
#         args.output,
#         args.dpi,
#         args.quality,
#         args.max_width,
#         args.max_height,
#         args.no_crop,
#         args.verbose
#     )
#
#     if result:
#         logger.info(f"Successfully optimized image: {result}")
#         sys.exit(0)
#     else:
#         logger.error("Failed to optimize image")
#         sys.exit(1)
#
# if __name__ == "__main__":
#     main()
# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/scitex-writer/scripts/python/optimize_figure.py
# --------------------------------------------------------------------------------
