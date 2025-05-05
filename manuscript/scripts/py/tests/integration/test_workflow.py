#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-05 12:45:00 (ywatanabe)"

"""
Integration tests for SciTex workflow
"""

import os
import sys
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import modules to test
from revise import revise_by_GPT
from check_terms import check_terms_by_GPT
from insert_citations import insert_citations
from gpt_client import GPTClient
from file_utils import load_tex, save_tex
from tests.fixtures import SAMPLE_TEX_PATH, SAMPLE_BIB_PATH, load_fixture

@unittest.skipIf('OPENAI_API_KEY' not in os.environ, 
                 "Skipping integration tests because OPENAI_API_KEY is not set")
class TestMockedWorkflow(unittest.TestCase):
    """Integration tests for SciTex workflow using mocked GPT responses"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Copy sample files to temp directory
        self.test_tex_path = os.path.join(self.temp_dir, "test.tex")
        self.test_bib_path = os.path.join(self.temp_dir, "test.bib")
        
        # Load and save sample files to temp directory
        self.sample_tex = load_fixture("sample_tex.tex")
        self.sample_bib = load_fixture("sample_bib.bib")
        save_tex(self.sample_tex, self.test_tex_path)
        save_tex(self.sample_bib, self.test_bib_path)
        
        # Mock GPT client
        self.gpt_client_patcher = patch("gpt_client.GPTClient")
        self.mock_gpt_client = self.gpt_client_patcher.start()
        
        # Create mock instance and responses
        self.mock_instance = MagicMock()
        self.mock_gpt_client.return_value = self.mock_instance
        
        # Mock responses for different operations
        self.mock_instance.return_value = MagicMock(side_effect=self._mock_gpt_response)
    
    def tearDown(self):
        """Tear down test fixtures"""
        # Remove temp directory
        shutil.rmtree(self.temp_dir)
        
        # Stop patches
        self.gpt_client_patcher.stop()
    
    def _mock_gpt_response(self, prompt):
        """Generate mock responses based on the prompt content"""
        if "revise" in prompt.lower():
            return "Revised: " + self.sample_tex
        elif "check" in prompt.lower() and "term" in prompt.lower():
            return "Term usage was checked and no mistakes were found."
        elif "citation" in prompt.lower():
            # Add a citation to the text
            cited_text = self.sample_tex.replace(
                "Scientific writing requires precise language",
                "Scientific writing requires precise language \\cite{smith2020example}"
            )
            return cited_text
        else:
            return "Mock response for: " + prompt[:50] + "..."
    
    def test_revise_workflow(self):
        """Test the revision workflow"""
        # Run the revision
        revised_text = revise_by_GPT(
            self.test_tex_path,
            verbose=True
        )
        
        # Check that GPT was called with the correct prompt
        self.mock_instance.assert_called()
        call_args = self.mock_instance.call_args[0][0]
        self.assertIn("revise", call_args.lower())
        
        # Check that the revised text contains the expected content
        self.assertIn("Revised:", revised_text)
    
    def test_check_terms_workflow(self):
        """Test the terminology checking workflow"""
        # Run the terminology check
        feedback = check_terms_by_GPT(
            self.test_tex_path,
            verbose=True
        )
        
        # Check that GPT was called with the correct prompt
        self.mock_instance.assert_called()
        call_args = self.mock_instance.call_args[0][0]
        self.assertIn("check", call_args.lower())
        self.assertIn("term", call_args.lower())
        
        # Check that the feedback contains the expected content
        self.assertEqual(feedback, "Term usage was checked and no mistakes were found.")
    
    def test_insert_citations_workflow(self):
        """Test the citation insertion workflow"""
        # Run the citation insertion
        with patch("insert_citations.show_diff") as mock_show_diff:
            modified_text = insert_citations(
                self.test_tex_path,
                self.test_bib_path,
                verbose=True
            )
        
        # Check that GPT was called with the correct prompt
        self.mock_instance.assert_called()
        call_args = self.mock_instance.call_args[0][0]
        self.assertIn("citation", call_args.lower())
        
        # Check that the modified text contains the inserted citation
        self.assertIn("\\cite{smith2020example}", modified_text)
    
    def test_full_workflow(self):
        """Test the full workflow (revise, check terms, insert citations)"""
        # Run the full workflow
        # 1. Revise
        revise_by_GPT(self.test_tex_path)
        
        # 2. Check terms
        check_terms_by_GPT(self.test_tex_path)
        
        # 3. Insert citations
        with patch("insert_citations.show_diff"):
            insert_citations(self.test_tex_path, self.test_bib_path)
        
        # Check the final file
        final_text = load_tex(self.test_tex_path)
        
        # Check that the text contains the expected content
        self.assertIn("Revised:", final_text)
        self.assertIn("\\cite{smith2020example}", final_text)

if __name__ == "__main__":
    unittest.main()