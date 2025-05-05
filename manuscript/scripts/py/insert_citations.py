#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-05 12:10:00 (ywatanabe)"

"""
Insert citations in TeX files using GPT and bibliography
"""

import os
import sys
import logging
from typing import Optional

from config import GPT_MODEL_ADVANCED, init_env
from gpt_client import GPTClient
from file_utils import load_tex, save_tex, back_up, show_diff
from prompt_loader import format_prompt

# Initialize environment
init_env()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("insert_citations")

def insert_citations(
    input_path: str,
    bib_path: str,
    output_path: Optional[str] = None,
    model: Optional[str] = None,
    create_backup: bool = True,
    verbose: bool = False,
    show_changes: bool = True,
) -> str:
    """
    Insert citations in a TeX file using GPT and bibliography.
    
    Args:
        input_path: Path to the input TeX file
        bib_path: Path to the bibliography file
        output_path: Path to save the output file (defaults to input_path)
        model: GPT model to use (defaults to GPT_MODEL_ADVANCED)
        create_backup: Whether to create a backup of the input file
        verbose: Whether to print verbose output
        show_changes: Whether to show the changes made
        
    Returns:
        The modified text with citations inserted
        
    Raises:
        FileNotFoundError: If the input or bibliography file does not exist
        IOError: If there's an error reading or writing files
    """
    # Set default output path if not provided
    if output_path is None:
        output_path = input_path
        
    # Load the TeX and bibliography files
    logger.info(f"Loading TeX file: {input_path}")
    tex_contents = load_tex(input_path)
    
    logger.info(f"Loading bibliography file: {bib_path}")
    bib_contents = load_tex(bib_path)
    
    # Format the prompt with the TeX and bibliography contents
    prompt = format_prompt(
        "insert_citations",
        tex_content=tex_contents,
        bib_content=bib_contents
    )
    
    # Initialize GPT client
    gpt = GPTClient(
        model=model or GPT_MODEL_ADVANCED,
        verbose=verbose
    )
    
    # Insert citations
    logger.info(f"Inserting citations in {input_path} with {gpt.model}...")
    inserted_text = gpt(prompt)
    
    # Create backup if requested
    if create_backup:
        back_up(input_path)
    
    # Save the modified text
    save_tex(inserted_text, output_path)
    logger.info(f"Text with citations saved to: {output_path}")
    
    # Show differences if requested
    if show_changes:
        print("\nChanges made:")
        print(show_diff(tex_contents, inserted_text))
    
    return inserted_text

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Insert citations in TeX files")
    parser.add_argument("--input", "-i", required=True, help="Input file path")
    parser.add_argument("--bib", "-b", required=True, help="Bibliography file path")
    parser.add_argument("--output", "-o", help="Output file path (defaults to input)")
    parser.add_argument("--model", "-m", help="GPT model to use")
    parser.add_argument("--no-backup", action="store_true", help="Disable backup creation")
    parser.add_argument("--no-diff", action="store_true", help="Disable showing changes")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    try:
        insert_citations(
            args.input,
            args.bib,
            args.output,
            args.model,
            not args.no_backup,
            args.verbose,
            not args.no_diff
        )
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        if args.verbose:
            logger.exception("Detailed error information:")
        sys.exit(1)