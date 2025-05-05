#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-05 13:45:00 (ywatanabe)"

"""
Example script demonstrating how to use the SciTex Python API.

This script shows how to use the core modules directly for custom workflows.
"""

import os
import sys
import tempfile

# Add the SciTex scripts directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../manuscript/scripts/py")))

# Import SciTex modules
from gpt_client import GPTClient
from file_utils import load_tex, save_tex, show_diff
from prompt_loader import load_prompt, format_prompt
from config import GPT_MODEL_DEFAULT

def main():
    """Demonstrate the SciTex Python API."""
    print("SciTex Python API Demo")
    print("=====================\n")
    
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        sample_tex_path = os.path.join(temp_dir, "sample.tex")
        
        # 1. Create a sample TeX file
        print("1. Creating a sample TeX file...")
        sample_tex = """
\\section{Introduction}
This is a sample LaTeX document. It's purpose is to demonstrate the SciTex Python API.
The document has some gramatical errors and typos that will be fixed by GPT.
"""
        save_tex(sample_tex, sample_tex_path)
        print(f"   Sample file created at: {sample_tex_path}")
        
        # 2. Initialize the GPT client
        print("\n2. Initializing GPT client...")
        client = GPTClient(
            model=GPT_MODEL_DEFAULT,
            verbose=True
        )
        print(f"   Client initialized with model: {client.model}")
        
        # 3. Load the revision prompt
        print("\n3. Loading the revision prompt...")
        try:
            prompt = load_prompt("revise")
            print("   Prompt loaded successfully")
        except FileNotFoundError:
            # If the prompt file doesn't exist, create a simple prompt
            prompt = """
            You are a helpful assistant specialized in improving LaTeX documents.
            Please revise the following LaTeX document to fix any grammatical errors and typos:
            """
            print("   Using fallback prompt")
        
        # 4. Revise the text
        print("\n4. Revising the text...")
        revised_text = client(prompt + sample_tex)
        print("   Text revised successfully")
        
        # 5. Show the differences
        print("\n5. Showing differences between original and revised text:")
        diff = show_diff(sample_tex, revised_text)
        print(diff)
        
        # 6. Save the revised text
        revised_path = os.path.join(temp_dir, "revised.tex")
        save_tex(revised_text, revised_path)
        print(f"\n6. Revised text saved to: {revised_path}")
        
        # 7. Demonstrate formatting a prompt with variables
        print("\n7. Demonstrating prompt formatting with variables...")
        try:
            formatted_prompt = format_prompt(
                "insert_citations",
                tex_content="Sample content",
                bib_content="Sample bibliography"
            )
            print("   Prompt formatted successfully")
        except (FileNotFoundError, KeyError):
            # If the prompt file doesn't exist or has wrong variables
            print("   (Skipped due to missing prompt template)")
        
        print("\nDemo complete!")

if __name__ == "__main__":
    main()