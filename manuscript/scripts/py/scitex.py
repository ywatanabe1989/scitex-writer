#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-05 12:15:00 (ywatanabe)"

"""
SciTex - AI-assisted scientific manuscript preparation system

This script provides a unified command-line interface for SciTex tools.
"""

import os
import sys
import logging

from config import init_env
from cli import parse_args, validate_file_paths

# Initialize environment
init_env()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("scitex")

def main() -> None:
    """Main entry point for SciTex CLI."""
    try:
        # Parse command-line arguments
        args = parse_args()
        
        # Validate file paths
        validate_file_paths(args)
        
        # Set verbosity level
        if args.get("verbose"):
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Execute the requested command
        command = args.get("command")
        
        if command == "revise":
            from revise import revise_by_GPT
            revise_by_GPT(
                args["input"],
                args.get("output"),
                args.get("model"),
                not args.get("no_backup", False),
                args.get("verbose", False)
            )
        
        elif command == "check-terms":
            from check_terms import check_terms_by_GPT
            check_terms_by_GPT(
                args["input"],
                args.get("model"),
                args.get("verbose", False)
            )
        
        elif command == "insert-citations":
            from insert_citations import insert_citations
            insert_citations(
                args["input"],
                args["bibliography"],
                args.get("output"),
                args.get("model"),
                not args.get("no_backup", False),
                args.get("verbose", False),
                not args.get("no_diff", False)
            )
        
        else:
            logger.error(f"Unknown command: {command}")
            sys.exit(1)
        
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        if "verbose" in args and args["verbose"]:
            logger.exception("Detailed error information:")
        sys.exit(1)

if __name__ == "__main__":
    main()