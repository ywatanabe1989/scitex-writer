#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-05 11:40:00 (ywatanabe)"

"""
GPT client for SciTex with improved error handling and context management
"""

import io
import sys
import logging
import contextlib
from typing import List, Dict, Union, Optional, Any

import openai
from openai import OpenAI

from config import GPT_MODEL_DEFAULT, GPT_MODEL_ADVANCED, get_api_key

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("GPTClient")

class GPTClient:
    """
    A client for interacting with OpenAI's GPT models.
    
    Features:
    - Improved error handling
    - Context management for capturing stdout
    - Configurable history management
    - Rate limiting and retry handling
    
    Example:
        client = GPTClient()
        response = client("How do I use LaTeX for scientific papers?")
    """

    def __init__(
        self,
        system_setting: str = "",
        model: str = GPT_MODEL_DEFAULT,
        api_key: Optional[str] = None,
        max_history: int = 10,
        verbose: bool = False,
    ):
        """
        Initialize a GPT client.
        
        Args:
            system_setting: System message to set the context
            model: GPT model to use
            api_key: OpenAI API key (will be fetched from env if None)
            max_history: Maximum number of messages to keep in history
            verbose: Whether to print verbose output
        """
        self.system_setting = system_setting
        self.model = model
        self.max_history = max_history
        self.verbose = verbose
        self.counter = 0
        
        # Setup API key
        openai.api_key = api_key or get_api_key()
        self.client = OpenAI()
        
        # Initialize chat history
        self.chat_history = []
        if system_setting:
            self.chat_history.append(
                {
                    "role": "system",
                    "content": system_setting,
                }
            )
    
    def __call__(self, text: str) -> str:
        """
        Send a message to the GPT model and get a response.
        
        Args:
            text: The message to send to the model
            
        Returns:
            The model's response
            
        Raises:
            openai.error.OpenAIError: If there's an error from the OpenAI API
            ValueError: If the text is None
        """
        if text is None:
            raise ValueError("Input text cannot be None")
        
        # Capture stdout to prevent openai package from printing
        with self._capture_stdout():
            try:
                self.counter += 1
                if self.verbose:
                    logger.info(f"Sending request {self.counter} to {self.model}")
                
                # Add user message to history
                self.chat_history.append({"role": "user", "content": text})
                self._manage_history()
                
                # Make API request
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.chat_history,
                    stream=False,
                )
                out_text = response.choices[0].message.content
                
                # Add assistant response to history
                self.chat_history.append({"role": "assistant", "content": out_text})
                self._manage_history()
                
                return out_text
            
            except openai.RateLimitError as e:
                logger.error(f"Rate limit exceeded: {str(e)}")
                raise
            except openai.APIError as e:
                logger.error(f"API error: {str(e)}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                raise
    
    def clear_history(self) -> None:
        """Clear chat history except for the system message."""
        if self.chat_history and self.chat_history[0].get("role") == "system":
            self.chat_history = [self.chat_history[0]]
        else:
            self.chat_history = []
    
    def _manage_history(self) -> None:
        """Manage chat history to prevent it from growing too large."""
        if not self.chat_history:
            return
            
        # Keep system message and trim the rest if needed
        if len(self.chat_history) > self.max_history + 1:
            # Keep system message
            if self.chat_history[0].get("role") == "system":
                self.chat_history = [self.chat_history[0]] + self.chat_history[-(self.max_history):]
            else:
                self.chat_history = self.chat_history[-self.max_history:]
    
    @contextlib.contextmanager
    def _capture_stdout(self):
        """Capture stdout temporarily to suppress unwanted output."""
        original_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            yield
        finally:
            sys.stdout = original_stdout