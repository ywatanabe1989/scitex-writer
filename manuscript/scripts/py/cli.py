#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-05 11:50:00 (ywatanabe)"

"""
Command-line interface for SciTex scripts
"""

import argparse
import os
import sys
import logging
from typing import Dict, Any, Optional, List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("cli")

def setup_common_args(parser: argparse.ArgumentParser) -> None:
    """
    Add common arguments to a parser.
    
    Args:
        parser: The argparse parser to add arguments to
    """
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--model", "-m",
        help="GPT model to use (default depends on the script)"
    )

def setup_file_args(parser: argparse.ArgumentParser) -> None:
    """
    Add file-related arguments to a parser.
    
    Args:
        parser: The argparse parser to add arguments to
    """
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Input file path"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path (defaults to overwriting input)"
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Disable automatic backup of input files"
    )

def create_revise_parser(subparsers) -> None:
    """
    Create a parser for the 'revise' command.
    
    Args:
        subparsers: The subparsers object from argparse
    """
    parser = subparsers.add_parser(
        "revise",
        help="Revise a TeX file using GPT"
    )
    setup_common_args(parser)
    setup_file_args(parser)
    parser.add_argument(
        "--system-message",
        help="Custom system message for GPT"
    )

def create_check_terms_parser(subparsers) -> None:
    """
    Create a parser for the 'check-terms' command.
    
    Args:
        subparsers: The subparsers object from argparse
    """
    parser = subparsers.add_parser(
        "check-terms",
        help="Check terminology consistency in a TeX file"
    )
    setup_common_args(parser)
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Input file path"
    )

def create_insert_citations_parser(subparsers) -> None:
    """
    Create a parser for the 'insert-citations' command.
    
    Args:
        subparsers: The subparsers object from argparse
    """
    parser = subparsers.add_parser(
        "insert-citations",
        help="Insert citations in a TeX file"
    )
    setup_common_args(parser)
    setup_file_args(parser)
    parser.add_argument(
        "--bibliography", "-b",
        required=True,
        help="Bibliography file path"
    )

def create_parser() -> argparse.ArgumentParser:
    """
    Create an argument parser for SciTex commands.
    
    Returns:
        An argparse parser
    """
    parser = argparse.ArgumentParser(
        description="SciTex - AI-assisted scientific manuscript preparation",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(
        title="commands",
        dest="command",
        help="Command to execute"
    )
    
    # Add command parsers
    create_revise_parser(subparsers)
    create_check_terms_parser(subparsers)
    create_insert_citations_parser(subparsers)
    
    return parser

def parse_args(args: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Parse command-line arguments.
    
    Args:
        args: Command-line arguments (defaults to sys.argv[1:])
        
    Returns:
        A dictionary of parsed arguments
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    # Convert to dictionary
    args_dict = vars(parsed_args)
    
    # Handle missing command
    if not args_dict.get("command"):
        parser.print_help()
        sys.exit(1)
    
    return args_dict

def validate_file_paths(args: Dict[str, Any]) -> None:
    """
    Validate file paths in arguments.
    
    Args:
        args: Dictionary of parsed arguments
        
    Raises:
        FileNotFoundError: If a required file does not exist
    """
    # Check input file
    if "input" in args and not os.path.exists(args["input"]):
        raise FileNotFoundError(f"Input file not found: {args['input']}")
    
    # Check bibliography file
    if "bibliography" in args and not os.path.exists(args["bibliography"]):
        raise FileNotFoundError(f"Bibliography file not found: {args['bibliography']}")
    
    # Set default output path if not provided
    if "input" in args and "output" not in args:
        args["output"] = args["input"]

def run_command(args: Dict[str, Any]) -> None:
    """
    Run the command specified in the arguments.
    
    Args:
        args: Dictionary of parsed arguments
    """
    command = args.get("command")
    
    if command == "revise":
        from revise import revise_by_GPT
        revise_by_GPT(args["input"], args.get("output"), args.get("model"))
    
    elif command == "check-terms":
        from check_terms import check_terms_by_GPT
        check_terms_by_GPT(args["input"], args.get("model"))
    
    elif command == "insert-citations":
        from insert_citations import insert_citations
        insert_citations(args["input"], args["bibliography"], args.get("output"), args.get("model"))

def main() -> None:
    """Main entry point for the CLI."""
    try:
        args = parse_args()
        validate_file_paths(args)
        run_command(args)
    except FileNotFoundError as e:
        logger.error(str(e))
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