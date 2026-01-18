#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: crop_tif.py

import os
import sys
from pathlib import Path

# Add scripts/python to path for imports
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))


# Add your tests here
def test_placeholder():
    """TODO: Add tests for crop_tif.py"""
    pass


if __name__ == "__main__":
    import pytest

    pytest.main([os.path.abspath(__file__), "-v"])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/scitex-writer/scripts/python/crop_tif.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# """
# TIF Image Cropping Utility
#
# This script provides functionality for cropping TIF images by automatically
# detecting content areas and removing excess whitespace.
# """
#
# import os
# import argparse
# import cv2
# import numpy as np
# from typing import Tuple, Optional
#
#
# def find_content_area(image_path: str) -> Tuple[int, int, int, int]:
#     """
#     Find the bounding box of the content area in an image.
#
#     Args:
#         image_path: Path to the image file
#
#     Returns:
#         Tuple containing (x, y, width, height) of the content area
#
#     Raises:
#         FileNotFoundError: If the image cannot be read
#     """
#     # Read the image
#     img = cv2.imread(image_path)
#     if img is None:
#         raise FileNotFoundError(f"Unable to read image file: {image_path}")
#
#     # Convert to grayscale
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#
#     # Apply adaptive thresholding for better detection of content
#     # This works better for images with varying brightness
#     thresh = cv2.adaptiveThreshold(
#         gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
#     )
#
#     # Alternative method: standard thresholding
#     # _, thresh = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)
#
#     # Find all non-zero points (colored or non-white pixels)
#     points = cv2.findNonZero(thresh)
#
#     # Get the bounding rectangle around the non-zero points
#     if points is not None:
#         x, y, w, h = cv2.boundingRect(points)
#         return x, y, w, h
#     else:
#         # If no points found, return the whole image
#         h, w = img.shape[:2]
#         return 0, 0, w, h
#
#
# def resize_image(
#     img: np.ndarray,
#     target_dpi: int = 300,
#     max_width: int = 2000,
#     max_height: int = 2000,
#     verbose: bool = False
# ) -> np.ndarray:
#     """
#     Resize an image to meet target DPI and maximum dimensions constraints.
#
#     Args:
#         img: Input image as numpy array
#         target_dpi: Target DPI (dots per inch) for the image
#         max_width: Maximum width in pixels
#         max_height: Maximum height in pixels
#         verbose: Whether to print detailed information
#
#     Returns:
#         Resized image as numpy array
#     """
#     height, width = img.shape[:2]
#
#     # Calculate if resizing is needed
#     if width > max_width or height > max_height:
#         # Determine the scaling factor to fit within max dimensions
#         scale_factor = min(max_width / width, max_height / height)
#
#         # Calculate new dimensions
#         new_width = int(width * scale_factor)
#         new_height = int(height * scale_factor)
#
#         if verbose:
#             print(f"Resizing image from {width}x{height} to {new_width}x{new_height}")
#             print(f"Scale factor: {scale_factor:.2f}")
#
#         # Resize the image
#         resized_img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
#         return resized_img
#     else:
#         if verbose:
#             print(f"No resizing needed, image dimensions {width}x{height} are within limits")
#         return img
#
# def crop_tif(
#     input_path: str,
#     output_path: Optional[str] = None,
#     margin: int = 30,
#     resize: bool = True,
#     target_dpi: int = 300,
#     max_width: int = 2000,
#     max_height: int = 2000,
#     overwrite: bool = False,
#     verbose: bool = False
# ) -> None:
#     """
#     Crop a TIF image to its content area with a specified margin and optionally resize it.
#
#     Args:
#         input_path: Path to the input TIF image
#         output_path: Path to save the cropped image (defaults to input_path if overwrite=True)
#         margin: Margin in pixels to add around the content area
#         resize: Whether to resize the image to meet target constraints
#         target_dpi: Target DPI for the resized image
#         max_width: Maximum width in pixels for the resized image
#         max_height: Maximum height in pixels for the resized image
#         overwrite: Whether to overwrite the input file
#         verbose: Whether to print detailed information
#
#     Raises:
#         FileNotFoundError: If the input image cannot be read
#         ValueError: If output path is not specified and overwrite is False
#     """
#     # Determine output path
#     if output_path is None:
#         if overwrite:
#             output_path = input_path
#         else:
#             raise ValueError("output_path must be specified if overwrite=False")
#
#     # Read the image
#     img = cv2.imread(input_path)
#     if img is None:
#         raise FileNotFoundError(f"Unable to read image file: {input_path}")
#
#     original_height, original_width = img.shape[:2]
#
#     if verbose:
#         print(f"Original image dimensions: {original_width}x{original_height}")
#
#     # Find the content area
#     x, y, w, h = find_content_area(input_path)
#
#     if verbose:
#         print(f"Content area detected at: x={x}, y={y}, width={w}, height={h}")
#
#     # Calculate the coordinates with margin, clamping to the image boundaries
#     x_start = max(x - margin, 0)
#     y_start = max(y - margin, 0)
#     x_end = min(x + w + margin, img.shape[1])
#     y_end = min(y + h + margin, img.shape[0])
#
#     if verbose:
#         print(f"Cropping to: x={x_start}:{x_end}, y={y_start}:{y_end}")
#         print(f"New dimensions: {x_end-x_start}x{y_end-y_start}")
#
#     # Crop the image using the bounding rectangle with margin
#     cropped_img = img[y_start:y_end, x_start:x_end]
#
#     # Resize the image if requested
#     if resize:
#         cropped_img = resize_image(cropped_img, target_dpi, max_width, max_height, verbose)
#
#     # Save the processed image
#     cv2.imwrite(output_path, cropped_img)
#
#     # Calculate space saved
#     final_height, final_width = cropped_img.shape[:2]
#     area_reduction = 1 - ((final_width * final_height) / (original_width * original_height))
#     area_reduction_pct = area_reduction * 100
#
#     print(f"Image processed: {input_path}")
#     print(f"Size changed from {original_width}x{original_height} to {final_width}x{final_height}")
#     print(f"Saved {area_reduction_pct:.1f}% of the original area")
#
#     if output_path != input_path:
#         print(f"Saved to: {output_path}")
#
#
# def batch_crop_tifs(
#     directory: str,
#     output_directory: Optional[str] = None,
#     margin: int = 30,
#     resize: bool = True,
#     target_dpi: int = 300,
#     max_width: int = 2000,
#     max_height: int = 2000,
#     recursive: bool = False,
#     verbose: bool = False
# ) -> None:
#     """
#     Process all TIF files in a directory.
#
#     Args:
#         directory: Directory containing TIF files to process
#         output_directory: Directory to save processed files (defaults to same as input)
#         margin: Margin to add around the content area
#         resize: Whether to resize images to meet target constraints
#         target_dpi: Target DPI for resized images
#         max_width: Maximum width in pixels for resized images
#         max_height: Maximum height in pixels for resized images
#         recursive: Whether to process subdirectories
#         verbose: Whether to print detailed information
#     """
#     if not os.path.isdir(directory):
#         raise ValueError(f"Directory not found: {directory}")
#
#     # Create output directory if it doesn't exist
#     if output_directory and not os.path.exists(output_directory):
#         os.makedirs(output_directory)
#
#     # Get the list of TIF files
#     files = []
#     if recursive:
#         for root, _, filenames in os.walk(directory):
#             for filename in filenames:
#                 if filename.lower().endswith(('.tif', '.tiff')):
#                     files.append(os.path.join(root, filename))
#     else:
#         files = [os.path.join(directory, f) for f in os.listdir(directory)
#                 if f.lower().endswith(('.tif', '.tiff'))]
#
#     print(f"Found {len(files)} TIF files to process")
#
#     # Process each file
#     for index, file_path in enumerate(files):
#         if verbose:
#             print(f"\nProcessing [{index+1}/{len(files)}]: {file_path}")
#         else:
#             print(f"Processing [{index+1}/{len(files)}]: {os.path.basename(file_path)}")
#
#         # Determine output path
#         if output_directory:
#             rel_path = os.path.relpath(file_path, directory)
#             output_path = os.path.join(output_directory, rel_path)
#
#             # Create subdirectories if needed
#             output_subdir = os.path.dirname(output_path)
#             if not os.path.exists(output_subdir):
#                 os.makedirs(output_subdir)
#         else:
#             output_path = file_path
#
#         # Process the image
#         try:
#             crop_tif(
#                 file_path,
#                 output_path,
#                 margin,
#                 resize,
#                 target_dpi,
#                 max_width,
#                 max_height,
#                 output_path == file_path,
#                 verbose
#             )
#         except Exception as e:
#             print(f"Error processing {file_path}: {e}")
#
#
# def main():
#     """Main function to parse arguments and execute the appropriate action."""
#     # Set up argument parser
#     parser = argparse.ArgumentParser(
#         description="Process TIF images: crop to content area, resize, and optimize for publications.",
#         formatter_class=argparse.ArgumentDefaultsHelpFormatter
#     )
#
#     # Add subparsers for the different modes
#     subparsers = parser.add_subparsers(dest="mode", help="Operation mode")
#
#     # Single file mode
#     file_parser = subparsers.add_parser("file", help="Process a single file")
#     file_parser.add_argument("-i", "--input", required=True, help="Input TIF file path")
#     file_parser.add_argument("-o", "--output", help="Output TIF file path (defaults to input if --overwrite)")
#     file_parser.add_argument("--overwrite", action="store_true", help="Overwrite the input file")
#
#     # Batch mode
#     batch_parser = subparsers.add_parser("batch", help="Process multiple files")
#     batch_parser.add_argument("-d", "--directory", required=True, help="Directory containing TIF files")
#     batch_parser.add_argument("-o", "--output-directory", help="Output directory for processed files")
#     batch_parser.add_argument("-r", "--recursive", action="store_true", help="Process subdirectories recursively")
#
#     # Common arguments
#     for subparser in [file_parser, batch_parser]:
#         subparser.add_argument("--margin", type=int, default=30, help="Margin size around the content area")
#         subparser.add_argument("--no-resize", action="store_true", help="Disable automatic resizing")
#         subparser.add_argument("--dpi", type=int, default=300, help="Target DPI for resized images")
#         subparser.add_argument("--max-width", type=int, default=2000, help="Maximum width in pixels")
#         subparser.add_argument("--max-height", type=int, default=2000, help="Maximum height in pixels")
#         subparser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
#
#     # Parse arguments
#     args = parser.parse_args()
#
#     # Execute the appropriate action
#     if args.mode == "file":
#         crop_tif(
#             args.input,
#             args.output,
#             args.margin,
#             not args.no_resize,  # Invert --no-resize flag to get resize boolean
#             args.dpi,
#             args.max_width,
#             args.max_height,
#             args.overwrite,
#             args.verbose
#         )
#     elif args.mode == "batch":
#         batch_crop_tifs(
#             args.directory,
#             args.output_directory,
#             args.margin,
#             not args.no_resize,  # Invert --no-resize flag to get resize boolean
#             args.dpi,
#             args.max_width,
#             args.max_height,
#             args.recursive,
#             args.verbose
#         )
#     else:
#         parser.print_help()
#
#
# if __name__ == "__main__":
#     main()
# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/scitex-writer/scripts/python/crop_tif.py
# --------------------------------------------------------------------------------
