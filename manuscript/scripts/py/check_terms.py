#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-05 12:05:00 (ywatanabe)"

"""
Check terminology consistency in TeX files using GPT
"""

import os
import sys
import re
import logging
from typing import Optional

from config import GPT_MODEL_ADVANCED, init_env
from gpt_client import GPTClient
from file_utils import load_tex
from prompt_loader import load_prompt

# Initialize environment
init_env()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("check_terms")

def preprocess_tex(text: str) -> str:
    """
    Preprocess TeX content to remove LaTeX commands except for cite and ref.
    
    Args:
        text: The TeX content to preprocess
        
    Returns:
        Preprocessed text with most LaTeX commands removed
    """
    # Remove LaTeX commands except for \cite and \ref
    return re.sub(r"\\(?!cite|ref)[a-zA-Z]+(\[[^\]]+\])?(\{[^\}]+\})?", "", text)

def check_terms_by_GPT(
    input_path: str,
    model: Optional[str] = None,
    verbose: bool = False,
) -> str:
    """
    Check terminology consistency in a TeX file using GPT.
    
    Args:
        input_path: Path to the input TeX file
        model: GPT model to use (defaults to GPT_MODEL_ADVANCED)
        verbose: Whether to print verbose output
        
    Returns:
        The feedback text with terminology issues
        
    Raises:
        FileNotFoundError: If the input file does not exist
        IOError: If there's an error reading the file
    """
    # Load the TeX file
    logger.info(f"Loading TeX file: {input_path}")
    text = load_tex(input_path)
    
    # Preprocess the text to remove LaTeX commands
    processed_text = preprocess_tex(text)
    
    # Load the term checking prompt
    prompt_text = load_prompt("check_terms")
    
    # Initialize GPT client
    gpt = GPTClient(
        model=model or GPT_MODEL_ADVANCED,
        verbose=verbose
    )
    
    # Check terminology
    logger.info(f"Checking terminology in {input_path} with {gpt.model}...")
    feedback = gpt(prompt_text + processed_text)
    
    # Print the feedback
    print(feedback)
    
    return feedback

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Check terminology consistency in TeX files")
    parser.add_argument("--input", "-i", required=True, help="Input file path")
    parser.add_argument("--model", "-m", help="GPT model to use")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    try:
        check_terms_by_GPT(
            args.input,
            args.model,
            args.verbose
        )
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        if args.verbose:
            logger.exception("Detailed error information:")
        sys.exit(1)