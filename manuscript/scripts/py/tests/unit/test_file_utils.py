#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-05 12:30:00 (ywatanabe)"

"""
Unit tests for file_utils.py
"""

import os
import sys
import unittest
import tempfile
import shutil
from unittest.mock import patch, mock_open

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from file_utils import (
    load_tex,
    save_tex,
    back_up,
    show_diff,
    ensure_dir,
    get_file_extension
)
from tests.fixtures import SAMPLE_TEX_PATH, load_fixture

class TestFileUtils(unittest.TestCase):
    """Test cases for file_utils.py"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.sample_content = load_fixture("sample_tex.tex")
        self.test_file_path = os.path.join(self.temp_dir, "test_file.tex")
        
        # Create a test file
        with open(self.test_file_path, "w", encoding="utf-8") as file:
            file.write(self.sample_content)
    
    def tearDown(self):
        """Tear down test fixtures"""
        # Remove temporary directory and its contents
        shutil.rmtree(self.temp_dir)
    
    def test_load_tex(self):
        """Test loading TeX content from a file"""
        # Test with existing file
        content = load_tex(self.test_file_path)
        self.assertEqual(content, self.sample_content)
        
        # Test with non-existent file
        non_existent_path = os.path.join(self.temp_dir, "non_existent.tex")
        with self.assertRaises(FileNotFoundError):
            load_tex(non_existent_path)
    
    def test_save_tex(self):
        """Test saving TeX content to a file"""
        new_content = "New test content"
        new_file_path = os.path.join(self.temp_dir, "new_file.tex")
        
        # Save content to a new file
        save_tex(new_content, new_file_path)
        
        # Check that the file was created with the correct content
        with open(new_file_path, "r", encoding="utf-8") as file:
            saved_content = file.read()
        
        self.assertEqual(saved_content, new_content)
        
        # Test with I/O error
        with patch("builtins.open", mock_open()) as mock_file:
            mock_file.side_effect = IOError("Mock I/O error")
            with self.assertRaises(IOError):
                save_tex(new_content, new_file_path)
    
    def test_back_up(self):
        """Test backing up a file"""
        # Test with existing file
        backup_path = back_up(self.test_file_path)
        
        # Check that the backup directory was created
        backup_dir = os.path.join(self.temp_dir, ".old")
        self.assertTrue(os.path.exists(backup_dir))
        
        # Check that the backup file was created with the correct content
        self.assertTrue(os.path.exists(backup_path))
        with open(backup_path, "r", encoding="utf-8") as file:
            backup_content = file.read()
        
        self.assertEqual(backup_content, self.sample_content)
        
        # Test with non-existent file
        non_existent_path = os.path.join(self.temp_dir, "non_existent.tex")
        with self.assertRaises(FileNotFoundError):
            back_up(non_existent_path)
    
    def test_show_diff(self):
        """Test showing differences between strings"""
        original_text = "This is a test."
        modified_text = "This is a modified test."
        
        # Test with bash format (default)
        diff_result = show_diff(original_text, modified_text)
        self.assertIn("This is a ", diff_result)
        self.assertIn("modified ", diff_result)
        self.assertIn("test.", diff_result)
        
        # Test with TeX format
        diff_result_tex = show_diff(original_text, modified_text, for_tex=True)
        self.assertIn("This is a ", diff_result_tex)
        self.assertIn("\\GREENSTARTS ", diff_result_tex)
        self.assertIn("modified ", diff_result_tex)
        self.assertIn("\\GREENENDS ", diff_result_tex)
        self.assertIn("test.", diff_result_tex)
    
    def test_ensure_dir(self):
        """Test ensuring a directory exists"""
        test_dir = os.path.join(self.temp_dir, "test_dir")
        
        # Test creating a new directory
        ensure_dir(test_dir)
        self.assertTrue(os.path.exists(test_dir))
        self.assertTrue(os.path.isdir(test_dir))
        
        # Test with existing directory (should not raise error)
        ensure_dir(test_dir)
        
        # Test with I/O error
        with patch("os.makedirs") as mock_makedirs:
            mock_makedirs.side_effect = IOError("Mock I/O error")
            with self.assertRaises(IOError):
                ensure_dir(os.path.join(test_dir, "another_dir"))
    
    def test_get_file_extension(self):
        """Test getting file extensions"""
        # Test with various file paths
        self.assertEqual(get_file_extension("file.txt"), "txt")
        self.assertEqual(get_file_extension("path/to/file.tex"), "tex")
        self.assertEqual(get_file_extension("file.with.multiple.dots.pdf"), "pdf")
        self.assertEqual(get_file_extension("file_no_extension"), "")
        self.assertEqual(get_file_extension(".hidden_file"), "")

if __name__ == "__main__":
    unittest.main()