#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-05 12:00:00 (ywatanabe)"

"""
Revise TeX files using GPT for improved grammar and style
"""

import os
import sys
import logging
from typing import Optional

from config import GPT_MODEL_DEFAULT, init_env
from gpt_client import GPTClient
from file_utils import load_tex, save_tex, back_up
from prompt_loader import load_prompt

# Initialize environment
init_env()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("revise")

def revise_by_GPT(
    input_path: str,
    output_path: Optional[str] = None,
    model: Optional[str] = None,
    create_backup: bool = True,
    verbose: bool = False,
) -> str:
    """
    Revise a TeX file using GPT for improved grammar and style.
    
    Args:
        input_path: Path to the input TeX file
        output_path: Path to save the revised file (defaults to input_path)
        model: GPT model to use (defaults to GPT_MODEL_DEFAULT)
        create_backup: Whether to create a backup of the input file
        verbose: Whether to print verbose output
        
    Returns:
        The revised text
        
    Raises:
        FileNotFoundError: If the input file does not exist
        IOError: If there's an error reading or writing files
    """
    # Set default output path if not provided
    if output_path is None:
        output_path = input_path
        
    # Load the TeX file
    logger.info(f"Loading TeX file: {input_path}")
    text = load_tex(input_path)
    
    # Load the revision prompt
    prompt_text = load_prompt("revise")
    
    # Initialize GPT client
    gpt = GPTClient(
        model=model or GPT_MODEL_DEFAULT,
        verbose=verbose
    )
    
    # Revise the text
    logger.info(f"Revising {input_path} with {gpt.model}...")
    revised_text = gpt(prompt_text + text)
    
    # Create backup if requested
    if create_backup:
        back_up(input_path)
    
    # Save the revised text
    save_tex(revised_text, output_path)
    logger.info(f"Revised text saved to: {output_path}")
    
    return revised_text

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Revise TeX files using GPT")
    parser.add_argument("--input", "-i", required=True, help="Input file path")
    parser.add_argument("--output", "-o", help="Output file path (defaults to input)")
    parser.add_argument("--model", "-m", help="GPT model to use")
    parser.add_argument("--no-backup", action="store_true", help="Disable backup creation")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    try:
        revise_by_GPT(
            args.input,
            args.output,
            args.model,
            not args.no_backup,
            args.verbose
        )
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        if args.verbose:
            logger.exception("Detailed error information:")
        sys.exit(1)