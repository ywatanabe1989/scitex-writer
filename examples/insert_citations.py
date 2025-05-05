#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-05 13:35:00 (ywatanabe)"

"""
Example script for inserting citations in a TeX file.

This script demonstrates the basic usage of the insert_citations function.
"""

import os
import sys
import argparse

# Add the SciTex scripts directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../manuscript/scripts/py")))

# Import SciTex modules
from insert_citations import insert_citations

def main():
    """Main function to parse arguments and insert citations in a TeX file."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Insert citations in a TeX file")
    parser.add_argument("--input", "-i", required=True, help="Input file path")
    parser.add_argument("--bib", "-b", required=True, help="Bibliography file path")
    parser.add_argument("--output", "-o", help="Output file path (defaults to input)")
    parser.add_argument("--model", "-m", help="GPT model to use")
    parser.add_argument("--no-backup", action="store_true", help="Disable backup creation")
    parser.add_argument("--no-diff", action="store_true", help="Disable showing changes")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Check if input and bibliography files exist
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' does not exist.")
        sys.exit(1)
        
    if not os.path.exists(args.bib):
        print(f"Error: Bibliography file '{args.bib}' does not exist.")
        sys.exit(1)
    
    # Insert citations in the TeX file
    try:
        print(f"Inserting citations in '{args.input}' using bibliography '{args.bib}'...")
        modified_text = insert_citations(
            args.input,
            args.bib,
            args.output,
            args.model,
            not args.no_backup,
            args.verbose,
            not args.no_diff
        )
        output_path = args.output or args.input
        print(f"Citation insertion complete. Output saved to '{output_path}'.")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()