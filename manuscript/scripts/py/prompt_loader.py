#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-05 11:45:00 (ywatanabe)"

"""
Prompt loader for SciTex
"""

import os
from typing import Dict, Optional

from config import TEMPLATES_DIR

def load_prompt(template_name: str) -> str:
    """
    Load a prompt template from the templates directory.
    
    Args:
        template_name: Name of the template file (without .txt extension)
        
    Returns:
        The content of the template file as a string
        
    Raises:
        FileNotFoundError: If the template file does not exist
        IOError: If there's an error reading the template file
    """
    template_path = os.path.join(TEMPLATES_DIR, f"{template_name}.txt")
    
    try:
        with open(template_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Template file not found: {template_path}")
    except IOError as e:
        raise IOError(f"Error reading template file {template_path}: {str(e)}")

def format_prompt(template_name: str, **kwargs) -> str:
    """
    Load and format a prompt template with the provided variables.
    
    Args:
        template_name: Name of the template file (without .txt extension)
        **kwargs: Variables to format the template with
        
    Returns:
        The formatted template as a string
        
    Raises:
        KeyError: If a required variable is missing
        ValueError: If there's an error formatting the template
    """
    template = load_prompt(template_name)
    
    try:
        return template.format(**kwargs)
    except KeyError as e:
        raise KeyError(f"Missing required variable for template {template_name}: {str(e)}")
    except ValueError as e:
        raise ValueError(f"Error formatting template {template_name}: {str(e)}")

# Available prompt templates
AVAILABLE_TEMPLATES = {
    "revise": "Revise TeX content for grammar and style",
    "check_terms": "Check terminology consistency in TeX content",
    "insert_citations": "Insert citations in TeX content using bibliography",
}

def list_templates() -> Dict[str, str]:
    """
    List available prompt templates.
    
    Returns:
        A dictionary of template names and descriptions
    """
    return AVAILABLE_TEMPLATES