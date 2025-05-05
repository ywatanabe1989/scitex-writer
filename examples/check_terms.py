#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-05 13:40:00 (ywatanabe)"

"""
Example script for checking terminology consistency in a TeX file.

This script demonstrates the basic usage of the check_terms_by_GPT function.
"""

import os
import sys
import argparse

# Add the SciTex scripts directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../manuscript/scripts/py")))

# Import SciTex modules
from check_terms import check_terms_by_GPT

def main():
    """Main function to parse arguments and check terminology in a TeX file."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Check terminology consistency in a TeX file")
    parser.add_argument("--input", "-i", required=True, help="Input file path")
    parser.add_argument("--model", "-m", help="GPT model to use")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' does not exist.")
        sys.exit(1)
    
    # Check terminology in the TeX file
    try:
        print(f"Checking terminology in '{args.input}'...")
        feedback = check_terms_by_GPT(
            args.input,
            args.model,
            args.verbose
        )
        print("\nTerminology Check Results:")
        print("-------------------------")
        print(feedback)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()