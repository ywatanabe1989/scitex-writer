#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-05 12:40:00 (ywatanabe)"

"""
Unit tests for gpt_client.py
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from gpt_client import GPTClient
from config import GPT_MODEL_DEFAULT, GPT_MODEL_ADVANCED

class TestGPTClient(unittest.TestCase):
    """Test cases for gpt_client.py"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock API key
        self.api_key_patcher = patch("gpt_client.get_api_key")
        self.mock_get_api_key = self.api_key_patcher.start()
        self.mock_get_api_key.return_value = "test_api_key"
        
        # Mock OpenAI client
        self.openai_client_patcher = patch("gpt_client.OpenAI")
        self.mock_openai_client = self.openai_client_patcher.start()
        
        # Create a mock response
        self.mock_response = MagicMock()
        self.mock_response.choices = [MagicMock()]
        self.mock_response.choices[0].message.content = "Test response"
        
        # Set up the mock client to return the mock response
        self.mock_client_instance = MagicMock()
        self.mock_client_instance.chat.completions.create.return_value = self.mock_response
        self.mock_openai_client.return_value = self.mock_client_instance
    
    def tearDown(self):
        """Tear down test fixtures"""
        self.api_key_patcher.stop()
        self.openai_client_patcher.stop()
    
    def test_init(self):
        """Test initialization of GPTClient"""
        # Test with default parameters
        client = GPTClient()
        self.assertEqual(client.model, GPT_MODEL_DEFAULT)
        self.assertEqual(client.system_setting, "")
        self.assertEqual(client.max_history, 10)
        self.assertEqual(client.verbose, False)
        self.assertEqual(client.counter, 0)
        self.assertEqual(len(client.chat_history), 0)
        
        # Test with custom parameters
        client = GPTClient(
            system_setting="Test system",
            model=GPT_MODEL_ADVANCED,
            max_history=5,
            verbose=True
        )
        self.assertEqual(client.model, GPT_MODEL_ADVANCED)
        self.assertEqual(client.system_setting, "Test system")
        self.assertEqual(client.max_history, 5)
        self.assertEqual(client.verbose, True)
        self.assertEqual(client.counter, 0)
        self.assertEqual(len(client.chat_history), 1)
        self.assertEqual(client.chat_history[0]["role"], "system")
        self.assertEqual(client.chat_history[0]["content"], "Test system")
    
    def test_call(self):
        """Test calling the client with a message"""
        client = GPTClient()
        
        # Test with a simple message
        response = client("Test message")
        
        # Check that the response is correct
        self.assertEqual(response, "Test response")
        
        # Check that the chat history was updated
        self.assertEqual(len(client.chat_history), 2)
        self.assertEqual(client.chat_history[0]["role"], "user")
        self.assertEqual(client.chat_history[0]["content"], "Test message")
        self.assertEqual(client.chat_history[1]["role"], "assistant")
        self.assertEqual(client.chat_history[1]["content"], "Test response")
        
        # Check that the counter was incremented
        self.assertEqual(client.counter, 1)
        
        # Check that the OpenAI API was called correctly
        self.mock_client_instance.chat.completions.create.assert_called_once_with(
            model=GPT_MODEL_DEFAULT,
            messages=client.chat_history,
            stream=False
        )
        
        # Test with None input
        with self.assertRaises(ValueError):
            client(None)
    
    def test_openai_errors(self):
        """Test handling of OpenAI errors"""
        client = GPTClient()
        
        # Test with Rate Limit Error
        self.mock_client_instance.chat.completions.create.side_effect = \
            MagicMock(side_effect=openai.RateLimitError("Rate limit exceeded"))
        
        with self.assertRaises(openai.RateLimitError):
            client("Test message")
        
        # Test with API Error
        self.mock_client_instance.chat.completions.create.side_effect = \
            MagicMock(side_effect=openai.APIError("API error"))
        
        with self.assertRaises(openai.APIError):
            client("Test message")
        
        # Test with generic exception
        self.mock_client_instance.chat.completions.create.side_effect = \
            MagicMock(side_effect=Exception("Generic error"))
        
        with self.assertRaises(Exception):
            client("Test message")
    
    def test_clear_history(self):
        """Test clearing the chat history"""
        # Test with system message
        client = GPTClient(system_setting="Test system")
        client("Test message")
        self.assertEqual(len(client.chat_history), 3)
        
        client.clear_history()
        self.assertEqual(len(client.chat_history), 1)
        self.assertEqual(client.chat_history[0]["role"], "system")
        
        # Test without system message
        client = GPTClient()
        client("Test message")
        self.assertEqual(len(client.chat_history), 2)
        
        client.clear_history()
        self.assertEqual(len(client.chat_history), 0)
    
    def test_manage_history(self):
        """Test managing chat history size"""
        # Test with system message
        client = GPTClient(system_setting="Test system", max_history=3)
        
        # Add more messages than max_history
        for i in range(5):
            client(f"Test message {i}")
        
        # Check that the history was trimmed correctly
        self.assertEqual(len(client.chat_history), 4)  # 1 system + 3 latest
        self.assertEqual(client.chat_history[0]["role"], "system")
        self.assertEqual(client.chat_history[1]["content"], "Test message 3")
        self.assertEqual(client.chat_history[3]["content"], "Test response")
        
        # Test without system message
        client = GPTClient(max_history=3)
        
        # Add more messages than max_history
        for i in range(5):
            client(f"Test message {i}")
        
        # Check that the history was trimmed correctly
        self.assertEqual(len(client.chat_history), 3)
        self.assertEqual(client.chat_history[0]["content"], "Test message 4")
        self.assertEqual(client.chat_history[2]["content"], "Test response")

# Import here to avoid actual API calls during tests
import openai

if __name__ == "__main__":
    unittest.main()