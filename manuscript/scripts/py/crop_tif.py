#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TIF Image Cropping Utility

This script provides functionality for cropping TIF images by automatically 
detecting content areas and removing excess whitespace.
"""

import os
import argparse
import cv2
import numpy as np
from typing import Tuple, Optional


def find_content_area(image_path: str) -> Tuple[int, int, int, int]:
    """
    Find the bounding box of the content area in an image.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Tuple containing (x, y, width, height) of the content area
        
    Raises:
        FileNotFoundError: If the image cannot be read
    """
    # Read the image
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Unable to read image file: {image_path}")

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply adaptive thresholding for better detection of content
    # This works better for images with varying brightness
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )
    
    # Alternative method: standard thresholding
    # _, thresh = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)

    # Find all non-zero points (colored or non-white pixels)
    points = cv2.findNonZero(thresh)

    # Get the bounding rectangle around the non-zero points
    if points is not None:
        x, y, w, h = cv2.boundingRect(points)
        return x, y, w, h
    else:
        # If no points found, return the whole image
        h, w = img.shape[:2]
        return 0, 0, w, h


def crop_tif(
    input_path: str, 
    output_path: Optional[str] = None, 
    margin: int = 30,
    overwrite: bool = False,
    verbose: bool = False
) -> None:
    """
    Crop a TIF image to its content area with a specified margin.
    
    Args:
        input_path: Path to the input TIF image
        output_path: Path to save the cropped image (defaults to input_path if overwrite=True)
        margin: Margin in pixels to add around the content area
        overwrite: Whether to overwrite the input file
        verbose: Whether to print detailed information
        
    Raises:
        FileNotFoundError: If the input image cannot be read
        ValueError: If output path is not specified and overwrite is False
    """
    # Determine output path
    if output_path is None:
        if overwrite:
            output_path = input_path
        else:
            raise ValueError("output_path must be specified if overwrite=False")
    
    # Read the image
    img = cv2.imread(input_path)
    if img is None:
        raise FileNotFoundError(f"Unable to read image file: {input_path}")
    
    original_height, original_width = img.shape[:2]
    
    if verbose:
        print(f"Original image dimensions: {original_width}x{original_height}")

    # Find the content area
    x, y, w, h = find_content_area(input_path)
    
    if verbose:
        print(f"Content area detected at: x={x}, y={y}, width={w}, height={h}")

    # Calculate the coordinates with margin, clamping to the image boundaries
    x_start = max(x - margin, 0)
    y_start = max(y - margin, 0)
    x_end = min(x + w + margin, img.shape[1])
    y_end = min(y + h + margin, img.shape[0])
    
    if verbose:
        print(f"Cropping to: x={x_start}:{x_end}, y={y_start}:{y_end}")
        print(f"New dimensions: {x_end-x_start}x{y_end-y_start}")

    # Crop the image using the bounding rectangle with margin
    cropped_img = img[y_start:y_end, x_start:x_end]

    # Save the cropped image
    cv2.imwrite(output_path, cropped_img)
    
    # Calculate space saved
    new_height, new_width = cropped_img.shape[:2]
    area_reduction = 1 - ((new_width * new_height) / (original_width * original_height))
    area_reduction_pct = area_reduction * 100
    
    print(f"Image cropped: {input_path}")
    print(f"Size reduced from {original_width}x{original_height} to {new_width}x{new_height}")
    print(f"Saved {area_reduction_pct:.1f}% of the original area")
    
    if output_path != input_path:
        print(f"Saved to: {output_path}")


def batch_crop_tifs(
    directory: str, 
    output_directory: Optional[str] = None,
    margin: int = 30, 
    recursive: bool = False,
    verbose: bool = False
) -> None:
    """
    Process all TIF files in a directory.
    
    Args:
        directory: Directory containing TIF files to process
        output_directory: Directory to save processed files (defaults to same as input)
        margin: Margin to add around the content area
        recursive: Whether to process subdirectories
        verbose: Whether to print detailed information
    """
    if not os.path.isdir(directory):
        raise ValueError(f"Directory not found: {directory}")
    
    # Create output directory if it doesn't exist
    if output_directory and not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    # Get the list of TIF files
    files = []
    if recursive:
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                if filename.lower().endswith(('.tif', '.tiff')):
                    files.append(os.path.join(root, filename))
    else:
        files = [os.path.join(directory, f) for f in os.listdir(directory) 
                if f.lower().endswith(('.tif', '.tiff'))]
    
    # Process each file
    for file_path in files:
        if verbose:
            print(f"\nProcessing: {file_path}")
        
        # Determine output path
        if output_directory:
            rel_path = os.path.relpath(file_path, directory)
            output_path = os.path.join(output_directory, rel_path)
            
            # Create subdirectories if needed
            output_subdir = os.path.dirname(output_path)
            if not os.path.exists(output_subdir):
                os.makedirs(output_subdir)
        else:
            output_path = file_path
        
        # Crop the image
        try:
            crop_tif(file_path, output_path, margin, output_path == file_path, verbose)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")


def main():
    """Main function to parse arguments and execute the appropriate action."""
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Crop TIF images to content area with margin.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Add subparsers for the different modes
    subparsers = parser.add_subparsers(dest="mode", help="Operation mode")
    
    # Single file mode
    file_parser = subparsers.add_parser("file", help="Process a single file")
    file_parser.add_argument("-i", "--input", required=True, help="Input TIF file path")
    file_parser.add_argument("-o", "--output", help="Output TIF file path (defaults to input if --overwrite)")
    file_parser.add_argument("--overwrite", action="store_true", help="Overwrite the input file")
    
    # Batch mode
    batch_parser = subparsers.add_parser("batch", help="Process multiple files")
    batch_parser.add_argument("-d", "--directory", required=True, help="Directory containing TIF files")
    batch_parser.add_argument("-o", "--output-directory", help="Output directory for processed files")
    batch_parser.add_argument("-r", "--recursive", action="store_true", help="Process subdirectories recursively")
    
    # Common arguments
    for subparser in [file_parser, batch_parser]:
        subparser.add_argument("--margin", type=int, default=30, help="Margin size around the content area")
        subparser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute the appropriate action
    if args.mode == "file":
        crop_tif(
            args.input, 
            args.output, 
            args.margin, 
            args.overwrite,
            args.verbose
        )
    elif args.mode == "batch":
        batch_crop_tifs(
            args.directory, 
            args.output_directory,
            args.margin, 
            args.recursive,
            args.verbose
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()