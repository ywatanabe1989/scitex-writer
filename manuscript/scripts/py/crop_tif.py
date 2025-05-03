#!./.env/bin/python
# -*- coding: utf-8 -*-

import cv2
import numpy as np


def find_content_area(image_path):
    # Read the image
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Unable to read image file: {image_path}")

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Threshold the image to get all non-white areas.
    # Set the threshold close to 255 to exclude only white or nearly white areas.
    _, thresh = cv2.threshold(gray, 254, 255, cv2.THRESH_BINARY_INV)

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


def crop_tif(lpath_tif, margin=30):
    # Read the image
    img = cv2.imread(lpath_tif)

    # Find the content area
    x, y, w, h = find_content_area(lpath_tif)

    # Calculate the coordinates with margin, clamping to the image boundaries
    x_start = max(x - margin, 0)
    y_start = max(y - margin, 0)
    x_end = min(x + w + margin, img.shape[1])
    y_end = min(y + h + margin, img.shape[0])

    # Crop the image using the bounding rectangle with margin
    cropped_img = img[y_start:y_end, x_start:x_end]

    # Save the cropped image
    cv2.imwrite(lpath_tif, cropped_img)
    print(f"\n{lpath_tif} was cropped.")


if __name__ == "__main__":
    import argparse

    # Set up argument parser
    parser = argparse.ArgumentParser(description="Crop TIF images to content area.")
    parser.add_argument(
        "-l", "--lpath_tif", type=str, help="Path to the TIF image file to be cropped."
    )
    parser.add_argument(
        "--margin", type=int, default=30, help="Margin size around the content area."
    )

    # Parse arguments
    args = parser.parse_args()

    # Crop the TIF image
    crop_tif(args.lpath_tif, margin=args.margin)

    # ./.env/bin/python ./scripts/py/crop_tif.py -l ./src/figures/Figure_ID_04.tif
