"""Test fixtures for SciTex tests."""

import os

# Get the fixtures directory path
FIXTURES_DIR = os.path.dirname(os.path.abspath(__file__))

# Sample file paths
SAMPLE_TEX_PATH = os.path.join(FIXTURES_DIR, "sample_tex.tex")
SAMPLE_BIB_PATH = os.path.join(FIXTURES_DIR, "sample_bib.bib")
SAMPLE_PROMPT_PATH = os.path.join(FIXTURES_DIR, "sample_prompt.txt")

# Helper functions for tests
def get_fixture_path(filename):
    """
    Get the absolute path to a fixture file.
    
    Args:
        filename: Name of the fixture file
        
    Returns:
        Absolute path to the fixture file
    """
    return os.path.join(FIXTURES_DIR, filename)

def load_fixture(filename):
    """
    Load the content of a fixture file.
    
    Args:
        filename: Name of the fixture file
        
    Returns:
        Content of the fixture file as a string
    """
    path = get_fixture_path(filename)
    with open(path, "r", encoding="utf-8") as file:
        return file.read()