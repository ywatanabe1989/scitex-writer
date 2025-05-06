#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-05 13:20:05 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTex/manuscript/scripts/python/config.py
# ----------------------------------------
import os
__FILE__ = (
    "./manuscript/scripts/python/config.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Configuration settings for SciTex
"""

import sys

# GPT Models
GPT_MODEL_DEFAULT = "gpt-4o-mini"
GPT_MODEL_ADVANCED = "gpt-4o-mini-high"

# Error messages
API_KEY_ERROR = (
    "The OpenAI API key must be set as an environment variable to use ChatGPT. "
    "Please visit https://openai.com/blog/openai-api for more information. "
    "To set the key, run the command: "
    "echo 'export OPENAI_API_KEY=\"<YOUR_OPENAI_API_KEY>\"' >> ~/.bashrc. "
    "Replace <YOUR_OPENAI_API_KEY> with your actual API key, "
    "which might look similar to 'sk**AN'."
)

# File paths
SCRIPTS_DIR = "./scripts/python/"
TEMPLATES_DIR = "./scripts/python/templates/"

# Colors for diff display
DIFF_COLORS = {
    "bash": {
        "start_green": "\x1b[38;5;16;48;5;2m",
        "end_green": "\x1b[0m",
        "start_red": "\x1b[38;5;16;48;5;1m",
        "end_red": "\x1b[0m",
    },
    "tex": {
        "start_green": "\\GREENSTARTS ",
        "end_green": "\\GREENENDS ",
        "start_red": "\\REDSTARTS ",
        "end_red": "\\REDENDS ",
    },
}


def get_api_key():
    """Get OpenAI API key from environment variables with validation."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(API_KEY_ERROR)
    return api_key


def init_env():
    """Initialize environment settings."""
    # Add scripts directory to path for imports
    if SCRIPTS_DIR not in sys.path:
        sys.path.append(SCRIPTS_DIR)

# EOF
