#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-11 (ywatanabe)"


"""
Custom logging setup for scitex-writer scripts

Provides color-coded logging with custom levels matching scitex.logging conventions.
This module is standalone and only depends on stdlib.

Dependencies:
  - packages:
    - logging (stdlib)

IO:
  - input-files: None
  - output-files: None (logs to stderr)
"""

import logging

# Add custom log levels (matching scitex conventions)
SUCCESS = 31  # Between WARNING (30) and ERROR (40)
FAIL = 35  # Between WARNING (30) and ERROR (40)

# Add custom levels with 4-character abbreviations
logging.addLevelName(SUCCESS, "SUCC")
logging.addLevelName(FAIL, "FAIL")
logging.addLevelName(logging.DEBUG, "DEBU")
logging.addLevelName(logging.INFO, "INFO")
logging.addLevelName(logging.WARNING, "WARN")
logging.addLevelName(logging.ERROR, "ERRO")
logging.addLevelName(logging.CRITICAL, "CRIT")


def success(self, message, *args, **kwargs):
    """Log success message."""
    if self.isEnabledFor(SUCCESS):
        self._log(SUCCESS, message, args, **kwargs)


def fail(self, message, *args, **kwargs):
    """Log failure message."""
    if self.isEnabledFor(FAIL):
        self._log(FAIL, message, args, **kwargs)


# Add methods to Logger class
logging.Logger.success = success
logging.Logger.fail = fail


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support - colors entire message."""

    COLORS = {
        "DEBU": "\033[90m",  # Grey
        "INFO": "\033[90m",  # Grey
        "SUCC": "\033[32m",  # Green
        "WARN": "\033[33m",  # Yellow
        "FAIL": "\033[91m",  # Light Red
        "ERRO": "\033[31m",  # Red
        "CRIT": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record):
        # Format the message first
        formatted = super().format(record)

        # Apply color to entire message based on level
        levelname = record.levelname
        if levelname in self.COLORS:
            color = self.COLORS[levelname]
            return f"{color}{formatted}{self.RESET}"

        return formatted


def setup_logger(name: str, verbose: bool = False) -> logging.Logger:
    """Set up logger with custom formatting and levels.

    Args:
        name: Logger name
        verbose: Enable verbose logging

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    # Remove existing handlers
    logger.handlers = []

    # Create console handler with formatting
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG if verbose else logging.INFO)

    # Use colored formatter
    formatter = ColoredFormatter("%(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def getLogger(name: str, verbose: bool = False) -> logging.Logger:
    """Get a logger with custom scitex formatting.

    This is a convenience wrapper around setup_logger that provides
    a similar interface to logging.getLogger() from stdlib.

    Args:
        name: Logger name (typically __name__)
        verbose: Enable verbose logging (default: False)

    Returns:
        Configured logger instance with custom levels and colors
    """
    return setup_logger(name, verbose)


# EOF
