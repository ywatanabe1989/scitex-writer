#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-05 12:35:00 (ywatanabe)"

"""
Unit tests for prompt_loader.py
"""

import os
import sys
import unittest
from unittest.mock import patch, mock_open

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from prompt_loader import (
    load_prompt,
    format_prompt,
    list_templates,
    AVAILABLE_TEMPLATES
)
from tests.fixtures import SAMPLE_PROMPT_PATH, load_fixture

class TestPromptLoader(unittest.TestCase):
    """Test cases for prompt_loader.py"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_prompt = load_fixture("sample_prompt.txt")
        
        # Create a patch for the TEMPLATES_DIR in config
        self.templates_dir_patcher = patch("prompt_loader.TEMPLATES_DIR", 
                                          os.path.dirname(SAMPLE_PROMPT_PATH))
        self.mock_templates_dir = self.templates_dir_patcher.start()
    
    def tearDown(self):
        """Tear down test fixtures"""
        self.templates_dir_patcher.stop()
    
    def test_load_prompt(self):
        """Test loading a prompt template"""
        # Test with existing template
        prompt = load_prompt("sample_prompt")
        self.assertEqual(prompt, self.sample_prompt)
        
        # Test with non-existent template
        with self.assertRaises(FileNotFoundError):
            load_prompt("non_existent_template")
        
        # Test with I/O error
        with patch("builtins.open", mock_open()) as mock_file:
            mock_file.side_effect = IOError("Mock I/O error")
            with self.assertRaises(IOError):
                load_prompt("sample_prompt")
    
    def test_format_prompt(self):
        """Test formatting a prompt template with variables"""
        # Test with valid variables
        formatted_prompt = format_prompt(
            "sample_prompt",
            variable1="value1",
            variable2="value2",
            content="Sample content"
        )
        
        # Check that the variables were correctly replaced
        self.assertIn("value1", formatted_prompt)
        self.assertIn("value2", formatted_prompt)
        self.assertIn("Sample content", formatted_prompt)
        self.assertNotIn("{variable1}", formatted_prompt)
        self.assertNotIn("{variable2}", formatted_prompt)
        self.assertNotIn("{content}", formatted_prompt)
        
        # Test with missing variable
        with self.assertRaises(KeyError):
            format_prompt("sample_prompt", variable1="value1")
        
        # Test with formatting error
        with patch("prompt_loader.load_prompt") as mock_load_prompt:
            # Create a template with an invalid format specifier
            mock_load_prompt.return_value = "Invalid {0} format"
            with self.assertRaises(ValueError):
                format_prompt("invalid_template", variable1="value1")
    
    def test_list_templates(self):
        """Test listing available templates"""
        templates = list_templates()
        
        # Check that the function returns the expected dictionary
        self.assertEqual(templates, AVAILABLE_TEMPLATES)
        
        # Check that templates dictionary is not empty
        self.assertTrue(templates)
        
        # Check for expected templates
        self.assertIn("revise", templates)
        self.assertIn("check_terms", templates)
        self.assertIn("insert_citations", templates)

if __name__ == "__main__":
    unittest.main()