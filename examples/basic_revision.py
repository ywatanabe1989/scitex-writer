#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-05 13:30:00 (ywatanabe)"

"""
Example script for revising a TeX file using GPT.

This script demonstrates the basic usage of the revise_by_GPT function.
"""

import os
import sys
import argparse

# Add the SciTex scripts directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../manuscript/scripts/py")))

# Import SciTex modules
from revise import revise_by_GPT

def main():
    """Main function to parse arguments and revise a TeX file."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Revise a TeX file using GPT")
    parser.add_argument("--input", "-i", required=True, help="Input file path")
    parser.add_argument("--output", "-o", help="Output file path (defaults to input)")
    parser.add_argument("--model", "-m", help="GPT model to use")
    parser.add_argument("--no-backup", action="store_true", help="Disable backup creation")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' does not exist.")
        sys.exit(1)
    
    # Revise the TeX file
    try:
        print(f"Revising '{args.input}'...")
        revised_text = revise_by_GPT(
            args.input,
            args.output,
            args.model,
            not args.no_backup,
            args.verbose
        )
        output_path = args.output or args.input
        print(f"Revision complete. Output saved to '{output_path}'.")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()