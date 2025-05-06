#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-06 11:45:00 (system)"
# File: /home/ywatanabe/proj/SciTex/scripts/py/scitex_config.py
# ----------------------------------------

"""
Centralized configuration management for SciTex

This module provides functionality to load, access, and manage
configuration settings for the SciTex system from the central
YAML configuration file.
"""

import os
import sys
import yaml
from pathlib import Path
import logging
from typing import Any, Dict, Optional, Union

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scitex_config")

# Default config file location
DEFAULT_CONFIG_PATH = Path(__file__).parent.parent.parent / "config.yaml"


class ConfigurationError(Exception):
    """Exception raised for configuration errors."""
    pass


class SciTexConfig:
    """
    Configuration manager for SciTex system.
    
    Loads configuration from a YAML file and provides
    methods to access configuration values.
    """
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration file.
                         If None, the default path is used.
        """
        self.config_path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
        self.config = self._load_config()
        self._setup_logging()
        
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file.
        
        Returns:
            Dict containing the configuration values.
            
        Raises:
            ConfigurationError: If the config file cannot be read or parsed.
        """
        try:
            if not self.config_path.exists():
                logger.warning(f"Config file not found: {self.config_path}")
                logger.info("Using default configuration values")
                return self._default_config()
                
            with open(self.config_path, "r") as f:
                config = yaml.safe_load(f)
                logger.info(f"Loaded configuration from {self.config_path}")
                return config
        except (yaml.YAMLError, OSError) as e:
            logger.error(f"Error loading configuration: {str(e)}")
            raise ConfigurationError(f"Failed to load configuration: {str(e)}")
            
    def _default_config(self) -> Dict[str, Any]:
        """
        Provide default configuration values.
        
        Returns:
            Dict containing default configuration values.
        """
        # Minimal default configuration
        return {
            "paths": {
                "scripts_dir": "./scripts",
                "python_scripts": "./scripts/py",
                "shell_scripts": "./scripts/sh",
            },
            "latex": {
                "compiler": "pdflatex",
                "flags": "-interaction=nonstopmode",
            },
            "figures": {
                "formats": ["tif", "png", "jpg", "pdf"],
                "dpi": 300,
            },
            "ai": {
                "default_model": "gpt-4o-mini",
            },
            "logging": {
                "level": "info",
            }
        }
        
    def _setup_logging(self) -> None:
        """Configure logging based on configuration settings."""
        log_config = self.config.get("logging", {})
        log_level = log_config.get("level", "info").upper()
        log_format = log_config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        
        # Set the log level
        numeric_level = getattr(logging, log_level, logging.INFO)
        logger.setLevel(numeric_level)
        
        # Set up file logging if specified
        log_file = log_config.get("file")
        if log_file:
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
                
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(logging.Formatter(log_format))
            logger.addHandler(file_handler)
    
    def get(self, path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            path: Dot-separated path to the configuration value.
                 For example, "latex.compiler" to get the LaTeX compiler.
            default: Default value to return if the path is not found.
            
        Returns:
            The configuration value, or the default if not found.
        """
        current = self.config
        for part in path.split('.'):
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        return current
    
    def get_path(self, path: str, relative_to_config: bool = True) -> Path:
        """
        Get a filesystem path from the configuration.
        
        Args:
            path: Dot-separated path to the configuration value.
            relative_to_config: If True, paths are interpreted as
                                relative to the config file directory.
                                
        Returns:
            Path object for the specified path.
        """
        path_str = self.get(path)
        if not path_str:
            raise ConfigurationError(f"Path not found in configuration: {path}")
            
        path_obj = Path(path_str)
        
        # If path is relative and relative_to_config is True,
        # interpret it as relative to the config file directory
        if relative_to_config and not path_obj.is_absolute():
            return self.config_path.parent / path_obj
            
        return path_obj
    
    def set(self, path: str, value: Any) -> None:
        """
        Set a configuration value using dot notation.
        
        Args:
            path: Dot-separated path to the configuration value.
            value: Value to set.
            
        Note:
            This only changes the in-memory configuration.
            Call save() to write changes to disk.
        """
        parts = path.split('.')
        current = self.config
        
        # Navigate to the parent of the target key
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Set the value
        current[parts[-1]] = value
        
    def save(self, path: Optional[Union[str, Path]] = None) -> None:
        """
        Save the current configuration to a YAML file.
        
        Args:
            path: Path to save the configuration to.
                  If None, uses the path the config was loaded from.
                  
        Raises:
            ConfigurationError: If the config cannot be saved.
        """
        save_path = Path(path) if path else self.config_path
        
        try:
            # Create directory if it doesn't exist
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(save_path, "w") as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
                logger.info(f"Configuration saved to {save_path}")
        except (yaml.YAMLError, OSError) as e:
            logger.error(f"Error saving configuration: {str(e)}")
            raise ConfigurationError(f"Failed to save configuration: {str(e)}")


# Create a global config instance
_config_instance = None

def get_config(reload: bool = False, config_path: Optional[Union[str, Path]] = None) -> SciTexConfig:
    """
    Get the global configuration instance.
    
    Args:
        reload: If True, reload the configuration even if already loaded.
        config_path: Path to the configuration file.
                    If None, the default path is used.
                    
    Returns:
        SciTexConfig instance.
    """
    global _config_instance
    if _config_instance is None or reload:
        _config_instance = SciTexConfig(config_path)
    return _config_instance


# Helper functions for common configuration access patterns
def get_latex_compiler() -> str:
    """Get the configured LaTeX compiler."""
    return get_config().get("latex.compiler", "pdflatex")

def get_latex_flags() -> str:
    """Get the configured LaTeX compiler flags."""
    return get_config().get("latex.flags", "-interaction=nonstopmode")

def get_figure_formats() -> list:
    """Get the list of supported figure formats."""
    return get_config().get("figures.formats", ["tif", "png", "jpg", "pdf"])

def get_scripts_dir() -> Path:
    """Get the scripts directory path."""
    return get_config().get_path("paths.scripts_dir")

def get_api_key() -> str:
    """
    Get the API key for AI integration.
    
    Returns:
        str: The API key.
        
    Raises:
        ConfigurationError: If the API key is not set.
    """
    env_var = get_config().get("ai.api_key_env_var", "OPENAI_API_KEY")
    api_key = os.getenv(env_var)
    
    if not api_key:
        raise ConfigurationError(
            f"The API key must be set as environment variable '{env_var}'. "
            "Please set this variable with your API key."
        )
    
    return api_key

def get_default_model() -> str:
    """Get the default AI model."""
    return get_config().get("ai.default_model", "gpt-4o-mini")


if __name__ == "__main__":
    # Simple demonstration of usage when run as a script
    print("SciTex Configuration")
    print("-------------------")
    
    config = get_config()
    
    # Print some configuration values
    print(f"LaTeX Compiler: {get_latex_compiler()}")
    print(f"Figure Formats: {get_figure_formats()}")
    print(f"Default AI Model: {get_default_model()}")
    
    # Test a configuration path
    path_to_test = "paths.scripts_dir"
    print(f"{path_to_test}: {config.get(path_to_test, 'Not found')}")